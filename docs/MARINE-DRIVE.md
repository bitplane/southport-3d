# Marine Drive and north Marine Lake block plan

The `southport.marine-drive.public-realm` and
`southport.marine-drive.frontage-placeholders` assets extend the canvas from the
existing Marine Parade/Promenade junction, across Marine Way Bridge to the Ocean
Plaza junction, then northeast along Marine Drive to the Fairway roundabout.
They also connect the north lake Promenade frontage back to the Leicester quarter.
The bounded plan uses site X -190–1390 m and Y 175–930 m, clipped to its authored
study polygon. The lower175–230m strip fills the VictoriaStreet connection north
of the original Stanley ground. The southern lake/Princes Park, pier beyond the road, western half
of Ocean Plaza and wider Hesketh residential/golf area are outside this pass.

There are 116 neutral building volumes, 125 road/access source segments, and 28
longer mapped paths. They preserve footprints and approximate height groups,
including the Waterfront Hotel's rounded end and lower attached building. Flat
caps are height bounds; facades, pitched roofs, spires, basement architecture and
small roof furniture are deliberately unresearched. Narrow routes at Albert Place,
rear alleys and restaurant drive-throughs remain open. Five conflicting OSM
outline/route locations receive conservative access reservations, individually
recorded with the original outline and removed area in `research/measurements.json`.
Exact canopies and possible covered passages at those conflicts remain uncertain.

Google Maps actual textured 3D was inspected through four close hotel/theatre
orbits, opposing north-lake/Fairway orbits, a middle frontage orbit and an Albert
Place close view. The retained OSM axes/outlines are attributed seeds, checked
against these views and registered aerials. A central flat-view scale bar is
20 m over 55 CSS pixels. Aug 2024 bridge, July 2026 Marine Drive/Promenade and
August 2026 Fairway Street View add ground-level evidence. The coverage and
measurement records distinguish views actually seen from obscured private walls
and deferred detailed elevations. Reference captures remain private outside Git.

Dated evidence overrides stale shapes: Sefton Council confirmed the theatre
complex's demolition in [March 2025](https://www.sefton.gov.uk/mysefton-news/latest-news/leading-contractor-graham-to-deliver-marine-lake-events-centre-in-southport/)
and [site construction progress in September 2026](https://sefton.gov.uk/mysefton-news/latest-news/marine-lake-events-centre-works-progressing-at-impressive-pace/).
The former main theatre and attached service volume are retained only as retired
research outlines. A brown provisional construction reservation replaces them;
current excavations, retaining walls and the new ramp are not a surveyed model.
No completed future events-centre volume is invented.

Roads are planar ownership arrangements before height evaluation. Complete
buffered curves create the shared junction mouths; paint replaces road faces.
Victoria Street now joins Bath Street in the Stanley ground recipe, and Bank
Square joins Booth Street in the Leicester recipe; their existing building and
courtyard exclusions are retained. The Promenade/Leicester junction has a small painted mini-roundabout, rather
than a raised island inferred from circular OSM axes. Exact existing X85 and
Marine Parade Y310 handovers preserve road, median, paving and paint boundaries.
Car parks retain their outlines and entry routes; individual bay markings and
most small aisle topology are omitted. The Marine Drive seawalk and continuous
low seawall are separate from its inland asphalt parking. Property walls,
dropped kerbs, tactile layouts, drainage and most ordinary street furniture
remain deferred rather than filling unknown boundaries with walls.

`regions/southport/elevation/marine-drive.json` owns the named bounded mainland,
road, bridge and water surfaces. It preserves the Leicester Y230 grade and
existing 2.2 m Promenade datum. The shallow bridge pavement rises to an estimated
3.4 m, above water estimated at 0.6 m; these are metres above the memorial's
estimated local zero, **not surveyed or sea-level heights**. Every profile break
is split into the ground meshes. Buildings keep level top bounds; their foundations follow the mainland profile.
Interior floors are not modelled. Bridge guardrails use the shared metric
generator, remain upright and are seated on the bridge profile. The A-frame and
stays are provisional silhouettes, with pylon height 28±5 m. Bridge joints and
engineering details are outside this footprint pass.

Eight bounded ground parts share the `southport/marine-corridor` support identity.
Water, bridge structure and seawall parts are non-ground. Islands remain separate
land inside the water outline. All three viewing levels retain the same fixed
canvas and massing geometry; no fine architectural geometry is being decimated
into District. Solid authored materials need no photographic textures or atlases.
The budgets are fixed at 60,000 ground triangles, 30,000 structure/water triangles
and 15,000 placeholder triangles per level, with combined downloads below 14 MB.

The asset validators test triangle interiors against the named profile, closed
placeholder volumes, exact footprint controls, road clearance and all mesh
surfaces. The complete fast coplanar scan records exact triangle identities and
locations for narrow float32/fan seam residues; it rejects positive-width
conflicts. These numerical findings are not blanket asset exemptions or a claim
of mathematical overlap freedom. `check_published_seams.py` checks the actual
three-level GLBs, neighbouring handovers, identical level geometry and budgets,
and retains the neighbouring exported overlap review queue outside Git.

## Review record

All four affected assets built and validated, then published together through
`project.py publish`: Marine ground/placeholders, Stanley ground and Leicester
ground. Existing Burlington courtyard exclusions were retained. Source check
passed after staging (53 assets, 975 source files).

| Per level | Triangles | GLB bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Marine ground/structure/water | 79,530 | 5,214,960 | 5,120,192 |
| 116 placeholder volumes | 3,068 | 570,356 | 284,788 |
| Combined | 82,598 | 5,785,316 | 5,404,980 |

These totals are the same for Detail, Walk and District. The 59,159 ground and
20,371 structure/water triangles remain within their separately declared budgets.
All 127 parts classify their meshes exactly once; 381 part/level GLBs were checked.
Solid materials embed no images. Actual exported arrays are identical across the
three levels, rather than merely having equal triangle counts.

The exported neighbour review passed **99 seam probes** at the existing X85,
Marine Parade Y310, Stanley Y175, Leicester Y230 and internal coastal tile cuts.
The complete selected-neighbour scan covered 123,553 triangles at each level.
Its 571 candidate pairs break down into 468 Marine internal numerical residues,
one new/old pavement boundary residue and 102 older neighbour candidates. The
Marine internal count and area agree with the full master scan; every explicit
intersection is narrower than 0.183 mm, totalling 0.048263 m² across the area.
The new/old seam residue is 0.000075571 m² and 0.0647 mm wide. Exact surfaces,
triangle identities and locations are retained in private audit JSON.

One older, unmodified X22 Nevill/Marine Parade kerb-to-paving group has nine
candidates totalling 0.004292 m², including a 32.6 mm-wide intersection. It was
reviewed close in the assembled viewer and remains an explicitly recorded older
candidate outside the new ownership area; this work does not claim the whole
neighbourhood is mathematically overlap-free. The remaining older candidates
also remain in the private review queue.

Reference comparisons used the assembled overview, rounded hotel/bridge view,
Fairway approach, Victoria/Bath and BankSquare/Booth junctions, then pedestrian
bridge and seawalk views. The north-lake outline, island placements, principal
road alignments and volume groups match the researched broad shapes. The
retired theatre is a brown construction reservation rather than the old 3D roof.
Precise property walls, roof forms and current construction levels remain the
limits described above.

Whole-area, junction and pedestrian inspection requested Detail, Walk and
District with `pending=0`, `failed=0` and `settled=true`. All 127 Marine units were
present in the overview. Because the three contents are identical, the tileset
collapses their chains and reports these units as Detail at all requested
settings; separate exported arrays were checked at all three levels. Walking
retained eye height 5.024564 m at the inspected bridge point and 3.900000 m on the
seawalk. A below-deck view retained its existing height and did not snap onto the
bridge or non-walkable water. Live scene replacements preserved support height.

Private review artifacts are under `../output/marine-drive/`, including final
level overviews, junction/bridge/seawalk captures, `seam-probes.json`, each level's
full neighbouring audit, and `cross-asset-triage.json`. Renders are under the
ordinary asset build directories. The audited packages were confirmed unchanged
through the subsequent Burlington scene publication (`6fc02f26…`).

