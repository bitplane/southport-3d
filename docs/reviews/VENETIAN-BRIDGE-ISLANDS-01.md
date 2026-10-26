# Venetian Bridge and islands: implementation and independent review brief

Task `074c5aaaff9d4a09baace83cce103975`, 26 October 2026.
User: “build out this bridge and the two islands and their shapes. be detailed
with the bridge specially, including the gates and lamp posts etc.”
Implementer: Terra 6.1 high; independent visual reviewer: foreground agent.

## Baseline and scope

The saved snag view marks the Venetian Bridge through both southern Marine Lake
islands, including its shore approaches. It does not mark Marine Way's cable-stay
bridge or Southport Pier. The current map has coarse island polygons, a thin deck
and solid placeholder parapets. This is an initial implementation brief, not a
claim that the islands or bridge have already been surveyed by the reviewer.

Existing owner: `regions/southport/marine-lake-south/public-realm/`. Its script
builds `venetian-ground` separately from `lake-water`, with underside and rail
envelopes in `shore-walls`. Island polygons also subtract holes from water.
Read the layout, measurements, current elevation interfaces and docs/MARINE-LAKE-SOUTH.md
before edits. The old 5.2 m width and old deck height are uncertain estimates;
some documentation predates the rough-height migration. Read actual current
controls rather than copying a prose number. Existing elevations referencing DSM
samples are supporting hypotheses, not proof of the finished bridge profile.

Scope: complete bridge, gates, posts/lamps, balustrades, deck/underside/supports
that can be evidenced, both island outlines and broad landform, and bounded
shore/island access connections. Do not expand into lake-wide terrain modelling,
the pier, park buildings or unrelated attractions.

## Independent reference inspected

Stephen Craven's photograph, taken 26 June 2023:
https://www.geograph.org.uk/photo/7531530
Image: https://s0.geograph.org.uk/geophotos/07/53/15/7531530_39b4f9bf.jpg
Root opened and visually inspected the actual image. Private review capture:
`../output/venetian-review-reference.png`.

Clearly visible: cream balustrades with turned balusters, substantial rectangular
panelled piers and cap/base profiles; green ornamental columns with shaped bases
and capitals; a pale globe fitting on the nearest column, with differing apparent
lamp-top states farther away; transverse timber deck boards; a green side gate;
and a raised central crossing/profile in the distance. This one photograph does
NOT establish all gates, lamp counts or current condition. Do not repeat the one
visible globe onto every post without checking other views.

Supplementary lead (search result found, image not yet inspected by root):
https://flickr.com/photos/jonncrisp/53570085357/ (dated 5 March 2024).
Existing source links also include King's Gardens council material and heritage
entry1001535. Historic reconstruction/restoration dates do not replace current
visual evidence. Keep all working reference images private; source links only
in Git and no photographic textures in distributed assets.

## Phase 1: evidence, layout and measured profile

1. Inspect actual Google Maps 3D from both shores and both sides; obtain an
   overhead view with scale. Gather ground-level Street View/Maps photos and
   Mapillary or other photographs showing gates, rail panels, lamp fittings,
   centre span, island banks and underside. Record loaded views, capture dates,
   missing coverage and contradictions; black pages are not inspected imagery.
2. Trace both islands individually from imagery. Record tip locations, maximum
   widths, necks and bridge intersections relative to the registered shore ends.
   Do not mirror or stretch one generic island to stand for both. Distinguish the
   vegetated crown, bank toe/waterline, hard retaining edges and trees overhanging
   the water. OSM outlines and shadows are not automatically shoreline evidence.
3. Create a station table along the crossing: shore thresholds, supports/abutments,
   island crossings, slope changes, central crown and gates/landings. Record deck
   width, rail height, clear opening, underside/deck thickness and water clearance
   as measured ratios or explicitly bounded estimates. Separate water, island
   ground, deck and lower access levels. Establish whether the apparent hump and
   changes in alignment are structural or merely viewing perspective.
4. Use simple editable slopes and purposeful breaks. Preserve the user's rough
   height strategy: no fine DSM draping, no artificial lumps in paved approaches,
   no attempt to reproduce photogrammetric ripples. Preserve a consistent water
   level and credible bank transitions. Ground changes stay bounded to the task.
5. Build and render only the measured main shapes first. Submit overhead and two
   opposing profile/oblique comparisons to root before final decorative repetition
   or expensive packaging. Continue independent fitting prototypes while reviewed.

Acceptance: different island outlines agree with aerial landmarks; bridge profile
and spans agree with side evidence; approaches connect without floating edges;
water remains water, not a walkable filled plane. Main-form discrepancies must
be fixed before calling the layout ready.

## Phase 2: bridge craftsmanship and island treatment

### Balustrades and posts

Build one representative panel from the photo: shaped base rail and handrail,
turned baluster profile, correct spacing/count per panel, panelled square piers,
plinths/caps and their relationship to green lamp columns. Use a measured section,
not cylinders or rectangular pickets at Detail. Follow the actual deck gradient
with consistent panel ownership and credible changes of angle. Inspect end panels,
island junctions and central span transitions before repeating the prototype.

### Lamps and gates

Research the green column silhouette: pedestal, shaft taper/flutes if visible,
rings/capital, bracket and light head. Record post locations and differences in
present/missing fittings by dated view. Avoid generic streetlights from a different
street. Show a close reference/model comparison of one complete lamp.

Identify every gate's actual location and purpose, including any side gates onto
islands or maintenance access. Model opening, gate leaf construction, posts,
hinges/latch and approach/landing where visible. Do not add a speculative cross-
bridge barrier because the task mentions gates. A closed gate must not float
above its landing or lead into water. Unknown access construction remains explicit.

### Deck, structure and materials

Use the observed transverse board direction, plausible board width/joints and
restrained texture scale. Geometry for important edges, nosings and slope breaks;
fine board seams can become texture at distance. Research underside, supports
and abutments from side images; don't leave an unexplained floating ribbon.
Use cream painted balustrade and green fittings from the selected dated state,
with restrained material variation rather than fabricated grime or ornaments.

### Islands

Shape the two islands with broad measured crowns/banks, credible grass/soil/stone
transitions and evidenced planting masses. Remove the current arbitrary bright
vertical perimeter strips where they do not correspond to a hard retaining edge.
Preserve erosion or retaining construction only where visible, not inferred from
low-resolution 3D noise. Do not populate decorative wildlife or unrelated park
furniture. Island access paths/steps, if present, must meet the gate landings.

Acceptance: normal eye-height view along the bridge, one complete balustrade
panel, one lamp, each gate, both island banks and a side/underside view all have
usable reference/model comparisons. Both shores must be recognisable and connected.

## Phase 3: ownership, LoDs, tests and acceptance

Prefer a separate bridge asset if that provides clean detail/LoD ownership, while
island ground/water holes remain with the existing public-realm owner. Whichever
layout is chosen, remove corresponding old deck/rails/underside in the same
publication: do not leave duplicate support surfaces or a hidden solid parapet.
Update water cutouts and island land together; retain neighbouring shoreline seams.

Define fixed District mesh/texture budgets before implementing its envelope.
Distant representation must preserve spans, hump/profile, island silhouettes and
major lamps/posts. Walk retains the characteristic balustrade rhythm, gate openings
and usable deck; choose per-feature reduction. Detail may use lathed balusters;
coarser substitutes must not close the main visual openings into a solid wall.
Baking should follow actual replacement surfaces, not serve as an excuse to flatten
all structure. Avoid texture sizes or coarse topology growing with decorative detail.

Required checks: finite/nondegenerate exports, surface ownership/coplanarity within
and between affected assets; all shore/approach/island seams; no deck/ground/water
duplicate faces; bridge and lower-route walking support stay distinct. Test walks
from each shore across every slope break, and a lower camera beside/under the span
without snapping onto the bridge. Check both island waterline joins in all LoDs.

Deliver incremental root reviews: (1) layout/profile, (2) completed fittings and
banks, (3) published all-three-LoD assembled scene. Confirm the actual target tiles
are loaded in captures; no inside-mesh/black/off-target screenshots as acceptance.
Keep the snag in progress until independent root review passes. Passing tests or
publishing a skeleton is not completion. Fix review findings and resubmit.

Preserve other agents' source changes. Coordinate catalog publication with the
BHS revision agent; package-only work may run independently. One Blender process
per worker, threads4, freeze source during bakes, use project runner locks. Scoped
commits authorized, no push. Record elapsed time, rework, checks, final per-LoD
triangle/download/GPU sizes and unresolved estimates without invented token costs.
