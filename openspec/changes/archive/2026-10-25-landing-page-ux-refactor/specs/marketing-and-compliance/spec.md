## MODIFIED Requirements

### Requirement: Modern Landing Page with Brand Identity
The system SHALL display a public, responsive landing page with the identity "JapanToGo - FROM JAPAN TO YOUR DOOR", featuring a streamlined anchor-only navigation header without legal links, a hero section displaying a visual suite mockup without exposing the confidential warehouse address, an interactive workflow comparator stating 20% service fee (¥ 2.000 floor) for both assisted purchase and pure redirection, a curated store showcase, an offline-resilient landed cost simulator, and an interactive FAQ accordion.

#### Scenario: Public visitor accesses landing page header
- **WHEN** an unauthenticated visitor navigates to `/`
- **THEN** the header displays solely:
  - Brand logo linking to `/`
  - In-page navigation anchors: "Como funciona" (`#como-funciona`), "Lojas" (`#lojas`), "Simulador" (`#simulador`), and "Dúvidas" (`#faq`) with no duplicate links
  - Ghost/outline action button "Entrar" (`/login`)
  - Highlighted primary red button "Criar conta" (`/register`)
  - No links to "Termos de uso", "Privacidade" or "特定商取引法" in the main navigation header (these remain in the footer)

#### Scenario: Public visitor views Hero section
- **WHEN** a visitor views the hero section
- **THEN** the system renders:
  - High-impact value proposition "Compre no Japão. Receba no Brasil."
  - Primary CTA button "Criar Minha Suíte Grátis" and secondary button "Simular Custos"
  - A visual service mockup on the right side depicting a parcel in the user's suite with a digital weight badge ("Pesado: 350g"), status indicator, and simulated 5-angle inspection photo thumbnails
  - No disclosure of the physical warehouse address (〒540-0027 or Osaka street address), reserving confidential warehouse details strictly for authenticated users

#### Scenario: Visitor compares service workflows
- **WHEN** a visitor views the "Como funciona" section
- **THEN** the system displays:
  - "Compra assistida (代行)": JapanToGo purchases items under demand, with a 20% service fee (minimum floor of ¥ 2.000)
  - "Redirecionamento puro": Customer purchases directly and ships to the warehouse; JapanToGo handles receipt, precision gram weighing, up to 5 inspection photos, and consolidation, charging a 20% service fee on declared value (minimum floor of ¥ 2.000)
  - No references to "Sem taxa de 20%" or "Quem tem cartão japonês"

### Requirement: Interactive Landed Cost Simulator
The system SHALL provide an interactive Landed Cost Simulator executing locally and reactively in client-side code on the landing page, eliminating network fetch errors ("Failed to fetch"), supporting instant updates on keystrokes, and calculating the 20% service fee (minimum ¥ 2.000 floor), official Japan Post freight bands (Small Packet / EMS), and Brazilian customs projections (60% RTS + ICMS calculated por dentro).

#### Scenario: Calculating landed cost reactively on the landing page
- **WHEN** a visitor types or changes the item price, weight, or shipping method in the landing page simulator
- **THEN** the simulator recalculates immediately without network latency or "Failed to fetch" errors, displaying:
  - Base item price in JPY and BRL
  - Service fee of 20% with a minimum floor of ¥ 2.000 for both assisted purchase and forwarding
  - Freight estimated according to Japan Post weight bands
  - Brazilian customs projection (60% federal RTS + applicable ICMS calculated por dentro)
  - Estimated total in BRL and JPY with currency rate indicator and cost breakdown bars
