# Eastbank Street bridge canvas

The Eastbank assets extend the existing Lord Street/Chapel Street canvas to the
Scarisbrick New Road / Southbank Road roundabout. Fifty provisional building
volumes reserve the adjoining frontages, rear ranges and larger retail envelopes.
Roads, junction mouths, pavements and the short railway bridge are a separate
public-realm asset. These are replaceable footprint/height envelopes, not finished
building architecture. A single mapped range may contain several properties.

The geographic plan retains attributed OSM source geometry, compared against
loaded Google satellite imagery, four wider 3D rotations and four closer rotations.
The bridge was checked separately in a 150 m aerial view. August 2024 Street View
from 136 Eastbank Street shows the bridge parapets, slab footways, coloured edge
strip, double yellow restrictions and curved white lamps. August 2019 VR360TV road
panoramas cover the middle approach and roundabout approach. Private screenshots
are retained outside Git; source links and dates are in each asset's references.

The primary plan decisions are the continuous Eastbank alignment, the railway
opening, open side-street mouths, intact street-front footprints and the complete
roundabout ring with bounded exit stubs. OSM was used as a seed, not a survey.
Existing Lord and station-quarter volumes own their footprints; this asset does
not duplicate them. The Chapel pedestrian polygons remain with their existing
owner. New building geometry and ground both read the same named elevation plan.

## Elevation pilot

`regions/southport/elevation/eastbank.json` retains the existing north seam and
references the Chapel pavement control through an explicit include. The road
rises to a provisional 5.1 m pavement level at the bridge, then descends to 3.1 m
at the roundabout, relative to the memorial's estimated zero. Interior controls
have stated uncertainty up to 1.5 m. These figures describe a plausible relative
profile from visible slopes; **they are not measured road elevations**. Railway
cutting height is separately estimated at local zero. No engineering clearance
or structural design claim follows from this model.

Road and pavement share profile knots and separate vertical offsets. The cutting
is a distinct surface below the deck. Profile breaks are inserted before ground
triangulation, and all three viewing levels retain the same walkable geometry.
Building roofs/floors remain level; provisional bases meet the profile. This is
not a surveyed terrain surface for the entire rear of every property.

The first legacy migration is Chapel Street: its nine published ground GLBs
(three parts × three levels) have exactly unchanged vertex positions. Ground and
furniture now consume the shared record instead of repeating the entrance-ramp
formula. See [ELEVATION.md](ELEVATION.md) for the library and authoring contract.

## Review limits

Widths and footprint edges remain roughly ±1–2 m; building heights ±3 m. The
closer bridge aerial corrected an initially over-wide road/deck interpretation.
Bridge parapets are simple structural envelopes; mosaic panels, lampposts,
railway equipment, car-park markings and detailed shop fronts are deferred.
White/yellow markings cover the observed bridge stretch only. Side-road slopes,
rear courts, the precise crest and entrance levels need later measurement.

Validators check closed placeholder volumes and ground contact, building/road
exclusions, profile planes at triangle interiors, ground seams, coplanar surface
ownership, export budgets and identical ground across LoDs. The bridge's upper
and lower support levels are tested at the same XY position. Browser review also
checks both levels through actual tileset replacement; this does not substitute
for improving the evidence behind the height estimates.

The six-asset exported neighbour audit retains two narrow float32 boundary
slivers at the Chapel handover: Eastbank section-5 courts/paving against station
west paving, pair-area sums 0.000219 and 0.000135 m² at each level. These are
recorded numerical seam residues, not a claim of zero overlap. Two unrelated
pre-existing Lord Street ground candidates remain outside this change.

Run the published neighbour seam checks with
`python3 regions/southport/eastbank-street/public-realm/scripts/check_published_seams.py`.
It checks 30 probes across the three levels, including the intentional 120 mm
Chapel kerb step. The Blender validator also checks that step has a road-facing
vertical kerb, rather than an open edge between two owners.
