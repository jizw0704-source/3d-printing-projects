# Repository workflow

- Add future 3D printing projects as separate directories and link them in the root README.
- Follow each project AGENTS.md and README for build/lint commands.
- Preserve accepted dimensions and geometry unless a change is requested.
- CAD models and image deliverables are intentionally tracked; omit local printer jobs and credentials.
- Separate rendered images, AI illustrations, real photos and user-reported results.
- Documentation-only migration: validate relative links and unchanged model hashes; no need to regenerate geometry.

- Every published project README must include `## 设计图 / Design` followed by `## 实际效果图 / In context`, each with an image and an explicit render/AI/photo caption. Mirror this pair in the root README. Use the current accepted model; label historical imagery.
- Gallery rendering (unchanged geometry): `/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python-exit-code 1 --python scripts/render_gallery.py`; then `uv run scripts/compose_design_gallery.py`. Format/lint: `uv run --with ruff ruff format --check scripts`; `uv run --with ruff ruff check scripts`.
