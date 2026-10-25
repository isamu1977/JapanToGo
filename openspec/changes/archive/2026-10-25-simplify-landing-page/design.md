## Context

The JapanToGo marketing landing page currently aggregates multiple informational components on a single scroll path: Hero, Workflow Comparison, Store Showcase, Operational Pillars, a duplicate "Comparativo Rápido de Taxas" block, an embedded "Transparência" section housing the full `LandedCostCalculator`, FAQ, and Final CTA. 

User testing and feedback indicate that having the full interactive calculator embedded inline introduces cognitive friction and lengthens the landing page unnecessarily, while the duplicate quick fee cards merely re-state what is already documented in the workflow cards. Isolating the calculator to `/simulador` and pruning redundant blocks establishes a cleaner reading hierarchy and a focused calculation tool.

## Goals / Non-Goals

**Goals:**
- Eliminate the redundant "Comparativo Rápido de Taxas" block in `WorkflowComparison.svelte`.
- Remove the inline fee summary and embedded `LandedCostCalculator` from `src/routes/(marketing)/+page.svelte`.
- Ensure `src/routes/(marketing)/simulador/+page.svelte` is the canonical, rich destination for landed cost estimations.
- Update header navigation and Hero secondary button to point directly to `/simulador`.
- Re-balance vertical spacing across remaining landing page sections ("Como Funciona" -> "Lojas Recomendadas" -> "Pilares Operacionais" -> "FAQ" -> "Final CTA").

**Non-Goals:**
- Removing or altering the core calculation logic of `LandedCostCalculator.svelte` or `calculator.ts`.
- Altering the pricing structure (20% fee, ¥ 2.000 floor, official Japan Post rates, and RTS + ICMS remain intact).

## Decisions

1. **Direct Route Linking**:
   - In `NavHeader.svelte`, the `navItems` array will distinguish in-page anchors (`#como-funciona`, `#lojas`, `#faq`) from page routes (`/simulador`). This prevents broken in-page jump attempts and provides an instant transition to the calculator.
   - In `HeroSection.svelte`, the secondary CTA button `href="#simulador"` is updated to `href="/simulador"`.

2. **Clean Landing Page Component Composition**:
   - `+page.svelte` will compose:
     1. `<HeroSection />`
     2. `<WorkflowComparison />` (without fee comparison cards)
     3. `<StoreShowcase />`
     4. `<OperationalPillars />`
     5. `<FaqAccordion />`
     6. `<FinalCta />`
   - Unused imports (`LandedCostCalculator`, `ShieldCheck`, `ArrowRight`, `fees` array) are cleaned up from `+page.svelte`.

3. **Isolated Dedicated `/simulador` Route**:
   - The `/simulador` page retains the full calculator, explanatory cards, and disclaimers with its own dedicated layout container and metadata.

## Risks / Trade-offs

- *User looking for instant calculator on the home page* → Mitigated by prominent CTA buttons in the Hero ("Simular Custos") and main navigation ("Simulador"), which load `/simulador` instantaneously via SvelteKit client-side routing.
