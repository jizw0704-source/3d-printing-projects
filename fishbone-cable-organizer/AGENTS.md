# Project workflow

- Python 3.12, uv-managed; preserve V06 geometry unless a design change is requested.
- Setup: `uv sync --locked`
- Format: `uv run ruff format src/design.py`
- Lint: `uv run ruff check src/design.py`
- Build and geometry checks: `uv run python src/design.py`
- Geometry assertions run during build; no separate test suite or type checker is configured.
- STEP/STL and README image assets are intentional versioned deliverables.
- Keep local 3MF, G-code, device identifiers and credentials out of Git.
- Clearly distinguish CAD renders, AI illustrations, slicer estimates and physical test results.
