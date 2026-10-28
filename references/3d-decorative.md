# Decorative depth (no real 3D scene)

Lightest first:

| Want | Use | Weight |
|---|---|---|
| Card tilts toward the cursor, glare | Plain CSS + ~15 lines of JS (below), or `vanilla-tilt` | 0–3 KB |
| Flip cards, layered parallax, cube/carousel | CSS 3D transforms (`perspective`, `preserve-3d`) | 0 KB |
| Animated gradient/blob background | CSS (`@property` animated gradients) or a small canvas/shader | 0–5 KB |
| Ready-made animated backgrounds (waves, birds, fog, net, globe) | **Vanta.js** (needs three.js, or p5 for some effects) | ~150 KB with three |
| Small flat-shaded 3D illustration you can spin (logo, icon, mascot) | **Zdog** | ~10 KB |

## Tilt without a library

```js
for (const card of document.querySelectorAll('[data-tilt]')) {
  card.addEventListener('pointermove', (e) => {
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
    card.style.transform = `perspective(800px) rotateX(${-y * 10}deg) rotateY(${x * 10}deg)`;
    card.style.setProperty('--gx', `${(x + 0.5) * 100}%`); card.style.setProperty('--gy', `${(y + 0.5) * 100}%`);
  });
  card.addEventListener('pointerleave', () => (card.style.transform = ''));
}
```

```css
[data-tilt] { transition: transform .2s ease-out; will-change: transform; }
[data-tilt]::after { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none;
  background: radial-gradient(circle at var(--gx) var(--gy), #fff3, transparent 50%); }
@media (hover: none), (prefers-reduced-motion: reduce) { [data-tilt] { transform: none !important; } }
```

Keep the max angle at 8–12°. More than that looks cheap.

vanilla-tilt equivalent: `VanillaTilt.init(els, { max: 10, glare: true, 'max-glare': 0.2, gyroscope: false })`.

## Vanta

```js
import * as THREE from 'three';
import NET from 'vanta/dist/vanta.net.min';
const fx = NET({ el: '#hero', THREE, color: 0x6c5ce7, backgroundColor: 0x0b0b12, points: 8, maxDistance: 20 });
// on unmount / route change:
fx.destroy();
```

Load it only on desktop and only when visible. On mobile and reduced-motion, show a static gradient or image instead. Always call `destroy()`, otherwise it leaks the WebGL context.

## Zdog

```js
import Zdog from 'zdog';
const illo = new Zdog.Illustration({ element: '.zdog', dragRotate: true, zoom: 4 });
new Zdog.Box({ addTo: illo, width: 20, height: 20, depth: 20, stroke: false,
  color: '#6c5ce7', leftFace: '#4b3fc9', rightFace: '#8f84f0', topFace: '#b3abff' });
(function loop() { illo.rotate.y += 0.01; illo.updateRenderGraph(); requestAnimationFrame(loop); })();
```

Shapes: `Ellipse, Rect, RoundedRect, Polygon, Shape (paths), Box, Cylinder, Cone, Hemisphere`. Group them with `Anchor`/`Group`. Use `<svg>` as the element for crisp scaling, or `<canvas>` for many shapes.

Stop the loop when offscreen or under reduced motion: render one frame and stop.

## Pitfalls

- Several WebGL backgrounds on one page will crash mobile Safari. Use one at most.
- `will-change` on dozens of elements wastes memory. Only set it on what actually moves.
- Tilt on touch devices feels broken, so disable it with `(hover: none)`.
