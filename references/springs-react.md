# Springs, gestures and layout animation in React

**Default: Motion** (formerly Framer Motion, package `motion`). It covers entrances, exit animations, layout/shared-element transitions, drag, gestures and springs with one API.

**Use react-spring** only if the project already has it, or for heavy imperative physics on many values (data viz, canvas) where its hook model fits better.

```bash
npm i motion
```

```jsx
import { motion, AnimatePresence, useScroll, useTransform, useReducedMotion } from 'motion/react';
```

## Springs: think in feel, not numbers

Prefer `visualDuration` + `bounce` over stiffness/damping. They're easier to reason about.

| Feel | Transition |
|---|---|
| Snappy UI (buttons, toggles) | `{ type: 'spring', visualDuration: 0.25, bounce: 0 }` |
| Friendly (cards, modals) | `{ type: 'spring', visualDuration: 0.4, bounce: 0.2 }` |
| Playful (stickers, mascots) | `{ type: 'spring', visualDuration: 0.6, bounce: 0.45 }` |

Bounce above ~0.3 on everyday UI feels toy-like. Save it for delight moments.

## Core patterns

```jsx
// enter
<motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} />

// hover / press
<motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} />

// exit (needs AnimatePresence and a key)
<AnimatePresence>{open && <motion.div key="m" exit={{ opacity: 0, scale: 0.95 }} />}</AnimatePresence>

// layout: size/position changes animate automatically
<motion.div layout />

// shared element: same layoutId in two places morphs between them
<motion.img layoutId={`photo-${id}`} />

// drag with constraints and fling
<motion.div drag="x" dragConstraints={{ left: -200, right: 0 }} dragElastic={0.1} />

// in view
<motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true, margin: '-10%' }} />
```

## Stagger children

```jsx
const list = { show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0 } };
<motion.ul variants={list} initial="hidden" animate="show">
  {items.map((i) => <motion.li key={i.id} variants={item} />)}
</motion.ul>
```

## Scroll-linked

```jsx
const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
const y = useTransform(scrollYProgress, [0, 1], ['-10%', '10%']);
<motion.img style={{ y }} />
```

If it doesn't need React state, the CSS version in `scroll.md` is cheaper.

## Reduced motion

Wrap the app in `<MotionConfig reducedMotion="user">`: transforms are skipped, opacity stays. For custom cases, use `const reduce = useReducedMotion()`.

## react-spring quick reference (if already used)

```jsx
import { useSpring, useTrail, animated } from '@react-spring/web';
const s = useSpring({ from: { opacity: 0, y: 20 }, to: { opacity: 1, y: 0 }, config: { tension: 280, friction: 24 } });
<animated.div style={s} />
```

`useTrail` gives staggered lists, `useTransition` handles mount/unmount, `@use-gesture/react` handles drag.

## Pitfalls

- Bundle size: in Next/Vite, `LazyMotion` + `m` components cut Motion to a few KB when you only need basics.
- Don't animate on every render by changing `initial`. Keep keys stable.
- `layout` on huge lists is expensive. Use it on the moving pieces only.
- Server components: Motion components need `'use client'`.
