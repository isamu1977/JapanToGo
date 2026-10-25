## Why

To operate as a cross-border proxy and package forwarding service between Japan, Brazil, and international destinations, JapanToGo must comply with international privacy frameworks (LGPD in Brazil, GDPR in the European Union, and APPI in Japan). Users require transparent cookie consent management with script gating, clear channels for customer and suite inquiries with direct messaging, and explicit operational disclosures regarding prohibited air cargo, customs liability (DDU/DAP), and used goods/auction mandates.

## What Changes

- **Cookie Consent Banner & Management (GDPR / LGPD / APPI)**:
  - Modern floating cookie banner at the bottom of the viewport in Portuguese.
  - Three user actions: "Aceitar todos", "Rejeitar não essenciais", and "Preferências" (granular modal for technical, analytics, and marketing cookies).
  - Persistence of consent in `localStorage` and client cookies (`jtg_cookie_consent`).
  - Preventive blocking of third-party scripts/analytics until explicit opt-in consent is granted.
  - Dedicated `/cookies` page explaining cookie classifications and purposes.
- **Customer Contact Channel (`/contato` & `POST /api/contact`)**:
  - Clean responsive contact form collecting Name, Email, Subject (Dúvida sobre envio, Orçamento, Suporte a pedido existente), Suite Number (optional), and Message.
  - Backend API endpoint `POST /api/contact` (and `/api/v1/contact`) validating payloads, dispatching internal operational notifications and automated customer confirmation.
  - Direct display of official support channels: official WhatsApp direct link, email `contato@japantogo.com`, and operating hours in both Japan (JST) and Brazil (BRT).
- **Operational Regulation & Customer Protection Pages**:
  - `/itens-proibidos`: Categorized guide detailing prohibited international air cargo (loose lithium batteries, flammable perfumes, aerosols, meats, plants/seeds, and sanctioned goods).
  - `/envios-e-devolucoes`: Shipping and returns policy detailing handling times, DDU/DAP customs clearance responsibilities, unclaimed parcels at customs, and return/refund conditions.
  - `/termos-usados`: Terms of science and risk acknowledgment for auction and secondhand marketplace purchases (Mercari, Yahoo! Auctions), clarifying JapanToGo's role as purchasing proxy and physical inspection agent.
- **Global Footer Update**:
  - Update "Informações legais" section with links to Termos de uso, Política de privacidade (including DPO contact info), 特定商取引法に基づく表記 (Tokushōhō), Política de cookies, Itens proibidos, and Envios e devoluções.
  - Update "Serviços" section with a direct link to Contato.

## Capabilities

### Modified Capabilities
- `marketing-and-compliance`: Add Cookie Consent Banner with preventative script blocking, `/cookies` policy page, responsive Contact page with `/api/contact` backend handler, specialized operational policy pages (`/itens-proibidos`, `/envios-e-devolucoes`, `/termos-usados`), and updated footer links.

## Impact

- Frontend: SvelteKit routes (`/cookies`, `/contato`, `/itens-proibidos`, `/envios-e-devolucoes`, `/termos-usados`), cookie consent store and banner component, layout and footer updates.
- Backend: FastAPI route `POST /api/v1/contact` (aliased at `/api/contact`), contact schemas, test suites.
- Dependencies & Privacy: Consent gating mechanism in frontend without breaking core app navigation.
