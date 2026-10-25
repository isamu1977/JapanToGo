## Why

The term "suíte" (suite) is an industry-specific jargon borrowed from American package forwarders that frequently confuses Brazilian consumers unfamiliar with cross-border logistics. Replacing "suíte" across the frontend and customer-facing communications with direct, intuitive terminology ("Box", "Meus Pacotes", "Meu Estoque", and "Endereço no Japão") eliminates cognitive friction, clarifies how packages are identified at the Osaka warehouse, and increases onboarding conversion while preserving the underlying database architecture.

## What Changes

- **Landing Page & Hero Section**:
  - Primary CTA button changed from "Criar Minha Suíte Grátis" to "Pegar Meu Endereço no Japão".
  - Hero subhead updated from "Você acompanha cada etapa pela sua suíte" to "Você acompanha cada etapa em tempo real pelo seu painel".
  - Demonstration card badge updated from "SUÍTE #JTG-1001" to "BOX #JTG-1001".
  - Card footer explanatory text updated to: "O seu código exclusivo de Box (#JTG-XXXX) e o endereço completo ficam disponíveis no seu painel assim que você se cadastra".
- **Authenticated Client Area (Dashboard & Navigation)**:
  - Navigation menu item changed from "Minha Suíte" to "Meus Pacotes" (maintaining route `/suite` to avoid breaking links).
  - Address display page (`/endereco` and `AddressCard.svelte`): identify the user code as "Código do seu Box: #JTG-XXXX", clearly instructing users to place it alongside the building complement line for sorting.
  - Dashboard and shipments flow: update labels such as "Itens na suíte" to "Itens no seu Box" or "Meus Pacotes", and "Sua suíte está vazia" to "Seu Box está vazio".
  - Pre-order status updates: replace "Item adicionado à sua suíte" with "Item recebido no seu Box / Estoque".
- **Technical Integrity & Compliance**:
  - Retain the database column `suite_code` and internal API endpoints (`/api/v1/suite`) to prevent breaking migrations, schemas, and historical data.
  - Update marketing, contact form, and policy texts to consistently use "Box" and "painel" instead of "suíte".

## Capabilities

### Modified Capabilities
- `marketing-and-compliance`: Update Hero CTA, value copy, visual demonstration badge ("BOX #JTG-1001"), and footer notes across marketing and legal pages.
- `auth-and-suite-management`: Update client address display labels and navigation text to replace "suíte" with "Código do Box" and "Meus Pacotes".

## Impact

- Frontend:
  - `HeroSection.svelte` (CTA, copy, badge, card footer).
  - `AppShell.svelte` (navigation label "Meus Pacotes", header tag).
  - `AddressCard.svelte` and `/endereco/+page.svelte` (clear Box code guidance).
  - `/dashboard/+page.svelte`, `/suite/+page.svelte`, `/envios/+page.svelte`, `/pre-pedidos/+page.svelte`.
  - Policy, contact, and auth screens (`/contato`, `/login`, `/register`, `/cookies`).
- Backend: None (database schemas, sequences, and API contracts remain fully backward compatible).
