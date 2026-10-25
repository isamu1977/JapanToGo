## 1. Project Scaffolding & Infrastructure

- [x] 1.1 Create root project directory structure with `backend/` and `frontend/` folders
- [x] 1.2 Setup `docker-compose.yml` **for Coolify production deployment only** (backend + frontend services, persistent volume for media uploads, external PostgreSQL reached through `DATABASE_URL`) — no PostgreSQL container is started for local development
- [x] 1.3 Create multi-stage `Dockerfile` and `.dockerignore` for FastAPI backend (Python 3.12-slim)
- [x] 1.4 Create multi-stage `Dockerfile` and `.dockerignore` for SvelteKit frontend (Node.js 22-alpine with adapter-node — SvelteKit 3 requires `Promise.withResolvers`)
- [x] 1.5 Configure environment variable template files (`.env.example` in root, backend, and frontend) covering `DATABASE_URL` (asyncpg driver), discrete `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME`, `JWT_SECRET`, `COOKIE_DOMAIN`, `CORS_ORIGINS` and `UPLOADS_DIR`
- [x] 1.6 Provide local development bootstrap (`scripts/setup_local_db.sh` + README section) that creates the `japantogo` database on the native PostgreSQL server (`createdb japantogo`) and runs `alembic upgrade head`


## 2. Backend Core, Database Models & Migrations

- [x] 2.1 Setup backend Python dependencies in `backend/requirements.txt` (FastAPI, uvicorn, SQLAlchemy 2.0, asyncpg, Alembic, Pydantic v2, python-jose, passlib, bcrypt, pillow, python-multipart)
- [x] 2.2 Configure core application settings (`app/core/config.py`) using Pydantic Settings with a single `DATABASE_URL` source of truth using the async `postgresql+asyncpg` driver (overridable through the discrete `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` variables), database connection pool (`app/core/database.py`), and error handling
- [x] 2.3 Implement SQLAlchemy models for `User` with PostgreSQL sequence for auto-generating `suite_code` (`JTG-XXXX`), and `LegalTermsAcceptance`
- [x] 2.4 Implement SQLAlchemy models for `PreOrder` and `PreOrderItem` (types `assisted_purchase` and `forwarding`, status tracking, and item details)
- [x] 2.5 Implement SQLAlchemy models for `SuiteItem` and `InspectionPhoto` (weight in grams, tracking, storage status, and photo associations)
- [x] 2.6 Implement SQLAlchemy models for `Shipment` (shipping method EMS/Small Packet, packing status, customs declaration JSONB, recipient CPF/address, and tracking)
- [x] 2.7 Initialize and configure Alembic with asyncpg driver in `backend/alembic/`, reading the **same** `DATABASE_URL` from the application settings (`alembic/env.py`) so migrations and application never target different databases, and generate the initial migration script

## 3. Authentication, Security & RBAC

- [x] 3.1 Implement password hashing and verification utilities using passlib/bcrypt (`app/core/security.py`)
- [x] 3.2 Implement JWT token generation for access tokens and refresh tokens with proper expiration times
- [x] 3.3 Implement authentication dependencies (`get_current_user`, `require_client`, `require_admin`) in `app/core/dependencies.py`
- [x] 3.4 Create Pydantic auth schemas (`UserRegister`, `UserLogin`, `TokenResponse`, `UserProfile`) in `app/schemas/auth.py`
- [x] 3.5 Implement REST endpoints for user registration, login, token refresh, and profile retrieval in `app/api/v1/auth.py`

## 4. Business Logic Services & REST APIs

- [x] 4.1 Implement `fee_calculator.py` service enforcing the 20% service fee and ¥ 2.000 minimum floor rule for orders under ¥ 10.000, along with Landed Cost calculations (JPY -> BRL, freight estimation, and RTS 60% + ICMS)
- [x] 4.2 Implement `file_storage.py` service with image processing (Pillow compression to WebP, dimension limits, and secure upload directory handling)
- [x] 4.3 Implement `japan_post_export.py` service to format shipment data into Japan Post International Mail My Page payload format
- [x] 4.4 Implement Pre-Orders endpoints (`POST /api/v1/pre-orders/assisted`, `POST /api/v1/pre-orders/forwarding` with file upload, `GET /api/v1/pre-orders`)
- [x] 4.5 Implement Client Suite endpoints (`GET /api/v1/suite/me`, `GET /api/v1/suite/me/address`)
- [x] 4.6 Implement Client Shipments endpoints (`POST /api/v1/shipments/request`, `GET /api/v1/shipments`)
- [x] 4.7 Implement Public Landed Cost Calculator endpoint (`POST /api/v1/calculator/simulate`)
- [x] 4.8 Implement Admin endpoints: operational metrics dashboard (`GET /api/v1/admin/dashboard`), pre-orders queue and status updates (`PUT /api/v1/admin/pre-orders/{id}/purchase`), warehouse check-in with photo uploads (`POST /api/v1/admin/warehouse/checkin`), and shipments queue with dispatch tracking and Japan Post export (`GET /api/v1/admin/shipments/{id}/export-japan-post`)

## 5. Frontend Foundation & Shared Components

- [x] 5.1 Initialize SvelteKit project with TypeScript, Tailwind CSS v4, Lucide Svelte, and `@sveltejs/adapter-node`
- [x] 5.2 Configure PWA manifest (`manifest.json`), service worker registration, and app icons
- [x] 5.3 Implement strongly typed API client (`src/lib/api/client.ts`) with interceptors for JWT injection and token refresh
- [x] 5.4 Implement reactive authentication store (`src/lib/stores/auth.ts`) handling login, logout, and user profile state
- [x] 5.5 Implement reusable UI components: `AddressCard.svelte` (Japanese kanji & Romaji address with 1-click copy), `LandedCostCalculator.svelte`, and `PhotoGallery.svelte` (modal inspection viewer)

## 6. Public & Marketing Routes

- [x] 6.1 Implement `(marketing)` group layout and Navigation Header with brand identity "JapanToGo - FROM JAPAN TO YOUR DOOR"
- [x] 6.2 Build high-converting Landing Page (`src/routes/(marketing)/+page.svelte`) with hero section, process explainer (代行 & Redirecionamento), and CTA buttons
- [x] 6.3 Build dedicated Interactive Landed Cost Simulator page (`src/routes/(marketing)/simulador/+page.svelte`)
- [x] 6.4 Build Terms of Use page (`src/routes/(marketing)/termos/+page.svelte`) in bilingual Portuguese/Japanese
- [x] 6.5 Build Privacy Policy page (`src/routes/(marketing)/privacidade/+page.svelte`) in bilingual Portuguese/Japanese
- [x] 6.6 Build Specified Commercial Transactions Act notice page (`src/routes/(marketing)/tokushoho/+page.svelte` - 特定商取引法に基づく表記)
- [x] 6.7 Implement Authentication views: Login (`src/routes/(auth)/login/+page.svelte`) and Register (`src/routes/(auth)/register/+page.svelte`) with legal terms acceptance checkbox

## 7. Client Area Dashboard & Workflows (PWA)

- [x] 7.1 Implement `(app)` group layout shell with responsive sidebar/bottom-nav optimized for mobile and desktop
- [x] 7.2 Build Client Dashboard home (`src/routes/(app)/dashboard/+page.svelte`) summarizing active pre-orders, items in suite, and pending shipments
- [x] 7.3 Build Suite Address page (`src/routes/(app)/endereco/+page.svelte`) with prominent `suite_code` display and 1-click copy cards for Amazon JP, Rakuten, etc.
- [x] 7.4 Build Assisted Purchase request form (`src/routes/(app)/pre-pedidos/novo-assistida/+page.svelte`) with dynamic multi-item list and real-time fee preview
- [x] 7.5 Build Redirection pre-order form (`src/routes/(app)/pre-pedidos/novo-redirecionamento/+page.svelte`) with mandatory receipt upload
- [x] 7.6 Build My Suite inventory page (`src/routes/(app)/suite/+page.svelte`) showing received items, weighed grams, status badge, and inspection photo gallery modal
- [x] 7.7 Build Shipment Consolidation page (`src/routes/(app)/envios/novo/+page.svelte`) with item selector, shipping method picker (EMS/Small Packet), customs declaration editor, and CPF/address validation

## 8. Admin Operational Portal

- [x] 8.1 Implement `(admin)` group layout shell with administrative security guards
- [x] 8.2 Build Admin Dashboard (`src/routes/(admin)/admin/dashboard/+page.svelte`) displaying operational counters and pending actions
- [x] 8.3 Build Pre-Orders Management view (`src/routes/(admin)/admin/pre-pedidos/+page.svelte`) with filtering, purchase completion modal, and domestic tracking entry
- [x] 8.4 Build Warehouse Fast Check-in view (`src/routes/(admin)/admin/warehouse-checkin/+page.svelte`) with rapid search by suite code, scale weight input in grams, and camera/upload widget for up to 5 inspection photos
- [x] 8.5 Build Dispatch Management view (`src/routes/(admin)/admin/envios/+page.svelte`) with shipment details, 1-click "Exportar para Japan Post" generator, and international tracking registration modal

## 9. Integration, Verification & Deployment Readiness

- [x] 9.1 Run backend tests and verify database migrations, constraints, and business logic calculations (fee floor, Landed Cost)
- [x] 9.2 Verify frontend build (`npm run build`) and PWA asset generation
- [x] 9.3 Perform local end-to-end smoke test using the **native local stack** (native PostgreSQL on `localhost:5432` + `uvicorn --reload` + `npm run dev`) verifying communication between backend, frontend, and PostgreSQL — `docker-compose up` is reserved for the Coolify deploy path
- [x] 9.4 Validate Coolify deployment configuration (`docker-compose.yml` + Dockerfiles), environment variable specifications, and persistent volume bindings
