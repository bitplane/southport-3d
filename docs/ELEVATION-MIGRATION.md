# Measured elevation migration

The whole published map is being moved from estimated grades to a common
measured reference before the pier is modelled. The existing town publication
remains the baseline until connected ground, foundations, furniture and bridge
approaches have been checked together. The separate terrain review does not
mean the town migration is complete.

## Reference and datum

`regions/southport/elevation/survey/terrain.json` describes the Environment
Agency 2022 composite DTM, source service, checksums, survey records, licence
and transformation. The downloaded 5 km square is BNG E331000–336000,
N415000–420000. Only numerical tiles needed around the map are source. Raw
TIFFs, the comparison DSM, index captures and OSTN15 grid stay in
`../references/elevation`.

Native raster spacing is 1 m. Contributing surveys report 0.15 m vertical
RMSE; this is not a guarantee for every interpolated pixel or kerb. Intersecting
metadata contains 28 September 2018 and 28 March 2019 acquisitions. Check dates
by survey polygon, particularly where current imagery shows newer construction.

Registration uses the publisher's WGS84 tangent frame, system PROJ with OSTN15,
and an affine BNG fit checked over a 5 km square (maximum fit residual about
0.015 m). This does not remove uncertainty in reconstructed footprint positions
or WGS84/ETRS89 alignment.

The provisional datum tie uses site XY `(±10.5, -4/0/4)` on the roads beside the
memorial, away from its steps. Subtracting existing road heights from DTM gives
local zero **6.485294 m ODN**, with a 0.0452 m spread among six samples. Samples
are retained in metadata. This is not a surveyed memorial benchmark. Do not
confuse ODN with chart datum or a tidal height.

Source tiles store millimetres as int16 plus an explicit validity mask, retaining
native 1 m sampling with at most 0.0005 m quantisation error. Missing coverage
fails rather than becoming zero or clamping to a tile edge. Bilinear sampling
reads neighbouring tiles across boundaries.

## Whole-map audit

`tools/audit_elevation.py` reads actual published ground GLBs in viewer coordinates.
It compares horizontal-area-weighted triangle centroids with DTM, writing a
report, point samples and image to `../output/elevation`. The initial audit covers
104 ground parts across 18 assets. It finds discrepancies; it does not certify
every stair tread. Large replacement triangles also need interior checks.

Several waterfront parts differ by metres; some inland streets are too low.
The Nevill centreline at site Y40 is about -0.53 m local; at Y260 it is +3.29 m.
A single copied linear grade cannot represent the area.

DSM can provide deck evidence, with explicit outlier review. At Marine Way Bridge
the pylon crosshead produces samples tens of metres above the road. DTM beneath
a removed bridge is not deck evidence. Interpolated water cells are not a
water-level survey.

## Migration contract

1. Retain an immutable published baseline outside Git.
2. Establish shared surfaces and ownership for a connected region. Keep roads,
   paths, islands, retaining faces, water and decks distinct. Use imagery to
   locate sharp breaks smoothed or removed by the raster.
3. Move placeholder foundations and furniture using the same surfaces. Keep
   floors, roofs and furnishings level/upright. Detailed buildings need deliberate
   floor anchors plus updated foundations, canopy posts, thresholds and steps;
   translating a building alone does not prove its entrances fit.
4. Use observed stair counts and independently established landing levels.
   Neither a 1 m DTM nor a convenient generator setting establishes riser count.
5. Adjust bridges after surrounding levels agree. Check beam depth and underside
   clearance; retain separate walking supports above and below each deck.
6. Check triangle interiors, native-survey error, shared seams, building contact,
   clearance and exported LoDs. Publish connected groups, not isolated tiles.
7. Begin detailed pier work only after terrain and bridge corrections.

The terrain mesh budget is independent of building detail. Choose spacing by
measured approximation error. The Hoghton pilot uses 5 m cells with a bounded 2.5 m service-access
refinement to keep owned road probes within 0.25 m of native DTM. Refinement
boundaries retain the coarse surface height, avoiding cracks at handovers. Explicit retaining walls and stairs still need separate geometry.
`conform(..., preserve_triangles=True)` avoids centroid fans on untouched triangles
while retaining inserted neighbour junctions. Legacy topology stays unchanged
unless its caller opts in. A 0.05 mm proximity weld is explicitly enabled in
the migrated planar canvases to prevent doubled-back fans at nearly identical
float32 junctions; the default legacy welding behavior is unchanged.

A survey surface can have an `offset_profile` with ordinary named controls.
This retains an authored dropped kerb or ramp while following the measured terrain.
Both the terrain lattice and the ramp breaklines split geometry. Chapel uses it
for the existing 0.12 m entrance drop; that drop is still an authored estimate.

## State and reproduction

The shared reference, bounded survey surface, numeric source checks, tile-seam
and mesh-plane tests, and whole-map audit are implemented. Hoghton ground and
placeholder foundations are the first isolated migration pilot, sharing
`elevation/hoghton.json`. Its authored 0.12 m kerb remains explicit: roads follow
the measured grid and paving is offset above it. This is not a kerb survey.
Hoghton, Leicester, Stanley, West Street, the Lord Street corridor, Nevill and
Chapel/Station ground and placeholder foundations have now been built and checked
as isolated packages. The first five have exported triangle-plane and ground-LoD
equality checks; Nevill retains its crossing, parking-recess and ownership probes,
and Chapel retains entrance-ramp and furniture-contact checks. Nevill upper-street
and Promenade renders have been inspected. These checks do not complete the
assembled-neighbourhood or detailed-building attachment review. Remaining regions,
waterfront level breaks and bridge corrections are pending. Pier modelling remains
deferred.

For acquisition, use WCS 2.0.1 `GetCoverage`, the service and coverage ID in the
metadata, BNG `subset=E(...)`, `subset=N(...)`, and `format=image/tiff`. Obtain
`https://cdn.proj.org/uk_os_OSTN15_NTv2_OSGBtoETRS.tif` in the private reference
directory. Ordinary builds need neither PROJ nor network downloads.

```sh
python3 tools/audit_elevation.py
python3 tools/prepare_terrain.py
python3 tools/create_elevation_review.py
/usr/bin/python3 -m pytest -q tests/test_terrain.py tests/test_elevation.py
```

The disposable local review is `/reviews/elevation/`: a toggle for the isolated
migrated region packages, measured terrain, optional
published-ground points, actual/exaggerated height scales and road orientation
guides. It is not the migrated town. Recreate it after publication if needed.

Use `python3 tools/project.py publish --package-only --asset <id>` to build and
check all three LoDs without changing the live catalog. Publish the connected
group normally only once its neighbours and detailed model attachments agree.


## Waterfront staging

Marine Drive mainland ground and placeholder foundations use the measured field.
Nine bounded 1.25 m refinements resolve sharp shore gradients that a uniform 5 m
lattice missed. The full ground validator checks 9,696 owned mainland road probes
against native pixels (maximum difference 0.2496 m), triangle planes, ownership
and a fixed 360,000-triangle regional budget. The current build has 351,499
triangles. The existing ownership audit records sub-millimetre numerical residues
separately; it does not certify every non-coplanar intersection.

This region is **not** in the published migration review or the main town yet:
its lake plane and bridge/approach profiles still have old levels. Those layers
must be reconciled before assembled review. Do not interpret a successful isolated
ground build as a usable waterfront publication.

The survey predates work at the Marine Lake Events Centre. Sefton's
[August 2025 earthworks update](https://www.sefton.gov.uk/mysefton-news/latest-news/marine-lake-events-centre-construction-moves-into-earthworks-stage/)
records ground lowering; its
[January 2026 update](https://www.sefton.gov.uk/mysefton-news/latest-news/vinci-announced-as-main-contractor-for-marine-lake-events-centre/)
describes a new ramp from Upper Promenade. Keep that construction reservation
provisional until current layout/level evidence is checked. The planning committee
report for DC/2022/01391 identifies AECOM's 17 June 2022 flood risk assessment
(MLEC-ACM-XX-XX-RP-W-OO2) and drainage strategy as potential level evidence; these
underlying reports have not yet been obtained. Lake water remains an independent
level, not an automatic interpretation of DTM interpolation over water.

Next connected migrations: London Square and its gardens/approaches, Glebe Place,
Eastbank and Tulketh railway layers, southern lake/park/esplanade, then all detailed
building foundations and entrances. Check neighbouring exported seams together,
followed by measured bridge deck/approach and underside-clearance corrections.
No main-catalog elevation switch or pier modelling has been performed.

## London Square and Glebe Place staging

London Square and Glebe Place now have isolated measured-ground packages in the
review, making nine connected inland regions staged. The square preserves its
explicit dropped kerbs, crossing ramps, planting offsets and upright furniture.
The reflecting pools remain level and cut through underlying road bases, rather
than letting the rising terrain emerge through their water. Long garden returns
and parking walls follow terrain breakpoints. Detailed neighbouring building
thresholds and the memorial foundation remain to be reconciled.

A bounded 20 × 45 m refinement behind the bank/Posting House resolves the service
lane depression. It samples the existing 1 m raster on a 0.625 m mesh; this adds
no survey information, but keeps interpolation error below the 0.25 m allowance.
The square's road-centroid maximum difference from native DTM is 0.2280 m.
All three exported levels retain identical ground. The current district package
is 122,502 triangles including furniture; regional aggregation is still separate.

Glebe's throat retains its explicit 0.12 m rise and fall, with ground and bollards
on the shared field. Its planar surface boundaries are conformed before lifting,
then float32 junctions welded within 0.05 mm. Collapsed split slivers below that
width are removed before they can become doubled-back triangle fans. The scoped
ground overlap validator passes without raising its overlap-area tolerance.

`python3 tools/check_elevation_seams.py` checks actual exported road surfaces on
both sides of the Glebe mouth and Nevill junction. All 21 pairs across three LoDs
agree within 0.000039 m after accounting for the real gradient and throat ramp.
This samples those seams; it does not certify every neighbouring asset boundary.
Package validators independently check 6,429 Glebe and 52,242 square road/ground
triangles per level against their declared planes. Overview and garden renders
are also reviewed because numerical height checks alone missed the old road
under the newly level pools.

The main town still uses its preserved baseline. Eastbank/railway, the remaining
waterfront layers, detailed building attachments and bridges are outstanding.
