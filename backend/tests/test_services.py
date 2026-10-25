"""Warehouse address, Japan Post export and file storage tests."""

from __future__ import annotations

import io

from httpx import AsyncClient
from PIL import Image

from app.services.file_storage import FileStorage
from app.services.japan_post_export import CustomsLine, build_export
from app.services.suite_service import build_warehouse_address
from tests.conftest import login


class FakeShipment:
    """Minimal stand-in for the Shipment ORM object."""

    recipient_name = "Maria Silva"
    recipient_postal_code = "01310-100"
    recipient_state = "SP"
    recipient_city = "Sao Paulo"
    recipient_address = "Av. Paulista, 1000\nApto 42"
    recipient_phone = "+55-11-90000-0000"
    shipping_method = "ems"
    total_weight_grams = 1450
    international_tracking_code = "EJ123456789JP"
    customs_declaration = {
        "items": [
            {"description": "T-shirt", "quantity": 2, "declared_value_jpy": 3000},
            {"description": "Sneakers", "quantity": 1, "declared_value_jpy": 12000},
        ]
    }


class TestWarehouseAddress:
    def test_injects_the_suite_code(self) -> None:
        address = build_warehouse_address("JTG-1001")

        assert "JTG-1001" in address["ja"]["complement"]
        assert "JTG-1001" in address["ja"]["full"]
        assert "JTG-1001" in address["romaji"]["complement"]
        assert "JTG-1001" in address["romaji"]["full"]

    def test_provides_both_scripts(self) -> None:
        address = build_warehouse_address("JTG-1001")

        assert address["ja"]["postal_code"].startswith("〒")
        assert address["romaji"]["postal_code"] == "540-0027"
        assert address["ja"]["company"]
        assert address["romaji"]["company"]

    def test_handles_a_missing_suite_code(self) -> None:
        address = build_warehouse_address(None)

        assert address["ja"]["complement"]
        assert address["romaji"]["complement"]


class TestJapanPostExport:
    def test_contains_every_required_field(self) -> None:
        export = build_export(FakeShipment())
        payload = export.to_dict()

        assert payload["recipient_name"] == "Maria Silva"
        assert payload["country_code"] == "BR"
        assert payload["postal_code"] == "01310-100"
        assert payload["state_city"] == "SP / Sao Paulo"
        assert payload["address_line_1"] == "Av. Paulista, 1000"
        assert payload["address_line_2"] == "Apto 42"
        assert payload["recipient_phone"] == "+55-11-90000-0000"

    def test_aggregates_the_customs_lines(self) -> None:
        export = build_export(FakeShipment())

        assert export.total_quantity == 3
        # declared_value_jpy is the total value of each line.
        assert export.total_declared_value_jpy == 15000
        assert len(export.contents) == 2

    def test_renders_a_copy_paste_block(self) -> None:
        text = build_export(FakeShipment()).to_text()

        assert "Recipient Name" in text
        assert "Country Code       : BR" in text
        assert "T-shirt" in text
        assert "JPY 15,000" in text

    def test_renders_csv(self) -> None:
        csv_text = build_export(FakeShipment()).to_csv()
        lines = csv_text.splitlines()

        assert lines[0].startswith("recipient_name,")
        assert len(lines) == 3  # header + 2 customs lines

    def test_accepts_overridden_customs_lines(self) -> None:
        export = build_export(
            FakeShipment(),
            customs_lines=[CustomsLine("Handbag", 1, 50000)],
        )

        assert export.total_quantity == 1
        assert export.total_declared_value_jpy == 50000


class TestFileStorage:
    def _png(self, size: tuple[int, int] = (3000, 2000)) -> bytes:
        buffer = io.BytesIO()
        Image.new("RGB", size, (30, 90, 160)).save(buffer, format="PNG")
        return buffer.getvalue()

    async def test_compresses_and_resizes_to_webp(self, tmp_path) -> None:
        from tests.conftest import make_upload

        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload("foto.png", self._png())

        stored = await storage.save_image(upload)

        assert stored.url.startswith("/uploads/")
        assert stored.content_type == "image/webp"

        with Image.open(stored.stored_path) as image:
            assert image.format == "WEBP"
            assert image.width <= 1920
            assert image.height <= 1080

    async def test_rejects_a_non_image_payload(self, tmp_path) -> None:
        """A Windows executable is detected and refused even named as .png."""
        from tests.conftest import make_upload

        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload(
            "malware.png",
            b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00",
            content_type="image/png",
        )

        from app.core.errors import ValidationError

        try:
            await storage.save_image(upload)
        except ValidationError as exc:
            assert "Unsupported file type" in exc.message
        else:  # pragma: no cover - the call must raise
            raise AssertionError("expected a ValidationError")

    async def test_rejects_more_than_five_photos(self, tmp_path) -> None:
        from tests.conftest import make_upload

        storage = FileStorage(base_dir=tmp_path)
        uploads = [
            make_upload(f"p{index}.png", self._png((100, 100)))
            for index in range(6)
        ]

        from app.core.errors import ValidationError

        try:
            await storage.save_inspection_photos(uploads)
        except ValidationError as exc:
            assert "maximum of 5" in exc.message
        else:  # pragma: no cover - the call must raise
            raise AssertionError("expected a ValidationError")

    async def test_discards_the_client_filename(self, tmp_path) -> None:
        """The original name is dropped; the file is stored under a UUID."""
        import uuid as uuid_module

        from tests.conftest import make_upload

        storage = FileStorage(base_dir=tmp_path)
        upload = make_upload("../../etc/passwd.png", self._png((100, 100)))

        stored = await storage.save_image(upload)

        assert "/" not in stored.filename
        assert ".." not in stored.filename
        assert stored.filename.endswith(".webp")
        # The stored name is a UUIDv4 with the canonical extension.
        assert uuid_module.UUID(stored.filename.removesuffix(".webp")).version == 4
        assert str(tmp_path) in stored.stored_path


class TestSuiteEndpoints:
    async def test_address_contains_the_suite_code(
        self, client: AsyncClient, client_user
    ) -> None:
        await login(client, client_user.email, "client-password1")

        response = await client.get("/api/v1/suite/me/address")

        assert response.status_code == 200
        body = response.json()
        assert body["suite_code"] == "JTG-9001"
        assert "JTG-9001" in body["ja"]["full"]
        assert "JTG-9001" in body["romaji"]["full"]
