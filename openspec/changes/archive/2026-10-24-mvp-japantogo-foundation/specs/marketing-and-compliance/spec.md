## ADDED Requirements

### Requirement: Modern Landing Page with Brand Identity
The system SHALL display a public, responsive landing page with the identity "JapanToGo - FROM JAPAN TO YOUR DOOR", explaining the two primary workflows (Compra Assistida and Redirecionamento Puro), transparent fee structure, and calls to action for registration and cost simulation.

#### Scenario: Public visitor accesses landing page
- **WHEN** an unauthenticated visitor navigates to `/`
- **THEN** the system renders the landing page featuring the hero section, step-by-step workflow guide, suite benefits, fee calculator highlight, and navigation links to legal pages and login

### Requirement: Interactive Landed Cost Simulator
The system SHALL provide an interactive Landed Cost Simulator capable of estimating total landed costs in BRL and JPY, taking as inputs item price (JPY), order type, and estimated parcel weight (grams).

#### Scenario: Calculating assisted purchase landed cost
- **WHEN** a user enters item price of ¥ 8.000 JPY, estimated weight of 1000g, and selects EMS shipping to Brazil
- **THEN** the simulator displays:
  - Base item price in JPY and converted to BRL
  - JapanToGo service fee of ¥ 2.000 JPY (minimum floor)
  - Estimated EMS freight cost
  - Brazil customs import tax projection (60% federal RTS + applicable ICMS calculated 'por dentro')
  - Estimated total in BRL and JPY with an exchange rate disclaimer

#### Scenario: Calculating pure forwarding landed cost
- **WHEN** a user enters item price of ¥ 15.000 JPY, selects Redirection with estimated weight of 500g and Small Packet shipping
- **THEN** the simulator excludes the assisted purchase fee, computes the freight estimate and projected import duties, showing the total landed cost

### Requirement: Gateway-Compliant Japanese Legal Notice Pages
The system SHALL provide public legal compliance pages adhering to Japanese e-commerce legal standards required by payment processors (Square, Stripe, Wise), including Terms of Use (利用規約), Privacy Policy (プライバシーポリシー), and Specified Commercial Transactions Act disclosure (特定商取引法に基づく表記).

#### Scenario: Visitor views Tokushoho legal disclosure
- **WHEN** a visitor navigates to `/tokushoho`
- **THEN** the system renders the Japanese Specified Commercial Transactions Act notice disclosing company/operator name, contact email, operating address in Japan, pricing and additional fees, payment terms, delivery timelines, and cancellation/return policies in bilingual Japanese and Portuguese

#### Scenario: User registers and records legal terms acceptance
- **WHEN** a user completes registration
- **THEN** the system records an entry in `legal_terms_acceptance` with the user ID, term types accepted (`terms_of_service`, `privacy_policy`), version string, timestamp, and client IP address
