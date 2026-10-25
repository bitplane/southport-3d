# Stanley Street / Bath Street block plan

The two `southport.stanley-street` assets establish the block behind Lord Street,
from Nevill Street to Bold Street. Twenty-four neutral volumes reserve the
unmodelled external building outlines. Three independently streamed ground
sections provide Stanley Street, Bath Street and the connecting Bold Street
section, narrow public footways, private paved courts and planted reservations.
Flat building tops are provisional height bounds, not reconstructed roofs.

## Evidence and registration

The source records retain attributed OSM outline seeds, compared with a
geographically calibrated north-up aerial and two previously captured Google
Maps 3D obliques. The aerial reveals the long southern Stanley terrace, individual
Bath houses, deeper club ranges, gardens, forecourts and lower rear outbuildings.
Broad height changes divide the long terrace; the divisions are not cadastral
claims. Existing canonical Lord/Nevill outlines take precedence and are subtracted
from the new volumes, avoiding duplicated wings.

July 2026 Stanley/Bold Street View and August 2024 Bath/Bold views establish
narrow footways, rounded junction corners, double yellow edge lines and the
south-Stanley/west-Bold parking arrangement. Bath's large private forecourts
remain separate from its narrow public pavement. The materials, parking endpoints
and garden extents are approximate dated interpretations. The initial research
session could not load live 3D Earth, so retained 3D captures provide context;
this pass does not claim a fresh complete orbit or detailed elevation survey.

Plan offsets are approximately 1–2 m uncertain and heights 2–4 m uncertain.
Building ornament, actual roof shapes, private garden layouts, walls, street
lamps and other furniture await individual modelling passes. There are no copied
reference-image textures. Paving maps are small authored repeats.

## Surface ownership and seams

The existing Lord corridor owns the area below site Y=65. Exact Nevill side-road
mouths and authored forecourts remain with their existing owner. New ground
subtracts these areas and every existing/new building outline. The cut geometry
therefore leaves access space without laying a second floor beneath buildings.

Roads and paint derive from the same continuous road union. Rounded junction
returns are offset before clipping into the three sections; section boundaries
never become kerbs or painted lines. Double yellows continue across the Nevill
Stanley/Bath stubs. Broken white lines denote parking edges, not a central lane.
Give-way bars at the western Stanley/Bold approach are dimension estimates.

Material polygons replace one another in plan; paint does not float above an
uncut asphalt face. Shared boundaries are conformed before grading. Nevill stub
end vertices match the existing owner's 0.1 mm export grid to prevent independent
float32 rounding from creating overlap slivers. Physical kerbs remain at every
level. The interior grade is estimated but matches the neighbouring boundary
datums; it is not a surveyed terrain model.

## Viewing levels and checks

All levels retain the fixed block-plan geometry. Future detailed buildings will
replace these placeholders rather than grow their complexity. Ground textures
reduce from 256 pixels to 128 and 64 pixels; geometry stays fixed so pavements,
access gaps and seams remain stable.

The published area has 7,293 triangles at each level (444 for the volumes and
6,849 for the ground). Including embedded textures, it transfers approximately
1.29 MB at Detail, 1.18 MB at Walk and 1.16 MB at District, across 27 parts.

Validation checks closed positive building volumes, their retained footprint
vertices and floor contact; 559 road samples, footprint exclusions, narrow
footways and surface ownership; finite nondegenerate float32 triangles and
same-facing coplanar overlaps. Exported Detail/Walk/District probes cover 51
samples across internal sections and Nevill/Lord joins. The published-neighbour
audit finds no Stanley-related overlap at any level; pre-existing unrelated
neighbour findings are outside this task.

The Blender plan and assembled viewer overview were compared with the aerial
and retained 3D captures. The viewer was checked with all 27 new parts actually
loaded at Detail, Walk and District. Research links, measurement inputs and
remaining uncertainties are in each asset's `research/` directory. Private review
captures and audit reports stay outside Git in `../output/stanley-quarter/`.


The October 2026 yard repair beside Nevill 16–22 replaces only the bounded
courtyard colour mask with dark service asphalt, cuts out the observed rear
projection and Willow shed footprints, and keeps the delivery lane open.
The existing public-realm asset remains its sole ground owner. New probes check
three supported yard points and both building exclusions; the full road,
footprint and coplanar ground checks also pass. Levels remain estimates.

Actual published GLBs were reviewed together with both buildings, frontage
placeholders and Embassy at Detail, Walk and District, from the saved report
camera and a clear elevated oblique. A disposable local comparison avoided the
town-wide forced Detail cache limit; screenshots and comparison files remain
outside Git. A 19 m exported-ground route at site x=24, y=103 down to84 had
96 supported samples at every LoD, with a largest adjacent height change of
0.1171 m. This is a geometric support check, not a surveyed access assessment.
