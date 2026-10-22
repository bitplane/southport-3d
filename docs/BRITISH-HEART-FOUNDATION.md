# British Heart Foundation, 116 Lord Street

The building continues the Lord Street frontage from 118–122 towards Christ
Church. Select **116 Lord Street — British Heart Foundation** in the viewer.
Source lives in `regions/southport/london-square/lord-street-116/`.

The exterior includes the white cladding surround, fourteen repeated window
modules with green-grey spandrels, asymmetric casement bars, red tiled piers,
black plinth, deep glazed entrance returns, steps and transoms. Raised fascia
lettering and a hand-authored interpretation of the visible heart/pulse emblem
are separate bakeable panels. The entrance reads “WELCOME to BHF Southport”.
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
far end. The long rectangular rear envelope, roof fittings and church-side
attachment need further evidence; no Chapel Street elevation is implied.

Architecture, roof and shopfront stream separately. Walk keeps the inexpensive
window grid and entrance geometry and bakes lettering/emblems to 512-pixel
panels. District replaces repeated window/spandrel modules with one shared
256-pixel baked prototype and omits handles/downlights. Wall openings, red
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
visible window modules, unobscured sign centres, recessed doors and three steps.
Publication checks full-panel window bake coverage as well as ordinary GLB
validation. Rear geometry is explicitly provisional.

| Level | Placed triangles | GLB bytes including maps | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 18,360 | 2,369,880 | 846,179 |
| walk | 2,816 | 1,228,000 | 1,042,008 |
| district | 848 | 404,488 | 248,379 |

All nine GLBs and window bake checks passed. Browser review covered Walk and
District front/oblique views and automatic Detail at the entrance; all 31 scene
parts loaded without errors. Twelve Python checks and viewer policy tests passed.
