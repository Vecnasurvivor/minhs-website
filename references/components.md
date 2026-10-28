# Ready-made animated components

Both libraries are copy-into-your-project (shadcn-style), not runtime dependencies. You own the code after install, so edit it freely.

| Library | Good for | Needs |
|---|---|---|
| **Magic UI** (magicui.design) | Landing-page polish: marquee, bento grid, animated beam, number ticker, globe, shimmer/border-beam buttons, dock | React + Tailwind + `motion` |
| **React Bits** (reactbits.dev) | Expressive text and background effects: split/blur/scramble text, aurora, particles, magnet, click spark, gooey nav | React, with JS/TS × CSS/Tailwind variants. Some effects use three/ogl/gsap |

## Install

Open the component's page and copy its exact install command. Both publish shadcn registry URLs:

```bash
npx shadcn@latest add "<registry url from the component page>"
```

If the project has no `components.json`, run `npx shadcn@latest init` first. With React Bits you can also copy the source manually; pick the variant that matches the project (TS + Tailwind usually).

## Choosing well

- One hero effect per page, plus at most one or two supporting effects. Stacking aurora + particles + scramble text reads as a template.
- Match the brand: geometric and calm → Magic UI marquee, ticker, beams. Playful/creative → React Bits text effects.
- Check what the effect pulls in. A background built on three.js adds ~150 KB. Lazy-load it, or pick a CSS-only one.
- Text effects must stay real text: keep it selectable and readable by screen readers (`aria-label` on the wrapper and `aria-hidden` on per-letter spans if the component splits text).

## After install, always

1. Swap hardcoded colours for the project's tokens/CSS vars.
2. Add a reduced-motion branch (most components don't have one): render the static state.
3. Remove props and code paths you don't use, since you own the file.
4. Test on a phone. Particle counts and blur radii usually need halving.
5. Run `scripts/motion_audit.py`.
