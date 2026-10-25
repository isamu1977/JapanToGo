## ADDED Requirements

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
