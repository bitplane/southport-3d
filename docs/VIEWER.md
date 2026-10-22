# Local viewer and streaming build

The working levels are:

| Level | Purpose | Starting automatic band |
| --- | --- | --- |
| **Detail** | Close inspection of carvings, lettering, shop fronts and architecture | Within 8 m of a part's bounds |
| **Walk** | Ground-level exploration with reduced geometry and baked detail | Between Detail and District |
| **District** | Looking across a square or several buildings; retain recognisable envelopes and openings | Beyond 70 m of a part's bounds |

These are adjustable starting bands, not claims of perceptual equivalence. The viewer applies 15% hysteresis to avoid flickering between levels. Changing zoom changes camera distance. It selects each part independently; Detail for the obelisk does not require Detail for every colonnade. Larger towns will need visibility and screen-space scheduling refinements. Regional tiles and merged regional textures are deliberately deferred.

## Build and open

```sh
python3 tools/project.py publish
python3 tools/serve.py
```

`publish` discovers asset publication.json files, rebuilds stale masters, assembles levels, verifies GLBs, and writes the local static viewer to dist/. It does **not** deploy to the internet. Unchanged checked model packages are reused, so changing viewer code normally only refreshes static files/catalog. `--rebuild` explicitly regenerates masters and packages.

Open http://127.0.0.1:8765. If the server is on another machine, forward it:

```sh
ssh -N -L 8765:127.0.0.1:8765 user@server
```

Then open http://localhost:8765 on your own computer. The default server listens on loopback and serves only dist/, not the source/reference workspace. In a restricted agent sandbox, run the server from a normal SSH shell; the browser MCP can then visit the same host-local URL. Port forwarding carries the model downloads, so the first detailed view may be slower over a remote connection.

The viewer uses a version-pinned Three.js 0.180.0 import map from jsDelivr; no Node installation or bundler is required to run it. The browser needs internet access for those JavaScript modules and WebGL 2. Vendoring those dependencies for fully offline use remains a separate setup option. Tests use Node 24 and run without downloading Three.js.

## Controls and tuning

- Orbit: drag to rotate, scroll to move closer, right-drag to pan. Viewpoint buttons and Overview reset the view.
- Walk: WASD or arrows, Shift to move faster, drag to look. Capture mouse enables pointer lock; Escape releases it. Walking follows the ground at a 1.7 m eye height. This is an inspection navigator, not a collision/physics simulation: it can pass through walls.
- View settings: force a level, change the automatic distance bands, change rendering resolution, and toggle wireframe/shadows. Statistics show placed triangles, transfer bytes and approximate resident GPU resource bytes.
- Select a site to focus another asset. The UI is populated entirely from catalog.json.

Parts appear first at District where available, then switch only after the requested level is loaded. At most two downloads run concurrently. Obsolete fetches are cancelled, and the current model remains visible during replacement. Inactive resources are evicted least-recently-used against a 256 MiB estimate. Active models remain pinned, so forcing Detail everywhere can exceed that soft budget. GPU estimates are not a browser process-memory measurement.

## Adding a building

1. Add the usual asset.json, source scripts and research inputs. Keep the metric origin and uncertainty documented. Declare any extra host-Python export checks in asset.json's validation_checks list; other buildings do not need the memorial's checks.
2. Add publication.json, using the memorial as an example. Declare `detail`, `walk`, `district`, the source blend, local frame (`site` with yaw from east, or `east-north`), elevation relative to the shared local datum, streaming parts/collections, viewpoints and walking spawn.
3. Classify every exportable mesh into exactly one rule. Each reduced level needs a reasoned `keep`, `omit`, `replace`, `generator` or `decimate` action, with an explicit bake decision where it changes geometry. `keep` is a deliberate decision to retain an envelope/opening, not a catch-all for unreviewed objects. Missing or overlapping classifications fail the build. Collections containing authoring-only guides must be explicitly listed in `excluded_collections` with a reason; meshes outside all declared parts/exclusions fail too.
4. Put building-specific generator adapters beside its construction scripts. Generic bake/export/catalog/viewer code belongs in tools/ and viewer/. Repeated compatible source meshes reuse the same generated mesh and baked materials within a package.
5. Run `python3 tools/project.py publish`. Review Detail/Walk/District from front, oblique and walking views. Check placement against adjoining assets. No viewer code should need editing to add the building.

The common world frame is **east, up, south** in metres. Publication computes horizontal offsets from WGS84 origins in a local ENU frame. glTF already converts Blender Z-up to Y-up. The declared site yaw is applied exactly once when placing an asset. Vertical origins must use a consistent project datum; the current memorial uses a local estimated zero, not surveyed elevation.

## Files and checks

- `build/<asset>/package/`: generated levels, reused bake maps, assembly coverage and validated package metadata.
- `dist/catalog.json`: only data the viewer needs, including bounds, transforms, level URLs, hashes and resource sizes.
- `dist/assets/<asset>/`: content-addressed GLBs with embedded textures. Hard links are used on the same filesystem to avoid duplicate disk blocks.
- The catalog changes only after all assets validate. One previous catalog's resources are retained for open browser tabs; older publication resources are pruned on subsequent builds.

The master remains read-only during LOD assembly. Each source prototype is processed once per compatible material/scale group, then reused for its instances. Texture dimensions are capped per level; normals are renormalised after downsampling. The source and recipe signatures invalidate stale outputs. GLBs are checked for positions, indices, transforms, texture embedding, budgets and non-increasing placed triangle counts. The original full memorial validators still run when its master changes.

Run source and policy tests with:

```sh
python3 tools/project.py check
python3 -m unittest discover -s tests -v
node --test viewer/tests/*.test.js
```

Current limitations: no regional tiling, full collision physics, KTX2/mesh compression, GPU instance batching across parts, or automatic visual-quality certification. District deliberately retains some architectural envelopes and openings while reducing/omitting heavy detail; it is not the tiny whole-town proxy discussed for future regional views.

## First memorial package measurements (2026-10-22, before separate ground asset)

These totals include the fixed District ground and embedded textures, in decimal MB. They describe all placed geometry, not just triangles visible in one camera view.

| Forced level | Placed triangles | Total GLB bytes | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 9,412,654 | 178.04 MB | 14.95 MB |
| Walk | 1,552,492 | 62.62 MB | 16.73 MB |
| District | 351,680 | 35.84 MB | 3.87 MB |

Part splitting duplicates some resources across GLBs; Detail therefore exceeds the earlier single-file 131 MB master. Walk introduces baked maps and can have more image bytes despite much less geometry. Further envelope simplification, shared textures and compression remain worthwhile. These are working inspection levels, not final town-scale budgets.

Validation: the master build and its existing export checks passed; all 13 part/level GLBs passed publication inspection. All 307 nonempty physical meshes have declared part/rule coverage, with the survey guide explicitly excluded. Python contract tests, JavaScript policy tests and syntax checks passed. A second publication reused the checked packages. Browser checks exercised all five parts, forced Walk/District, automatic close-up Detail, viewpoint changes, walking movement, orbit/overview and wireframe toggling without asset errors. Walk and District colonnade screenshots were inspected; openings and column silhouettes remain present, with loss of fine carving at District expected. Full visual equivalence, pointer lock and hardware performance have not been certified; the agent browser's low frame rate is not a useful desktop GPU benchmark.

The separate public-realm asset now replaces the memorial’s old ground part in the combined scene. See [public-realm ownership, spatial parts and evidence limits](PUBLIC-REALM.md). The table above remains the historical first-package measurement.
