## MODIFIED Requirements

### Requirement: Interactive Store Showcase and Discovery
The system SHALL display a curated directory of popular Japanese e-commerce platforms and specialty stores (Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Surugaya, Pokémon Center JP) featuring official stylized brand marks on transparent backgrounds, category labels, operational mode badges, and direct links to the official store websites opening in a new tab.

#### Scenario: Visitor browses popular Japanese stores
- **WHEN** a visitor views the store showcase on the landing page
- **THEN** the system displays:
  - Stylized official visual brand marks for each Japanese marketplace
  - Category filters and mode indicators (Compra assistida / Redirecionamento)
  - Cards with subtle borders, elevation on hover (`hover:-translate-y-1 hover:shadow-md transition-all`), and external links with `target="_blank"` and `rel="noopener noreferrer"`
