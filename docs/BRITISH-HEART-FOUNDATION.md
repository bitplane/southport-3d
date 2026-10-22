# British Heart Foundation, 116 Lord Street

The building continues the Lord Street frontage from 118–122 towards Christ
Church. Select **116 Lord Street — British Heart Foundation** in the viewer.
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
-76.68; the southwest edge is registered against the OSM church boundary. The thirteen-module count is established by the user-supplied unobscured Street View screenshots, correcting the earlier count of fourteen. The rear envelope and church-side attachment still need a measured survey; no Chapel Street elevation is implied. Roof feature positions are now calibrated from close Google/ Airbus satellite views within the existing estimated envelope.

Architecture, roof and shopfront stream separately. Walk keeps the inexpensive
window grid and entrance geometry and bakes lettering/emblems to 512-pixel
panels. District replaces repeated window/spandrel modules with one shared
256-pixel baked prototype and omits handles/downlights. Detail alone carries tiny threshold grout geometry; Walk retains the stepped envelope. Wall openings, red
piers, entrance recess and roof silhouette remain physical. No global
mesh-decimation ratio is used.

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

Measurements after the facade and rooftop passes:

| Level | Placed triangles | GLB bytes including maps | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 33,790 | 4,529,656 | 1,479,745 |
| walk | 12,542 | 2,646,348 | 1,655,586 |
| district | 1,798 | 640,816 | 366,066 |

The initial pass passed all nine GLBs and window bake checks. Its browser review covered Walk and
District front/oblique views and automatic Detail at the entrance; all 31 scene
parts loaded without errors. Twelve Python checks and viewer policy tests passed at that point.

The 2026-10-22 exterior review used the archived full facade, close BID entrance, Geograph and aerial captures. It corrected tile aspect/scale, glazing reveals/seals, panel retainers, the single welcome board, circular downlights and smaller door fittings; smoothed the hand-authored pulse emblem; and removed unsupported roof boxes. Fresh master validation and front/oblique/entrance/upper-window renders passed. Combined-viewer and reduced-level review passed in the coordinated publication pass. The thirteen upper modules are now visible in the supplied full-front screenshots; opaque glazing and the church-side/rear envelope remain deliberate limitations.

The coordinated three-building publication passed all nine GLBs for this asset
and its bake checks. Browser review covered automatic close-up Detail and forced
Walk/District front and oblique views. All 31 combined scene parts loaded without
asset errors. Thirteen Python tests and the viewer policy test pass.

The rooftop pass uses the close satellite view and elevated panorama together.
It replaces the featureless slab with stepped brick parapets and coping, three
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

Walk retains the coarse housings, parapets, recess and plant cabinets plus fan
rims, rails and vents. District keeps the low-cost roof envelopes and cabinet
silhouettes but omits the rails, fan rims and small vents. Fine fan guards and
cabinet seams are Detail-only, as are the tiny threshold joints. The recess is
an actual opening in four disjoint roof fields with a lower external floor;
a validation ray checks it has not been filled by the former slab. Roof rear,
roof plant and plan renders support top-down and oblique review; the viewer
has **Roof plant** and **Roof rear** presets.

The terminal-bay/rooftop publication pass passed master validation, fresh
renders, all declared GLBs and bake coverage checks. Browser roof review
covered Walk and District; thirteen Python tests and the viewer policy test
also passed.

The user-supplied Street View screenshots received on 2026-10-22 supersede the
older distant frontage interpretation. They establish TWO entrances: a narrow
left doorway reached by the raised side ramp, and the central recessed doors
between projecting faceted display windows. The ramp includes its sloping
walking surface, black retaining cheek and red rail. The central threshold has
two dark tiled risers and a deep landing; the right display has a separate pale
stepped apron. Two distinct welcome panels and their visible text are retained.
The upper elevation now has thirteen modules, with procedural small green mosaic
tiles rather than aggregate noise. The completed rooftop geometry is unchanged.

The building-owned ramp reaches local Y -22.06; the public-realm pavement is its
underlying approach. These raised surfaces must not be replaced with duplicate
flat pavement. The image `screenshot-20261022-104131.png` explicitly displays
August 2024. The other three supplied images lack a date panel, so their date is
not asserted. Private filenames and observations are recorded alongside a Google
Maps location link; none of the screenshots are committed or used as textures.
The recess/projection topology and step count are observed, while metric sizes,
ramp slope and some door subdivisions remain estimated. Both recesses and the
ramp/railing remain physical at all three LODs. Fine hardware and threshold grout
continue to follow their existing omission rules.

The access ramp and retaining cheek use outward mesh winding. A raised infill
closes the small gap between the ramp and recessed left doorway. Walking surfaces
use separate matte dark tiles; the polished vertical shop plinth is preserved.
These surfaces remain physical at every LOD.

## Screenshot correction pass publication budgets

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 44,386 | 5,356,664 | 1,349,971 |
| walk | 13,216 | 2,736,580 | 1,584,140 |
| district | 2,706 | 812,620 | 381,086 |
