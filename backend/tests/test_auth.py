"""Authentication, session cookie management and RBAC tests."""

from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import login

REGISTER_PAYLOAD = {
    "email": "nova.conta@example.com",
    "password": "senha-super-segura1",
    "full_name": "Nova Conta",
    "phone": "+55-11-98888-0000",
    "accept_terms": True,
    "accept_privacy": True,
}


class TestRegistration:
    async def test_creates_client_with_suite_code(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

        assert response.status_code == 201
        body = response.json()
        assert body["user"]["role"] == "client"
        assert body["user"]["suite_code"].startswith("JTG-")
        assert body["user"]["suite_code"][4:].isdigit()

    async def test_sets_http_only_session_cookies(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

        cookies = response.headers.get_list("set-cookie")
        names = {cookie.split("=", 1)[0] for cookie in cookies}
        assert {"access_token", "refresh_token"} <= names

        for cookie in cookies:
            if cookie.split("=", 1)[0] in {"access_token", "refresh_token"}:
                assert "HttpOnly" in cookie
                assert "SameSite=lax" in cookie.replace("SameSite=Lax", "SameSite=lax")

    async def test_response_body_never_exposes_a_token(
        self, client: AsyncClient
    ) -> None:
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        body = response.json()

        assert "access_token" not in body
        assert "refresh_token" not in body
        assert body["token_type"] == "cookie"

    async def test_duplicate_email_is_rejected(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "conflict"

    async def test_legal_acceptance_is_mandatory(self, client: AsyncClient) -> None:
        payload = {**REGISTER_PAYLOAD, "accept_terms": False}
        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    async def test_weak_password_is_rejected(self, client: AsyncClient) -> None:
        payload = {**REGISTER_PAYLOAD, "password": "short"}
        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    async def test_password_without_digit_is_rejected(self, client: AsyncClient) -> None:
        payload = {**REGISTER_PAYLOAD, "password": "onlyletters"}
        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    async def test_password_without_letter_is_rejected(
        self, client: AsyncClient
    ) -> None:
        payload = {**REGISTER_PAYLOAD, "password": "1234567890"}
        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    async def test_suite_codes_are_unique(self, client: AsyncClient) -> None:
        first = await client.post(
            "/api/v1/auth/register",
            json={**REGISTER_PAYLOAD, "email": "a@example.com"},
        )
        second = await client.post(
            "/api/v1/auth/register",
            json={**REGISTER_PAYLOAD, "email": "b@example.com"},
        )

        assert first.json()["user"]["suite_code"] != second.json()["user"]["suite_code"]


class TestLogin:
    async def test_valid_credentials(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": REGISTER_PAYLOAD["email"],
                "password": REGISTER_PAYLOAD["password"],
            },
        )

        assert response.status_code == 200
        assert response.json()["user"]["email"] == REGISTER_PAYLOAD["email"]
        assert "access_token" not in response.json()

    async def test_session_cookie_authenticates_requests(
        self, client: AsyncClient
    ) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        assert response.json()["email"] == REGISTER_PAYLOAD["email"]

    async def test_wrong_password(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": REGISTER_PAYLOAD["email"], "password": "senha-errada"},
        )

        assert response.status_code == 401

    async def test_unknown_email(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nao.existe@example.com", "password": "senha-super-segura1"},
        )

        assert response.status_code == 401


class TestTokenRefresh:
    async def test_rotates_both_cookies(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        original = client.cookies.get("refresh_token")

        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        assert "access_token" not in response.json()
        assert client.cookies.get("refresh_token") != original
        assert client.cookies.get("access_token")

    async def test_missing_cookie(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    async def test_garbage_cookie_is_rejected(self, client: AsyncClient) -> None:
        client.cookies.set("refresh_token", "not-a-jwt")

        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401


class TestProfile:
    async def test_requires_authentication(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_returns_the_current_profile(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        assert response.json()["email"] == REGISTER_PAYLOAD["email"]

    async def test_bearer_header_is_no_longer_accepted(
        self, client: AsyncClient
    ) -> None:
        """Tokens must come from the HttpOnly cookie, never from a header."""
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])
        cookie_token = client.cookies.get("access_token")

        client.cookies.clear()
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {cookie_token}"},
        )

        assert response.status_code == 401


class TestLogout:
    async def test_clears_the_session_cookies(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])

        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 204
        assert not client.cookies.get("access_token")
        assert not client.cookies.get("refresh_token")


class TestRoleBasedAccessControl:
    async def test_client_cannot_reach_admin_endpoints(
        self, client: AsyncClient
    ) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])

        response = await client.get("/api/v1/admin/dashboard")

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "permission_denied"

    async def test_client_can_reach_client_endpoints(
        self, client: AsyncClient
    ) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        await login(client, REGISTER_PAYLOAD["email"], REGISTER_PAYLOAD["password"])

        response = await client.get("/api/v1/suite/me")

        assert response.status_code == 200

    async def test_admin_can_reach_admin_endpoints(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")

        response = await client.get("/api/v1/admin/dashboard")

        assert response.status_code == 200
        assert "clients" in response.json()

    async def test_admin_cannot_reach_client_only_endpoints(
        self, client: AsyncClient, admin_user
    ) -> None:
        await login(client, admin_user.email, "admin-password1")

        response = await client.get("/api/v1/suite/me")

        assert response.status_code == 403

    async def test_register_with_cpf_and_api_prefix_alias(
        self, client: AsyncClient
    ) -> None:
        payload = {
            **REGISTER_PAYLOAD,
            "email": "cpf-user@example.com",
            "cpf_tax_id": "12345678901",
        }
        res_reg = await client.post("/api/auth/register", json=payload)
        assert res_reg.status_code == 201
        data = res_reg.json()
        assert data["user"]["cpf_tax_id"] == "12345678901"
        assert data["user"]["suite_code"].startswith("JTG-")

        # Check /api/auth/me
        res_me = await client.get("/api/auth/me")
        assert res_me.status_code == 200
        assert res_me.json()["cpf_tax_id"] == "12345678901"

        # Check /api/auth/logout
        res_logout = await client.post("/api/auth/logout")
        assert res_logout.status_code == 204

