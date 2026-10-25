# Christ Church side court and Corporation Street

`southport.lord-street.christ-church-approach` fills the passage between the Town
Hall and Christ Church, the church’s brick-paved side court and raised planting
strip, and the unfilled northern section of Corporation Street. Church and
neighbouring building geometry remains separate and unchanged.

Actual Google Maps 3D imagery was inspected from three opposing headings on
25 October 2026. Two registered satellite captures retain pixel/coordinate scale
inputs at approximately 0.177 m per pixel. Loaded pedestrian panoramas from May
2011 show the slab passage, brick court, low red-brick wall and pale coping,
planting, slatted benches, bin, notice board and access posts. The aerial supports
the broad layout; current exact furniture positions are not established by those
older panoramas. Private images, overlays and review captures remain outside Git
under `../references/mapping-sol-trial` and `../output/mapping-sol-trial`.

The new ground excludes the exact retained church and neighbouring block
footprints and all five existing station-ground polygons. The station asset
already owns Corporation Street south of Y=-105 m. The church-gardens asset
hands over only X=-127.9..-117.4 m, Y=-29.72..-18.0 m, removing every old surface
layer in that polygon. This joins the side approach to the existing garden
without placing a second floor underneath it. The Town Hall-side path north of
Y=-29.72 remains with church-gardens; the photographed bin stands on that owner.

A continuous mitred wall begins at Y=-26 m, leaving the existing northern
cross-path and the side-court mouth open. The wall is estimated at 0.85 m high and 0.28 m wide,
with a pale projecting coping. The lawn rises to an estimated 0.45 m plateau and
falls toward 0.07 m edges; the cross-path remains flat paving between this lawn and the existing garden.
The inherited grade meets the station’s 0.7845 m datum south of Y=-36 m.

Two benches, a bin and the slim access posts reuse the existing metric furniture
families. Tree and hedge proxies retain controlled sampling at each level. A
restrained notice-board silhouette carries a blank panel because its lettering
is not established. These placements are estimates from dated views, not a
current survey or a claim about individual tree species.

Detail, Walk and District keep the bounded ground outlines, physical lawn edges,
continuous wall and open approaches. Furniture and planting use explicit reduced
family generators; no whole-area decimation or photographic textures are used.
The source declares triangle, download and GPU limits for each level, checked
against the actual exported files at publication. Ground and furniture stream in
separate court and passage parts so walking rays cannot follow a bench or wall.

Validation covers every new mesh, including repeated furniture/planting
prototypes, wall/coping and noticeboard interfaces. It checks access continuity,
exact footprint/station exclusions, furniture ground contact, finite triangles,
family reductions and coplanar ownership. The older garden has a separate
regression requiring the handed-over polygon to be empty. Exported neighbour
and seam checks complement the source checks; detailed architecture and current
furniture replacement variants remain outside this pass.

## Published review, 25 October 2026

The final package uses 13,377 / 5,385 / 2,797 placed triangles and 887,764 /
493,852 / 240,052 download bytes at Detail / Walk / District. The measured GPU
estimates are 4.74 / 1.42 / 0.44 MB. Texture caps of 256 / 128 / 64 pixels keep
this bounded area below its declared limits.

All 79 source access samples, 553 excluded-surface samples and 40 bench/hedge
support samples pass. The repeated coarse bench retains the existing family’s
outer shape; one union timber cross-section removes overlapping seat/back end
skins found only in the exported District representation. All three bench
prototypes now have explicit coplanar regressions.

The final exported audit has no finding touching this asset or the changed
Christ Church ground at any level. Other retained architecture/furniture
findings remain in the private report for separate review. All 57 exported
boundary probes pass. The assembled GPU viewer loaded all four new parts at
each requested level with no pending downloads or asset failures; pedestrian
views check the wall, cross-path opening, floor handovers and ground following.
Private comparison captures and complete audit outputs remain in the trial
output directory. These checks do not establish surveyed or current furniture
positions; the older pedestrian evidence and estimated levels remain limits.
