# Project instructions

- Stable design baseline: v14/. Only V14 is retained in the current tree. Historical versions remain recoverable from Git history. Future geometry changes should preserve this baseline until explicitly accepted.
- Read the version README and validation.json before edits. Keep the hello/honeycomb style and distinguish geometry validation from physical testing.
- CAD deliverables (STEP/STL), preview PNG/HTML, and validation JSON are intentionally tracked. Never track credentials, environment files, printer access codes, or caches.
- From v14/: build and geometry checks: `uv run --with cadquery==2.8.0 --with matplotlib==3.11.2 --with trimesh --with shapely==2.1.2 python design.py`.
- Format: `uv run --with ruff==0.15.6 ruff format design.py`. Check formatting: `uv run --with ruff==0.15.6 ruff format --check design.py`. Lint: `uv run --with ruff==0.15.6 ruff check design.py`.
- Preview: `uv run --with trimesh python -m http.server 8776 --bind 127.0.0.1`; open http://127.0.0.1:8776/viewer.html in the right-hand Codex panel. No independent type checker is configured.
- Do not send print, heat, or motion commands without explicit user authorization. Never describe the design as physically validated without actual test evidence.
