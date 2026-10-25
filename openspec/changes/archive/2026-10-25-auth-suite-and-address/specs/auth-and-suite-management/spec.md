## MODIFIED Requirements

### Requirement: User Registration and Unique Suite Code Allocation
The system SHALL allow new users to register with email, password, full name, phone number, and optional CPF tax ID (`cpf_tax_id`). Upon registration as a `client`, the system SHALL generate an immutable and unique `suite_code` formatted as `JTG-XXXX` (e.g., `JTG-1001`) via atomic PostgreSQL sequence, and automatically issue HttpOnly session cookies.

#### Scenario: Successful Client Registration
- **WHEN** a new user provides valid registration details with email, password, full name, phone, and optional CPF
- **THEN** the system creates a user record with role `client`, generates an auto-incremented unique `suite_code` starting from `JTG-1001`, sets secure session cookies, and returns the created user profile

#### Scenario: Duplicate Email Registration
- **WHEN** a user attempts to register with an email that is already registered
- **THEN** the system rejects the registration with a 409 Conflict error and does not generate a suite code

### Requirement: Warehouse Suite Address Display and One-Click Copy
The system SHALL provide clients with the official JapanToGo warehouse address in Japan, displaying it in Japanese kanji/kana and Romanized script, with the client's `suite_code` injected into the building complement line (`サンシャイン 4F #JTG-XXXX`), and offering one-click copy buttons with visual success feedback for each individual line as well as a quick action button to copy the complete formatted address.

#### Scenario: Client views warehouse suite address
- **WHEN** a logged-in client views the address page in their dashboard
- **THEN** the system renders:
  - Japanese version with 氏名, 郵便番号, 都道府県, 市区町村, 丁目・番地・号, 建物名・部屋番号, and 電話番号
  - Romanized version with Name, Postal Code, Prefecture, City, Street / Number, Building / Unit, and Phone
  - Individual copy buttons with immediate visual feedback for each row
  - Quick action button to copy the full formatted address
