## MODIFIED Requirements

### Requirement: JWT Authentication and Session Management
The system SHALL authenticate users using email and password, issuing both JWT access token and refresh token stored exclusively in secure, `HttpOnly`, `SameSite=Lax` cookies. The system SHALL NOT transmit access tokens in JSON response bodies for `localStorage` persistence. The system SHALL hash passwords using `bcrypt` or `argon2id` via Passlib and enforce a restrictive CORS middleware accepting only configured origins.

#### Scenario: Successful Login with HttpOnly Cookies
- **WHEN** a registered user submits valid email and password credentials
- **THEN** the system verifies the password hash, sets both `access_token` and `refresh_token` as `HttpOnly`, `SameSite=Lax` cookies (with `Secure` flag enabled in production environments), and returns only the public user profile without exposing raw tokens in the response body

#### Scenario: Token Refresh via Cookie
- **WHEN** a client presents a valid `refresh_token` cookie to the token refresh endpoint
- **THEN** the system issues a new `access_token` cookie, rotates the `refresh_token` cookie, and returns a success confirmation

#### Scenario: Unauthorized Cross-Origin Request Blocked by CORS
- **WHEN** a request originates from an unapproved third-party origin header not present in `CORS_ORIGINS`
- **THEN** the system rejects the cross-origin preflight request and does not attach permissive CORS headers
