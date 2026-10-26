# South Marine Lake and seaward quarter block plan

Snag `a996ab166e984318922eac83b3b68781` requests the missing blocks in its
marked seaward view, further to the right, and the remainder of Marine Lake.
The saved camera and box project approximately to site X−821…−25 m,
Y 26…498 m; the right edge reaches about Y 1196 m. The selected Anchor Street
asset is unrelated to that geographic request.

The new `southport.marine-lake-south.public-realm` and
`southport.marine-lake-south.frontage-placeholders` assets cover the bounded
X−850…85 m, Y 65…930 m study, yielding the existing Marine Drive study and
actual neighbouring ground ownership. They connect Duke Street, Kingsway,
Coronation Walk, West Street and the Promenade with Kings Gardens, the southern
lake, Princes Park, western Ocean Plaza and the coastal road. The earlier
[Marine Drive pass](MARINE-DRIVE.md) retains the northern lake and its roads.
The independently detailed Marine Way Bridge retains its own structure and
profiles; this pass does not change it.

There are **76 neutral building envelopes**, **135 road/access source segments**
and **183 mapped paths**. Flat caps are approximate roof-height bounds. They
include the Royal Clifton group, western cinema/leisure block, Premier Inn,
Morrisons, Splash World and smaller park/service buildings. The petrol station
canopy is a raised slab, leaving its mapped road open underneath. Its supports
are deferred. Existing footprints and replacement buildings are not duplicated.
Two uncertain or out-of-scope seed outlines are omitted with reasons; conservative
access corrections retain their original outlines and removed areas.

## Evidence and measurements

Google Maps actual textured 3D was inspected from four opposing overview views,
four close lake/garden/Promenade views and opposing close Ocean Plaza views.
The investigation covered roof extents, side and rear groups, open approaches,
the hard southern lake edge, irregular Princes Park bank and raised Esplanade.
July 2026 Promenade and West Street panoramas, August 2026 opposing coastal
panoramas and an older November 2015 Ocean Plaza panorama were visibly loaded.
Older tenant signs are not reconstructed. Several user panoramas in the gardens
failed to load; their locations and failures are recorded. A Mapillary search
yielded no useful local coverage.

The attributed OSM axes and outlines are seeds checked against that imagery.
At zoom 18 the registered aerial scale is about 0.354 m per CSS pixel. Four
right-click latitude/longitude controls locate the Venetian footbridge through
the two islands; they replace the old aerial seed's lateral jogs. Its width is
estimated at 5.2±0.8 m from 14–15 pixels across the deck. Roof parallax, wall
visibility and flat-cap estimates leave typical footprint uncertainty 1–3 m,
width uncertainty 1–2 m and height uncertainty 2–3 m. Detailed elevations,
individual rides and the pier are outside this placeholder pass.

The [Historic England landform description](https://historicengland.org.uk/listing/the-list/list-entry/1001535)
corroborates the lowered lido, retaining boundaries and different northwest bank.
It supplies historic context, not a current height survey. Source URLs, dates,
coverage and measurement inputs are in each asset's research records. Captures
remain private under `../references/lake-south-*`.

## Ground, walls and support

Road, parking, paving, lawns, sand and courts form one ownership arrangement
before height evaluation. Paint replaces road faces. Buffered complete road
curves retain junction mouths; no kerb closes a tile cut. Building footprints
are removed from ground, with the elevated canopy explicitly exempted.

The formal lake edge has an estimated 5.5 m lower lido and 4 m upper walk;
the Princes Park bank keeps its irregular planted boundary and mapped path.
The lido top, exposed waterline face and upper retaining face have separate
owners. End ramp reservations connect the estimated levels. The Venetian bridge
is a separate support part above non-walkable water, continuing over the islands.
The later [Venetian Bridge and islands reconstruction](VENETIAN-BRIDGE.md) replaces its former rail envelopes with detailed open balustrades and bounded shore connections; precise abutments and levels remain estimated.

`regions/southport/elevation/marine-lake-south.json` includes the existing Marine
water control and owns bounded mainland, West/Nevill return, lido, Esplanade,
access and bridge surfaces. The datum is the memorial's **estimated local zero**,
not sea level. Upper park/bridge 2.2 m, lido 1.0 m and Esplanade crest 4.2 m are
estimates with explicit uncertainty. The inland Esplanade reservation shares
its road profile. A broad lower-garden access and three parking entrances use
bounded ramp planes, avoiding steps across the roads. Foundations meet their
named terrain; roofs stay level. Precise entrances and private boundaries remain
unresearched.

The original West Street floor ended through a mapped car park and Promenade
approach. The same parking and road polygons now extend into its existing ground
recipe, retaining old courtyard exclusions and suppressing invented parking bay
marks. Bank Passage has a short graded apron onto the retained Lord pavement.

The neighbour boundary interface records the last reviewed exported ownership
rings, including the updated Stanley yard. It preserves holes and excludes
interior material boundaries. A later neighbour boundary change needs a coordinated
interface refresh and repeat export review. The supplied published seam checker
is a repeatable check of that contract.

## Viewing levels and checks

Each building has a separate streaming part. The new public realm has 23 nonempty
ground cells, a separate Venetian support part, water and shore structures.
One empty northern cell is intentionally not published. The two assets therefore
publish 102 parts and 306 part/level files. Ordinary ground shares
`southport/south-seaward-ground`; bridge support uses
`southport/south-venetian`. Water and wall parts are not walkable.

The bounded canvas and placeholder buildings remain deliberately coarse. The Venetian Bridge now has separate Detail, Walk and District fitting geometry; see its reconstruction record. It has no photographic images or atlas. Declared per-level
budgets are 150,000 public-realm triangles (120,000 ground and 30,000 structure),
20,000 placeholder triangles,21 MB combined download and 45 MB estimated GPU data.
Added detailed architecture must replace a placeholder with its own independently
budgeted District representation.

| New assets per level | Triangles | GLB bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Ground, water and structures | 81,548 | — | — |
| 76 placeholder volumes | 2,008 | — | — |
| Combined | 83,556 | 4,984,700 | 4,480,932 |

The actual exported geometry arrays match across Detail, Walk and District.
Every master mesh enters the coplanar audit. Closed positive building volumes,
footprints, terrain contact, clear roads and triangle-interior profile agreement
are checked in ordinary builds. An exported master regression samples 9,732
supported road points at intervals no greater than 1 m and finds no step above
the viewer's 0.45 m walking threshold.

The actual three-level neighbour review passes 147 height probes, including Lord,
West, the Promenade and coastal handovers. Each complete selected-neighbour scan
retains older findings separately. The new assets have 489 internal and 91 neighbour
numerical candidates per level, totalling about 0.048395 m², with maximum explicit
intersection width 0.204 mm. Exact owners, triangle identities and intersection
locations remain in private audit files. These are bounded float 32/grid residues;
no positive-width architectural conflict is exempted. The 671 older candidates
remain in the review queue; this work does not certify the whole town as
mathematically overlap-free.

The two lake-water exports together cover the complete authored water outline
minus its islands:336,679.1548 m² in source and 336,679.1469 m² after export.
All 3,363 interior grid probes are covered at each level. Water remains at the
shared 0.6 m estimate and is non-walkable.

The saved snag camera and seaward oblique were reviewed against the references.
The lake silhouette, island bridge, frontage groups, open courts, main roads and
hard/soft shore distinction agree at the declared placeholder scale. Forced
Detail, Walk and District settled with no failed loads. Identical new contents
collapse to tiles labelled Detail at each requested level; separate exported
arrays were nevertheless checked. Upper walk, lido and bridge walking eye heights
were 3.9 m, 2.7 m and 3.9 m. The below-bridge view stayed at 1.6 m, without snapping to the bridge. Short keyboard movement down the parking ramp lowered the eye from 4.538 m to 4.344 m, with no failed loads or pending tiles afterward. Fine landform, precise plot walls, decorative rails,
architectural roofs and current small site changes remain the limits above.

Private review artifacts are under `../output/lake-south/`; ordinary renders and
build reports are under the three affected asset build directories. Repeat the
published checks with `scripts/check_published_seams.py` and
`scripts/check_published_water.py` from the new public-realm asset directory.
