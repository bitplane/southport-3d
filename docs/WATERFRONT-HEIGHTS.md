# Waterfront height reconstruction

The waterfront migration is integrated into the main town for ordinary snag
review. It does not establish the pier datum or certify every ground height. The reference is the
EA terrain/last-return surface survey, with the provisional memorial tie described
in [the elevation migration](ELEVATION-MIGRATION.md).

## Raster-derived surfaces

Waterfront ground now uses the shared 100 m editable controls described in
[rough town ground heights](ELEVATION-MIGRATION.md). Fine survey refinements are
removed. Roads and concrete areas use broad planar slopes; the old native-raster
error threshold is no longer a design target. Paving retains an authored 0.12 m
kerb allowance. Placeholder roofs stay level, with footings below the local grade.
The lower Marine Way promenade has its own rough 0.3 m local landing control,
separate from the elevated road; it must not inherit the upper road's broad plane.

Ground smooth normals allow the GLB exporter to share terrain vertices. Kerbs and
retaining faces remain separate hard-edged meshes. This reduces download/GPU cost
without changing surface positions, triangle-plane tests or walking support.

`elevation/survey/waterfront-decks.json` stores native DSM and DTM probes, the
source checksum, transverse sample offsets, coordinate frame and survey records.
The [EA last-return DSM](https://www.data.gov.uk/dataset/cf3f1137-c12b-44a1-a835-e80fe4a60b92/lidar-composite-dsm-2022-1m)
contains objects as well as ground. Deck medians use narrow centre strips; neither
vegetation nor the Marine Way pylon is treated as a road height.

The Venetian crossing has a central hump and lower approach spans. Its independent
DSM profile replaces the old flat 2.2 m plane. The deck continues over both islands,
with ground retained underneath; clipping it to open water produces missing spans.
End controls join the measured approach pavement. The provisional 0.30 m structural
depth and 1.10 m rail height are still estimates. Decorative bridge detail is deferred.

Marine Way's measured **reference** profile excludes stations 95–105 m around the
pylon/crosshead, interpolating between clean neighbouring deck samples. It now drives the published structural and road packages. Abutments and the
western retaining base meet the measured mainland. All three exported ground
levels pass 123 upper/lower support and lateral promenade checks; the three
structural levels pass exported coplanar checks. Approach centreline differences
from the terrain are centimetres, but their full-width retaining transitions
still require assembled visual review. Pylon heights remain older reconstruction
estimates and must not be described as surveyed. The inclined pylon shafts
continue to an authored -3.5 m local cut-off below visible water, preserving their
existing above-water inclination. This closes the exposed truncated legs; it
does not model or establish the concealed foundations or lakebed.

## Evidence and remaining breaks

Google Maps textured 3D was inspected from two rotated directions on 26 October
2026 around Funland, the pier entrance, Marine Way and the lower promenade. Private
captures are `../references/elevation/funland-3d-east.png` and
`funland-3d-west.png`. They show the upper forecourt, lower lakeside walk and bridge
relationships; they do not establish a stair count.

[Historic England's garden description](https://historicengland.org.uk/listing/the-list/list-entry/1001535)
identifies a roughly 1.2 m drop from Marine Walk to the lido, retaining walls beside
the raised Esplanade and access beneath the pier. Those sharp breaks can receive explicit
landing/step geometry when those features are modelled. The rough base is sufficient
for continued town mapping; a detailed terrain reconstruction is not required.
Funland landing levels, stair count, thresholds and under-pier clearance remain
estimates to check during the corresponding detailed work.

The working lake plane is 4.15 m ODN, consistent with interpolated raster values
over the lake. This is **not a measured operating water level**. It is a separate,
explicitly provisional control with 0.5 m uncertainty. Do not derive ground, deck
heights or pier geometry from it. The previous 0.6 m local water estimate is retained
in the superseded controls for comparison. A current level survey or suitable
shoreline reference is still needed to establish the water plane confidently.


## Funland source review

`python3 tools/audit_elevation.py --waterfront-reference` compares native DTM and
DSM along four recorded 110 m transects at 1 m intervals. Recipe, imagery links
and limitations are in `elevation/survey/waterfront-review.json`; generated JSON
and profile charts stay in `../output/elevation`. The 444 probes flag 122 sample
positions for review (surface separation of at least 1 m or an adjacent DTM
slope above 25%). These are triage flags, not 122 confirmed ground defects.

At site (-20, 340), DTM is about 3.33 m local and DSM about 10.20 m: this is within
the provisional Funland footprint. Neither establishes the building's floor.
At (0, 380), DTM is about -0.67 m and DSM 3.30 m, demonstrating competing levels
near the crossing; the lower value must not be substituted for the upper deck.
The open forecourt samples near (0, 300) agree around 3.22 m, which is a candidate
ground observation, not independent verification of its absolute elevation.

May 2011 Street View was inspected facing the arcade, forecourt and pier entrance.
It confirms their accessible paved connection, but the kiosk obscures the stairs.
A lower-side query returned no imagery. Stair count, lower landing registration
and current alterations remain unresolved. No ground or building was moved based
on these diagnostic flags. See the elevation guidance for separate evidence and
mesh-consistency acceptance.
