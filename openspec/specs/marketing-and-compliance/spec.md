# marketing-and-compliance Specification

## Purpose
Defines the public landing page with the "JapanToGo - FROM JAPAN TO YOUR DOOR" identity, the interactive landed cost simulator (JPY to BRL conversion, 20% service fee, freight estimate and the RTS 60% + ICMS projection), and the Japanese legal notice pages (利用規約, プライバシーポリシー, 特定商取引法に基づく表記) required by payment gateways.
## Requirements
### Requirement: Modern Landing Page with Brand Identity
The system SHALL display a public, responsive landing page with the identity "JapanToGo - FROM JAPAN TO YOUR DOOR", featuring a streamlined navigation header without legal links, a hero section displaying a visual box mockup without exposing the confidential warehouse address, intuitive customer-focused copy ("Pegar Meu Endereço no Japão", "acompanhe em tempo real pelo seu painel"), an interactive workflow comparator stating 20% service fee (¥ 2.000 floor) for both assisted purchase and pure redirection without redundant quick comparison blocks, a curated store showcase, and an interactive FAQ accordion, while routing simulator calculations to the dedicated `/simulador` page.

#### Scenario: Public visitor accesses landing page header
- **WHEN** an unauthenticated visitor navigates to `/`
- **THEN** the header displays:
  - Brand logo linking to `/`
  - In-page navigation anchors: "Como funciona" (`#como-funciona`), "Lojas" (`#lojas`), and "Dúvidas" (`#faq`)
  - Direct route link for "Simulador" pointing to `/simulador`
  - Ghost/outline action button "Entrar" (`/login`)
  - Highlighted primary red button "Criar conta" (`/register`)
  - No links to "Termos de uso", "Privacidade" or "特定商取引法" in the main navigation header (these remain in the footer)

#### Scenario: Public visitor views Hero section
- **WHEN** a visitor views the hero section
- **THEN** the system renders:
  - High-impact value proposition "Compre no Japão. Receba no Brasil."
  - Value copy highlighting real-time tracking through the dashboard: "Você acompanha cada etapa em tempo real pelo seu painel."
  - Primary CTA button "Pegar Meu Endereço no Japão" linking to `/register`
  - Secondary button "Simular Custos" linking directly to the dedicated `/simulador` route
  - A visual service mockup on the right side depicting a parcel in the user's box with badge "BOX #JTG-1001", status indicator, digital weight badge ("Pesado: 350g"), and simulated 5-angle inspection photo thumbnails
  - Explanatory footnote: "O seu código exclusivo de Box (#JTG-XXXX) e o endereço completo ficam disponíveis no seu painel assim que você se cadastra"
  - No disclosure of the physical warehouse address (〒540-0027 or Osaka street address), reserving confidential warehouse details strictly for authenticated users

#### Scenario: Visitor compares service workflows
- **WHEN** a visitor views the "Como funciona" section
- **THEN** the system displays:
  - Tabbed or switchable views for "Compra assistida (代行)" and "Redirecionamento puro (転送)"
  - Each view clearly details the 20% service fee (minimum floor of ¥ 2.000), operational turnaround, and 4-step sequence
  - No redundant "Comparativo Rápido de Taxas" card block rendered beneath the workflow tabs
  - Direct visual transition from the workflow section to the "Lojas Recomendadas" showcase

### Requirement: Interactive Landed Cost Simulator
The system SHALL provide an interactive Landed Cost Simulator on a dedicated route at `/simulador`, executing locally and reactively in client-side code, eliminating network fetch errors ("Failed to fetch"), supporting instant updates on keystrokes, and calculating the 20% service fee (minimum ¥ 2.000 floor), official Japan Post freight bands (Small Packet / EMS), and Brazilian customs projections (60% RTS + ICMS calculated por dentro).

#### Scenario: Calculating landed cost reactively on the dedicated simulator page
- **WHEN** a visitor types or changes the item price, weight, or shipping method on `/simulador`
- **THEN** the simulator recalculates immediately without network latency or "Failed to fetch" errors, displaying:
  - Base item price in JPY and BRL
  - Service fee of 20% with a minimum floor of ¥ 2.000 for both assisted purchase and forwarding
  - Freight estimated according to Japan Post weight bands
  - Brazilian customs projection (60% federal RTS + applicable ICMS calculated por dentro)
  - Estimated total in BRL and JPY with currency rate indicator and cost breakdown bars
  - Explanatory breakdown cards for service fees, freight, and Brazilian customs

### Requirement: Gateway-Compliant Japanese Legal Notice Pages
The system SHALL provide public legal compliance pages adhering to Japanese e-commerce legal standards required by payment processors (Square, Stripe, Wise), including Terms of Use (利用規約), Privacy Policy (プライバシーポリシー), and Specified Commercial Transactions Act disclosure (特定商取引法に基づく表記).

#### Scenario: Visitor views Tokushoho legal disclosure
- **WHEN** a visitor navigates to `/tokushoho`
- **THEN** the system renders the Japanese Specified Commercial Transactions Act notice disclosing company/operator name, contact email, operating address in Japan, pricing and additional fees, payment terms, delivery timelines, and cancellation/return policies in bilingual Japanese and Portuguese

#### Scenario: User registers and records legal terms acceptance
- **WHEN** a user completes registration
- **THEN** the system records an entry in `legal_terms_acceptance` with the user ID, term types accepted (`terms_of_service`, `privacy_policy`), version string, timestamp, and client IP address

### Requirement: Interactive Store Showcase and Discovery
The system SHALL display a curated directory of popular Japanese e-commerce platforms and specialty stores (Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Surugaya, Pokémon Center JP) featuring official stylized brand marks on transparent backgrounds, category labels, operational mode badges, and direct links to the official store websites opening in a new tab.

#### Scenario: Visitor browses popular Japanese stores
- **WHEN** a visitor views the store showcase on the landing page
- **THEN** the system displays:
  - Stylized official visual brand marks for each Japanese marketplace
  - Category filters and mode indicators (Compra assistida / Redirecionamento)
  - Cards with subtle borders, elevation on hover (`hover:-translate-y-1 hover:shadow-md transition-all`), and external links with `target="_blank"` and `rel="noopener noreferrer"`

### Requirement: Frequently Asked Questions Accordion
The system SHALL provide an interactive FAQ accordion addressing essential customs clearance, prohibited items, consolidation, and delivery questions with keyboard accessibility and animated transitions.

#### Scenario: Visitor expands FAQ item
- **WHEN** a visitor clicks or presses Enter/Space on an FAQ question
- **THEN** the item toggles open, updates `aria-expanded="true"`, and reveals clear guidance on Brazilian import taxes, prohibited items, and shipping times

### Requirement: Cookie Consent Banner and Script Gating
The system SHALL display a floating cookie consent banner at the bottom of the viewport for visitors who have not yet established cookie preferences, offering granular controls ("Aceitar todos", "Rejeitar não essenciais", and "Preferências"), storing consent in `localStorage` and client cookies (`jtg_cookie_consent`), and preventively blocking third-party and analytics scripts until explicit opt-in consent is provided.

#### Scenario: First-time visitor views cookie banner
- **WHEN** a visitor navigates to any page of the platform without an existing `jtg_cookie_consent` record
- **THEN** the system displays a floating banner at the bottom of the screen with clear Brazilian Portuguese copy, three action buttons ("Aceitar todos", "Rejeitar não essenciais", "Preferências"), and a direct link to `/cookies`

#### Scenario: Visitor accepts all cookies
- **WHEN** a visitor clicks "Aceitar todos"
- **THEN** the system stores consent with `necessary: true`, `analytics: true`, `marketing: true`, sets expiration, hides the banner, and unblocks analytics tracking

#### Scenario: Visitor rejects non-essential cookies
- **WHEN** a visitor clicks "Rejeitar não essenciais"
- **THEN** the system stores consent with `necessary: true`, `analytics: false`, `marketing: false`, hides the banner, and keeps non-essential scripts blocked

#### Scenario: Visitor configures custom preferences
- **WHEN** a visitor clicks "Preferências"
- **THEN** an accessible preferences modal opens allowing granular toggles for analytics and marketing cookies while keeping necessary cookies locked to active, saving custom preferences upon confirmation

### Requirement: Dedicated Cookie Policy Page
The system SHALL provide a dedicated `/cookies` page detailing the categories, lifetimes, origins, and specific purposes of all cookies utilized on JapanToGo (technical session/auth, performance analytics, and user preference cookies).

#### Scenario: Visitor accesses the cookie policy
- **WHEN** a user navigates to `/cookies`
- **THEN** the system displays the complete cookie disclosure, categorizing cookies into Necessários, Analíticos, and Preferências, with instructions on how to manage or revoke consent directly from the browser

### Requirement: Customer Support Channel and Contact API
The system SHALL provide a responsive contact page at `/contato` featuring a validated inquiry form and official communication channels, accompanied by a backend endpoint `POST /api/contact` (and `POST /api/v1/contact`) that validates messages, logs support inquiries, and sends operational notifications and automated confirmations.

#### Scenario: Visitor submits contact inquiry
- **WHEN** a user fills out the contact form at `/contato` with valid name, email, subject, message, and optional suite code, and submits the form
- **THEN** the frontend sends a `POST` request to `/api/contact`, which validates the payload, logs the inquiry, returns a HTTP 200/201 response with confirmation message, and the frontend displays a success state

#### Scenario: Visitor views official direct channels
- **WHEN** a visitor visits `/contato`
- **THEN** the page displays direct links to the official WhatsApp support channel, direct email `contato@japantogo.com`, and clear operational hours displayed in both Japan Standard Time (JST) and Brasília Time (BRT)

### Requirement: Prohibited Air Cargo Guide
The system SHALL provide a dedicated visual guide at `/itens-proibidos` categorizing prohibited and restricted international air cargo under Japan Post, ICAO, and IATA regulations.

#### Scenario: Visitor consults prohibited items list
- **WHEN** a visitor accesses `/itens-proibidos`
- **THEN** the system displays structured, icon-illustrated categories covering flammable liquids/perfumes, loose lithium batteries and power banks, pressurized aerosols, perishable meats/seeds, counterfeit products, and items under international sanctions, clarifying why these cannot be airmailed

### Requirement: International Shipping and Customs Returns Policy
The system SHALL provide an international shipping, customs, and returns policy at `/envios-e-devolucoes` outlining fulfillment timelines, customs clearance responsibilities under DDU/DAP terms, procedures for unclaimed or rejected parcels, and return/refund limitations.

#### Scenario: Visitor consults shipping and customs liability
- **WHEN** a visitor navigates to `/envios-e-devolucoes`
- **THEN** the system details standard packing and dispatch times (1-3 business days), clarifies that destination customs clearance and import duties (e.g., Brazilian RTS and ICMS) are the sole legal responsibility of the importer (DDU/DAP), details the 20-30 day deadline for customs payment in Brazil before package abandonment, and defines refund rules

### Requirement: Used and Auction Terms of Science
The system SHALL provide a dedicated terms page at `/termos-usados` establishing JapanToGo's legal role as a purchasing mandatary and physical intermediary for secondhand platforms (Mercari, Yahoo! Auctions, Rakuten Rakuma), explaining auction bidding irrevocability and inspection scope.

#### Scenario: Visitor consults auction and used goods policy
- **WHEN** a user navigates to `/termos-usados`
- **THEN** the system outlines that bids placed on Yahoo! Auctions cannot be retracted, that JapanToGo inspects external physical condition and package contents against seller photos but cannot guarantee internal electronic functionality or original authenticity certificates, and clarifies the customer's assumption of marketplace seller risks

### Requirement: Global Legal and Service Navigation in Footer
The system SHALL display an updated footer with full regulatory links in the "Informações legais" column (Termos de uso, Política de privacidade, Tokushōhō, Política de cookies, Itens proibidos, Envios e devoluções) and the direct Contato link in the "Serviços" column across all pages.

#### Scenario: Visitor views footer links
- **WHEN** a user views the website footer on any page
- **THEN** the footer renders:
  - "Informações legais" including Termos de uso (`/termos`), Política de privacidade (`/privacidade`), 特定商取引法 (`/tokushoho`), Política de cookies (`/cookies`), Itens proibidos (`/itens-proibidos`), and Envios e devoluções (`/envios-e-devolucoes`)
  - "Serviços" including a direct link to Contato (`/contato`)

