"""Security hardening tests.

Covers the five pillars of the security-hardening change:

* HttpOnly cookie sessions and token rotation
* IDOR prevention across every user scoped resource
* Magic bytes file validation and the 5 MB limit
* Anti-SSRF URL validation
* Rate limiting on the public authentication and simulator endpoints
"""

from __future__ import annotations

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.core.errors import PayloadTooLargeError, ValidationError
from app.core.rate_limit import limiter
from app.services.file_storage import FileStorage, detect_mime_type
from app.services.ssrf_validator import SSRFError, is_safe_url, validate_url
from tests.conftest import login, make_upload


# ---------------------------------------------------------------------------
# 6.1 - HttpOnly cookie authentication and token refresh
# ---------------------------------------------------------------------------
class TestCookieSession:
    async def test_login_sets_httponly_cookies(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "cookie@example.com",
                "password": "senha-super-segura1",
                "full_name": "Cookie User",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "cookie@example.com", "password": "senha-super-segura1"},
        )

        assert response.status_code == 200
        cookies = response.headers.get_list("set-cookie")
        for name in ("access_token", "refresh_token"):
            header = next(c for c in cookies if c.startswith(f"{name}="))
            assert "HttpOnly" in header
            assert "SameSite=lax" in header.replace("SameSite=Lax", "SameSite=lax")

    async def test_no_token_is_exposed_in_the_response_body(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "notoken@example.com",
                "password": "senha-super-segura1",
                "full_name": "No Token",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        body = response.json()
        assert "access_token" not in body
        assert "refresh_token" not in body
        assert "token" not in body

    async def test_the_session_cookie_authenticates_requests(
        self, client: AsyncClient
    ) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "session@example.com",
                "password": "senha-super-segura1",
                "full_name": "Session User",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        assert response.json()["email"] == "session@example.com"

    async def test_refresh_rotates_the_session(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "rotate@example.com",
                "password": "senha-super-segura1",
                "full_name": "Rotate User",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )
        original_access = client.cookies.get("access_token")
        original_refresh = client.cookies.get("refresh_token")

        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        assert client.cookies.get("refresh_token") != original_refresh
        assert client.cookies.get("access_token") != original_access

    async def test_logout_clears_the_cookies(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "bye@example.com",
                "password": "senha-super-segura1",
                "full_name": "Bye User",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        await client.post("/api/v1/auth/logout")

        assert not client.cookies.get("access_token")
        assert not client.cookies.get("refresh_token")


# ---------------------------------------------------------------------------
# 6.2 - IDOR prevention
# ---------------------------------------------------------------------------
class TestIdorPrevention:
    async def _two_clients(self, client: AsyncClient) -> tuple[str, str]:
        """Create two clients and return (suite_code_a, suite_code_b)."""
        codes = []
        for index, email in enumerate(("victim@example.com", "attacker@example.com")):
            await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "senha-super-segura1",
                    "full_name": f"User {index}",
                    "phone": "+55-11-90000-0000",
                    "accept_terms": True,
                    "accept_privacy": True,
                },
            )
            codes.append((await client.get("/api/v1/auth/me")).json()["suite_code"])
        return codes[0], codes[1]

    async def test_client_cannot_read_another_pre_order(
        self, client: AsyncClient
    ) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "victim@example.com",
                "password": "senha-super-segura1",
                "full_name": "Victim",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )
        created = await client.post(
            "/api/v1/pre-orders/assisted",
            json={
                "items": [
                    {
                        "product_url": "https://www.amazon.co.jp/dp/B0VICTIM",
                        "product_name": "Produto privado",
                        "quantity": 1,
                        "unit_price_jpy": 5000,
                    }
                ]
            },
        )
        pre_order_id = created.json()["id"]

        # A brand new session belonging to another client.
        async with AsyncClient(
            transport=ASGITransport(app=client._transport.app),
            base_url="http://testserver",
        ) as attacker:
            await attacker.post(
                "/api/v1/auth/register",
                json={
                    "email": "attacker@example.com",
                    "password": "senha-super-segura1",
                    "full_name": "Attacker",
                    "phone": "+55-11-90000-0001",
                    "accept_terms": True,
                    "accept_privacy": True,
                },
            )
            response = await attacker.get(f"/api/v1/pre-orders/{pre_order_id}")

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "permission_denied"

    async def test_client_cannot_read_another_suite_item(
        self, client: AsyncClient, admin_user
    ) -> None:
        # The admin creates an item for the victim client.
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "victim@example.com",
                "password": "senha-super-segura1",
                "full_name": "Victim",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )
        suite_code = (await client.get("/api/v1/auth/me")).json()["suite_code"]

        await login(client, admin_user.email, "admin-password1")
        created = await client.post(
            "/api/v1/admin/warehouse/checkin",
            data={
                "suite_code": suite_code,
                "description": "Caixa privada",
                "weight_grams": "800",
            },
        )
        assert created.status_code == 201
        item_id = created.json()["id"]

        async with AsyncClient(
            transport=ASGITransport(app=client._transport.app),
            base_url="http://testserver",
        ) as attacker:
            await attacker.post(
                "/api/v1/auth/register",
                json={
                    "email": "attacker@example.com",
                    "password": "senha-super-segura1",
                    "full_name": "Attacker",
                    "phone": "+55-11-90000-0001",
                    "accept_terms": True,
                    "accept_privacy": True,
                },
            )
            response = await attacker.get(f"/api/v1/suite/me/items/{item_id}")

        assert response.status_code == 403

    async def test_client_cannot_read_another_shipment(
        self, client: AsyncClient, admin_user
    ) -> None:
        # The victim client registers and receives a suite item from the admin.
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "victim@example.com",
                "password": "senha-super-segura1",
                "full_name": "Victim",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )
        suite_code = (await client.get("/api/v1/auth/me")).json()["suite_code"]

        await login(client, admin_user.email, "admin-password1")
        item = await client.post(
            "/api/v1/admin/warehouse/checkin",
            data={
                "suite_code": suite_code,
                "description": "Caixa privada",
                "weight_grams": "800",
            },
        )
        assert item.status_code == 201
        item_id = item.json()["id"]

        # The victim requests a shipment for that item.
        await login(client, "victim@example.com", "senha-super-segura1")
        created = await client.post(
            "/api/v1/shipments/request",
            json={
                "suite_item_ids": [item_id],
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
                "recipient_cpf": "11144477735",
                "recipient_phone": "+55-11-90000-0000",
                "recipient_postal_code": "01310-100",
                "recipient_address": "Av. Paulista, 1000",
            },
        )
        assert created.status_code == 201, created.text
        shipment_id = created.json()["id"]

        # A different client must not be able to read it.
        async with AsyncClient(
            transport=ASGITransport(app=client._transport.app),
            base_url="http://testserver",
        ) as attacker:
            await attacker.post(
                "/api/v1/auth/register",
                json={
                    "email": "attacker@example.com",
                    "password": "senha-super-segura1",
                    "full_name": "Attacker",
                    "phone": "+55-11-90000-0001",
                    "accept_terms": True,
                    "accept_privacy": True,
                },
            )
            response = await attacker.get(f"/api/v1/shipments/{shipment_id}")

        assert response.status_code == 403

    async def test_unknown_resource_returns_404(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "ghost@example.com",
                "password": "senha-super-segura1",
                "full_name": "Ghost",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        response = await client.get(f"/api/v1/pre-orders/{uuid.uuid4()}")

        assert response.status_code == 404

    async def test_admin_can_reach_the_admin_endpoints(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")

        response = await client.get("/api/v1/admin/dashboard")

        assert response.status_code == 200

    async def test_client_is_rejected_by_every_admin_route(
        self, client: AsyncClient
    ) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "nosy@example.com",
                "password": "senha-super-segura1",
                "full_name": "Nosy",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        for path in (
            "/api/v1/admin/dashboard",
            "/api/v1/admin/pre-orders",
            "/api/v1/admin/shipments",
            "/api/v1/admin/warehouse/search?q=JTG-9001",
        ):
            response = await client.get(path)
            assert response.status_code == 403, path


# ---------------------------------------------------------------------------
# 6.3 - Magic bytes validation
# ---------------------------------------------------------------------------
def _png_bytes(size: tuple[int, int] = (200, 200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, (10, 120, 200)).save(buffer, format="PNG")
    return buffer.getvalue()


#: A minimal Windows PE header (``MZ`` + DOS stub).
PE_PAYLOAD = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"


class TestMagicBytes:
    def test_detects_png(self) -> None:
        assert detect_mime_type(_png_bytes()) == "image/png"

    def test_detects_jpeg(self) -> None:
        buffer = io.BytesIO()
        Image.new("RGB", (50, 50), (0, 0, 0)).save(buffer, format="JPEG")
        assert detect_mime_type(buffer.getvalue()) == "image/jpeg"

    def test_detects_pdf(self) -> None:
        assert detect_mime_type(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n") == "application/pdf"

    def test_undetectable_payload(self) -> None:
        assert detect_mime_type(b"just some random text") is None

    async def test_renamed_executable_is_rejected(self, tmp_path) -> None:
        """A PE binary renamed to .jpg must not be accepted."""
        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload("foto.jpg", PE_PAYLOAD, content_type="image/jpeg")

        with pytest.raises(ValidationError) as excinfo:
            await storage.save_image(upload)

        assert "Unsupported file type" in excinfo.value.message

    async def test_renamed_script_is_rejected(self, tmp_path) -> None:
        """A shell script renamed to .png must not be accepted."""
        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload(
            "foto.png", b"#!/bin/sh\nrm -rf /\n", content_type="image/png"
        )

        with pytest.raises(ValidationError):
            await storage.save_image(upload)

    async def test_declared_content_type_is_not_trusted(self, tmp_path) -> None:
        """The client header says PNG but the bytes are a PE binary."""
        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload("foto.png", PE_PAYLOAD, content_type="image/png")

        with pytest.raises(ValidationError):
            await storage.save_image(upload)

    async def test_payload_over_5mb_is_rejected(self, tmp_path) -> None:
        """Files above the hard 5 MB limit are refused with HTTP 413."""
        storage = FileStorage(base_dir=tmp_path)
        oversized = b"\x89PNG\r\n\x1a\n" + b"0" * (5 * 1024 * 1024 + 1024)
        upload = make_upload("grande.png", oversized, content_type="image/png")

        with pytest.raises(PayloadTooLargeError) as excinfo:
            await storage.save_image(upload)

        assert excinfo.value.status_code == 413

    async def test_upload_over_5mb_returns_413(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "victim@example.com",
                "password": "senha-super-segura1",
                "full_name": "Victim",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )
        suite_code = (await client.get("/api/v1/auth/me")).json()["suite_code"]

        await login(client, admin_user.email, "admin-password1")
        oversized = b"\x89PNG\r\n\x1a\n" + b"0" * (5 * 1024 * 1024 + 1024)
        response = await client.post(
            "/api/v1/admin/warehouse/checkin",
            data={
                "suite_code": suite_code,
                "description": "Pacote gigante",
                "weight_grams": "100",
            },
            files=[("photos", ("grande.png", oversized, "image/png"))],
        )

        assert response.status_code == 413

    async def test_stored_file_uses_a_uuid_name(self, tmp_path) -> None:
        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload("original-name.png", _png_bytes())

        stored = await storage.save_image(upload)

        assert stored.filename.endswith(".webp")
        assert uuid.UUID(stored.filename.removesuffix(".webp")).version == 4
        assert "original-name" not in stored.filename


# ---------------------------------------------------------------------------
# 6.4 - Anti-SSRF validation
# ---------------------------------------------------------------------------
class TestSsrfValidator:
    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost:8000/admin",
            "http://127.0.0.1/admin",
            "https://127.0.0.1/admin",
            "http://[::1]/admin",
            "https://169.254.169.254/latest/meta-data/",
            "http://10.0.0.5/internal",
            "http://172.16.0.1/internal",
            "http://192.168.1.1/internal",
            "ftp://example.com/file",
            "file:///etc/passwd",
            "javascript:alert(1)",
        ],
    )
    def test_blocks_dangerous_urls(self, url: str) -> None:
        assert is_safe_url(url) is False
        with pytest.raises(SSRFError):
            validate_url(url)

    def test_blocks_the_cloud_metadata_endpoint(self) -> None:
        with pytest.raises(SSRFError) as excinfo:
            validate_url("https://169.254.169.254/latest/meta-data/iam/")

        assert "private or restricted" in excinfo.value.message

    def test_accepts_a_public_https_url(self) -> None:
        # 93.184.216.34 is a public address (example.com).
        result = validate_url("https://example.com/product/123")

        assert result.scheme == "https"
        assert result.hostname == "example.com"
        assert result.resolved_ips

    def test_rejects_a_non_https_scheme(self) -> None:
        with pytest.raises(SSRFError) as excinfo:
            validate_url("http://example.com/product")

        assert "Only HTTPS" in excinfo.value.message

    def test_rejects_a_url_without_hostname(self) -> None:
        with pytest.raises(SSRFError):
            validate_url("https:///path/only")

    def test_rejects_an_empty_url(self) -> None:
        with pytest.raises(SSRFError):
            validate_url("")

    async def test_assisted_purchase_rejects_a_private_url(
        self, client: AsyncClient
    ) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "ssrf@example.com",
                "password": "senha-super-segura1",
                "full_name": "SSRF",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        response = await client.post(
            "/api/v1/pre-orders/assisted",
            json={
                "items": [
                    {
                        "product_url": "http://169.254.169.254/latest/meta-data/",
                        "product_name": "Produto malicioso",
                        "quantity": 1,
                        "unit_price_jpy": 1000,
                    }
                ]
            },
        )

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "ssrf_blocked"


# ---------------------------------------------------------------------------
# 6.5 - Rate limiting
# ---------------------------------------------------------------------------
class TestRateLimiting:
    @pytest.fixture(autouse=True)
    def _enable_limiter(self):
        limiter.enabled = True
        yield
        limiter.enabled = False

    async def test_login_is_rate_limited(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "brute@example.com",
                "password": "senha-super-segura1",
                "full_name": "Brute",
                "phone": "+55-11-90000-0000",
                "accept_terms": True,
                "accept_privacy": True,
            },
        )

        statuses = []
        for _ in range(8):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "brute@example.com", "password": "senha-errada"},
            )
            statuses.append(response.status_code)

        assert 429 in statuses, statuses
        assert statuses.index(429) <= 5  # the limit is 5/minute

    async def test_rate_limited_response_is_429(self, client: AsyncClient) -> None:
        for _ in range(8):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "ninguem@example.com", "password": "errada"},
            )
            if response.status_code == 429:
                assert response.json()["error"]["code"] == "rate_limit_exceeded"
                break
        else:  # pragma: no cover - the limit must trigger
            raise AssertionError("the rate limit was never reached")

    async def test_calculator_is_rate_limited(self, client: AsyncClient) -> None:
        payload = {
            "item_price_jpy": 8000,
            "weight_grams": 1000,
            "order_type": "assisted_purchase",
            "shipping_method": "ems",
        }

        statuses = []
        for _ in range(35):
            response = await client.post("/api/v1/calculator/simulate", json=payload)
            statuses.append(response.status_code)

        assert 429 in statuses, statuses


# ---------------------------------------------------------------------------
# Log masking
# ---------------------------------------------------------------------------
class TestLogMasking:
    def test_masks_a_formatted_cpf(self) -> None:
        from app.core.logging_config import mask_text

        assert mask_text("CPF 123.456.789-09 enviado") == (
            "CPF ***.***.***-** enviado"
        )

    def test_masks_a_bare_cpf(self) -> None:
        from app.core.logging_config import mask_text

        assert "12345678909" not in mask_text("cpf=12345678909")

    def test_masks_a_password(self) -> None:
        from app.core.logging_config import mask_text

        masked = mask_text('{"password": "super-secreta"}')

        assert "super-secreta" not in masked
        assert "***" in masked

    def test_masks_a_bearer_token(self) -> None:
        from app.core.logging_config import mask_text

        masked = mask_text("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig")

        assert "eyJhbGciOiJIUzI1NiJ9" not in masked

    def test_masks_a_jwt(self) -> None:
        from app.core.logging_config import mask_text

        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiIxMjM0NTY3ODkwIn0"
            ".aGVsbG8td29ybGQtc2lnbmF0dXJl"
        )
        masked = mask_text(f"token={token}")

        assert token not in masked
