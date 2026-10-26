# British Heart Foundation, 116 Lord Street

## District envelope

District uses `scripts/district.py`: a separate fixed-topology envelope,
not a reduction of the detailed mesh. Detail and Walk remain unchanged.

The 316-triangle envelope retains the two recessed entrances, display facets,
access ramp/steps, stepped parapets, roof recess and major rooftop masses. Four
condensers become one bank; fine rails, mouldings, frames and relief become
appearance rather than source geometry. The three atlas materials use base
colour, tangent-space normals and roughness: 512×256 architecture, 256×256 roof,
and 512×128 shopfront. Bakes run at four times each dimension then area-downsample;
this preserves thin window bars more consistently. No reference photos are baked.

Recorded District export: 316 triangles, 221,044 download bytes including
textures and 4,226,651 estimated GPU bytes. Consult generated package reports
for current measurements after changes.

Hard publication budgets are 430 triangles across three parts, 800,000 download
bytes and 5 MiB estimated GPU bytes. The actual meshes/embedded images are checked.
A regression changes the detailed window count from 13 to 1,300 and verifies that
the envelope geometry does not change. Major footprint/roof changes still require
an explicit envelope review. Projection coverage checks are useful heuristics,
not proof of correspondence; matching-camera visual inspection remains required.

Matching front, roof/rear and 70 m comparisons established the pilot's visual
acceptance. Close views deliberately lose fine lettering, frames and fittings.
Private baseline/comparison artifacts live under `../output/bhf-district-pilot/`;
`tools/create_lod_review.py` can generate a separate comparison page. This is a
review tool, not an additional town LoD.

## Building evidence and geometry

The building continues the Lord Street frontage from 118–122 towards Christ
Church.
Source lives in `regions/southport/london-square/lord-street-116/`.

The exterior includes the white cladding surround, thirteen repeated window
modules with green-grey mosaic spandrels, asymmetric casement bars, recessed glass with dark perimeter seals and spandrel retainers, narrow vertical red tiled piers,
black plinth, deep glazed entrance returns, steps and transoms. Raised fascia
lettering and a hand-authored interpretation of the visible heart/pulse emblem
are separate bakeable panels. The two entrances have distinct framed welcome boards; the central one reads “WELCOME to BHF Southport”. Circular soffit fittings, door hinges/closers and threshold tile joints are modelled for nearby inspection.
Glazing is opaque; stock displays, interiors and unreadable notices are omitted.

The daytime Southport Guide photograph and Bertie Cunningham / Southport BID
entrance photograph are the principal facade references. Google aerial and
street panoramas, Geograph and the wider Visiter photograph establish context.
Their URLs, credits and observations are in `research/references.json`; no
reference photographs are distributed or used in generated maps.

All metric dimensions are visually calibrated estimates. The site frame is the
same as the memorial and adjoining terrace. The front spans site X -50.8 to
-76.68; the southwest edge is registered against the OSM church boundary. The thirteen-module count is established by the user-supplied unobscured Street View screenshots. The rear envelope and church-side attachment still need a measured survey; no Chapel Street elevation is implied. Roof feature positions are now calibrated from close Google/ Airbus satellite views within the existing estimated envelope.

Architecture, roof and shopfront are separate parts. Walk keeps the inexpensive
window grid and entrance geometry, baking lettering/emblems to 512-pixel panels.
Detail alone carries tiny threshold joints. District uses the independent
envelope above; no global decimation ratio is used.

The public-realm asset owns the widened pavement approach through X -77,
tapering at X -80 towards the church. The building owns its entrance steps, raised access ramp and retaining cheek. Ground and building dimensions remain unsurveyed.

Build and inspect:

```sh
python3 tools/project.py build southport.london-square.lord-street-116
python3 tools/project.py build southport.london-square.lord-street-116 --stage render
python3 tools/project.py publish
chafa build/southport.london-square.lord-street-116/renders/contact-sheet.png
```

Validation checks finite meshes, packed textures, neighbouring bounds, thirteen
visible window modules, unobscured sign centres, recessed doors and two central risers. Rays from below also check that each downlight lens is visible rather than hidden behind the soffit.
Publication checks full-panel window bake coverage as well as ordinary GLB
validation. Rear geometry is explicitly provisional.

Close satellite and elevated panorama evidence support stepped brick parapets and coping, three
capped edge housings, a shallow external walled recess, an elongated pitched
rooflight/vent and the rear plant platform. Four circular-top condensers sit
alongside the larger pale cabinet, perimeter steelwork and a small terminal.
Scattered vent caps, a pipe cluster, flashing and authored felt laps complete
the visible roof surface. These are source-built shapes and procedural maps;
the satellite photograph is neither distributed nor projected onto the model.

The plan and evidence limits live in `research/roof-layout.json`. Satellite
outlines identify the housings, but do not prove they are access stairheads:
no doors, ladders or stairs have been invented. The rectangular recess's depth,
rooflight/vent function, equipment heights and railing construction remain
interpretations. Rear ownership boundaries and dimensions are not surveyed.

Walk retains housings, parapets, plant cabinets, fan rims, rails and vents.
Detail adds fan guards and cabinet seams. The roof recess is a real opening in
four disjoint fields with a lower floor, verified by a downward ray. The plan and
roof/rear renders expose its construction; District simplifications are above.

The user-supplied Street View screenshots received on 2026-10-22 supersede the
older distant frontage interpretation. They establish TWO entrances: a narrow
left doorway reached by the raised side ramp, and the central recessed doors
between projecting faceted display windows. The ramp includes its sloping
walking surface, black retaining cheek and red rail. The central threshold has
two dark tiled risers and a deep landing; the right display has a separate pale
stepped apron. Two distinct welcome panels and their visible text are retained.
The upper elevation now has thirteen modules, with procedural small green mosaic
tiles rather than aggregate noise.

The building-owned ramp reaches local Y -22.06; the public-realm pavement is its
underlying approach. These raised surfaces must not be replaced with duplicate
flat pavement. The image `screenshot-20261022-104131.png` explicitly displays
August 2024. The other three supplied images lack a date panel, so their date is
not asserted. Private filenames and observations are recorded alongside a Google
Maps location link; none of the screenshots are committed or used as textures.
The recess/projection topology and step count are observed, while metric sizes,
ramp slope and some door subdivisions remain estimated. Both recesses and the
ramp remain physical at all three LoDs; District omits fine rails. Fine hardware and threshold grout
continue to follow their existing omission rules.

The access ramp and retaining cheek use outward mesh winding. A raised infill
closes the small gap between the ramp and recessed left doorway. Walking surfaces
use separate matte dark tiles; the polished vertical shop plinth is preserved.
These surfaces remain physical at every LOD.

## Surface checks and rear coverage

Rooflight pitch faces must point upward; double-sided materials must not hide
inward winding. Checks also cover entrance closures, visible lenses and bake
coverage. Retained exported-model reviews cover front, close, roof/rear and
combined pavement approaches; they do not establish surveyed dimensions.

The Glebe Place court-facing side follows the private photos attached to snag
9648072a74f14fbfac2ad9c4483b92d7 (the close Street View frame is dated November
2020). It has exposed brick, pale lintels, barred and unbarred upper windows,
two black collection doors on raised landings, steps and rails, a roller door,
a low utility enclosure and rainwater pipes. Two previously detached roof-edge
boxes now continue down as brick shafts at the wall edge. Their top-down
positions remain calibrated estimates; their precise internal function is
unknown. The third, farther roof housing retains its earlier provisional form.
Court dimensions, window positions and landing heights are estimated from the
photos. Major geometry remains at all three levels; fine rails, pipes and shutter
ribs are omitted at District. No hidden rooms or unreadable warning notices
are invented.
