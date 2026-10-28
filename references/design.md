# Design without AI slop

AI slop is what you get when nothing was decided, so every choice falls back to the most common pattern. The cure is to make decisions from the PRD (audience, tone, positioning angle) and write them down as tokens.

If the `impeccable` or `design-review` skills are installed, they're good for deep critique passes. This file is the working standard.

## 1. Directions (web-designer proposes 2–3)

Each direction is one short block:
- **Name + one-line mood**, tied to the audience (e.g. "Workshop manual: honest, tactile, for tradespeople who distrust polish")
- **Type**: display + body pairing, with sizes for h1/body
- **Palette**: bg, fg, accent, muted, and one surprise colour, each a hex value with a contrast note
- **Layout idea**: grid, density, how the hero is composed
- **Signature detail**: the one thing people will remember (a texture, a cursor, an unusual nav, an illustration style, a motion moment)
- **Reference**: which RESEARCH.md gap it exploits

The directions must differ in kind, not only in colour.

## 2. Defaults to reject (unless the PRD gives a reason)

- Inter / Roboto / Arial / system-ui as the *display* face. They're fine as body text when chosen deliberately.
- Purple→blue gradients, glassmorphism cards, glowing blobs behind the hero.
- A centred hero with headline, subline, two buttons, then three icon cards, then logos, then testimonials, then FAQ, then CTA. The template page.
- Emojis as icons, and random 3D illustrations.
- Generic copy: "Elevate your …", "Unlock …", "Seamless", "All-in-one", "Revolutionize".
- Everything with the same border radius, the same shadow and the same spacing.
- Stock photos of people pointing at laptops.
- Fake trust: invented logos, "Trusted by 10,000+", 5-star blocks with no source.

## 3. Tokens (write into CLAUDE.md, use as CSS custom properties)

```css
:root {
  --font-display: "…", serif;  --font-body: "…", sans-serif;
  --step--1: clamp(.83rem, .8rem + .15vw, .9rem);  --step-0: clamp(1rem, .95rem + .25vw, 1.125rem);
  --step-1: clamp(1.25rem, 1.1rem + .6vw, 1.5rem);  --step-3: clamp(2rem, 1.5rem + 2.5vw, 3.5rem);
  --space-1: .25rem; --space-2: .5rem; --space-3: 1rem; --space-4: 1.5rem; --space-5: 2.5rem; --space-6: 4rem; --space-7: 6rem;
  --bg: …; --fg: …; --muted: …; --accent: …; --accent-fg: …; --border: …;
  --radius-s: 6px; --radius-l: 16px;
  --ease-out: cubic-bezier(.2,.7,.2,1);
}
@media (prefers-color-scheme: dark) { :root { /* only if the PRD wants dark mode */ } }
```

- Type scale: use a ratio (1.2–1.333) via `clamp()` so it's fluid with no breakpoints. Body text ≥ 16 px, line length 60–75ch, line height 1.5 for body and 1.1 for display.
- Colour: one accent used sparingly, mostly for the CTA. Check contrast for every fg/bg pair (≥ 4.5:1).
- Fonts: at most 2 families, `font-display: swap`, self-hosted or Google Fonts with `preconnect`. Subset if possible.
- Spacing: only use the scale, never random px values.

## 4. Layout

- Mobile first. Design at 375 px, then widen.
- Use a grid on purpose (e.g. 12 columns, with content that breaks the grid once for emphasis).
- Use whitespace to show hierarchy; don't reach for borders.
- One primary CTA per screen. Secondary actions look secondary.
- Aim for one memorable composition moment per page, not ten.

## 5. Interface rules (every component)

- **States**: default, hover, focus-visible, active, disabled, loading, empty, error, success. Design all of them.
- **Focus**: a visible ring (`outline: 2px solid var(--accent); outline-offset: 2px`), never removed and never covered by sticky headers (`scroll-margin-top`).
- **Touch targets**: ≥ 44×44 px with spacing between them.
- **Forms**: a visible label (a placeholder isn't a label), the correct `type` / `inputmode` / `autocomplete`, errors next to the field, focus moved to the first error on submit, input kept after an error, submit not disabled before the form is complete, and the button shows progress.
- **Images**: `width`/`height` or `aspect-ratio` set, `alt` text, sized `srcset`, lazy below the fold.
- **Icons**: one icon set, and icon-only buttons get an `aria-label`.
- **Nested radii**: inner radius = outer radius − padding, so corners stay concentric.
- **Numbers, dates and money**: formatted with `Intl.*` for the user's locale.
- **Motion**: see the motion guides. Purposeful, short, and respecting reduced motion.

## 6. Copy

- Write the headline from the visitor's problem or desired outcome, in their words, and keep it specific: "Same-week boiler repair in Leeds" beats "Heating solutions you can trust".
- Subline: who it's for and how it works, in one sentence.
- CTA labels: verb + outcome ("Book a free call", "Get my quote"). Never "Submit" or "Learn more" alone.
- Errors say what happened and how to fix it.
- Proof must be real, specific and attributed. Missing facts become `[NEEDS: …]`.
- Cut every sentence that would be true of any competitor.

If installed, the `copywriting` skill is a deeper guide.

## 7. Self-check before showing the user

- [ ] Could this page belong to a competitor with the logo swapped? If yes, it's slop. Redo the signature detail and the headline.
- [ ] Every section maps to a PRD need.
- [ ] Contrast, focus and the 375 px layout all checked.
- [ ] No placeholder content is left unflagged.
