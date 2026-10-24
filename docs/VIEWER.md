# Local viewer and streaming build

The working levels are:

| Level | Purpose | Starting automatic band |
| --- | --- | --- |
| **Detail** | Close inspection of carvings, lettering, shop fronts and architecture | Within 8 m of a part's bounds |
| **Walk** | Ground-level exploration with reduced geometry and baked detail | Between Detail and District |
| **District** | Looking across a square or several buildings; retain recognisable envelopes and openings | Beyond 70 m of a part's bounds |

These are adjustable starting bands, not claims of perceptual equivalence. The viewer applies 15% hysteresis to avoid flickering between levels. Changing zoom changes camera distance. It selects each part independently; Detail for the obelisk does not require Detail for every colonnade. Larger towns will need visibility and screen-space scheduling refinements. Loose spatial cells now bound loading; merged regional geometry/textures and screen-space error selection remain deferred.

## Build and open

```sh
python3 tools/project.py publish
python3 tools/serve.py
```

`publish` discovers asset publication.json files, rebuilds stale masters, assembles levels, verifies GLBs, and writes the local static viewer to dist/. It does **not** deploy to the internet. Unchanged checked model packages are reused, so changing viewer code normally only refreshes static files/catalog. `--rebuild` explicitly regenerates masters and packages.

During concurrent modelling, use `publish --asset <asset-id>` (repeat the option for several assets) to update completed assets while retaining every other asset at its last published version. This locks only the catalog and selected assets; another worker can continue its build. Unpublished drafts are not added. Omitting `--asset` still performs the full catalog build. A partial publication intentionally does not claim that retained models match their currently edited source.

Open http://127.0.0.1:8765. If the server is on another machine, forward it:

```sh
ssh -N -L 8765:127.0.0.1:8765 user@server
```

Then open http://localhost:8765 on your own computer. The default server listens on loopback and serves only dist/, not the source/reference workspace. In a restricted agent sandbox, run the server from a normal SSH shell; the browser MCP can then visit the same host-local URL. Port forwarding carries the model downloads, so the first detailed view may be slower over a remote connection.

The viewer uses a version-pinned Three.js 0.180.0 import map from jsDelivr; no Node installation or bundler is required to run it. The browser needs internet access for those JavaScript modules and WebGL 2. Vendoring those dependencies for fully offline use remains a separate setup option. Tests use Node 24 and run without downloading Three.js.

## Controls and tuning

- Orbit: drag to rotate, scroll to move closer, right-drag to pan. WASD or arrows move the target and camera together horizontally relative to the view; Shift moves faster. Movement scales with viewing distance. Overview explicitly resets the view.
- Walk: WASD or arrows, Shift to move faster, drag to look. Capture mouse enables pointer lock; Escape releases it. Switching to Walk keeps your horizontal position and heading, placing your eyes 1.7 m above the ground below. If ground is still loading or absent, the camera stays at its current height and retries without jumping to a saved spawn. Walking follows the ground at a 1.7 m eye height. This is an inspection navigator, not a collision/physics simulation: it can pass through walls.
- View settings: force a level, change the automatic distance bands, change rendering resolution, and toggle wireframe/shadows. Statistics show placed triangles, transfer bytes and approximate resident GPU resource bytes.
- The viewer remembers camera position, orientation, orbit target and navigation mode in local storage, including across hard refreshes. Each browser/origin keeps its own view. Clearing site data resets it; unavailable storage simply disables persistence. Snag links and restored snag cameras continue to work without a location picker.

Parts normally appear first at District, then refine within the memory budget. Each model streamer allows two concurrent downloads. Obsolete fetches are cancelled; distant active models are retired as well as cached versions. A replacement usually keeps the old LoD visible, but it may release that version first if both cannot fit. See Spatial working set below for admission, deferral and staging limits.

## Adding a building

1. Add the usual asset.json, source scripts and research inputs. Keep the metric origin and uncertainty documented. Declare any extra host-Python export checks in asset.json's validation_checks list; other buildings do not need the memorial's checks.
2. Add publication.json, using the memorial as an example. Declare `detail`, `walk`, `district`, the source blend, local frame (`site` with yaw from east, or `east-north`), elevation relative to the shared local datum, streaming parts/collections, viewpoints and walking spawn.
3. Classify every exportable mesh into exactly one rule. Each reduced level needs a reasoned `keep`, `omit`, `replace`, `generator` or `decimate` action, with an explicit bake decision where it changes geometry. `keep` is a deliberate decision to retain an envelope/opening, not a catch-all for unreviewed objects. Missing or overlapping classifications fail the build. Collections containing authoring-only guides must be explicitly listed in `excluded_collections` with a reason; meshes outside all declared parts/exclusions fail too.
4. Put building-specific generator adapters beside its construction scripts. Generic bake/export/catalog/viewer code belongs in tools/ and viewer/. Repeated compatible source meshes reuse the same generated mesh and baked materials within a package.
5. Optional `publication_checks` in asset.json names host-Python scripts under the asset’s scripts directory. They receive `--package <validated package>` and `--recipe <publication.json>`, run on new and reused packages, and must exit nonzero on failure. Use these for appearance checks that ordinary GLB validation cannot provide; Prezzo checks window bake coverage. The catalog is not replaced after a failed check.
6. Run `python3 tools/project.py publish`. Review Detail/Walk/District from front, oblique and walking views. Check placement against adjoining assets. No viewer code should need editing to add the building.

The common world frame is **east, up, south** in metres. Publication computes horizontal offsets from WGS84 origins in a local ENU frame. glTF already converts Blender Z-up to Y-up. The declared site yaw is applied exactly once when placing an asset. Vertical origins must use a consistent project datum; the current memorial uses a local estimated zero, not surveyed elevation.

## Files and checks

- `build/<asset>/package/`: generated levels, reused bake maps, assembly coverage and validated package metadata.
- `dist/catalog.json`: complete audit/admin inventory, including bounds, transforms, level URLs, hashes and sizes. The browser uses `scene.json` and nearby cell manifests.
- `dist/assets/<asset>/`: content-addressed GLBs with embedded textures. Hard links are used on the same filesystem to avoid duplicate disk blocks.
- The catalog changes only after all assets validate. Retired model and cell resources are retained for at least 24 hours, then pruned during subsequent publications.

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

## Long signs and texture filtering

The streamer applies anisotropic filtering to loaded material textures, capped
at 16 and the device's reported limit (1 when unsupported). Long narrow sign
panels can otherwise look blurred despite sharp bake pixels, because ordinary
mip filtering discards detail along their long axis. The 118–122 Lord Street
review caught this in Walk/District; the same change improves Prezzo signage.
This costs additional texture samples, not additional downloads or geometry.
See [Three.js Texture anisotropy](https://threejs.org/docs/pages/Texture.html#anisotropy).
The read-only viewer state reports `textureAnisotropy`. Devices with lower
limits can still show softer signs; aspect-aware rectangular atlases remain a
future bake optimisation.

## Reporting snags

Use **Report snag** to mark a captured view, leave a comment and paste reference
photos. **Snag queue** reopens saved reports and camera positions. The local
server stores them outside the repository; restart `tools/serve.py` after
installing this feature. See [the snag workflow](SNAGS.md) for queue location,
agent claim/resolve commands and reference-image handling.


## Live model updates

Completed local publications appear without refreshing. The server emits an SSE
notification when the catalog or spatial scene bootstrap changes; clients also check every 15 seconds
and on returning to the tab, so static hosting and older servers still work.
Restart `tools/serve.py` after installing the event endpoint. No new port is needed.

Changed assets load in a separate scene, then swap together between frames;
unchanged assets keep their caches. Additions, removals, transforms and bounds are
included. A newer publication cancels an obsolete replacement batch. Failed loads
keep the existing scene and report the failure; movement, a new publication or reload retries the working set. View settings contains
**Pause live updates**. Reporting a snag automatically freezes updates and late LoD
activations; the report records the catalog revision and loaded resource filenames.
Camera position, mode and settings survive a swap. Walking rechecks ground height
at the same horizontal location. There is still no building collision physics.

A replacement batch has a 128 MiB estimated GPU-resource budget in addition to the
current scene. Oversized batches try District before refinement; if an existing-asset replacement at District
exceeds the staging budget, the viewer reports the failure and keeps its old geometry. Reload can apply a new initial working set. Estimates are not a hard cap on
browser RAM or texture-decoding allocations. Two replacement downloads can run
alongside the ordinary streamer's two requests. Pausing prevents application of a
batch; requests already in flight may finish offscreen.

Viewer-code, catalog-schema and geographic-frame changes show a reload notice
instead of attempting an unsafe hot swap. Reference assets retired from a catalog
remain on disk for at least 24 hours, cleaned during later publications. Tabs
paused or disconnected longer than that may need to resume or refresh to obtain
the latest catalog. Updates are whole changed GLBs, not binary patches or in-progress
Blender edits. Publish related building and ground changes in one command.

Live-update policy checks: `node tests/live-policy.mjs`. Python regression tests in
`tests/test_live_publication.py` cover retirement/reactivation and event delivery.

`tests/streamer-lifecycle.browser.js` is a Playwright `page.evaluate` function for
a loaded viewer page. It checks versioned caches, batch adoption, reporting freezes
and disposal of superseded asynchronous decodes using isolated fixture scenes.

## Spatial working set

The browser fetches `scene.json`, then only nearby hashed `cells/*.json` manifests.
The flat `catalog.json` is retained for audits, not browser discovery. Each part
appears once, in a metric cell chosen by centre and horizontal extent; published
bounds conservatively include every LoD after its world transform. Cell sizes
start at 64 m and increase by factors of four. A small origin-crossing object does
not become a root-level object. The bootstrap contains cell descriptors and asset
names/views, not every part. Paging this descriptor list is future work if needed.

Selection includes the camera frustum (up to its 3 km far plane) and a 250 m
near-camera safety area. A 64 m padding prefetches content at view edges, and an
8-second grace period retains recently visible cells/parts during turns and pans.
This also works in high orbit: visible ground is not limited to a fixed circle
below the camera. Defaults are a 256 MiB estimated payload budget and up to
128 MiB additional replacement staging space.
Set `viewer/world.json:streaming.radius`, `margin`, and `budget` to change the
published policy. These are payload estimates, not a cap on all browser/GPU RAM.
Visible parts take priority over nearby/offscreen retention; ground is prioritised
within each class, and coarse coverage is admitted before refinement. Retention
is expendable under memory pressure. Forced
Detail remains budgeted and geographically bounded. Distant active models are
removed and disposed; requests are aborted and obsolete decodes are discarded.
Parts that do not fit are labelled deferred in state/status rather than exceeding
the budget. Current assets can still exceed this budget even at District: they
need further LoD optimisation. No distant aggregate exists outside the horizon.

`python3 tools/project.py index` regenerates cells from the last-good published
catalog without rebuilding a building. Add `--viewer` to publish viewer code changes
without rebuilding any asset. Old catalog formats recover other LoD
bounds from matching package metadata or the published GLBs. Regular publication
also writes the spatial index. Immutable cells and GLBs precede the atomic scene
bootstrap; old resources retain the same 24-hour retirement grace period.

Live updates compare the current spatial working set and stage changed assets'
loaded parts. All cells come from one bootstrap revision; a per-asset revision
prevents mixed-version assembly. Travel transactions follow cell membership, finish without cancellation by small
camera movements, then replan for the latest view. Unchanged asset parts keep
their roots, caches and downloads as adjacent parts enter or leave. Only a new
publication revision cancels an outstanding transaction. Late cell fetches wait
for the next unfrozen update before changing scene membership. Replacement failure or an oversized existing-asset batch
keeps the previous scene and reports the failure; reload is a fallback for such
batches. Initial loading is progressive. Snag capture freezes adoption and records
both the applied `sceneRevision` and legacy `catalogRevision`, plus exact loaded
resource URLs. Camera persistence remains unchanged.

The server now observes both catalog and scene updates. An already running older
server still signals ordinary asset publications; index-only changes are caught
by the 15-second browser poll until that server is restarted.

`window.southport.getState()` reports loaded parts with asset IDs, deferred flags,
cell count, estimated residency/budget and staging bytes. It contains only the
current working set; do not map parts by flat catalog array order.
