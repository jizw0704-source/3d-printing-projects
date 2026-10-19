# Massage comb workflow

- V13 is a visually accepted surface-refinement prototype, GUI sliced but not submitted. Printing is paused by the user; a new explicit print request is required to resume. Preserve V12 as comparison. V10 was rejected; never reuse its print job.
- Latest user request explicitly authorizes changing the FRONT palm/tooth-root transition. Earlier V12 restrictions that locked those surfaces and demanded zero added CAD volume do not apply to this surface repair. Retain five teeth, 18 mm pitch, about 20 mm nominal length and the established bend; do not add outer ledges or ribs.
- Build actual mesh: `/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/v13/build.py` (input V12 STL; editable source saved to ignored surface-edit.blend).
- Validate/export preview: `uv run scalp-massage-comb/v13/validate.py` (inline Python dependencies).
- Format: `uv run --with ruff ruff format --check scalp-massage-comb/v13/*.py`.
- Lint: `uv run --with ruff ruff check scalp-massage-comb/v13/*.py`.
- JavaScript: `node --check scalp-massage-comb/v13/viewer.js`.
- Web format: `npx --yes prettier --check scalp-massage-comb/v13/viewer.html scalp-massage-comb/v13/viewer.js`.
- Render: `/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/v13/render.py`.
- Compose: `uv run scalp-massage-comb/v13/make_review.py` after the silhouette commands in v13/README.md.
- Preview: `uv run --python 3.12 python -m http.server 8858 --bind 127.0.0.1 --directory scalp-massage-comb`; open `/v13/viewer.html`.
- Require watertight, consistent, positive-volume, connected STL; five separate teeth at Y18, retained gaps and sampled bidirectional source distances in contact/rear grip regions. Distances are samples, not an exhaustive error bound.
- V13 is a mesh refinement, with no matching STEP. Never label the V12 STEP as V13. Do not claim analytical curvature continuity or physical comfort from shading, sampled geometry or silhouette overlap.
- Compare actual meshes with locked cameras, model scale, materials and lighting. Blender MCP is not available here; use and disclose local background execution without claiming native MCP integration.
- No standalone frontend build or type checker. CAD/mesh/showcase assets are intentional outputs; omit printer jobs, Blender intermediates and credentials. Do not push or submit a print unless requested.

- Current project status and generic slow settings: `docs/PRINT-PREPARATION-V13.md`. Geometry-validation JSON files are original check snapshots, not live printer status.
- Public scope: V13 plus the V12 STL/STEP/validation baseline; earlier working revisions remain local. Never label the V12 STEP as current.
- Product rendering: `/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python scalp-massage-comb/assets/render_showcase.py`; format/lint the same script with `uv run --with ruff ruff format --check` and `uv run --with ruff ruff check`.
