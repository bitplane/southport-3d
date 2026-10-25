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
