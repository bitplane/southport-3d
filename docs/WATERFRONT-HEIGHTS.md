# Waterfront height reconstruction

The waterfront migration is staged in the separate elevation review. It is not
ready to replace the main town or establish the pier datum. The reference is the
EA terrain/last-return surface survey, with the provisional memorial tie described
in [the elevation migration](ELEVATION-MIGRATION.md).

## Measured surfaces

Southern-lake ground uses the common 5 m terrain lattice, with sixteen bounded
refinements selected from actual owned-road errors: twelve at 2.5 m and four at
1.25 m. The old region-wide plateau and manually estimated parking access planes
are removed. All three LoDs retain the same ground. Public realm uses an explicit
0.12 m pavement offset; that remains an authored kerb allowance, not a kerb survey.
Placeholders retain level roofs and buried level footings.

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
pylon/crosshead, interpolating between clean neighbouring deck samples. It now drives the isolated structural and road packages. Abutments and the
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
the raised Esplanade and access beneath the pier. Those sharp breaks need explicit
geometry rather than the smoothed slope of a 1 m terrain raster. The measured
regional mesh is a foundation for that work, not a completed retaining-wall survey.
Funland's landing levels, stair count, thresholds and under-pier clearance remain
outstanding. Reconcile these before starting the pier model.

The working lake plane is 4.15 m ODN, consistent with interpolated raster values
over the lake. This is **not a measured operating water level**. It is a separate,
explicitly provisional control with 0.5 m uncertainty. Do not derive ground, deck
heights or pier geometry from it. The previous 0.6 m local water estimate is retained
in the superseded controls for comparison. A current level survey or suitable
shoreline reference is still needed to establish the water plane confidently.
