"""Pre-order, warehouse check-in and shipment consolidation tests."""

from __future__ import annotations

import io

from httpx import AsyncClient
from PIL import Image

from tests.conftest import login


def _png_bytes(color: tuple[int, int, int] = (10, 120, 200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (800, 600), color).save(buffer, format="PNG")
    return buffer.getvalue()


ASSISTED_PAYLOAD = {
    "items": [
        {
            "product_url": "https://www.amazon.co.jp/dp/B0TEST123",
            "product_name": "Camiseta Uniqlo",
            "quantity": 2,
            "unit_price_jpy": 3000,
            "options_description": "Tamanho M, cor preta",
        }
    ]
}


async def _register_client(client: AsyncClient, email: str) -> AsyncClient:
    """Register a client; the response sets the session cookies."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "senha-super-segura1",
            "full_name": "Fluxo Cliente",
            "phone": "+55-11-97777-0000",
            "accept_terms": True,
            "accept_privacy": True,
        },
    )
    assert response.status_code == 201, response.text
    return client


class TestAssistedPurchase:
    async def test_creates_pre_order_with_fee(self, client: AsyncClient) -> None:
        await _register_client(client, "fluxo@example.com")

        response = await client.post(
            "/api/v1/pre-orders/assisted", json=ASSISTED_PAYLOAD
        )

        assert response.status_code == 201
        body = response.json()
        assert body["type"] == "assisted_purchase"
        assert body["status"] == "submitted"
        assert body["total_items_price_jpy"] == 6000
        assert body["service_fee_jpy"] == 2000  # floor applied
        assert body["total_jpy"] == 8000
        assert len(body["items"]) == 1

    async def test_empty_items_are_rejected(self, client: AsyncClient) -> None:
        await _register_client(client, "vazio@example.com")

        response = await client.post(
            "/api/v1/pre-orders/assisted", json={"items": []}
        )

        assert response.status_code == 422

    async def test_proportional_fee_above_threshold(self, client: AsyncClient) -> None:
        await _register_client(client, "grande@example.com")
        payload = {
            "items": [
                {
                    "product_url": "https://www.rakuten.co.jp/1",
                    "product_name": "Item caro",
                    "quantity": 1,
                    "unit_price_jpy": 25000,
                }
            ]
        }

        response = await client.post("/api/v1/pre-orders/assisted", json=payload)

        assert response.status_code == 201
        assert response.json()["service_fee_jpy"] == 5000
        assert response.json()["total_jpy"] == 30000

    async def test_client_only_sees_own_orders(self, client: AsyncClient) -> None:
        await _register_client(client, "dono@example.com")
        await client.post("/api/v1/pre-orders/assisted", json=ASSISTED_PAYLOAD)

        # A second browser session (new client) must not see the first orders.
        from httpx import ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=client._transport.app), base_url="http://testserver"
        ) as other:
            await _register_client(other, "outro@example.com")
            response = await other.get("/api/v1/pre-orders")

        assert response.status_code == 200
        assert response.json() == []


class TestForwarding:
    async def test_receipt_is_mandatory(self, client: AsyncClient) -> None:
        await _register_client(client, "semrecibo@example.com")

        response = await client.post(
            "/api/v1/pre-orders/forwarding",
            data={"store_name": "Amazon JP", "description": "Caixa de sapatos"},
        )

        assert response.status_code == 422
        assert "receipt" in response.text.lower()

    async def test_creates_pre_order_with_receipt(self, client: AsyncClient) -> None:
        await _register_client(client, "comrecibo@example.com")

        response = await client.post(
            "/api/v1/pre-orders/forwarding",
            data={
                "store_name": "Amazon JP",
                "description": "Caixa de sapatos",
                "expected_domestic_tracking": "123456789012",
            },
            files={"receipt": ("recibo.png", _png_bytes(), "image/png")},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["type"] == "forwarding"
        assert body["store_name"] == "Amazon JP"
        assert body["receipt_url"].startswith("/uploads/")


class TestWarehouseCheckIn:
    async def test_search_by_suite_code(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")
        await _register_client(client, "busca@example.com")
        profile = await client.get("/api/v1/auth/me")
        suite_code = profile.json()["suite_code"]

        # The admin session must be restored (registering replaced the cookies).
        await login(client, admin_user.email, "admin-password1")
        response = await client.get(
            f"/api/v1/admin/warehouse/search?q={suite_code}"
        )

        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["suite_code"] == suite_code

    async def test_checkin_creates_suite_item(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")
        await _register_client(client, "checkin@example.com")
        profile = await client.get("/api/v1/auth/me")
        suite_code = profile.json()["suite_code"]

        await login(client, admin_user.email, "admin-password1")
        response = await client.post(
            "/api/v1/admin/warehouse/checkin",
            data={
                "suite_code": suite_code,
                "description": "Caixa de sapatos Nike",
                "weight_grams": "1450",
                "tracking_domestic": "123456789012",
            },
            files=[
                ("photos", ("p1.png", _png_bytes(), "image/png")),
                ("photos", ("p2.png", _png_bytes((200, 10, 10)), "image/png")),
            ],
        )

        assert response.status_code == 201
        body = response.json()
        assert body["weight_grams"] == 1450
        assert body["status"] == "in_storage"
        assert len(body["photos"]) == 2

    async def test_more_than_five_photos_are_rejected(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")
        await _register_client(client, "fotos@example.com")
        profile = await client.get("/api/v1/auth/me")
        suite_code = profile.json()["suite_code"]

        await login(client, admin_user.email, "admin-password1")
        files = [
            ("photos", (f"p{index}.png", _png_bytes(), "image/png"))
            for index in range(6)
        ]
        response = await client.post(
            "/api/v1/admin/warehouse/checkin",
            data={
                "suite_code": suite_code,
                "description": "Caixa grande",
                "weight_grams": "2000",
            },
            files=files,
        )

        assert response.status_code == 422
        assert "maximum of 5" in response.text


class TestShipmentConsolidation:
    async def test_request_requires_customs_declaration(
        self, client: AsyncClient
    ) -> None:
        await _register_client(client, "semdeclaracao@example.com")

        response = await client.post(
            "/api/v1/shipments/request",
            json={
                "suite_item_ids": ["00000000-0000-0000-0000-000000000001"],
                "shipping_method": "ems",
                "customs_declaration": {"items": []},
                "recipient_name": "Maria Silva",
                "recipient_cpf": "11144477735",
                "recipient_phone": "+55-11-90000-0000",
                "recipient_postal_code": "01310-100",
                "recipient_address": "Av. Paulista, 1000",
            },
        )

        assert response.status_code == 422

    async def test_request_rejects_invalid_cpf(self, client: AsyncClient) -> None:
        await _register_client(client, "cpfinvalido@example.com")

        response = await client.post(
            "/api/v1/shipments/request",
            json={
                "suite_item_ids": ["00000000-0000-0000-0000-000000000001"],
                "shipping_method": "ems",
                "customs_declaration": {
                    "items": [
                        {
                            "description": "T-shirt",
                            "quantity": 1,
                            "declared_value_jpy": 3000,
                        }
                    ]
                },
                "recipient_name": "Maria Silva",
                "recipient_cpf": "11111111111",
                "recipient_phone": "+55-11-90000-0000",
                "recipient_postal_code": "01310-100",
                "recipient_address": "Av. Paulista, 1000",
            },
        )

        assert response.status_code == 422

    async def test_valid_cpf_is_accepted(self) -> None:
        """A CPF with valid check digits passes validation."""
        from app.schemas.shipment import _validate_cpf

        assert _validate_cpf("111.444.777-35") == "11144477735"
        assert _validate_cpf("52998224725") == "52998224725"
