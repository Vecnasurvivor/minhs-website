# Designer vector animation: Lottie and Rive

| Situation | Use |
|---|---|
| Plays through (loader, success tick, hero loop), made in After Effects | **dotLottie** (`.lottie`, compressed) |
| Has to react: hover, click, follow cursor, change state, game-like | **Rive** (`.riv`, state machines) |
| Simple icon or line animation | Neither. Use an animated SVG or CSS (`timelines.md`) |

## Lottie (use dotLottie, not raw lottie-web)

```bash
npm i @lottiefiles/dotlottie-react      # React
npm i @lottiefiles/dotlottie-web        # vanilla
```

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';
<DotLottieReact src="/anim/success.lottie" autoplay loop={false}
  dotLottieRefCallback={(p) => (player.current = p)} />
// player.current.play() / pause() / setFrame(n) / setSpeed(1.5)
```

Vanilla: `new DotLottie({ canvas, src, autoplay: true, loop: true })`.

**Shrink files**: convert `.json` to `.lottie` (zip + dedupe, usually 50–80% smaller). Ask the designer to avoid raster images, expressions, effects and masks, since those are slow or unsupported. Pre-compose and trim unused layers.

**Scroll-scrubbed Lottie**: set `autoplay={false}` and call `setFrame(progress * totalFrames)` from IntersectionObserver or Motion's `useScroll`.

**Hover play**: `onMouseEnter={() => p.play()}` and `onMouseLeave={() => p.stop()}`.

## Rive

```bash
npm i @rive-app/react-canvas            # or @rive-app/canvas for vanilla
```

```jsx
import { useRive, useStateMachineInput } from '@rive-app/react-canvas';
const { rive, RiveComponent } = useRive({ src: '/anim/button.riv', stateMachines: 'Main', autoplay: true });
const hover = useStateMachineInput(rive, 'Main', 'isHover');   // boolean input
const press = useStateMachineInput(rive, 'Main', 'press');     // trigger input
<RiveComponent onMouseEnter={() => hover && (hover.value = true)}
               onMouseLeave={() => hover && (hover.value = false)}
               onClick={() => press?.fire()} />
```

Agree on names with the designer before they build: **state machine name** and **input names/types** (boolean, number, trigger). Those names are the API contract.

Newer Rive files may use **data binding** (view models) instead of inputs. Check the file's panel and use the matching runtime API for setting view-model properties.

Listen to events the designer fires: `rive.on(EventType.RiveEvent, (e) => …)`.

Size the canvas with its container (`style={{ width, height }}`). The runtime handles device pixel ratio.

## Both

- Lazy-load: mount the player only when near the viewport. Show the first frame as a static SVG/PNG placeholder.
- Reduced motion: show a static frame (`autoplay={false}` + `setFrame(last)`), or keep only essential state changes.
- Pause offscreen loops (IO → `pause()`), because they burn battery.
- Budget: aim for under 150 KB per file. Over ~500 KB means talk to the designer.
