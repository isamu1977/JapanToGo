# security-hardening Specification

## Purpose
Defines the defensive security controls of the JapanToGo platform: strict resource ownership validation to prevent IDOR, magic-byte validated file uploads with UUIDv4 storage, anti-SSRF protection for external product URLs, rate limiting on authentication and simulator endpoints, and masking of PII and credentials in logs.
## Requirements
### Requirement: Resource Ownership Validation and IDOR Prevention
The system SHALL strictly validate resource ownership on all user-scoped endpoints (pre-orders, suite items, inspection photos, and shipments). Queries SHALL enforce `WHERE id = :resource_id AND user_id = :current_user_id` for users with role `client`. Attempts to query, modify, or delete resources belonging to other users SHALL be blocked with HTTP 403 Forbidden. Only users with role `admin` SHALL be permitted to access resources across arbitrary user accounts.

#### Scenario: Client accesses their own pre-order or suite item
- **WHEN** an authenticated user with role `client` requests `/api/v1/pre-orders/{id}` where `{id}` belongs to their `user_id`
- **THEN** the system returns the pre-order details successfully

#### Scenario: Client attempts to access another client's pre-order (IDOR attempt)
- **WHEN** an authenticated user with role `client` attempts to request or modify `/api/v1/pre-orders/{other_user_order_id}`
- **THEN** the system rejects the request with HTTP 403 Forbidden (or HTTP 404 Not Found to prevent enumeration)

#### Scenario: Admin accesses arbitrary client resource
- **WHEN** an authenticated user with role `admin` requests `/api/v1/admin/pre-orders/{any_user_order_id}`
- **THEN** the system grants access and returns the requested resource

### Requirement: Secure File Upload Validation via Magic Bytes and UUIDv4 Storage
The system SHALL validate all uploaded files (inspection photos and purchase receipts) by inspecting their actual binary Magic Bytes. The system SHALL permit solely `image/jpeg`, `image/png`, `image/webp` and `application/pdf` (PDF allowed strictly for purchase receipts). The system SHALL enforce a maximum file size limit of 5 MB. The system SHALL discard original client-provided filenames and rename stored files to UUIDv4 (`{uuid4()}.{validated_extension}`). The system SHALL serve uploaded static assets with headers preventing script execution (`X-Content-Type-Options: nosniff`).

#### Scenario: Valid inspection photo upload
- **WHEN** an operator uploads a valid JPEG/PNG/WebP image under 5 MB whose magic bytes match its declared type
- **THEN** the system accepts the upload, saves the file with a UUIDv4 filename, and returns the asset reference

#### Scenario: Malicious file upload with spoofed extension
- **WHEN** a client or user attempts to upload an executable or script disguised as `.jpg` or `.png`
- **THEN** the system inspects magic bytes, detects the MIME mismatch, rejects the upload with HTTP 400 Bad Request, and deletes any temporary file

#### Scenario: Upload exceeding file size limit
- **WHEN** a user uploads a file exceeding 5 MB
- **THEN** the system rejects the upload with HTTP 413 Payload Too Large

### Requirement: Anti-SSRF Protection for External Product URLs
The system SHALL validate any external product URL submitted for metadata scraping. The URL MUST use the `https` scheme. The system SHALL resolve the destination hostname to IP addresses before initiating network connections and SHALL immediately reject any target IP that resolves to loopback (127.0.0.1/::1), private network ranges (RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), link-local addresses (RFC 3927: 169.254.0.0/16), or multicast/broadcast addresses.

#### Scenario: Valid external Japanese product URL
- **WHEN** a client submits a valid public HTTPS link (e.g., `https://www.amazon.co.jp/dp/...`)
- **THEN** the system resolves the hostname, verifies the IP is a public Internet address, and proceeds with the fetch

#### Scenario: SSRF attempt to internal network or cloud metadata service
- **WHEN** a client submits a URL pointing to `http://localhost`, `http://127.0.0.1`, `http://169.254.169.254`, or any private subnet IP
- **THEN** the system aborts the request immediately with HTTP 400 Bad Request and logs an SSRF prevention alert

### Requirement: Rate Limiting on Authentication and Simulator Endpoints
The system SHALL enforce rate limiting using `slowapi` on critical public endpoints: `/api/v1/auth/login` (maximum 5 requests per minute per IP), `/api/v1/auth/register` (maximum 3 requests per minute per IP), and `/api/v1/calculator/simulate` (maximum 30 requests per minute per IP).

#### Scenario: Rate limit exceeded on login
- **WHEN** a client or automated script exceeds 5 login attempts within a 60-second window from the same IP
- **THEN** the system blocks subsequent requests with HTTP 429 Too Many Requests and attaches standard retry headers

### Requirement: Sensitive Data Masking in Application and System Logs
The system SHALL sanitize logs to prevent leaks of Personally Identifiable Information (PII) and credentials. The system SHALL mask Brazilian CPF numbers, passwords, and API secret keys in all console and container log outputs.

#### Scenario: Logging request containing Brazilian CPF or authorization header
- **WHEN** the backend logs a request or error payload containing a CPF number or credential
- **THEN** the logging filter replaces the CPF with masked characters (e.g., `***.***.***-**`) and redacts authorization headers before writing to stdout
