# Scroll effects

## Choose

| Effect | Use |
|---|---|
| Fade/slide in once when visible | CSS `animation-timeline: view()`, or IntersectionObserver + a class |
| Effect scrubbed to scroll position (parallax, progress bar, image zoom) | CSS scroll-driven animations |
| Pinned section with steps that play while it's pinned | `position: sticky` + `view-timeline`, or GSAP ScrollTrigger if it's already in the project |
| Legacy project already using AOS | Keep AOS, don't add a second system |

Native scroll-driven animations run off the main thread. They work in Chromium and Safari 26+. Firefox has them behind a flag, so use `@supports` and let elements simply be visible there.

## Reveal on enter (pure CSS)

```css
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .reveal {
      animation: reveal linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 60%;
    }
  }
}
@keyframes reveal {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: none; }
}
```

Elements are visible by default. The animation only ever adds motion, so nothing stays hidden if CSS support or JS fails.

## Reveal on enter (IntersectionObserver, any browser)

```js
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) {
    e.target.classList.add('is-in');
    io.unobserve(e.target);           // play once
  }
}, { rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el));
```

```css
[data-reveal] { transition: opacity .6s ease, transform .6s cubic-bezier(.2,.7,.2,1); }
.js [data-reveal]:not(.is-in) { opacity: 0; transform: translateY(24px); }
@media (prefers-reduced-motion: reduce) { [data-reveal] { transition: opacity .3s; transform: none !important; } }
```

Add `class="js"` to `<html>` from a tiny inline script, so no-JS visitors see the content.

Stagger siblings with `transition-delay: calc(var(--i) * 60ms)` and set `style="--i:0"`, `--i:1`, and so on.

## Scrubbed effects

```css
/* reading progress bar */
.progress { position: fixed; inset: 0 0 auto; height: 3px; transform-origin: left;
  animation: grow linear both; animation-timeline: scroll(root); }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

/* parallax image inside its card */
.card img { animation: drift linear both; animation-timeline: view(); }
@keyframes drift { from { transform: translateY(-8%) scale(1.15); } to { transform: translateY(8%) scale(1.15); } }
```

`animation-range` names: `cover` (whole time it's on screen), `contain`, `entry`, `exit`. Mix with percentages: `entry 20% cover 50%`.

## Sticky storytelling

Give a tall wrapper (`height: 300vh`) a `view-timeline-name: --story`, put a `position: sticky; top: 0` child inside it, and animate the child's pieces with `animation-timeline: --story` and staggered `animation-range`. Scroll position then drives the steps without any JS.

## AOS (only if already installed)

`AOS.init({ once: true, duration: 600, offset: 80, disable: () => matchMedia('(prefers-reduced-motion: reduce)').matches })` with `data-aos="fade-up"` on elements. Call `AOS.refresh()` after content loads asynchronously.

## Pitfalls

- Don't hide above-the-fold content waiting for a reveal: it hurts LCP and looks broken.
- Don't hijack scroll speed or snap the whole page. Users hate it, and it breaks trackpads and keyboards.
- Never listen to `scroll` and set styles every event. Use scroll timelines, or IO + rAF.
- Big parallax on mobile: tone it down (`@media (max-width: 640px)`) or drop it.
