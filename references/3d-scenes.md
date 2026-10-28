# Real 3D scenes

| Situation | Use |
|---|---|
| Show one product model: rotate, zoom, AR on phone | **`<model-viewer>`**: one tag, AR built in |
| Designer builds the scene visually and wants to own it | **Spline** |
| VR/AR, 360° photo/video tour, headset support, HTML-first | **A-Frame** (WebXR) |
| Custom interactive 3D in a React app | **react-three-fiber** + drei |
| Custom 3D without React | three.js directly |

## model-viewer (try this first for products)

```html
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4/dist/model-viewer.min.js"></script>
<model-viewer src="/m/chair.glb" ios-src="/m/chair.usdz" poster="/m/chair.webp" alt="Oak chair"
  camera-controls auto-rotate ar ar-modes="webxr scene-viewer quick-look" loading="lazy" reveal="interaction"></model-viewer>
```

Pin an exact version in production. `poster` + `reveal="interaction"` means the 3D only loads when someone engages with it.

## Spline

```bash
npm i @splinetool/react-spline @splinetool/runtime
```

```jsx
import Spline from '@splinetool/react-spline';
<Spline scene="https://prod.spline.design/<id>/scene.splinecode"
  onLoad={(app) => { const obj = app.findObjectByName('Cube'); obj.rotation.y = 1; }}
  onSplineMouseDown={(e) => console.log(e.target.name)} />
```

Trigger designer-made interactions with `app.emitEvent('mouseHover', 'Button')`. Set variables with `app.setVariable('count', 3)`.

Export from Spline with "hide background" if it sits on your page, and turn off unused events.

Spline scenes are heavy (1–5 MB plus the runtime). Lazy-load them (`React.lazy` / dynamic import), show a poster image, and on mobile consider the poster alone.

## A-Frame (WebXR)

```html
<script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
<a-scene renderer="antialias: true; colorManagement: true" xr-mode-ui="enabled: true">
  <a-assets><a-asset-item id="room" src="/m/room.glb"></a-asset-item></a-assets>
  <a-entity gltf-model="#room"></a-entity>
  <a-sky color="#dfe8f0"></a-sky>
  <a-entity camera look-controls wasd-controls position="0 1.6 3">
    <a-entity cursor="rayOrigin: mouse" raycaster="objects: .clickable"></a-entity>
  </a-entity>
  <a-entity laser-controls="hand: right" raycaster="objects: .clickable"></a-entity>
</a-scene>
```

- 360 photo: `<a-sky src="pano.jpg">`. 360 video: `<a-videosphere>` (muted autoplay, start it on a user gesture).
- Custom behaviour: `AFRAME.registerComponent('name', { schema, init(){}, tick(t, dt){} })`. Keep `tick` cheap.
- AR on phone: `<a-scene xr-mode-ui="XRMode: ar">`. Hit-testing places objects on real surfaces.
- WebXR needs HTTPS. Test on a real headset/phone; desktop only shows the fallback.

## react-three-fiber

```bash
npm i three @react-three/fiber @react-three/drei
```

```jsx
<Canvas dpr={[1, 2]} camera={{ position: [0, 1, 4], fov: 45 }} frameloop="demand">
  <Suspense fallback={null}>
    <Environment preset="city" />
    <Model url="/m/chair.glb" />   {/* useGLTF inside */}
    <OrbitControls enablePan={false} />
  </Suspense>
</Canvas>
```

`frameloop="demand"` only renders when something changes, which saves battery for static scenes. Use `useGLTF.preload(url)` for models you know you'll need.

## Performance checklist (any engine)

- Models come out of the `3d-assets.md` pipeline: Draco/Meshopt compression, KTX2/WebP textures.
- `dpr` capped at 2, few lights (bake lighting instead), shadows off on mobile.
- Lazy-load below the fold, with a poster image always present, so there's never a blank box.
- Reduced motion: no auto-rotate, no camera fly-throughs.
- Accessibility: `alt`/`aria-label` describing the object, plus keyboard-reachable controls or a text alternative.
