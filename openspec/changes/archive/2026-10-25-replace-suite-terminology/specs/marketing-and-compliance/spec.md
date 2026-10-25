## MODIFIED Requirements

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
