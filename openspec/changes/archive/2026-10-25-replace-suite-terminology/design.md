## Context

In cross-border package forwarding, the term "suíte" is a direct translation of the English word "suite" (used by legacy American freight forwarders). However, Brazilian consumers frequently confuse "suíte" with hotel accommodations or physical rooms, creating confusion around what the code `#JTG-XXXX` represents.

By transitioning all user-facing copy to self-explanatory terms:
- **"Código do Box"** / **"Seu Box no Japão"** (clarifies that it is the customer's individual storage bin/inbox at the Osaka warehouse)
- **"Meus Pacotes"** / **"Meu Estoque"** (replaces "Minha Suíte" in the navigation)
- **"Pegar Meu Endereço no Japão"** (stronger, intent-focused CTA than "Criar Minha Suíte Grátis")

The system becomes immediately intuitive to Brazilian e-commerce shoppers without modifying backend database schemas.

## Goals / Non-Goals

**Goals:**
- Replace customer-facing references to "suíte" across the Landing Page, Hero section, and demonstration card with "Box", "Painel" and "Endereço no Japão".
- Update client application navigation: replace "Minha Suíte" with "Meus Pacotes" in `AppShell.svelte`.
- Update address instructions in `AddressCard.svelte` and `/endereco/+page.svelte` to highlight "Código do seu Box: #JTG-XXXX".
- Update dashboard, pre-order, and shipment status messages ("Item recebido no seu Box / Estoque").
- Update auth screens, contact forms, and legal policy pages to refer to "Box" and "painel do cliente".

**Non-Goals:**
- Renaming database columns (such as `users.suite_code`), sequence names, or backend Python attributes (`user.suite_code`). These remain unchanged to guarantee zero migration risk and total backward compatibility.
- Changing route URL `/suite` in SvelteKit (preserving existing bookmarks and internal links).

## Decisions

1. **Copy Terminology Mapping**:
   - `Criar Minha Suíte Grátis` &rarr; `Pegar Meu Endereço no Japão` (Hero CTA)
   - `Você acompanha cada etapa pela sua suíte` &rarr; `Você acompanha cada etapa em tempo real pelo seu painel`
   - `SUÍTE #JTG-1001` &rarr; `BOX #JTG-1001`
   - `Seu endereço privativo no galpão...` &rarr; `O seu código exclusivo de Box (#JTG-XXXX) e o endereço completo ficam disponíveis no seu painel assim que você se cadastra`
   - `Minha Suíte` (Menu) &rarr; `Meus Pacotes`
   - `Código de Suíte` &rarr; `Código do seu Box`
   - `Itens na suíte` &rarr; `Itens no seu Box` / `Meus Pacotes`
   - `Sua suíte está vazia` &rarr; `Seu Box está vazio`

2. **Zero-Downtime Backend Independence**:
   - The frontend API store `suiteCode` (`frontend/src/lib/stores/auth.ts`) and TypeScript types (`suite_code`) are kept internally, while UI display labels present "Código do Box".

## Risks / Trade-offs

- *Risk of broken regex or unit tests checking specific strings* &rarr; Update corresponding frontend test assertions where UI text is explicitly verified.
