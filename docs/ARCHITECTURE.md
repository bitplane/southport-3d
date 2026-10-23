# Architecture

Geographic folders are for people navigating the source. They need not match the runtime tile grid. Each asset has a stable dotted ID and an asset.json describing its source, metric units, geographic origin, orientation, components and available LODs.

The memorial retains its researched local coordinate system and site transformation. Before placing exported assets in a town scene, check the site recipe and actual exported coordinates: do not apply the site rotation twice. Blender uses Z-up; glTF export converts to glTF's Y-up convention. Geographic origins must be transformed into a common metric frame before combining assets. tools/publication.py projects asset origins into the viewer's common east/up/south frame; publication.json declares whether the asset needs its site yaw applied.

Generic Mesh/lathe/tube/text construction lives in lib/southport3d/geometry.py. Memorial colonnades, inscriptions, relief layout and survey corrections remain asset-specific. Extract another helper when it has a clear reusable interface; avoid turning a single building's assumptions into universal defaults.

tools/project.py is a manifest-driven runner shared by buildings and street assets. It discovers manifests, builds in an isolated directory and checks source files. Extra post-export checks are declared by each asset's validation_checks list. They are optional host-Python scripts, alongside the normal Blender validation stage; another building does not inherit memorial-specific checks.

Source includes Python recipes, JSON observations/calibrations and numeric NPZ relief depth fields. Existing NPZ data makes the master build independent of private photographs. Historical sculpting tools are retained for future corrections but may require local reference files. Do not confuse those optional research tools with the ordinary reproducible build path.

Generated Blender scenes, GLBs, baked/procedural maps, renders and validation reports live in build/. The local publication pipeline writes content-addressed GLBs and a viewer catalog into dist/, linked to source and recipe signatures. A future deployment can upload the same static package to hosting/object storage. Git remains a source repository. See docs/VIEWER.md for the supported contract.

Polygon clipping and ground-boundary conformance live in lib/southport3d/planar.py and conform.py. Site-specific layouts remain in each asset. The publication schema rejects unknown orchestration fields while leaving custom generator settings to the generator’s checks.

The runner locks each asset across build/export/render/LoD operations. Publication locks the catalog and all asset outputs for a consistent snapshot. Locks are advisory POSIX locks under ignored build/.locks; direct scripts bypass them. Runtime dependency records invalidate only stages that consumed changed shared modules. Master inputs are snapshotted; leaf stages cannot mutate the master. See [INCREMENTAL-BUILDS.md](INCREMENTAL-BUILDS.md). See [MODELLING-WORKFLOW.md](MODELLING-WORKFLOW.md) for the review process and lessons from the first block.

Metric parallel road-edge curves and ownership clipping live in `southport3d/road.py`. Use the same kerb curve for both paint offsets and clip it at the shared site station; a tile boundary is not a kerb return.

The viewer reads a compact `scene.json` bootstrap and content-addressed loose cell
manifests generated from the union of all published LoD bounds. The flat
`catalog.json` remains for whole-map audits. Source geographic folders do not
determine runtime cells. See [VIEWER.md](VIEWER.md) for residency and live updates.
