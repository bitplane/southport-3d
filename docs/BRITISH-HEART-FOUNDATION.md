# British Heart Foundation, 116 Lord Street

The building continues the Lord Street frontage from 118–122 towards Christ
Church. Select **116 Lord Street — British Heart Foundation** in the viewer.
Source lives in `regions/southport/london-square/lord-street-116/`.

The exterior includes the white cladding surround, fourteen repeated window
modules with green-grey spandrels, asymmetric casement bars, recessed glass with dark perimeter seals and spandrel retainers, narrow vertical red tiled piers,
black plinth, deep glazed entrance returns, steps and transoms. Raised fascia
lettering and a hand-authored interpretation of the visible heart/pulse emblem
are separate bakeable panels. The entrance reads “WELCOME to BHF Southport” on one framed transom board. Circular soffit fittings, door hinges/closers and threshold tile joints are modelled for nearby inspection.
Glazing is opaque; stock displays, interiors and unreadable notices are omitted.

The daytime Southport Guide photograph and Bertie Cunningham / Southport BID
entrance photograph are the principal facade references. Google aerial and
street panoramas, Geograph and the wider Visiter photograph establish context.
Their URLs, credits and observations are in `research/references.json`; no
reference photographs are distributed or used in generated maps.

All metric dimensions are visually calibrated estimates. The site frame is the
same as the memorial and adjoining terrace. The front spans site X -50.8 to
-76.68; the southwest edge is registered against the OSM church boundary. The
fourteen-module count is interpreted from oblique imagery with foliage at the
far end. The long rectangular rear envelope, church-side
attachment need further evidence; no Chapel Street elevation is implied. The second pass removes arbitrary equipment boxes: the aerial view establishes low rooftop features but cannot resolve their exact shapes or placement.

Architecture, roof and shopfront stream separately. Walk keeps the inexpensive
window grid and entrance geometry and bakes lettering/emblems to 512-pixel
panels. District replaces repeated window/spandrel modules with one shared
256-pixel baked prototype and omits handles/downlights. Detail alone carries tiny threshold grout geometry; Walk retains the stepped envelope. Wall openings, red
piers, entrance recess and roof silhouette remain physical. No global
mesh-decimation ratio is used.

The public-realm asset owns the widened pavement approach through X -77,
tapering at X -80 towards the church. The building adds only its entrance steps,
inside its footprint. Ground and building dimensions remain unsurveyed.

Build and inspect:

```sh
python3 tools/project.py build southport.london-square.lord-street-116
python3 tools/project.py build southport.london-square.lord-street-116 --stage render
python3 tools/project.py publish
chafa build/southport.london-square.lord-street-116/renders/contact-sheet.png
```

Validation checks finite meshes, packed textures, neighbouring bounds, fourteen
visible window modules, unobscured sign centres, recessed doors and three steps. Rays from below also check that each downlight lens is visible rather than hidden behind the soffit.
Publication checks full-panel window bake coverage as well as ordinary GLB
validation. Rear geometry is explicitly provisional.

Current measurements after the exterior review and coordinated publication:

| Level | Placed triangles | GLB bytes including maps | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 27,540 | 3,064,336 | 846,628 |
| walk | 8,824 | 1,554,376 | 1,022,469 |
| district | 820 | 387,880 | 234,873 |

The initial pass passed all nine GLBs and window bake checks. Its browser review covered Walk and
District front/oblique views and automatic Detail at the entrance; all 31 scene
parts loaded without errors. Twelve Python checks and viewer policy tests passed at that point.

The 2026-10-22 exterior review used the archived full facade, close BID entrance, Geograph and aerial captures. It corrected tile aspect/scale, glazing reveals/seals, panel retainers, the single welcome board, circular downlights and smaller door fittings; smoothed the hand-authored pulse emblem; and removed unsupported roof boxes. Fresh master validation and front/oblique/entrance/upper-window renders passed. Combined-viewer and reduced-level review passed in the coordinated publication pass. All fourteen upper modules remain an interpretation because foliage obscures the far end; opaque glazing and the church-side/rear envelope remain deliberate limitations.

The coordinated three-building publication passed all nine GLBs for this asset
and its bake checks. Browser review covered automatic close-up Detail and forced
Walk/District front and oblique views. All 31 combined scene parts loaded without
asset errors. Thirteen Python tests and the viewer policy test pass.
