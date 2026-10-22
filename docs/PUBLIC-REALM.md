# London Square ground and street furniture

The `southport.london-square.public-realm` asset owns the area's ground and ordinary street furniture. The memorial still owns its architecture and historic clustered lamps. Its old provisional paving and bollards remain in the standalone study but are explicitly excluded from the combined publication, so two competing floors are never streamed together.

The area shares the memorial's origin, site orientation and estimated 2.2% northwest fall. `research/layout.json` separates placements and dimensions from mesh construction. `research/references.json` records dated observations, links, attribution and uncertainties. The aerial panorama (January 2025), ground panorama (June 2018), Mapillary sequence (July 2019) and existing OSM geometry are complementary evidence, not a claim of a single-date survey.

## Working spatial split

The initial five walkable surface parts cover the two forecourts, island, roads and outer continuity paving. The initial three separate furniture parts cover the forecourts and island. Ground-following rays therefore cannot mistake a bench, bollard or signal for the pavement. Each part streams independently in the existing viewer; no viewer-specific asset code was added.

These are semantic area boundaries, not the final district tile grid. Keep curb-adjacent surfaces on exactly the same datum and retain crossing/road continuity. Split much larger roads by junction or bounded segment when they outgrow this square; avoid a single town-wide road mesh whose bounds force detailed loading everywhere.

## Geometry and materials

- Large paving squares, checker motifs, border bands and road markings use a small number of surface polygons. Shared authored repeating colour and normal maps carry rectangular slab variation and joints; no reference-image pixels are used.
- Kerbs retain a coarse physical edge at every level. The region boundary is open rather than decorated with an invented kerb or yellow line.
- `lib/southport3d/street.py` provides metric bollard, bench, bin, traffic/pedestrian signal, curved street-light, sagging-chain and guardrail generators. Placements, count and orientation remain in the area recipe.
- Walk omits bollard ribs and hardware and reduces curved sampling. District uses coarse profiles and drops chains and fine guardrails. Signals retain their coloured lenses and backing plates, but are not animated live signals. No directional lighting is baked into the texture maps.
- Maps cap at 512 pixels for Walk and 128 for District. Repeated furniture within compatible groups shares mesh/material prototypes. Parts currently embed shared maps independently; cross-part texture deduplication remains future work.

## Evidence limits and next survey pass

The core paving identity and furniture families are evidenced. Most kerb offsets, tile dimensions, counts, orientations and unmapped object placements are estimates. Some bench/bin positions use recorded OSM nodes; other placements explicitly cite photographic estimates. Access covers, drainage and tactile patches are interpreted details. Dropped-kerb ramp geometry, precise tactile layouts, signal equipment variants and their current configuration need closer evidence. The initial broad outer footway strips were continuity placeholders. The extension below replaces and continues them into bounded streets and gardens. Surrounding buildings, bus shelters and exact current equipment variants remain unfinished.

Use `python3 tools/project.py publish` to build and stream both assets. Render the area alone with `python3 tools/project.py build southport.london-square.public-realm --stage render`; then inspect the combined browser view for foundation contact, overlap, scale and LOD changes. Do not infer that an area is surveyed merely because its surfaces now join up.

## Validation and initial budgets (2026-10-22)

| Level | Placed triangles | GLBs including maps | Embedded maps |
| --- | ---: | ---: | ---: |
| Detail | 70,149 | 3.81 MB | 2.17 MB |
| Walk | 19,285 | 3.44 MB | 2.17 MB |
| District | 9,029 | 0.77 MB | 0.10 MB |

All 24 part/level GLBs passed publication inspection. All 104 mesh objects are classified; the model contains 76 furniture placements. Furniture generators have checked decreasing triangle counts. Surface batching reduced object count from hundreds of separate paint/paving pieces to a few groups per material. Polygon clipping removes underlying faces beneath motifs/paint rather than relying on small depth offsets; unit checks cover cutout areas and repeated subtraction. The viewer also enables logarithmic depth to support the scene's scale range; see the [Three.js renderer options](https://threejs.org/docs/pages/WebGLRenderer.html). Its fragment-depth cost needs testing on users' hardware.

The complete memorial rebuild and existing validators passed. Eleven host-Python tests passed, including a regression preventing a failed full build from leaving a reusable source stamp. Browser review loaded both assets (12 streaming parts), checked the combined overview and close paving/foundation contacts, and exercised automatic ground Detail selection and walking-height adjustment without asset load errors. Placement checks also require furniture bases to lie on their assigned pavement and keep the crossing openings clear. Browser screenshots and the Blender area overview are local build artifacts. Agent-browser performance is limited and is not a desktop GPU benchmark.

## Street and garden extension (2026-10-22)

The area now continues along London Street to the Chapel Street/Hoghton Street
junction (site Y = -144 m), with a short continuation to -154 m. Wright Street
and the station frontage farther along are outside this pass. Short mouths mark
Glebe Place, Anchor Street, Chapel Street and Hoghton Street for future adjoining
assets. Lord Street runs from site X = -104 to +154 m, including the two gardens
behind the colonnades and St George’s Place around the north-east garden.

`research/streets-osm.json` retains the selected OSM ways and furnishing nodes in
the shared metric frame, with attribution. `research/streets.json` records the
working extent, estimated grade, path widths and approximate canopy groups.
`extensions.py` owns the site-specific assembly; `lib/southport3d/landscape.py`
provides reusable capped walls and a controlled tree proxy. The gardens add
lawns, paths, open entrances, low coping, rectangular pools, a schematic round
fountain basin, benches, bins and mapped bus-stop poles. The fountain sculpture
and bus shelters are not yet modelled. Trees represent canopy groups rather than
surveyed individual specimens or species.

There are ten additional streaming parts: ground and furnishings for each garden
and each of three bounded London Street sections. The square ends at X = +/-41 m;
the extensions meet that boundary rather than overlaying its old oversized floor.
London Street splits at Y = -36, -76, -116 and -154 m. Ground and furnishings remain
separate, including tree trunks and retaining walls. The viewer still follows
ground without wall/plant collision physics.

The old estimated 2.2% site-Y slope is clamped outside +/-36 m. This preserves the
square seam without extrapolating a large height change along London Street;
outer longitudinal grades still need surveyed levels. Pools have horizontal
water surfaces. Crossing studs, tactile pads, signal positions and dropped
landings near Chapel/Hoghton are provisional interpretations, not a verified
current crossing layout. Footway widths, wall heights and planting positions are
also estimates. Source photographs remain private; published materials are
procedural colours/maps.

Keep coarse ground outlines, path openings and capped walls at every level.
Tree Walk reduces crown sampling while preserving lobes and trunks; District
replaces the lobes with one coarse crown and omits branches. Repeated furniture
and trees share master mesh data. Fine tree leaves are not generated, and no
photographic foliage is baked. The existing street furniture LOD policies apply
to the extension. A regional texture bake is still unnecessary at this scale.

Use the **Gardens**, **London Street** and **Area bounds** bookmarks on the
public-realm site. Local render artifacts are `renders/overview.png`,
`renders/gardens.png`, `renders/london-street.png` and
`renders/crossing-landing.png` beneath the public-realm build directory.

The expanded public realm has 18 independently streamed parts (54 GLBs) and 241
classified mesh objects. Its measured publication budgets, including embedded
maps, are:

| Level | Placed triangles | GLB bytes | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 147,488 | 8,279,688 | 4,835,767 |
| Walk | 51,696 | 8,289,296 | 4,835,767 |
| District | 22,680 | 1,885,472 | 215,217 |

Walk has fewer placed triangles but similar download size because shared maps
and export representation dominate this small area. These figures exclude the
memorial. All 54 GLBs passed publication inspection. The full memorial rebuild
and validators also passed after the shared library change. Eleven host-Python
tests and the viewer policy tests passed. Render review covers the expanded
overview, garden paths, London Street and the dropped crossing landing. Coplanar
path overlaps are clipped in stable order, and round joins close wedges at bends.

Browser review loaded all 22 combined scene parts without errors at forced
District and Walk, then verified automatic Detail selection for London Street
sections 2/3 at close range. Combined overview and garden screenshots are retained
locally as `renders/combined-overview.png` and `renders/combined-gardens.png`;
`renders/combined-london-detail.png` records the close automatic-level check.

## Prezzo integration

Adding 128 Lord Street exposed a gap between the estimated pavement edge and the
mapped building corner. Its approach now follows an estimated kerb around that
corner; the west London Street footway extends to site X = -10 m, meeting the
wall rather than leaving an uncovered strip. The building owns no walkable ground.
The revised public-realm totals are 147,705 / 51,913 / 22,897 triangles and
8,297,184 / 8,306,792 / 1,902,968 GLB bytes for Detail / Walk / District.

## 118–122 Lord Street approach

The next terrace continues the Prezzo frontage southwest. The perimeter and
southwest garden ground parts now carry the same widened approach out to site
X -52, with a taper to the earlier estimate at X -55. Kerbs and yellow lines
follow that edge; building assets add no duplicate floor. The kerb position is
visually estimated and can be refined with the next Lord Street frontage.

## 116 Lord Street approach

The same approach now extends past British Heart Foundation to X -77, tapering
to the prior ground estimate at X -80 by Christ Church. Building-specific steps
remain inside the recessed doorway. Kerb offsets remain photographic estimates.

## User-supplied Street View frontage review

The August 2024 view from 118 Lord Street (`screenshot-20261022-104131.png`,
provided privately on 2026-10-22) establishes black ribbed bollards along both
kerbs, a pale stone garden balustrade and globe lamps on its piers. The earlier
core bollards remain; nine posts continue the garden row towards BHF, and ten
posts mark the shop-side kerb. The service-road opening around site X -69 stays
clear. Counts, spacing, pier registration and heights are visually estimated;
this is not a surveyed street inventory.

Six open balustrade modules replace the low provisional edging on the observed
24 m stretch. Two pale-globe lamps stand on its piers. Their local shape generators
retain the globe, material bands and open baluster spacing at every level;
Walk and District reduce radial/profile samples. No solid wall proxy fills the
balustrade openings. The rest of the garden boundary remains provisional.
The new **Lord Street furniture** viewer bookmark and `lord-street-furniture.png`
and `garden-globe.png` renders expose this pass. No reference pixels are included
in the published model or Git sources.

## Screenshot correction pass publication budgets

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 179,221 | 8,537,132 | 4,835,767 |
| walk | 58,973 | 8,450,560 | 4,835,767 |
| district | 25,093 | 1,956,300 | 215,217 |

## Church gardens and corrected street seams

The [church-garden pass](LORD-STREET-GARDENS.md) transfers the ground west of
X=-73 to a new bounded asset and continues beyond St George’s Place to the other
church garden. London Square now owns only the memorial-side southwest garden;
the older X=-104 bound above describes the previous build. Its Sainsbury’s
crossing, service-road paving, parking/taxi bay edges and garden return furniture
have been refined from actual August 2024 and July 2026 Street View imagery.

Road paint now shares kerb geometry and tile limits. Both pairs meet across the
square/garden cuts, the London Street taper is correctly stationed, and ground
faces are conformed before export. NatWest has a wider corner approach. Glebe
Place’s detailed asset replaces the old provisional broad pavement stub. See the
linked document for exact ownership and remaining estimates.

The NatWest corner snag pass replaces the mirrored Prezzo kerb with a rounded
apron outside NatWest's actual square footprint. Its old diagonal crossed the
corner pier. The widened London Street footway, service-road blocks and red
approach mouth now meet explicit kerb/paint boundaries; regression rays check
paving around the pier and red surfacing through the former rectangular seam.
August 2024 Street View supports the layout; widths remain visual estimates.
Lord Street bench orientations also account for the generator's backrest at
local +Y, so garden rows face outward and opposite pavement rows face the road.

The Prezzo-side corner now follows the rounded kerb visible in the retained
August 2024 panorama, replacing its single diagonal cut. The slab apron, red
carriageway boundary and paired yellow lines use the same sampled curve; the
London Street neck joins tangentially. The estimated 6.2 m radius retains the
existing terrace registration. Combined close renders check both elevations.

## Post Office Avenue and Anchor Street expansion

The independently streamed `rear-streets-ground` part connects Post Office Avenue
from the St George’s frontage strip at Y=-27 to Anchor Street. Anchor continues
from the prior X=25 stub to X=160, covering the rear of the growing block. Centreline
bends come from the retained OSM extract in `research/corridor-extension.json`;
carriageway/pavement widths and grades remain estimates from retained aerials.
The junction cuts pavements out of the carriageway rather than layering them.
No kerb or paint crosses either open route or the outer ownership cut.

London Street footways extend to the registered frontages at14–20. The old
St George’s Place placeholder cut through the new Mansions/Sainsbury’s frontage;
its shop apron and opposite garden edge now follow those mapped elevations.
The garden’s south lawn/edging moves behind the corrected service-road footway.
The existing crossing follows the new kerbs; exact current parking restrictions
and additional street furniture are deferred rather than invented. Private rear
yards are outside this ground pass.

All levels retain the low-poly street outlines and physical kerbs; Walk/District
reduce texture resolution through the existing pipeline. `New street coverage`
is the viewer overview bookmark. No reference imagery is published.

Canopy meshes use an asset-local correction in `landscape_lod.py`: foliage
ellipsoids face outward and their pole caps are triangles without coincident
corners. Bark winding is retained. This applies to the master and all generated
levels; validation checks nonzero canopy triangle areas and positive signed
volume. The shared ellipsoid primitive still needs a separate caller audit.

Road clipping uses construction offsets as priorities. Surfaces that will be
flattened onto the same road datum must subtract one another even when those
priorities differ by more than the normal small overlay tolerance. This removes
the duplicate asphalt beneath the SW garden return lane. Validation counts
actual triangle intersections there, including overlaps within a batched mesh.
