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
windows and the turret. Aerial and supplied rear photographs establish the intersecting gabled hall roofs and three stepped flat cafe/annex roofs with rooflight arrays. Evidenced rear openings are modelled; no interior has been invented. Reference photographs
are not stored in Git or embedded in textures. Stone, brick and slate maps are
deterministically authored materials.

Detail retains the full architectural source. Walk retains the structural
geometry with fewer Gothic curve samples and omits fine leadwork and fittings.
District uses the independent fixed-budget envelope described below, preserving
major silhouettes and entrances while baking surface appearance. Historical
District review notes later in this document describe the previous recipe;
they do not constitute visual acceptance of the replacement.

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
beside the round corner, with its ridge below the café cap. August 2024 Street
View and the 10m scale in the aerial support an estimated 2.9m-wide, 4.9m-deep
porch: a long ridge towards the recessed doors, a timber gable towards the garden,
and two brick piers with pale caps supporting a continuous timber beam. Estimated
eaves/ridge heights are 3.02/3.87m above the building base; roof pitch and hidden
connections remain uncertain. Its sides are open passages, not missing walls. A full-height hall return closes the former gap above the annex.
The image carrying a Dola AI watermark was not used to infer interior detail.
No interior, temporary posters or photographic texture pixels were reproduced.

Detail and Walk retain the rounded envelope, cladding seams, porch and glazing.
District uses its own coarse curved frontage and porch receiver; fine trim and
lettering bake into the shared atlases. Validation checks clear
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

The exposed front shoulder beside the cafe follows the main roof underside,
closing the former triangular opening above its rectangular eaves-height wall.
Its back face meets the cafe-side return without overlapping exterior end caps.
This is a construction closure on the existing estimated envelope, not a new
roof pitch or height measurement. Private snag 2a2a1aec and the supplied cafe
aerial establish the affected junction; August 2024 Street View was rechecked
for the cafe-side context. Ray checks sample the sloping closure and above-roof
clearance, and the adjoining wall skins receive a coplanar-overlap check.

## Wing doors and tracery

The four wing windows use paired elongated upper lights with cusped lower
heads, distinct from the tower's roundel pattern. Their glazing is recessed;
Detail carries continuous diamond leading, while Walk preserves the same
stone pattern with fewer curve samples and omits the fine lead. Both pointed
side doors have a centre stile reaching the head, lower panels, a rail at
approximately one third of the opening height, and joined arched timber frames.
These proportions come from the private supplied close photographs, with
measurements and coverage limits in
[the wing evidence record](../regions/southport/lord-street/christ-church/research/wing-joinery-review.md).
Carved cusp profiles, joinery depth and glass appearance remain approximations.

Tracery and timber branches are unioned before extrusion. The concave wing
gables are triangulated before aperture clipping; continuous masonry skins and
opening reveals replace the internal caps of individually extruded fragments.
The validator checks a complete wing prototype, including its two windows,
door, blind tracery and wall interfaces, plus both wing walls for coplanar
overlaps. It casts through the masonry apertures and checks that the
door stile reaches its pointed head. This is scoped protection of the affected
features, not a claim that every old tower ornament is overlap-free.

Actual Detail and Walk exports were compared with the close photos from private
snag 87c1696b1a404712a447b59ec406298a. Oblique views of both wings confirmed the
elongated tracery, connected leading, full-height door stile and lower panels.
The repaired masonry no longer shows diagonal fragment-cap lines beneath the
windows. Roof, footprint, tower-window family and ground are unchanged.

## Fixed-budget District envelope

The independent District mesh retains the tower and open battlements, inset main
and wing doors, Gothic wing skyline, staged buttresses, octagonal stair turret,
T-shaped hall roof, stepped annex and rounded cafe/porch. The two roof operands
are bounded analytic masses, independent of decorative mesh detail. Closed
window/louvre appearance and small rooflights are baked into shared atlases;
tracery, small ironwork and mouldings do not add receiver topology. Atlas sizes
are 512×256 historic frontage, 512×256 modern hall and 256×256 roofs. Existing
research estimates remain; visual acceptance belongs to the owner for this pass.

Current checked District export: **1,518 triangles, 638,008 bytes including
textures and 5,424,324 bytes estimated GPU memory**. Its fixed receiver topology
and atlas sizes do not grow with the new wing tracery. Sampled rays had no misses; actual bake coverage,
normals and export budgets pass. Receiver overlap candidates are limited to
13 float32 edge slivers below 0.00001 m²; visual acceptance remains with the owner.


The final uniform exported audit checks all three church representations. It
finds no coplanar overlap involving the revised wing windows, doors or blind
tracery, including their wall interfaces. The only wing-wall findings retained
are the two pre-existing downward-facing tower-buttress foundation contacts at
site elevation 0.58 m (approximately 0.0374 m² per side), buried at ground level.
Other older church components remain outside this snag's cleanup scope; the
full generated report is in `build/christ-wing-audit/`, not source control.
The assembled town was inspected at the saved snag camera with the new Detail
tile loaded, zero failed loads and the streamer settled. Moving outward loaded
Walk at about 66 m and District at about 239 m; both retained the church in its
block, and the distant view settled with no failed loads. Fine carving, glazing
colour/patterns beyond the observed diamond leading, and metric dimensions
remain interpreted rather than surveyed.
