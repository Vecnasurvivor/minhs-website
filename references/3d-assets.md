# 3D assets: Blender / Substance → web

Target format is always **glTF binary (`.glb`)**. Add `.usdz` too if iOS Quick Look AR is needed.

## Budgets

| | Hero model | Background prop | Mobile total per page |
|---|---|---|---|
| Triangles | ≤ 100k | ≤ 10k | ≤ 200k |
| Texture size | 2048² | 512–1024² | — |
| File after compression | ≤ 3 MB | ≤ 300 KB | ≤ 5 MB |

## Blender

1. **Clean**: apply transforms (Ctrl+A → All Transforms), delete hidden/unused objects, merge by distance, recalc normals outward.
2. **Reduce**: Decimate modifier (collapse) on dense meshes. Bake high-poly detail into a normal map on a low-poly mesh.
3. **Materials**: Principled BSDF only. Image textures plugged in directly. Procedural nodes don't export, so bake them.
4. **Bake lighting** (Cycles → Bake → Combined/Diffuse) into a texture for static scenes. Then you need almost no realtime lights.
5. **Animation**: one action per clip, named clearly. Check "Group by NLA track" so each clip exports separately. Shape keys export as morph targets.
6. **Export** → glTF 2.0: Format *glTF Binary*, +Y up, Apply Modifiers, include only selected/visible, and leave compression off here (do it in the next step).

Scripted export (batch or CI):

```bash
blender -b scene.blend --python-expr "import bpy; bpy.ops.export_scene.gltf(filepath='out/model.glb', export_format='GLB', export_apply=True)"
```

## Substance 3D Painter

- Use the **glTF PBR Metal Roughness** export template. It outputs BaseColor, Normal (OpenGL), and **ORM** packed (R = occlusion, G = roughness, B = metallic), which is exactly what glTF expects.
- Texture set resolution: export at 2K, and downscale to 1K for mobile variants.
- One texture set per material. Fewer materials means fewer draw calls, so combine UDIMs/sets where you can.
- Normal maps must be OpenGL (+Y). DirectX normals look inverted.

## Optimize (always the last step)

```bash
npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress webp --texture-size 2048
# GPU-compressed textures (best for big scenes; needs KTX-Software installed):
npx @gltf-transform/cli optimize in.glb out.glb --compress draco --texture-compress ktx2
npx @gltf-transform/cli inspect out.glb      # check triangles, texture sizes, draw calls
```

Loaders must match the compression: three.js `DRACOLoader` / `MeshoptDecoder` / `KTX2Loader`. drei's `useGLTF` and `<model-viewer>` handle these for you.

## Verify

- Drop it into https://gltf-viewer.donmccurdy.com or https://modelviewer.dev/editor and check materials, scale (1 unit = 1 m), and animations.
- Run `scripts/motion_audit.py` to flag oversized `.glb` files.

## Common breakages

- Black/missing textures → the texture wasn't packed or was procedural. Bake it and re-export.
- Model is huge or tiny → transforms weren't applied, or the scene is in cm units.
- Looks flat → no environment map. Add an HDRI (`Environment` in drei, `environment-image` in model-viewer).
- Transparent parts render wrong → set alpha mode to Blend/Clip in Blender, and split transparent meshes.
