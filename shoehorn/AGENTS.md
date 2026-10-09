# Shoehorn workflow

- Preserve the accepted V04 shape: approximately 178 mm long, 41.9 mm wide, straight longitudinal centre line, transverse heel concavity, waisted handle and teardrop hole.
- Run commands from the repository root. Python dependencies use temporary uv environments; there is no project lockfile.
- Build: `uv run --python 3.12 --with cadquery==2.8.0 python shoehorn/v04/build.py`.
- Check exported meshes: `uv run --python 3.12 --with trimesh --with scipy --with networkx python shoehorn/v04/check_mesh.py`.
- Build preview data: `uv run --python 3.12 --with trimesh --with scipy python shoehorn/v04/build_preview.py`.
- Preview: `uv run --python 3.12 python -m http.server 8784 --bind 127.0.0.1 --directory shoehorn/v04`, then open `/viewer.html`.
- Lint: `uv run --with ruff ruff check shoehorn/v04`; `node --check shoehorn/v04/viewer.js`.
- Format: `uv run --with ruff ruff format shoehorn/v04`; `pnpm dlx prettier --write shoehorn/v04/viewer.html shoehorn/v04/viewer.js`.
- Render: `/Applications/Blender.app/Contents/MacOS/Blender -b -t 6 --python-exit-code 1 --python shoehorn/v04/render.py`; `uv run --python 3.12 --with pillow python shoehorn/v04/board.py`.
- Check CAD validity, a single solid, STEP round-trip and closed positive-volume STL after geometry edits. Inspect the actual preview on desktop and narrow screens after UI edits.
- CAD, images, preview mesh and validation records are intentionally tracked. Omit Blender backups, local logs and machine-specific print jobs. Label renders separately from physical results.
