# Pen holder workflow

- V08: accepted 16-feather silhouette, 90 mm high, approximately 83.4 mm wide. Preserve shared coordinates of white and black parts.
- Build from repository root: `uv run --python 3.12 --with cadquery==2.8.0 --with trimesh==4.12.2 --with scipy python shuttlecock-pen-holder/src/build_pen_v08.py`.
- Lint: `uv run --with ruff ruff check shuttlecock-pen-holder/src/build_pen_v08.py`.
- Format: `uv run --with ruff ruff format shuttlecock-pen-holder/src/build_pen_v08.py`.
- Build checks CAD validity, STL watertightness, STEP roundtrip and color partitions. These do not establish physical strength.
- Commit CAD source, STEP/STL, validation reports and labeled renders; exclude local 3MF/G-code and device credentials.
- Record slicing, job submission and physical acceptance separately.

- Render showcase: `uv run --python 3.12 --with vtk==9.6.2 --with Pillow==12.3.0 python shuttlecock-pen-holder/src/render_showcase.py`. The figure uses actual V08 meshes; do not label it as a photograph.
