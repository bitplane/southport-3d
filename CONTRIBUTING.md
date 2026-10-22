# Contributing

Start with one building or a clearly bounded improvement. Open a PR against `master` with the observed problem, source links, measurement assumptions, changes and validation results. Agree on the project licence before contributing work intended for public reuse; see RIGHTS.md.

Place buildings under `regions/<town>/<area>/<asset>/` with an `asset.json`, construction scripts and research recipes. Use a stable dotted ID, metric coordinates and an explicit geographic anchor. The first manifest is an example; the build runner currently supports the memorial workflow and will need an adapter for other construction pipelines.

Compare multiple views for elevations, roof form and ornaments. Mark occluded or uncertain details as estimates. Link to photographs instead of adding them to Git. Keep your local reference cache outside the source checkout (or in ignored references/ folders). Do not include login sessions or browser profiles.

Stage intended source files and run `python tools/project.py check`. Geometry changes also need a complete build/export/validation and visual review of affected views. Attach review renders through an appropriate licensed review channel rather than committing build products. Explain changes to scale, placement and visibility. Keep PRs small enough for another contributor to review.

Include a reasoned LOD recipe with new buildings: what gets omitted, replaced by an envelope, parameterised or selectively decimated at each level. Add controls as features are built, and run the [baked LOD workflow](docs/LOD-PIPELINE.md). Review front/oblique views and identify any explicit coverage deferral.

Add publication.json for new buildings and use the common [viewer/catalog pipeline](docs/VIEWER.md). Classify all exported meshes and verify Detail, Walk and District in the browser. Adding a building must not require editing viewer code.
