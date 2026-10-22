# London Square ground and street furniture

The `southport.london-square.public-realm` asset owns the area's ground and ordinary street furniture. The memorial still owns its architecture and historic clustered lamps. Its old provisional paving and bollards remain in the standalone study but are explicitly excluded from the combined publication, so two competing floors are never streamed together.

The area shares the memorial's origin, site orientation and estimated 2.2% northwest fall. `research/layout.json` separates placements and dimensions from mesh construction. `research/references.json` records dated observations, links, attribution and uncertainties. The aerial panorama (January 2025), ground panorama (June 2018), Mapillary sequence (July 2019) and existing OSM geometry are complementary evidence, not a claim of a single-date survey.

## Working spatial split

Five walkable surface parts cover the two forecourts, island, roads and outer continuity paving. Three separate furniture parts cover the forecourts and island. Ground-following rays therefore cannot mistake a bench, bollard or signal for the pavement. Each part streams independently in the existing viewer; no viewer-specific asset code was added.

These are semantic area boundaries, not the final district tile grid. Keep curb-adjacent surfaces on exactly the same datum and retain crossing/road continuity. Split much larger roads by junction or bounded segment when they outgrow this square; avoid a single town-wide road mesh whose bounds force detailed loading everywhere.

## Geometry and materials

- Large paving squares, checker motifs, border bands and road markings use a small number of surface polygons. Shared authored repeating colour and normal maps carry rectangular slab variation and joints; no reference-image pixels are used.
- Kerbs retain a coarse physical edge at every level. The region boundary is open rather than decorated with an invented kerb or yellow line.
- `lib/southport3d/street.py` provides metric bollard, bench, bin, traffic/pedestrian signal, curved street-light, sagging-chain and guardrail generators. Placements, count and orientation remain in the area recipe.
- Walk omits bollard ribs and hardware and reduces curved sampling. District uses coarse profiles and drops chains and fine guardrails. Signals retain their coloured lenses and backing plates, but are not animated live signals. No directional lighting is baked into the texture maps.
- Maps cap at 512 pixels for Walk and 128 for District. Repeated furniture within compatible groups shares mesh/material prototypes. Parts currently embed shared maps independently; cross-part texture deduplication remains future work.

## Evidence limits and next survey pass

The core paving identity and furniture families are evidenced. Most kerb offsets, tile dimensions, counts, orientations and unmapped object placements are estimates. Some bench/bin positions use recorded OSM nodes; other placements explicitly cite photographic estimates. Access covers, drainage and tactile patches are interpreted details. Dropped-kerb ramp geometry, precise tactile layouts, signal equipment variants and their current configuration need closer evidence. The broad outer footway strips are continuity placeholders, not completed adjoining streets. Vegetation, outer bus stops/shelters and surrounding buildings remain outside this pass.

Use `python3 tools/project.py publish` to build and stream both assets. Render the area alone with `python3 tools/project.py build southport.london-square.public-realm --stage render`; then inspect the combined browser view for foundation contact, overlap, scale and LOD changes. Do not infer that an area is surveyed merely because its surfaces now join up.

## Validation and initial budgets (2026-10-22)

| Level | Placed triangles | GLBs including maps | Embedded maps |
| --- | ---: | ---: | ---: |
| Detail | 70,149 | 3.81 MB | 2.17 MB |
| Walk | 19,285 | 3.44 MB | 2.17 MB |
| District | 9,029 | 0.77 MB | 0.10 MB |

All 24 part/level GLBs passed publication inspection. All 104 mesh objects are classified; the model contains 76 furniture placements. Furniture generators have checked decreasing triangle counts. Surface batching reduced object count from hundreds of separate paint/paving pieces to a few groups per material. Polygon clipping removes underlying faces beneath motifs/paint rather than relying on small depth offsets; unit checks cover cutout areas and repeated subtraction. The viewer also enables logarithmic depth to support the scene's scale range; see the [Three.js renderer options](https://threejs.org/docs/pages/WebGLRenderer.html). Its fragment-depth cost needs testing on users' hardware.

The complete memorial rebuild and existing validators passed. Eleven host-Python tests passed, including a regression preventing a failed full build from leaving a reusable source stamp. Browser review loaded both assets (12 streaming parts), checked the combined overview and close paving/foundation contacts, and exercised automatic ground Detail selection and walking-height adjustment without asset load errors. Placement checks also require furniture bases to lie on their assigned pavement and keep the crossing openings clear. Browser screenshots and the Blender area overview are local build artifacts. Agent-browser performance is limited and is not a desktop GPU benchmark.
