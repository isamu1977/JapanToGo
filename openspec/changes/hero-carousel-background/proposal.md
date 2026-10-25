## Why

The Hero section currently uses purely synthetic CSS radial gradients and geometric washes. Integrating an authentic, high-definition photo background carousel depicting genuine Osaka warehouse handling (white-glove item inspection, precision workbench box sealing, protective flat-lay cushioning, and final international dispatch parcels) establishes immediate human connection and operational credibility for cross-border buyers.

## What Changes

- **Atmospheric Background Carousel with Smooth Cross-Fade**:
  - Integrate four authentic operational photos located in `static/images/hero/`:
    * `/images/hero/hero-01.jpeg`: White-glove item inspection and check-in.
    * `/images/hero/hero-02.jpeg`: Workbench carton sealing and reinforced tape preparation.
    * `/images/hero/hero-03.jpeg`: Protective bubble wrap and flat-lay cushioning layout.
    * `/images/hero/hero-04.jpeg`: Final consolidated parcel weighed and labeled for international airmail.
  - Automatic slide cycling every 6 seconds with smooth cross-fade opacity transitions (1000ms–1500ms) eliminating abrupt cuts.
  - Subtle Ken Burns effect (slow organic scale from 1.0 to 1.04) for cinematic presence.
- **High-Contrast Readability Gradient Overlay**:
  - Layer a multi-stop dark gradient (`from-slate-950/95 via-slate-950/85 to-slate-900/80`) paired with a bottom vignette to ensure headline typography, trust pills, CTAs, and the right-hand Box demo card remain 100% legible.
  - Retain the subtle Japanese seigaiha / dot wash at low opacity over the images to preserve brand identity.
- **Discrete Slide Indicators & Navigation**:
  - Add 4 minimalistic translucent pill/dot indicators at the base of the Hero section, providing active status and supporting one-click manual slide selection.

## Capabilities

### Modified Capabilities
- `marketing-and-compliance`: Update `Requirement: Modern Landing Page with Brand Identity` to specify the authentic photo carousel background in the Hero section with smooth cross-fade, Ken Burns effect, high-contrast overlay, and slide indicators.

## Impact

- Frontend:
  - `src/lib/components/landing/HeroSection.svelte`: Add carousel state, interval timers, transition classes, and indicator controls.
  - `static/images/hero/`: Already populated with `hero-01.jpeg` through `hero-04.jpeg`.
  - Zero impact on backend APIs, database schemas, or build pipelines.
