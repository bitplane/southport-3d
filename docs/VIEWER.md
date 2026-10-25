# Local viewer and streaming build

The working levels are:

| Level | Purpose | Approximate automatic band (1000 px tall view) |
| --- | --- | --- |
| **Detail** | Close inspection of carvings, lettering, shop fronts and architecture | Within ~8 m of a building |
| **Walk** | Ground-level exploration with reduced geometry and baked detail | Between Detail and District |
| **District** | Looking across a square or several buildings; retain recognisable envelopes and openings | Beyond ~70 m of a building |

The viewer renders an [OGC 3D Tiles](https://docs.ogc.org/cs/22-025r4/22-025r4.html) hierarchy with [3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS) and chooses levels by **screen-space error**: each tile declares how far (in metres) it may deviate from the next finer one, and is refined when that error would exceed the allowed number of pixels. Bands therefore scale with field of view, window size and pixel ratio rather than being fixed distances. The unit of selection is a **building**: all of its parts switch level together. Distances are measured to the building's oriented bounding box, not a world-axis box around it.

Refinement is REPLACE: a coarser tile stays drawn until everything replacing it has loaded, so moving or turning never leaves gaps, and levels cross-fade over 300 ms instead of popping. When the memory budget is reached, refinement pauses and coarser tiles remain; nothing that is drawn is unloaded to make room. Far away, merged proxies cover groups of buildings (see Tiles and memory below).

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
- View settings: force a level, change the allowed on-screen error (lower is sharper and loads more), choose the memory budget, change rendering resolution, and toggle wireframe/shadows. Statistics show drawn triangles, tile bytes transferred and the renderer's resident estimate.
- The viewer remembers camera position, orientation, orbit target and navigation mode in local storage, including across hard refreshes. Each browser/origin keeps its own view. Clearing site data resets it; unavailable storage simply disables persistence. Snag links and restored snag cameras continue to work without a location picker.

On opening, the whole town appears within seconds as merged proxies, then refines where you look. Forcing a level refines every tile in view down to that level (still within the memory budget); collapsed tiles whose levels are identical count as each level they stand in for.

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
- `dist/catalog.json`: complete audit/admin inventory, including bounds, transforms, level URLs, hashes and sizes. The browser uses `scene.json` and the tileset it names.
- `dist/assets/<asset>/`: content-addressed per-part GLBs with embedded textures (the tile builder's input). Hard links are used on the same filesystem to avoid duplicate disk blocks.
- `dist/tiles/`: content-addressed tileset JSON and merged tile GLBs, built by `tools/tileset.py`; `build/tiles-cache/` remembers which recipe produced which tile so unchanged tiles are not rebuilt.
- The catalog changes only after all assets validate. Retired model and tile resources are retained for at least 24 hours, then pruned during subsequent publications.

The master remains read-only during LOD assembly. Each source prototype is processed once per compatible material/scale group, then reused for its instances. Texture dimensions are capped per level; normals are renormalised after downsampling. The source and recipe signatures invalidate stale outputs. GLBs are checked for positions, indices, transforms, texture embedding, budgets and non-increasing placed triangle counts. The original full memorial validators still run when its master changes.

Run source and policy tests with:

```sh
python3 tools/project.py check
python3 -m pytest tests
node --test viewer/tests/*.test.js
node tests/run-browser.mjs http://127.0.0.1:8765/   # needs tools/browser Playwright and Chrome
```

`tests/tiles.browser.js` flies the loaded viewer from the overview to street level, pans away and back, forces each level and swaps in a fresh tileset. It fails if any building in view is ever left without a drawn tile covering it, if a forced level is not honoured, or if a swap empties the scene. Pass a byte budget as a second argument to repeat it under memory pressure.

Current limitations: no full collision physics, KTX2/mesh compression, GPU instance batching, or automatic visual-quality certification. Distant proxies reuse District geometry with reduced or flattened textures; they are not separately simplified envelopes, so the whole-town proxy carries all District triangles.

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

The viewer applies anisotropic filtering to loaded material textures, capped
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

A new publication names a new content-addressed tileset. The viewer loads it
hidden alongside the current one, for the current camera, and swaps the two
between frames once the new view has settled (fully loaded, or as far as the
budget allows). Unchanged tiles keep their URLs, so they come from the browser
cache. The replacement has its own memory budget while it loads, so memory use
can briefly reach twice the budget during a swap. A
newer publication replaces an obsolete pending one. View settings contains
**Pause live updates**. Reporting a snag freezes tile selection and swaps;
the report records the scene revision and the drawn tiles' resource names.
Camera position, mode and settings survive a swap. Walking rechecks ground height
at the same horizontal location. There is still no building collision physics.

Viewer-code, catalog-schema and geographic-frame changes show a reload notice
instead of attempting an unsafe hot swap. Reference assets retired from a catalog
remain on disk for at least 24 hours, cleaned during later publications. Tabs
paused or disconnected longer than that may need to resume or refresh to obtain
the latest catalog. Updates are whole changed GLBs, not binary patches or in-progress
Blender edits. Publish related building and ground changes in one command.

Live-update policy checks: `node tests/live-policy.mjs`. Python regression tests in
`tests/test_live_publication.py` cover retirement/reactivation and event delivery.

## Tiles and memory

`tools/tileset.py` builds the hierarchy from the published catalog; publication
runs it automatically and `python3 tools/project.py index` reruns it (add
`--viewer` to install viewer code changes) without rebuilding any building.

- **Units.** Each asset is one unit, so its parts are merged per level into one
  GLB and always switch together. Assets wider than 96 m (roads, public realm) or
  whose merged Detail would exceed 64 MB (the war memorial) become one unit per part.
  Fixed-level parts draw their fixed level in every tile.
- **Unit chain.** District → Walk → Detail, each tile REPLACE-refining to the next.
  Consecutive levels with identical content collapse into one tile (most ground),
  so crossing a band never re-downloads the same mesh.
- **Proxies.** Buildings and ground get separate quadtrees over unit centres, so
  wide ground sections do not swell building cells. Leaf cells (at most 128 m or
  six units) hold a merged District proxy with textures capped at 128 px and no
  normal/roughness maps; inner nodes are empty. The root holds the whole town
  with textures replaced by their mean colour, so the first frame shows
  everything and a view keeps at most the root plus one cell per area resident.
- **Errors and caps.** Geometric errors are Detail 0, Walk 0.06 m, District 0.52 m,
  cell proxy 1.5 m, root 40 m. With the default 8 px target on a
  1000 px tall 50° view, District gives way to Walk at about 70 m and Walk to
  Detail at about 8 m. Textures are capped at 4096 / 2048 / 512 px for
  Detail / Walk / District. Change these in `tools/tileset.py`; the default pixel
  target is `viewer/world.json:lodPolicy.errorTarget`.
- **Budget.** `viewer/world.json:streaming.budget` (default 1 GiB) is the renderer's
  cache cap, measured as its estimate of geometry and texture bytes. Fully refined
  street views at the default error target need roughly 420–630 MB (the war
  memorial is the heaviest); the overview needs under 50 MB. When the tiles a view
  needs do not fit, the viewer raises its effective error target step by step until
  a complete coarser set fits, and relaxes it again when there is room. A camera
  very close to a heavy building still needs that building's fine tiles, so a small
  budget can leave such views on coarse proxies; they stay complete, never blank.

`window.southport.getState()` reports the drawn tiles with their unit, level and
resource, level counts, whether the view has settled, the resident estimate and
whether the budget is full.

Ground parts may declare `support_surface` to preserve a named support layer
across LoDs and live replacement. Walking retains nearby support rather than
snapping onto an overhead bridge or a lower floor. See [ELEVATION.md](ELEVATION.md).
