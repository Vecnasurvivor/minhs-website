# Timelines, staggers and SVG

First check whether CSS or `el.animate()` can do it. One element with one tween doesn't need a library. Reach for **Anime.js v4** (~10 KB, framework-agnostic) when you need sequencing, staggers, SVG drawing/morphing, or animating plain JS values. Use GSAP instead only if the project already uses it.

```bash
npm i animejs
```

v4 is modular, so import only what you use. The old v3 `anime({...})` global is gone.

```js
import { animate, createTimeline, stagger, svg, utils } from 'animejs';
```

## Single tween

```js
animate('.card', {
  y: [24, 0], opacity: [0, 1],
  duration: 600, ease: 'out(3)',
  delay: stagger(60),               // 0, 60, 120 ms…
});
```

v4 renamed several things: `ease` (not `easing`), `onComplete`/`onUpdate` callbacks, and shorthand transforms `x`, `y`, `scale`, `rotate`.

## Timeline

```js
const tl = createTimeline({ defaults: { duration: 500, ease: 'out(3)' } });
tl.add('.hero h1', { y: [40, 0], opacity: [0, 1] })
  .add('.hero p',  { opacity: [0, 1] }, '-=300')      // overlap 300 ms
  .add('.hero .cta', { scale: [0.9, 1], opacity: [0, 1] }, '<');  // with previous
tl.pause(); tl.play(); tl.seek(0); tl.reverse();
```

Position strings: `'+=200'` (after a gap), `'-=200'` (overlap), `'<'` (same start as the previous one), or an absolute ms number.

## Stagger patterns

- From the centre: `stagger(40, { from: 'center' })`
- Grid ripple: `stagger(30, { grid: [cols, rows], from: index })`
- Spread a value: `rotate: stagger([-10, 10])` gives every item a value between −10 and 10.

## SVG

```js
// draw a line
animate(svg.createDrawable('.path'), { draw: ['0 0', '0 1'], duration: 1200, ease: 'inOut(2)' });
// morph between two paths (similar point counts morph best)
animate('#shape', { d: svg.morphTo('#target') });
// move along a path
const { translateX, translateY, rotate } = svg.createMotionPath('#track');
animate('.dot', { translateX, translateY, rotate, duration: 3000, loop: true, ease: 'linear' });
```

The same line-draw in plain CSS is `stroke-dasharray: 1; stroke-dashoffset: 1` with `pathLength="1"` on the path, then animate the offset to 0.

## Number counter

```js
const obj = { v: 0 };
animate(obj, { v: 12840, duration: 1500, ease: 'out(4)', modifier: utils.round(0),
  onUpdate: () => (el.textContent = obj.v.toLocaleString()) });
```

## React

Run animations in `useEffect` scoped to a ref, and clean up:

```jsx
useEffect(() => {
  const a = animate(ref.current.querySelectorAll('li'), { opacity: [0, 1], delay: stagger(50) });
  return () => a.revert();
}, []);
```

## Reduced motion

```js
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
animate('.x', still ? { opacity: [0, 1], duration: 200 } : { y: [40, 0], opacity: [0, 1] });
```

## Pitfalls

- Animating `left/top/width` → use `x/y/scale`.
- Starting a timeline before fonts/images load can make it jump. Start after `document.fonts.ready` or the image's `load` event.
- Don't loop forever on things people read. Loops are for ambient decoration only, and pause them offscreen.
