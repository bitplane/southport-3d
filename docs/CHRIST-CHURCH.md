# Christ Church, Lord Street

Asset `southport.lord-street.christ-church` registers to the existing church-gardens
frame, using OSM way 371202092. It contains architecture only. Garden paving,
walling, trees and street furniture remain in the separate gardens asset.

The present building retains a Gothic stone frontage and a square battlemented
tower. The former spire is deliberately absent. The model includes paired
pointed belfry openings and louvres, geometric tracery, diamond round-window surrounds,
recessed pointed doors, stepped buttresses, a projecting octagonal stair turret,
flanking gables and the rebuilt red-brick hall/cafe behind the historic front.
The cafe-side middle tower window is blocked masonry, as visible in the close
reference photograph. The front middle window retains muted glazing.

Source links and image dates are in `research/references.json`. The footprint is
mapped; heights, roof pitches, opening sizes and relief depths are calibrated
estimates. Photographs establish the frontal composition, modern tall side
windows and the turret. Fresh satellite inspection establishes the main hall hip and three stepped flat cafe/annex roofs with rooflight arrays. Concealed
rear openings are omitted; no interior has been invented. Reference photographs
are not stored in Git or embedded in textures. Stone, brick and slate maps are
deterministically authored materials.

The structural envelope, roof slopes, battlements, buttresses, window recesses
and coarse mullions stay geometric at all levels. Walk and District regenerate
Gothic curves and round-window circles with fewer samples. Fine diamond leadwork,
small quoin skins and downpipes are omitted in the reduced levels. Tiny entrance
crockets are selectively simplified at Walk and omitted at District. No global
decimation is applied, and no solid-box proxy fills Gothic openings. The opaque
materials are shared with the master, so curve simplification does not replace
stone with a differently coloured bake. District reduces authored texture sizes
to 256 pixels; Walk uses 512.

Build and render:

```sh
python3 tools/project.py build southport.lord-street.christ-church
python3 tools/project.py build southport.lord-street.christ-church --stage render
```

The geometry validator checks all four tower walls have actual window openings,
eight belfry windows, three roundel windows, an open main doorway in the masonry, a closed
tower roof deck, five tall modern side windows, finite UV meshes and site bounds.
Fresh isolated-browser inspection checked August 2024 cafe-side Street View, May 2011 south garden Street View and satellite roof coverage. It corrected the initially inferred annex hip to stepped flat roofs. Google 3D Earth was unavailable, and no direct rear elevation was obtained. Global publication and combined-viewer placement are coordinated by the root agent during parallel work.

The standalone streaming package preflight classifies every mesh for all three
levels. Exported front and oblique renders were inspected at Detail, Walk and
District: openings, battlements, roundel windows, stepped roof silhouette and material
colours remain consistent. The package is approximately 70k / 43k / 34k placed
triangles and 4.8 / 3.3 / 3.0 MB (embedded textures included). These are building
levels for the current viewer, not a town-distance proxy; a later regional bake
can reduce the still-geometric Gothic window tracery further.

Fresh browser setup also exposed two issues fixed before handoff: the cafe sign
needed an explicit installed font to avoid missing-glyph boxes, and the old high
annex gutter had to be removed after replacing its pitched roof. Cafe side-wall
closure and three flat-roof/15-rooflight checks protect the revised silhouette.
The sign uses DejaVu Sans from the existing system font installation.

## Independent reference audit

Front and side photographs were compared with exported Detail and District views.
The retained facade, paired belfry openings, bell tower and rebuilt hall remain
recognisable across levels. An actual rendering defect was found at the tower
crenellations: merlons overlapped the parapet base with coplanar external faces,
producing black horizontal marks. Merlons now begin at the base top without
changing their upper silhouette. Fine tracery and stone weathering remain
interpreted; photographs do not establish surveyed heights or hidden roofs.

## Café 1821 snag reconstruction

Private report 233407 supplies a mapped aerial and a clear May 2026 frontage
photo. They establish the quarter-round corner, buff lower brickwork, weathered
vertical metal fascia, full-height white-framed glazing with opening top lights,
central paired doors and the two-line café/1821 sign. The previous broad box and
three separate windows have been replaced. The small porch stands separately
beside the round corner, with eaves above the café cap; its pitch and dimensions
remain estimates. A full-height hall return closes the former gap above the annex.
The image carrying a Dola AI watermark was not used to infer interior detail.
No interior, temporary posters or photographic texture pixels were reproduced.

The rounded envelope, cladding seams, porch and glazing remain geometric across
all levels; low-cost 24-segment curvature is retained. The authored sign letters
and rules bake to a shallow receiver at Walk/District. Validation checks clear
glazing rays, separated cafe/porch roofs and closure of the exposed hall return.

## Supplied facade photographs (reports 87c169 / 53ae49)

Four private reference captures show the front, side-door tracery and cafe-side
stair (one capture labelled June 2018). The stair has been moved to positive site
X, with its separate octagonal slate cap; the unsupported turret on the opposite
side is removed. The diamond features contain four-spoke round windows, not
clocks. They now have actual circular wall apertures and recessed glazing.
Burgundy door leaves, upper side-door glazing, blind gable tracery, inner-window
stone aprons, sloping battlements and buttress weatherings/niches follow those
photos. Fine spandrels, lights and crocket buds are interpreted exterior relief,
not scans; metric sizes and hidden rear features remain estimates. The authored
rubble texture uses irregular narrow courses; no reference pixels are published.

Roundel curves regenerate with fewer segments at Walk/District; wall openings,
stair silhouette, doors and major stone relief survive. Small lights and leading
are Detail-only, while crocket/spandrel relief simplifies at Walk and disappears
at District. Earlier package-size figures above describe the original build.


The rear modern range is transverse and gabled: its ridge meets the main hall
ridge at a T junction. A closed roof union preserves the valleys at every LoD.
The west gable has a circular cross-mullioned light, tall glazed entrance, two
narrow slots, pale coping and capped brick piers. Six recessed rear windows and
two pale string courses follow the supplied photographs. Exact heights, hidden
east-end treatment and small dimensions remain estimates. These simple roof,
wall-opening and frame meshes stay geometric at Walk and District; fine fittings
retain the existing omission policy. Source captures remain in the private snag
queue, with provenance recorded in the asset research catalogue.

The annex-facing hall side and transverse gable form one wall whose top follows
the roof shell's underside. The flat annex decks and their west return share
x = −89.55 m, avoiding an exposed strip at the junction. Validation checks the
shared edge and roof clearance; these are construction joins, not new surveyed
dimensions.
