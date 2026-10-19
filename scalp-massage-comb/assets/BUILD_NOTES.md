# Product render workflow

- Purpose: show the accepted V13 as a black PLA object on a light oak desktop; no claim of a completed print or actual finish.
- Source of truth: `../v13/massage-comb-v13.stl`; no geometry modifiers, no smoothing displacement, no added product parts. Only unit conversion, centering and shading are applied.
- Pipeline: the Blender skill harmonizer sets the unchanged-mesh constraint; pro-workflow guides camera/material/light order; materials, lighting, camera and rendering skills guide local Cycles execution. No Blender MCP backend is advertised in this session; local Blender background Python is used explicitly.
- Scope: one mesh source, one view, no reference reconstruction or texture atlas. Multiview registration and atlas reports are not applicable. The source hash is recorded in `showcase-v13.json`; previous comparison/validation evidence remains in `../v13/`.
- Render: neutral black dielectric PLA shading, illustrative fine layer bump only, soft area lights, 70 mm perspective camera, AgX, 128 samples and denoising. Procedural context objects use no external assets.
- Checks: draft image inspected before final rendering; all five teeth and grip visible, no product crop, no context object overlap. Final image inspected separately. Physical comfort, finish and support scars remain unverified.

```sh
COMB_RENDER_DRAFT=1 /Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/assets/render_showcase.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/assets/render_showcase.py
```
