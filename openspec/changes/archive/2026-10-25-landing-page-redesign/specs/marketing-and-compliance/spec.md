## MODIFIED Requirements

### Requirement: Modern Landing Page with Brand Identity
The system SHALL display a public, responsive landing page with the identity "JapanToGo - FROM JAPAN TO YOUR DOOR", featuring an immersive modern Japanese visual design, a hero section with animated suite address demonstration, an interactive workflow comparator for Compra Assistida and Redirecionamento Puro, a showcase of Japanese partner marketplaces, a landed cost simulator with instant presets, operational proof points, an interactive FAQ section, and clear calls to action.

#### Scenario: Public visitor accesses redesigned landing page
- **WHEN** an unauthenticated visitor navigates to `/`
- **THEN** the system renders the landing page featuring:
  - Hero section with brand value proposition, live operational trust badges (Osaka warehouse, pesagem em gramas, inspeção fotográfica), and interactive suite address preview card with copy action
  - Curated showcase of Japanese stores (Mercari, Amazon JP, Rakuten, Yahoo! Auctions, AmiAmi, Surugaya, Mandarake)
  - Interactive tabbed comparator between Compra Assistida (代行) and Redirecionamento Puro (Forwarding)
  - Interactive Landed Cost Simulator with 1-click product presets and dynamic cost breakdown
  - 4-pillar operational benefits showcase (pesagem digital, inspeção com 5 fotos, consolidação inteligente, fretes EMS/Small Packet)
  - Interactive FAQ accordion for import duties (RTS 60% + ICMS), delivery times, and prohibited goods
  - High-conversion footer and sticky CTA elements with mobile touch target compliance (>= 44px)

### Requirement: Interactive Landed Cost Simulator
The system SHALL provide an interactive Landed Cost Simulator capable of estimating total landed costs in BRL and JPY, accepting item price (JPY), order type, and parcel weight (grams), and featuring instant 1-click product category presets for common imported goods.

#### Scenario: Calculating assisted purchase landed cost with category preset
- **WHEN** a user selects a preset such as "Action Figure (Anime)" or enters ¥ 8.000 JPY with 1000g weight and EMS shipping
- **THEN** the simulator displays:
  - Base item price in JPY and converted to BRL
  - JapanToGo service fee (20% or minimum floor of ¥ 2.000)
  - Estimated EMS freight cost
  - Brazilian customs projection (60% federal RTS + applicable ICMS calculated 'por dentro')
  - Estimated total in BRL and JPY with exchange rate disclaimer and interactive breakdown toggles

#### Scenario: Calculating pure forwarding landed cost with category preset
- **WHEN** a user selects a preset such as "Caixa de Snacks Japoneses" or enters ¥ 4.000 JPY with 600g weight and Small Packet shipping
- **THEN** the simulator excludes the assisted purchase fee, computes the freight estimate and projected import duties, showing the total landed cost

## ADDED Requirements

### Requirement: Interactive Store Showcase and Discovery
The system SHALL display a curated directory of popular Japanese e-commerce platforms and specialty stores categorized by product genre to inspire users and demonstrate platform capability.

#### Scenario: Visitor browses popular Japanese stores
- **WHEN** a visitor views the store showcase on the landing page
- **THEN** the system displays Japanese store badges (Mercari, Rakuten, Amazon JP, Yahoo! Auctions, AmiAmi, Surugaya, Mandarake) with category labels and a clear indicator of whether they require assisted purchase or pure forwarding

### Requirement: Frequently Asked Questions Accordion
The system SHALL provide an interactive FAQ accordion addressing essential customs clearance, prohibited items, consolidation, and delivery questions with keyboard accessibility and animated transitions.

#### Scenario: Visitor expands FAQ item
- **WHEN** a visitor clicks or presses Enter/Space on an FAQ question
- **THEN** the item toggles open, updates `aria-expanded="true"`, and reveals clear guidance on Brazilian import taxes, prohibited items, and shipping times
