# V13 — soft palm/root transition

This revision addresses the front palm-tooth junction directly. The previous silhouette-only edit did not repair that surface. V12 is preserved.

## Method and scope

The source is V12 STL. Blender re-tessellates it at 0.18 mm, projects the vertices back to the source, then locally fairs the Y21–46 mm front-palm/root band with smooth weights. Tooth contacts, palm rear and flat base vertices have zero fairing weight. Validation separately measures the remeshing approximation; it does not claim exact CAD equality.

The retained candidate uses 1,200 weighted smoothing passes on the mesh, producing about 1.019 mm maximum local displacement and a 0.885% volume reduction. This modifies actual surface coordinates, not only display normals. A periodic-palm CAD trial with 3 mm root fillets failed kernel construction and was discarded without exporting an invalid solid.

## Delivered format

- `massage-comb-v13.stl`: the actual revised, checked mesh; about 90.53 × 49.22 × 15.30 mm.
- `mesh.bin`: the same geometry for the browser, with vertex normals for shading.
- `build.py`: reproducible Blender geometry edit; `surface-edit.blend` is an ignored local editable intermediate.
- `comparison.png`: actual old/new renders, identical camera, crop, light, scale and material; not a photo.
- `validation.json`, `surface-fairing.json`, `visual-review.json`: numerical evidence and limits.

No V13 STEP has been generated. The earlier STEP must not be presented as this mesh. Native Blender MCP was not available; the installed skill's mesh/refinement and fixed-view review principles were applied through local Blender background Python.

## Build and checks

From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/v13/build.py
uv run scalp-massage-comb/v13/validate.py
uv run --with ruff ruff format --check scalp-massage-comb/v13/*.py
uv run --with ruff ruff check scalp-massage-comb/v13/*.py
node --check scalp-massage-comb/v13/viewer.js
npx --yes prettier --check scalp-massage-comb/v13/viewer.html scalp-massage-comb/v13/viewer.js
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/v13/render.py
uv run --with opencv-python-headless --with numpy python "$HOME/.codex/skills/reference-to-3d/scripts/silhouette_validator.py" --reference scalp-massage-comb/v13/v12-front-mask.png --render scalp-massage-comb/v13/v13-front-mask.png --out scalp-massage-comb/v13/front-mask-validation.json
uv run --with opencv-python-headless --with numpy python "$HOME/.codex/skills/reference-to-3d/scripts/silhouette_validator.py" --reference scalp-massage-comb/v13/v12-side-mask.png --render scalp-massage-comb/v13/v13-side-mask.png --out scalp-massage-comb/v13/side-mask-validation.json
uv run scalp-massage-comb/v13/make_review.py
```

The inline `uv` environment carries only validation/review dependencies; no project-wide production package was added. No standalone frontend build or type checker exists.

## Validation and limits

Passed: closed/consistent/connected positive-volume mesh; five teeth at Y18 with gaps >6.4 mm; overall bounds within 3% of V12; deterministic contact/rear-grip two-way distance samples <0.02 mm; fixed-view renders, Python lint/format, JavaScript syntax, browser desktop/narrow layout and keyboard/view controls.

The full silhouette remains close (front IoU 99.105%, side IoU 98.878%) while the internal front-root surface changes visibly. Overlap scores preserve proportions; they do not score naturalness. Numerical and render review do not establish global G2 curvature continuity, physical comfort, snag resistance, fatigue or print finish. The user accepted the improved appearance. A new slow PLA slicing pass was subsequently completed in the GUI; printing is now paused by the user, with no task submitted. See [the current print record](../docs/PRINT-PREPARATION-V13.md). The numerical JSON files retain the state at their original geometry-check stage.


## Publication scope and product render

The repository includes this V13 source/output folder and the V12 STL, STEP and validation baseline required by the commands above. Earlier work-in-progress versions remain local; the project history summarizes the design decisions. The V12 STEP is historical and does not match V13.

The desktop product image is rendered directly from the unchanged V13 STL with black PLA shading in local Blender background mode:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/assets/render_showcase.py
uv run --with ruff ruff format --check scalp-massage-comb/assets/render_showcase.py
uv run --with ruff ruff check scalp-massage-comb/assets/render_showcase.py
```

[Product image](../assets/showcase-v13.png) · [Render provenance](../assets/showcase-v13.json) · [Render workflow and review](../assets/BUILD_NOTES.md)
