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
major silhouettes and entrances while baking surface appearance.

Build and render:

```sh
python3 tools/project.py build southport.lord-street.christ-church
python3 tools/project.py build southport.lord-street.christ-church --stage render
```

The geometry validator checks all four tower walls have actual window openings,
eight belfry windows, three roundel windows, an open main doorway in the masonry, a closed
tower roof deck, five tall modern side windows, finite UV meshes and site bounds.
Evidence includes August 2024 cafe-side Street View, May 2011 south-garden
Street View, aerials and supplied rear photographs. Later three-direction 3D
views resolve the cafe/porch relationship, without establishing hidden joints.
The cafe sign uses DejaVu Sans to ensure glyph coverage. Checks cover cafe wall
closure and the stepped flat roofs/rooflights. Tower merlons begin at the parapet
base top, avoiding duplicate coplanar outer faces. Fine tracery and weathering
remain interpreted rather than surveyed.

## Café 1821 and porch

Private report 233407 supplies a mapped aerial and a clear May 2026 frontage
photo. They establish the quarter-round corner, buff lower brickwork, weathered
vertical metal fascia, full-height white-framed glazing with opening top lights,
central paired doors and the two-line café/1821 sign. The small porch stands separately
beside the round corner, with its ridge below the café cap. August 2024 Street
View and the 10m scale in the aerial support an estimated 2.9m-wide, 4.9m-deep
porch: a long ridge towards the recessed doors, a timber gable towards the garden,
and two brick piers with pale caps supporting a continuous timber beam. Estimated
roof soffit/eaves/ridge heights are 3.02/3.12/3.87m above the building base; roof pitch and hidden
connections remain uncertain. Its sides are open passages, not missing walls. A full-height hall return closes the former gap above the annex.
The image carrying a Dola AI watermark was not used to infer interior detail.
No interior, temporary posters or photographic texture pixels were reproduced.

The porch has a thin folded roof, recessed horizontal timber gable boarding,
reddish stained verge/side fascia, and buff stone caps. Slate courses follow the
ridge at approximately 0.30m slate width and 0.20m course exposure. These details
follow the August 2024 close Street View; board widths, shell depth and colours
are estimated. Fresh three-direction Google 3D views confirm the small projecting
roof and its relation to the cafe; they do not resolve timber joints.

Detail and Walk retain the rounded envelope, cladding seams, porch and glazing.
District uses its own coarse curved frontage and porch receiver; fine trim and
lettering bake into the shared atlases. Validation checks clear
glazing rays, separated cafe/porch roofs and closure of the exposed hall return.

## Historic frontage and rear hall

Four private reference captures show the front, side-door tracery and cafe-side
stair (one capture labelled June 2018). The stair is on positive site X, with a separate octagonal slate cap. The diamond features contain four-spoke round windows, not
clocks. They now have actual circular wall apertures and recessed glazing.
Burgundy door leaves, upper side-door glazing, blind gable tracery, inner-window
stone aprons, sloping battlements and buttress weatherings/niches follow those
photos. Fine spandrels, lights and crocket buds are interpreted exterior relief,
not scans; metric sizes and hidden rear features remain estimates. The authored
rubble texture uses irregular narrow courses; no reference pixels are published.

Walk reduces roundel curve sampling while retaining openings, doors and major
relief; fine leading/lights are Detail-only. District follows the independent
envelope below.

The rear modern range is transverse and gabled: its ridge meets the main hall
ridge at a T junction. A closed roof union preserves the valleys at every LoD.
The west gable has a circular cross-mullioned light, tall glazed entrance, two
narrow slots, pale coping and capped brick piers. Six recessed rear windows and
two pale string courses follow the supplied photographs. Exact heights, hidden
east-end treatment and small dimensions remain estimates. Walk retains these roof and opening meshes; District uses its own envelope. Source captures remain in the private snag
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

Retained Detail/Walk comparisons with the supplied wing close-ups cover elongated
tracery, connected leading, door stiles and lower panels. Scoped overlap checks
cover the repaired wings; they are not a whole-asset certification.

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
Assembled viewer review covered the saved wing-snag viewpoint and all three
resident levels without failed loads. Fine carving, glazing beyond observed
leading and metric dimensions remain interpreted rather than surveyed.
