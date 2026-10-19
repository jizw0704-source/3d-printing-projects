# Publication checks — 2026-10-19

- V13 STL SHA-256 unchanged: `738ba2182f7e2160b3a154ae202eba4e92cfba4032a6b856794e526116cbd013`. No product geometry was rebuilt for publication.
- Ruff format/check passed for the V13 Python scripts and the new product render script. JavaScript syntax and Prettier checks passed for the V13 viewer.
- New render executed in local Blender 5.2.2 / Cycles; draft and final images visually inspected. Five teeth, their gaps and the grip are visible without cropping or context overlap. Source hash recorded with the image.
- Markdown relative links and staged file types checked; no printer jobs, credentials or device records included. JSON documents parse successfully.
- Whitespace check passed for documentation and source. The historical, unchanged Open CASCADE STEP contains exporter whitespace and is excluded from the prose/code whitespace check; it was not reformatted.
- Preview route `/v13/viewer.html` loaded the actual mesh and the updated paused-print status. Desktop/default and 390 × 844 narrow views inspected; text wraps and controls remain visible without horizontal overflow. Temporary viewport override reset.
- UI scope: one status paragraph updated, preserving the existing Pheno v1.4 neutral prototype layout, system-font fallback and controls. No style, interaction or loading/error behavior changed. Keyboard, forced-colors, reduced-motion, reduced-transparency and real-touch behavior were not re-tested in this documentation-only update; no new claim of full UI conformance is made. MiSans is not bundled or claimed delivered.
- No standalone frontend build, type checker or test suite exists for this static preview. No new dependency was added to the project. Rendering introduces no external asset downloads.
- Physical comfort, print finish, support removal, snag resistance and durability remain untested. Printing is paused by the user and has not been submitted.
