# auth-and-suite-management Specification

## Purpose
Defines account registration, the allocation of the immutable `suite_code` (JTG-XXXX) that identifies each client in the warehouse, JWT access/refresh session management, role based access control (`client` vs `admin`), and the display of the JapanToGo warehouse address in Japanese and Romanised script with one-click copy.
## Requirements
### Requirement: User Registration and Unique Suite Code Allocation
The system SHALL allow new users to register with email, password, full name, phone number, and optional CPF tax ID (`cpf_tax_id`). Upon registration as a `client`, the system SHALL generate an immutable and unique `suite_code` formatted as `JTG-XXXX` (e.g., `JTG-1001`) via atomic PostgreSQL sequence, and automatically issue HttpOnly session cookies.

#### Scenario: Successful Client Registration
- **WHEN** a new user provides valid registration details with email, password, full name, phone, and optional CPF
- **THEN** the system creates a user record with role `client`, generates an auto-incremented unique `suite_code` starting from `JTG-1001`, sets secure session cookies, and returns the created user profile

#### Scenario: Duplicate Email Registration
- **WHEN** a user attempts to register with an email that is already registered
- **THEN** the system rejects the registration with a 409 Conflict error and does not generate a suite code

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

### Requirement: Role-Based Access Control (RBAC)
The system SHALL enforce role-based access control protecting client endpoints and administrator endpoints.

#### Scenario: Client accessing client-only resources
- **WHEN** an authenticated user with role `client` accesses `/api/v1/suite/me`
- **THEN** the system allows access and returns only items belonging to that user's suite

#### Scenario: Client attempting to access admin-only resources
- **WHEN** an authenticated user with role `client` attempts to access any `/api/v1/admin/*` endpoint
- **THEN** the system rejects the request with a 403 Forbidden error

### Requirement: Warehouse Suite Address Display and One-Click Copy
The system SHALL provide clients with the official JapanToGo warehouse address in Japan, displaying it in Japanese kanji/kana and Romanized script, with the client's box identifier clearly labeled as "Código do seu Box: #JTG-XXXX" injected into the building complement line (`サンシャイン 4F #JTG-XXXX`), providing explicit instructions on attaching the Box code for sorting at the Osaka warehouse, offering one-click copy buttons with visual success feedback for each individual line as well as a quick action button to copy the complete formatted address, and representing the client's inventory in the navigation as "Meus Pacotes".

#### Scenario: Client views warehouse suite address
- **WHEN** a logged-in client views the address page in their dashboard
- **THEN** the system renders:
  - A prominent header card presenting "Código do seu Box: #JTG-XXXX" with one-click copy
  - Guidance explaining that the Box code is essential for package identification and check-in upon warehouse delivery
  - Japanese version with 氏名, 郵便番号, 都道府県, 市区町村, 丁目・番地・号, 建物名・部屋番号, and 電話番号
  - Romanized version with Name, Postal Code, Prefecture, City, Street / Number, Building / Unit, and Phone
  - Individual copy buttons with immediate visual feedback for each row
  - Quick action button to copy the full formatted address

