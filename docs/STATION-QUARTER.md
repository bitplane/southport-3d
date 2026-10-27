# Chapel Street and station quarter

This block plan extends the pedestrian route from London Street, past Southport
station, to the east pavement of Eastbank Street. Fourteen neutral volumes mark
the remaining Chapel frontages and station retail ranges. They are placeholders,
not reconstructed facades or roofs. Existing Town Hall, Atkinson/Primark and
London Street assets retain their ownership.

The two assets separate footprint massing from walkable ground and furniture:

- `southport.station-quarter.frontage-placeholders`: aerial-checked external
  outlines, split into broad roof ranges, with provisional height bounds.
- `southport.station-quarter.public-realm`: three independently streamed ground
  sections and three furniture groups, with open station, Corporation Street,
  Cambridge Arcade and Tulketh Street approach mouths.

The London Square asset gives up its former west asphalt stub at the Chapel
junction. The new paving meets the carriageway at site X=-4.3 m between Y=-150
and -138 m, and the retained London footways at X=-12.5 m outside that mouth.
A one-metre shallow ramp lowers the last paving strip by 120 mm to meet the
carriageway datum. Its exact run is provisional. There is no invented kerb or
yellow line across the pedestrian entrance. The
Eastbank end stops at its eastern pavement edge; the full highway scheme and
station platforms are outside this pass.

## Evidence and limits

The asset research records contain source links, dated observations, geographic
image controls and coverage gaps. Selected OSM outlines were overlaid on
calibrated Google aerials and checked against the visible external walls and
roof recesses. They are not assumed to be individual properties: in particular,
the station way combines retail, roof parking and platform structures. The
entrance passage is cut out of the ground-level volumes, with an elevated
placeholder above it. Rear court recesses remain open.

Google's 3D Earth view was attempted but unavailable on this host; the NVIDIA
driver did not respond. No photogrammetric roof orbit was achieved for this
pass. North and south aerials, the London mouth in August 2019, station approach
in June 2017 and Eastbank mouth in July 2026 establish the plan and pedestrian
character. Heights remain storey-based estimates, approximately ±2–4 m. Flat
upper surfaces represent bounds, not roof forms. Fine roof and rear architecture
must be researched before replacing these placeholders.

Grey slabs, lighter margins, dark furniture bands, curved lamps, slatted benches,
round planters and stainless entrance bollards are supported by street views.
Their precise spacing, counts and the simplified paving pattern are estimates.
All paving textures are authored; no reference pixels are distributed. The
common outer London Street datum of 0.7845 m is retained, with no claim of
surveyed longitudinal levels. Station refurbishment in 2026 does not establish
that the entire pedestrian street was repaved.

## Geometry and LOD contract

The placeholders have a fixed ceiling of 4,000 triangles and 250 KB per level,
with no textures. The initial fourteen volumes total 360 triangles. Detailed
replacements must declare `replace_with` on the corresponding block and author
an independent District envelope; adding facade detail must not inflate these
coarse budgets. Ground uses the same footprint records as hard exclusions,
except for elevated passage roofs, and therefore follows footprint corrections.

Ground surfaces are unioned, clipped and triangulated through the existing GEOS
plan helper. Route and furniture bands replace the base surface rather than
sitting above competing faces. The helper and neighbouring footprint records
are explicit build dependencies. Furniture is separate from ground ray casting;
its local generators reduce curved sampling and small fittings for Walk and
District. No whole-town ground mesh or shared architectural style is imposed.

At the former BHS arcade frontage, a bounded 2 m transition connects the rough
station surface to the higher building and entrance datum. It joins the separate
Chapel threshold and approach ground; its width and grades are estimates, not a
survey. The transition replaces the station surface in that strip.

The validators check closed positive placeholder volumes, exact retained plan
vertices, nondegenerate float32 triangles, coplanar overlaps, continuous walking
routes, station/arcade access, furniture contact and London ownership exclusions.
These checks establish geometry consistency, not survey accuracy. Private
comparison captures remain under `../references/station-quarter/` and
`../output/station-quarter/`.
