# Measured elevation migration

The raster-derived regional ground and placeholder packages are now integrated
through the ordinary town publication. Use the main viewer and snag queue for
remaining corrections; the separate elevation-review application is retired.
This integration does not certify the terrain as an as-built survey. Detailed
building thresholds, Eastbank/Tulketh layers and waterfront sharp breaks remain
open work. Waterfront correction is assigned to a background task; pier detail
remains deferred until its support levels are understood.

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
and published as connected regional packages. The first five have exported triangle-plane and ground-LoD
equality checks; Nevill retains its crossing, parking-recess and ownership probes,
and Chapel retains entrance-ramp and furniture-contact checks. Nevill upper-street
and Promenade renders have been inspected. These checks do not complete the
assembled-neighbourhood or detailed-building attachment review. Use ordinary
snags for remaining regions, waterfront level breaks and bridge corrections. Pier modelling remains
deferred.

For acquisition, use WCS 2.0.1 `GetCoverage`, the service and coverage ID in the
metadata, BNG `subset=E(...)`, `subset=N(...)`, and `format=image/tiff`. Obtain
`https://cdn.proj.org/uk_os_OSTN15_NTv2_OSGBtoETRS.tif` in the private reference
directory. Ordinary builds need neither PROJ nor network downloads.

```sh
python3 tools/audit_elevation.py
python3 tools/prepare_terrain.py
/usr/bin/python3 -m pytest -q tests/test_terrain.py tests/test_elevation.py
```

Review changes in the main viewer and record defects through its snag collector.
`publish --package-only --asset <id>` remains available for intermediate checks;
then publish corrected connected assets together with repeated `--asset` options.
The private baseline remains available for comparison, not as the active scene.


## Waterfront integration

Marine Drive mainland ground and placeholder foundations use the measured field.
Nine bounded 1.25 m refinements resolve sharp shore gradients that a uniform 5 m
lattice missed. The full ground validator checks 9,696 owned mainland road probes
against native pixels (maximum difference 0.2496 m), triangle planes, ownership
and a fixed 360,000-triangle regional budget. The current build has 355,097
triangles. The existing ownership audit records sub-millimetre numerical residues
separately; it does not certify every non-coplanar intersection.

Marine Drive and the southern lake are included in the main town, together with
the raster-derived bridge profiles.
See [waterfront heights](WATERFRONT-HEIGHTS.md) for deck evidence, provisional
water and the unresolved sharp retaining edges and Funland landing geometry.

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

Remaining connected migrations: Eastbank and Tulketh railway layers,
waterfront retaining breaks and landings, then all detailed
building foundations and entrances. Check neighbouring exported seams together,
followed by measured bridge deck/approach and underside-clearance corrections.
The regional elevation switch is published; pier modelling remains deferred.

## London Square and Glebe Place integration

London Square and Glebe Place now have isolated measured-ground packages in the
main town, making nine connected inland regions migrated. The square preserves its
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

The integrated main town now uses these regional packages. Eastbank/railway, the remaining
waterfront layers, detailed building attachments and bridges are outstanding.


## Waterfront package checks

Southern-lake public realm and placeholder foundations now use the common field.
Sixteen bounded refinements retain the 0.25 m native-road approximation limit.
Its 542,415-triangle package is about 21.74 MB per level; shared ground normals
reduce duplicate export vertices without altering terrain positions. This is
still a regional ground mesh, not the eventual simplified distant regional LoD.
All 517,267 checked exported ground triangles per level follow their named planes,
and ground arrays match exactly between levels. The Venetian deck is continuous
across both islands, with its measured central hump and independent terrain below.

Marine Drive's 355,097-triangle package is about 15.51 MB per level. Its 322,225
exported ground-plane checks per level pass within 0.000025 m. The structural
Marine Way exports pass all three coplanar checks, and 123 upper/lower road and
promenade support checks pass. These numerical results do not certify the sharp
shore retaining edges, every full-width approach join or Funland's stair count.
