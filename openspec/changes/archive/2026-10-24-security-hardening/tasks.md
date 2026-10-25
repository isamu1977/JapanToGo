## 1. Authentication & Cookie-Based Session Hardening

- [x] 1.1 Update backend FastAPI auth endpoints (`app/api/v1/auth.py`) to set both access and refresh tokens exclusively as `HttpOnly`, `SameSite=Lax` cookies, respecting `COOKIE_SECURE` configuration
- [x] 1.2 Remove token payload from login/refresh JSON response bodies to prevent any frontend `localStorage` persistence
- [x] 1.3 Update auth dependencies in `app/core/dependencies.py` to extract JWT directly from the `access_token` cookie
- [x] 1.4 Ensure password hashing uses Passlib with `bcrypt` or `argon2id` and verify password complexity constraints
- [x] 1.5 Configure restrictive CORS middleware in `app/main.py` allowing only origins configured via `CORS_ORIGINS` (application production domain and dev localhost)
- [x] 1.6 Update frontend API client (`src/lib/api/client.ts`) and stores (`src/lib/stores/auth.ts`) to use `credentials: 'include'` for transparent cookie transport and remove all `localStorage` token handling

## 2. Access Control & IDOR Prevention

- [x] 2.1 Audit all client endpoints in `app/api/v1/pre_orders.py` ensuring SQL queries enforce `WHERE id = :id AND user_id = :current_user.id` and reject cross-user access with HTTP 403 Forbidden
- [x] 2.2 Audit all client endpoints in `app/api/v1/suite.py` ensuring suite items and inspection photos are strictly scoped to the authenticated client's `user_id`
- [x] 2.3 Audit all client endpoints in `app/api/v1/shipments.py` ensuring shipments and linked items are strictly scoped to `current_user.id`
- [x] 2.4 Verify all administrative routes under `app/api/v1/admin/` require `require_admin` dependency and reject `client` role requests with HTTP 403 Forbidden

## 3. Secure File Uploads (Inspection Photos & Receipts)

- [x] 3.1 Add `puremagic` to `backend/requirements.txt`
- [x] 3.2 Update `file_storage.py` to inspect binary Magic Bytes, allowing only `image/jpeg`, `image/png`, `image/webp` for photos and receipts, and `application/pdf` exclusively for receipts
- [x] 3.3 Enforce a strict 5 MB file size limit per uploaded file in `file_storage.py` and reject oversized payloads with HTTP 413
- [x] 3.4 Discard client-supplied filenames and save files using randomized UUIDv4 filenames (`{uuid4()}.{validated_ext}`)
- [x] 3.5 Configure static files mounting in `app/main.py` with security headers (`X-Content-Type-Options: nosniff`) to disallow executable scripts

## 4. Anti-SSRF (Server-Side Request Forgery) Protection

- [x] 4.1 Implement `app/services/ssrf_validator.py` with strict URL scheme validation requiring `https://`
- [x] 4.2 Implement DNS resolution and IP validation in `ssrf_validator.py` rejecting loopback (127.0.0.1/::1), RFC 1918 private subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), and RFC 3927 link-local addresses (169.254.0.0/16)
- [x] 4.3 Integrate SSRF validation into assisted purchase product URL processing and metadata fetching

## 5. Rate Limiting & Sensitive Data Masking

- [x] 5.1 Add `slowapi` to `backend/requirements.txt` and initialize Limiter in `app/core/security.py` / `app/main.py`
- [x] 5.2 Apply rate limit decorators: `/api/v1/auth/login` (5/minute), `/api/v1/auth/register` (3/minute), and `/api/v1/calculator/simulate` (30/minute)
- [x] 5.3 Implement logging filter in `app/core/logging_config.py` to mask Brazilian CPF patterns (`***.***.***-**`), passwords, and authorization tokens across all stdout logs

## 6. Verification & Automated Testing

- [x] 6.1 Create automated tests for HttpOnly cookie authentication and token refresh
- [x] 6.2 Create automated tests for IDOR prevention verifying that User A cannot access User B's pre-orders, suite items, or shipments (HTTP 403)
- [x] 6.3 Create automated tests for Magic Bytes file validation rejecting renamed executable/script files and payloads > 5 MB
- [x] 6.4 Create automated tests for SSRF validator rejecting localhost, private IPs, and non-HTTPS URLs
- [x] 6.5 Verify rate limit rejection (HTTP 429) when exceeding route thresholds
