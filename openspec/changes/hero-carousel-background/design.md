## Context

The Hero section is the highest-value conversion viewport on the JapanToGo landing page. Previously, the hero used purely abstract dark gradient divs and CSS patterns. The client provided four genuine, high-quality photographs taken in an active logistics hub:
1. White-glove item inspection (`hero-01.jpeg`)
2. Workbench sealing and taping (`hero-02.jpeg`)
3. Cushioning and bubble wrap flat-lay (`hero-03.jpeg`)
4. Final tagged parcel prepared for international flight dispatch (`hero-04.jpeg`)

These photos need to be presented dynamically as a living background without reducing the crisp contrast of the foreground text and the Box demonstration card.

## Goals / Non-Goals

**Goals:**
- Implement a reactive cross-fade background carousel inside `HeroSection.svelte` using Svelte 5 runes (`$state`, `$effect`).
- Rotate slides automatically every 6 seconds with a 1200ms opacity transition.
- Incorporate a subtle Ken Burns zoom (1.0 to 1.04) on active slides.
- Add a dark legibility overlay: `bg-gradient-to-r from-slate-950/95 via-slate-950/85 to-slate-900/80` plus a vertical bottom gradient (`from-transparent to-ink-990`) to blend into following sections.
- Retain the traditional subtle Japanese dot/seigaiha pattern over the image layer for brand continuity.
- Provide 4 interactive pill/dot indicators for active slide awareness and manual slide selection.
- Implement pause-on-hover so users inspecting details are not interrupted.

**Non-Goals:**
- Adding bulky third-party carousel libraries (such as Swiper or Splide) which inflate bundle size; native SvelteKit CSS transitions are lighter, faster, and zero-dependency.
- Moving or altering the core content hierarchy of the Hero copy, CTA buttons, trust badges, or the right-hand Box demo card.

## Decisions

1. **Native CSS Cross-Fade & Ken Burns**:
   - All four `<img>` elements are rendered in the DOM with `loading="eager"` for the first image and `loading="lazy"` for remaining ones.
   - Transitions between slides are handled with CSS opacity (`opacity-0` vs `opacity-100`) and scale (`scale-100` to `scale-105`), timed to transition smoothly over `duration-1000 ease-in-out`.
   - Timer is managed via `setInterval` inside Svelte's `$effect` lifecycle, properly cleared on component teardown.

2. **Overlay Hierarchy (Z-Index / Layering)**:
   - `Layer 0`: Photographic background carousel with `object-cover object-center w-full h-full absolute inset-0`.
   - `Layer 1`: High-contrast dark gradient overlay (`bg-gradient-to-r from-slate-950/95 via-slate-950/85 to-slate-900/80` + bottom shadow).
   - `Layer 2`: Geometric seigaiha wash with low opacity (`opacity-30`).
   - `Layer 3`: Foreground content grid (`z-10`) containing value proposition, CTA buttons, metrics, and the Box mockup card.
   - `Layer 4`: Discrete slide navigation indicators.

## Risks / Trade-offs

- *Image file sizes (approx 2.8MB–3.3MB each)* &rarr; In development they load from local `static/`. In production, standard CDN caching / WebP compression can optimize byte sizes, while `loading="eager"` on slide 1 ensures no initial flash of unstyled background.
- *Contrast degradation on light photo spots* &rarr; Multi-stop dark gradient overlay with up to 95% opacity in the copy region guarantees accessibility (WCAG AA/AAA contrast ratios for white text).
