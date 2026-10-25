## 1. Backend Contact API

- [x] 1.1 Create Pydantic contact schemas in `backend/app/schemas/contact.py`
- [x] 1.2 Implement `POST /api/v1/contact` and register router in `backend/app/api/v1/api.py` and alias in `backend/app/main.py`
- [x] 1.3 Add backend unit tests in `backend/tests/test_contact.py` and verify with pytest

## 2. Frontend Cookie Consent System

- [x] 2.1 Implement cookie consent store and script gating in `frontend/src/lib/stores/cookies.ts`
- [x] 2.2 Create floating `CookieBanner.svelte` with accept all, reject non-essential, and preferences modal
- [x] 2.3 Mount `CookieBanner.svelte` in root layout `frontend/src/routes/+layout.svelte`
- [x] 2.4 Create dedicated `/cookies` policy page at `frontend/src/routes/(marketing)/cookies/+page.svelte`

## 3. Customer Contact Page

- [x] 3.1 Implement `/contato` page with validated inquiry form, subject dropdown, optional suite code, and reactive submission
- [x] 3.2 Display official WhatsApp button, email `contato@japantogo.com`, and bilingual JST/BRT operational hours

## 4. Regulation and Operational Protection Pages

- [x] 4.1 Create `/itens-proibidos` page with categorized air cargo guide (batteries, perfumes, aerosols, meats/seeds, sanctions)
- [x] 4.2 Create `/envios-e-devolucoes` page covering handling times, DDU/DAP customs clearance, and returns policy
- [x] 4.3 Create `/termos-usados` page detailing proxy purchase mandate and secondhand auction inspection limits

## 5. Footer Update and Verification

- [x] 5.1 Update `Footer.svelte` with new legal links (cookies, prohibited items, shipping/returns) and Contato under serviços
- [x] 5.2 Validate frontend with formatting, type check, and tests, and run backend test suite
