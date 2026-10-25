"""Unit tests for the public contact inquiry endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


class TestContactEndpoint:
    async def test_successful_submission(self, client: AsyncClient) -> None:
        payload = {
            "name": "Maria Silva",
            "email": "maria.silva@example.com",
            "subject": "Dúvida sobre envio",
            "suite_code": "JTG-1234",
            "message": "Olá, gostaria de saber se vocês consolidam caixas de diferentes lojas.",
        }

        response = await client.post("/api/v1/contact", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "sucesso" in data["message"].lower()

    async def test_submission_via_api_prefix_alias(self, client: AsyncClient) -> None:
        payload = {
            "name": "João Santos",
            "email": "joao.santos@example.com",
            "subject": "Orçamento de compra assistida",
            "message": "Quero comprar uma figure no Surugaya. Como funciona a cotação?",
        }

        response = await client.post("/api/contact", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    async def test_invalid_email_validation(self, client: AsyncClient) -> None:
        payload = {
            "name": "Carlos",
            "email": "not-an-email",
            "subject": "Suporte a pedido",
            "message": "Mensagem válida com mais de 10 caracteres.",
        }

        response = await client.post("/api/v1/contact", json=payload)
        assert response.status_code == 422

    async def test_message_too_short(self, client: AsyncClient) -> None:
        payload = {
            "name": "Carlos",
            "email": "carlos@example.com",
            "subject": "Dúvida",
            "message": "Oi",  # min length is 10
        }

        response = await client.post("/api/v1/contact", json=payload)
        assert response.status_code == 422
