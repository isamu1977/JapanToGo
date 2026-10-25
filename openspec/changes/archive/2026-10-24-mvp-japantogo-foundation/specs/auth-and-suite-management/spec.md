## ADDED Requirements

### Requirement: User Registration and Unique Suite Code Allocation
The system SHALL allow new users to register with email, password, full name, and phone number. Upon registration as a `client`, the system SHALL generate an immutable and unique `suite_code` formatted as `JTG-XXXX` (e.g., `JTG-1001`).

#### Scenario: Successful Client Registration
- **WHEN** a new user provides valid registration details with email, password, full name, and phone
- **THEN** the system creates a user record with role `client`, generates an auto-incremented unique `suite_code` starting from `JTG-1001`, and returns the created user profile

#### Scenario: Duplicate Email Registration
- **WHEN** a user attempts to register with an email that is already registered
- **THEN** the system rejects the registration with a 409 Conflict error and does not generate a suite code

### Requirement: JWT Authentication and Session Management
The system SHALL authenticate users using email and password, issuing a short-lived JWT access token and a secure HTTP-only refresh token.

#### Scenario: Successful Login
- **WHEN** a registered user submits valid email and password credentials
- **THEN** the system returns an access token in the JSON body, sets a secure HTTP-only refresh token cookie, and provides the user's profile including role and `suite_code`

#### Scenario: Token Refresh
- **WHEN** a client presents a valid refresh token cookie to the token refresh endpoint
- **THEN** the system issues a new JWT access token and rotates the refresh token

### Requirement: Role-Based Access Control (RBAC)
The system SHALL enforce role-based access control protecting client endpoints and administrator endpoints.

#### Scenario: Client accessing client-only resources
- **WHEN** an authenticated user with role `client` accesses `/api/v1/suite/me`
- **THEN** the system allows access and returns only items belonging to that user's suite

#### Scenario: Client attempting to access admin-only resources
- **WHEN** an authenticated user with role `client` attempts to access any `/api/v1/admin/*` endpoint
- **THEN** the system rejects the request with a 403 Forbidden error

### Requirement: Warehouse Suite Address Display and One-Click Copy
The system SHALL provide clients with the official JapanToGo warehouse address in Japan, displaying it in Japanese kanji/kana and Romanized script, with the client's `suite_code` injected into the address complement line, and offering a one-click copy feature.

#### Scenario: Client views warehouse suite address
- **WHEN** a logged-in client views the address tab or card in their dashboard
- **THEN** the system renders the complete Japanese warehouse postal code, prefecture, city, street number, and building complement line containing `#JTG-XXXX`, alongside the Romanized equivalent and copy buttons for each field
