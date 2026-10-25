## Why

The JapanToGo landing page currently has visual redundancies and cognitive overload, specifically a duplicate "Comparativo Rápido de Taxas" block below the workflow tabs and a heavy embedded landed cost calculator in the middle of the marketing journey. Moving the landed cost simulator to a dedicated, focused `/simulador` page and removing duplicate fee cards streamlines the landing page conversion flow, improves page load performance, and creates a clear, distraction-free calculation experience.

## What Changes

- **Removal of Redundant "Comparativo Rápido de Taxas"**:
  - Remove the duplicate side-by-side fee comparison card block located beneath the "Como Funciona" workflow tabs in `WorkflowComparison.svelte`.
  - Maintain fee information (20% service fee and ¥ 2.000 floor) cleanly embedded inside the primary workflow cards for each modality.
- **Extraction of Simulator from Home to Dedicated `/simulador` Route**:
  - Remove the entire "Transparência - Você sabe exatamente o que paga" section and embedded `LandedCostCalculator` from `src/routes/(marketing)/+page.svelte`.
  - Ensure `src/routes/(marketing)/simulador/+page.svelte` is a clean, dedicated calculation workspace with complete breakdown, official freight bands, and Brazilian customs projections.
- **Navigation and CTA Direct Links**:
  - Update the "Simulador" navigation link in `NavHeader.svelte` to route directly to `/simulador` rather than linking to in-page anchor `#simulador`.
  - Update the secondary hero CTA button in `HeroSection.svelte` ("Simular Custos") to navigate directly to `/simulador`.
- **Harmonized Section Flow and Vertical Rhythm**:
  - Transition directly from "Como Funciona" -> "Lojas Recomendadas" -> "Pilares Operacionais" -> "Dúvidas Frequentes (FAQ)" -> Final CTA -> Footer.
  - Review section paddings and transitions to maintain a balanced visual cadence without abrupt breaks or awkward spacing.

## Capabilities

### Modified Capabilities
- `marketing-and-compliance`: Modify landing page requirements to reflect the direct link to `/simulador`, hero CTA link update, removal of the duplicate fee comparison block, and dedicated placement of the interactive landed cost simulator on `/simulador`.

## Impact

- Frontend:
  - `src/routes/(marketing)/+page.svelte` (simplified layout without embedded simulator).
  - `src/lib/components/landing/WorkflowComparison.svelte` (removal of quick fee comparison cards).
  - `src/lib/components/layout/NavHeader.svelte` (direct route link for Simulador).
  - `src/lib/components/landing/HeroSection.svelte` (direct route link for Simular Custos).
  - `src/routes/(marketing)/simulador/+page.svelte` (refined dedicated simulator route).
- User Experience: Faster landing page scanning, reduced cognitive friction, clearer intent-based routing to the calculator tool.
