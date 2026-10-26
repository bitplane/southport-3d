# Agent instructions

Read the target asset.json and its research records before changing a building. Read README.md for initial project orientation, not on every task. Use the model-southport skill for research/modelling work. CLAUDE.md points to these same instructions. Follow the task-specific references below; do not preload every asset document, historical plan or review brief.

Use metres and retain each asset's documented coordinate origin and orientation. Keep construction source under regions/<town>/<area>/<asset>/; move reusable primitives into lib/southport3d only when their interface is useful independently of one building. The memorial currently uses a compatibility shim for geometry imports.

Use tools/project.py for ordinary builds. It copies inputs into build/ so report-writing scripts cannot overwrite source recipes. Build/export/render operations write the same Blender file: the runner locks each asset against competing writers. Direct scripts bypass these locks; run them sequentially for a given asset. Blender commands must use --python-exit-code 1 so script failures propagate.

Run at most one Blender process **per agent**, normally with `--threads 4`. Different agents may build/render/bake different assets concurrently; there is no global single-Blender slot. Keep per-asset writer locks and the catalog publication lock. A review checkpoint for one asset does not stop independent work by other agents. See [concurrency details](docs/MODELLING-WORKFLOW.md#build-and-inspect).

Do not commit downloaded reference images, page captures, browser profiles, credentials, generated textures, Blender files or GLBs. Keep source links, attribution, dates and uncertainty in the asset's research records. Numeric relief source surfaces are intentional source assets, not licence-free substitutes for the works they depict; see RIGHTS.md.

Run python tools/project.py check after staging intended files. For geometry changes, run a full asset build and inspect affected renders. Preserve the distinction between observed dimensions and estimates. Interiors and missing memorial names are deferred until supporting evidence arrives.

Prevent z-fighting during design: follow the [surface ownership checks](docs/MODELLING-WORKFLOW.md#surface-ownership-checks) before repeating components and before completing an asset. Put scoped overlap regressions in the asset validator; check exported LoDs and neighbouring seams too. A successful build or a wall-only check does not establish that the whole asset is free of visible conflicts.

Design Detail/Walk features and a separate fixed-budget District envelope. Follow docs/LOD-PIPELINE.md: preserve silhouette and major openings, use shared atlases, and keep coarse topology/texture dimensions independent of added detail. Set explicit triangle, download and GPU budgets before building the envelope; declare omissions and projection groups. Keep regional aggregation separate. See the BHF and memorial pilots for working examples.

Use master. Do not push or publish unless requested. The local viewer and Detail/Walk/District publication pipeline are implemented. Read docs/VIEWER.md before adding an asset: publish through the catalog, classify every exportable mesh exactly once, preserve the declared geographic frame, and test all three viewing levels. The viewer streams a 3D Tiles hierarchy built by tools/tileset.py (per-building LoD units, merged distant proxies); separately simplified regional envelopes and public hosting are deferred. Do not overstate geometric or visual fidelity.

For ground and street furnishings, read docs/PUBLIC-REALM.md. For new slopes and ground-height changes, follow docs/ELEVATION.md: use bounded named surfaces and shared height controls, split at profile breaks, and preserve distinct bridge/underpass levels. Use rough editable road-height controls and simple planar slopes by default; do not drape ground onto raster fluctuations or add fine terrain refinements. Raster data is supporting evidence, not a mesh target. Keep bridge decks and lower routes distinct, and add explicit landings/steps when modelling those features. Separate area surfaces from building assets and furniture from walkable ground. Keep observed features distinct from estimated placements; share metric furniture generators, not site-specific coordinates.

Follow the required evidence and comparison stages in docs/MODELLING-WORKFLOW.md: orbit 3D imagery, research every modelled elevation, record measurements and missing coverage, compare main shapes before ornament, and verify exported models against references. Builds and attractive renders alone do not establish completion. Establish roads, footprints, access gaps and placeholder building volumes for a bounded block before detailing individual buildings; replace placeholders on the agreed plan.

When asked to work through viewer snags, follow docs/SNAGS.md. Use tools/snags.py
to inspect and exclusively claim a report before editing; resolve it only after
the fix is built, reviewed and published locally. The default ../snags queue and
its screenshots/photos stay outside source control.

The project owner has given standing permission to run `claude -p` outside the
sandbox for read-only code and plan reviews. Do not request that permission again.
Keep review prompts read-only; this authorization does not extend to edits, pushes
or publication by Claude. Use an available permitted execution mechanism; recorded
user authorization does not override runtime restrictions. Avoid duplicate reviews
when the user has already started one.

Browser sessions expire after five idle minutes, including research browsers launched through MCP code. Prefer existing tabs; use browser_close when finished. After expiry, reopen the URL, recreate page variables and continue. See docs/SETUP.md for lifecycle details.

Keep documentation as current-state reference, not a work diary. Preserve source capture dates, measurements, uncertainty, design decisions and reproducible checks; put chronological repair narratives in commits and transient logs/screenshots in ignored output. Update existing sections instead of appending another pass. Read `docs/reviews/` briefs only for their assigned task; they are not general onboarding. See [documentation policy](docs/MODELLING-WORKFLOW.md#documentation-maintenance).
