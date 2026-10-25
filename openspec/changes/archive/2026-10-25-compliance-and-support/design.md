## Context

JapanToGo operates a cross-border proxy buying and forwarding platform between Japan and international markets (predominantly Brazil, as well as Portugal and the USA). As such, it must strictly comply with Brazilian LGPD (Lei Geral de Proteção de Dados), European GDPR (General Data Protection Regulation), and Japanese APPI (Act on the Protection of Personal Information). Additionally, customers require a transparent and reliable support channel (`/contato`), clear air cargo prohibitions (`/itens-proibidos`), international shipping/customs liability disclosures (`/envios-e-devolucoes`), and auction/secondhand purchase mandates (`/termos-usados`).

## Goals / Non-Goals

**Goals:**
- Provide a clean, modern floating cookie banner with opt-in script gating, three choices ("Aceitar todos", "Rejeitar não essenciais", "Preferências"), and persistent storage (`jtg_cookie_consent`).
- Create a dedicated `/cookies` policy page detailing cookie categories, purposes, and retention periods.
- Build a responsive `/contato` form and a robust backend endpoint `POST /api/contact` (and `/api/v1/contact`) validating input and logging inquiries for team dispatch and automated confirmation.
- Display official communication channels: direct WhatsApp button, official email `contato@japantogo.com`, and operational schedules in JST (Japan) and BRT (Brazil).
- Create rich, beautifully styled operational policy pages: `/itens-proibidos`, `/envios-e-devolucoes`, and `/termos-usados`.
- Update the global Footer to link to all legal policies and support channels.

**Non-Goals:**
- Relying on external paid CMP platforms (such as OneTrust or Cookiebot) that add heavy external JavaScript, latency, and third-party tracking.
- Requiring live third-party SMTP server credentials to pass automated tests; the contact service will log notifications and safely simulate delivery when external email provider keys are unconfigured.

## Decisions

1. **Native Lightweight Consent Management**:
   - Implemented via a client-side Svelte store (`$lib/stores/cookies.ts`) and a floating component (`$lib/components/ui/CookieBanner.svelte`).
   - Stores user preferences in `localStorage` and a cookie named `jtg_cookie_consent` containing JSON `{ necessary: true, analytics: boolean, marketing: boolean, timestamp: string }`.
   - Fires a custom window event (`jtg:cookie-consent-updated`) whenever preferences change, allowing any analytics or external script to initialize conditionally.

2. **Backend Contact Endpoint**:
   - Located at `backend/app/api/v1/contact.py`, schemas at `backend/app/schemas/contact.py`.
   - Endpoint: `POST /api/v1/contact` (aliased in `backend/app/main.py` as `/api/contact`).
   - Fields: `name`, `email`, `subject` (dropdown options: Dúvida sobre envio, Orçamento, Suporte a pedido existente, Outros), optional `suite_code`, and `message`.
   - Validated with Pydantic, returning a standardized response: `{ success: true, message: "Mensagem recebida com sucesso! Em breve retornaremos." }`.

3. **Consistent Visual Language & Accessible Pages**:
   - All new marketing and legal routes (`/cookies`, `/contato`, `/itens-proibidos`, `/envios-e-devolucoes`, `/termos-usados`) are placed under `frontend/src/routes/(marketing)/`.
   - Follow the existing design system: dark navy header/badges, crimson accents, gold indicators, card elevations, bilingual Japanese/Portuguese touches, and full semantic HTML.

## Risks / Trade-offs

- *Cookie banner obtrusiveness* → Fixed bottom floating card with subtle glassmorphism and dismissible preferences drawer that does not block mobile navigation.
- *Contact form spam or invalid inputs* → Strict Pydantic validations on backend (valid email format, min/max lengths) and client-side HTML5 input validation.
