# Prezzo, 128 Lord Street

## Fixed-budget District envelope

The independent envelope in `scripts/district.py` retains the chamfered corner,
three recessed street entrances, street mansard, nine dormers, six chimney stacks,
three pot groups and the stepped rear wings. Coarse landing slabs and six broad treads per flight
retain the open escape wells; fine treads, rails, aerials and small
hardware are omitted. Fine windows, stonework and signage are projected into
three shared atlas sets (architecture 512×512, roof 512×256, shopfront 512×128).
Metallic corner lanterns are explicitly excluded from the dielectric source bake.
Detail and Walk retain their existing recipes. Dimensions and rear uncertainty
are inherited from the reviewed model, not reinterpreted for the LoD rollout.
The owner handles visual acceptance; automated build, bake and budget checks remain.

Checked District export: **940 triangles, 492,920 bytes including textures and
7,438,424 bytes estimated GPU memory**, down from 25,708 triangles, 4,158,784
bytes and 26,036,018 GPU bytes. Geometry, bake coverage, normal maps, publication
budgets and the existing window/relief appearance check pass. Visual acceptance
remains with the owner.

Earlier modelling and review records below describe the source architecture and the former District implementation; the envelope policy above supersedes those older District recipes.

The first adjoining building uses the ordinary asset/publication contract:
`regions/southport/london-square/prezzo/`. No viewer changes or building-specific
publisher branches were needed. Select **Prezzo — 128 Lord Street** in the local
viewer; its bookmarks show the corner, Lord Street, London Street and roof.

The observed exterior has five Lord Street upper bays, three London Street upper
bays, a chamfered arched entrance, three upper storeys and a dormered mansard.
The reconstruction includes recessed sash windows, tall restaurant glazing,
Ionic-style fluted pilasters, quoin strips, window surrounds/keystones, the corner
window hood, stepped cornices and dentils, dormers, chimney stacks/pots and PREZZO
lettering. London Street has two large ground-floor glazed bays. Ornament is an
interpreted geometric approximation rather than an exact carving reproduction.

## Registration and evidence

The asset shares the square's WGS84 origin and 43.5293-degree site frame. The
corner follows the whole-block OSM way 371203985; that way does not separate the
individual restaurant building. Estimated lot limits and heights are recorded
in `research/layout.json`. Level floors start at the project's estimated 0.58 m
datum; dimensions have not been surveyed.

Evidence includes the January 2025 Google aerial panorama, Google satellite,
davidsong's July 2019 Mapillary sequence, and two undated property exterior
photographs. URLs, observations and limitations are in `research/references.json`.
No reference pixels are distributed or used as texture inputs. The square's
public-realm asset owns the adjusted corner approach and widened west London
Street pavement; the building does not introduce a second ground surface.

The stepped rear elevation now follows supplied November 2020 Street View;
its dimensions, occluded bases and some roof connections remain approximate. Glazing is opaque shading, with no interior model. Signage
reflects the reference photographs, not a verified current branding inventory.

## LOD decisions

Three streaming parts separate architecture, roof and shopfront. Walls and their
actual openings, corner arch, roof silhouette, dormers and chimneys are retained
at all levels. Shared mesh prototypes cover repeated windows, pilasters and signs.

Walk retains the sash meshes, reduces pilaster shaft/scroll sampling and omits
fine masonry skins and ornamental beads, and bakes raised lettering onto sign panels. District removes tiny
cornice dentils and pilaster scrolls, while replacing window detail with baked
planar receivers. Stone surrounds and wall openings remain independent geometry.
Window receivers deliberately flatten about 0.34 m of frame/sill/backing depth;
this is a geometric approximation, not a screen-space error guarantee. Their
base colour, tangent normal and roughness maps are baked without directional
lighting. Walk textures cap at 512 pixels; District caps at 256.

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 219,596 | 11,139,884 | 1,216,294 |
| Walk | 55,846 | 4,581,996 | 1,075,273 |
| District | 16,900 | 2,624,612 | 637,130 |

These are the building's three-part totals, excluding the street and memorial.
Walk's similar download size reflects retained architecture and baked-map cost;
there is no global decimation pass or claim of a final town-scale budget.

## Review and repeatable checks

```sh
python3 tools/project.py build southport.london-square.prezzo
python3 tools/project.py publish
python3 tools/project.py build southport.london-square.prezzo --stage render
chafa build/southport.london-square.prezzo/renders/contact-sheet.png
```

The validator checks finite geometry, UVs, packed textures, geographic bounds,
dormer/sign/chimney counts, and casts rays at all 44 window fronts. The ray check
guards against the error where a plausible window is obscured by a solid dormer
body. The final dormers have open cheeks and a recessed back, so glazing remains
visible. Meshes are triangulated before UV assignment/export for stable tangents.
All 233 meshes are classified at every level, and all nine publication GLBs pass
inspection. The model is rendered from both streets, the corner and above the
roof; the adjusted public realm also receives its normal full build and renders.

The publication now also runs `check_package.py` through the optional
`publication_checks` asset hook, including when reusing a package. This requires
at least 95% base-colour and roughness coverage for each full-panel window bake.
With the initial deeper sill, a 0.4 m projection cage left only 82–89% coverage, despite valid normal-map pixels;
a 0.6 m cage reaches the recessed backing and gives about 98.4% coverage. A regression
test reproduces the missed-colour-ray case. Failure prevents catalog replacement.
The unreadable London Street wall plaque is represented without invented text.

The initial browser review loaded all 25 combined scene parts without errors, exercised
forced Walk and District, and switched architecture/shopfront to Detail on a
close approach, then verified automatic roof Detail selection. The catalog includes the building without viewer-code edits.
Twelve host-Python tests and the viewer policy tests pass. A repeated publication
reuses all three asset packages and still runs the window-coverage check.
Local browser screenshots accompany the master renders under the building's
`renders/` directory; none are tracked reference or source assets.

## Roof correction pass

A farther-back January 2018 ground panorama, checked against the daylight
property photograph and January 2025 aerial, replaces the original uniform
chimney array. Six individually placed stacks comprise three capped stacks
(including the chamfer) and three tall terracotta pot groups. Lord Street rows
run into the roof along site Y; the London Street row follows site X. Pot counts
are interpreted as five per Lord Street group and four on London Street; hidden
flues and precise dimensions remain uncertain. Pots have collars and recessed
mouths. These inexpensive skyline features remain geometry at all three levels.

The mansard now uses parallel inset edges and face-local slate coordinates.
Courses follow each horizontal eave, including the corner, rather than rotating
with a dominant world-axis UV projection. Validation checks stack orientations,
pot groups and the slate course coordinates, alongside existing window rays.
Updated corner/roof renders and browser Walk/District comparisons are in the
ignored build renders directory.


## Close exterior detail pass

The official Prezzo frontage photograph and a daylight OpenRent aerial now
supplement the original property photographs and Mapillary view. Source links
and credits are recorded in the research catalogue; no images are included in
Git or projected onto the building.

Detail now has individually bevelled ashlar faces, broad corner rustication,
radial entrance stones and a keystone, layered window mouldings and interpreted
keystone relief, six-over-six sash divisions with separate rails and beads,
concave seven-flute pilasters with volutes and small egg-and-dart interpretations,
profiled bases and cornices, eaves brackets, a deeper double entrance with handles,
lanterns, an end doorway/transom, projecting sign and red window script.
Dormer windows are taller, with wedge cheeks and lead cap/sill flashings.
These are geometric interpretations of the visible architecture, not measured
carving reproductions. The rendered rear/service block remains schematic.

The close view has about 210,000 placed triangles and 10.08 MB across three GLBs.
Walk reduces the pilaster grid from 112×36 to 28×8 and removes fine ashlar skins,
small moulding subdivisions and ornamental strokes; the retained shell carries
the authored coursed stone map. District uses a flat pilaster shaft, omits small
hardware and bakes the window prototypes. All nine GLBs and the window-bake
coverage checks pass. The table above contains the new measured totals.

### Coincident surfaces

The cornices now form continuous mitred sweeps rather than overlapping facade
ends. Window rails are laid out without crossed front faces. Component-local
coplanar clipping in `surface_cleanup.py` removes duplicate same-facing patches,
preserving material ownership and prototype placement; it does not decimate or
move surfaces. Ground-contact underside caps are omitted because the public
realm supplies the floor. Rear/party wall ends are kept inside the street faces.
Dormer fronts now sit ahead of the mansard rather than intersecting its lower
window panes.

An independent triangle-intersection/ray audit reduced potentially exterior
coplanar overlaps from 91 to one roughly 4 mm² numerical sliver on a rear-wall
top edge; no street-face cases remained in that audit. This is a geometric check,
not a guarantee for every rendering device. A checked-in Blender regression checks union
area, material ownership, winding and idempotence on flat and tilted planes,
and preserves adjacent/opposite-facing surfaces. Validation also probes the lower and upper dormer
panes and all eleven sign centres to catch hidden glazing or lettering.

Use the new **Entrance detail**, **Pilasters** and **Upper stonework** bookmarks
with automatic detail, or force levels in View settings. Close-up PNGs are
`renders/entrance.png`, `renders/pilasters.png` and `renders/stonework.png` under
the Prezzo build directory, alongside the four-view contact sheet.

The revised build passes 13 Python tests (including the Blender surface ownership
regression), viewer policy tests, source checks and all publication checks.
Browser review compares forced Walk/District and automatic close-up Detail for
the entrance, upper stonework and roof, with no asset errors across 31 scene parts.

## London Street menu stonework

The central pier now has the framed stone relief above the menu and its hanging
shield-like pendant, with stepped frame, coping and shallow branching strokes.
The original corner photograph resolves the overall forms but not the carved
subject: this is an explicitly approximate interpretation, pending a close photo.
No heraldic identity or unreadable lettering has been invented.

Detail uses relief geometry. Walk and District bake this single component to a
two-triangle receiver with colour, roughness and normal maps at 512 and 256 pixels;
the receiver gives up depth and shadow parallax. The backing sits clear of the
wall's ashlar skin. The **London stonework** bookmark shows the feature; the
Blender close-up is `renders/london-menu.png`. Full build, all publication levels,
close/overview renders, browser level review and 13 Python tests pass.

The relief bake check requires 99.5% colour coverage inside the receiver UV
rectangle, excluding unused atlas borders; this catches unbacked strips at the
projecting coping ends.

## Coordinated London elevation review

The enlarged property photograph revealed that the London Street ground bay
away from the corner is not full-height glazing. It now has two three-light
registers, a broad stone spandrel between them, and a raised recessed apron.
The corner-adjacent glazed bay stays full height. The two central Ionic pilasters
now stand clear of the opening edges rather than overlapping their frames.

The menu is a narrow, tall dark display in a real shallow wall pocket, with a
separate smaller framed display below. The former brass-coloured surround has
been replaced by restrained dark joinery and stepped stone reveals. Its unreadable
copy remains blank. First-floor sash surrounds on both streets and the chamfer
now continue into inset aprons down to the belt course; the inappropriate
projecting sills at this level have been removed. Higher-storey sills remain.

These are visually calibrated proportions, not surveyed dimensions. The carving
above the menu remains approximate because the source cannot resolve its subject.
Roof stacks, pot directions, dormers and slates were compared with the existing
aerial/oblique references and did not need another change in this pass.

The pocket backs, reveals, spandrel, stone frames and pilaster placements remain
at every level. Walk retains the two glazing registers; District bakes their
joinery and spandrel together into the window receiver, while the larger stone
apron and opening stay separate geometry. Existing fine-bead and pilaster
sampling rules still apply. New validation rays check that pilasters do not hide
shop glazing near its edges and that the first-floor apron backs are recessed.
The **London ground floor** bookmark and `renders/london-ground.png` expose the
whole corrected arrangement; `london-menu.png` shows the central pier closely.

The coordinated three-building publication passed all nine GLBs for this asset
and its bake checks. Browser review covered automatic close-up Detail and forced
Walk/District front and oblique views. All 31 combined scene parts loaded without
asset errors. Thirteen Python tests and the viewer policy test pass.

## Terminal bays and gable ends

The 2026-10-22 follow-up restores the narrow plain terminal bays beyond the
main cornice on both street ends. Each has three slimmer upper windows and a
recessed entrance; the Lord Street bay provides the flats entrance identified
by the user. The previous doorway squeezed into the main pilaster was removed.
The London bay extends the footprint to site Y -41.2. The main Lord Street
bays were recalibrated within the existing block registration, leaving a 1.8 m
terminal bay before the adjoining terrace. These dimensions remain estimates.

The slate mansard now covers only the three street faces. Vertical gable/end
walls replace the guessed rear and party hips. The daylight aerial and satellite
view support a larger flat-roofed headhouse with two street-facing sash windows.
Terminal bay envelopes, recessed doors and gables remain at all LoDs; their
window details use the existing shared panel bakes at District.

Glebe Place's user-supplied Street View URL was tested, but Google returned
403 tiles and 500 metadata responses. The rear wall below the corrected roof
therefore remains a provisional envelope: rear windows, external stairs and
services have not been reconstructed or claimed verified. No private interiors
are included. New **Flats entrance** and **Rear roof** bookmarks aid review.

The terminal-bay/rooftop publication pass passed master validation, fresh
renders, all declared GLBs and bake coverage checks. Browser roof review
covered Walk and District; thirteen Python tests and the viewer policy test
also passed.

## Rear wings and 124 Lord Street entrance

User-supplied Street View screenshots showing **2 Glebe Place, November 2020**,
cross-checked with the supplied Google Maps 3D aerial, replace the provisional
flat rear wall and rooftop box. The exterior now has three stepped projecting
masses: a broad white-brick wing with paired wide/narrow sashes, a taller central
wing with smaller windows on two perpendicular faces and a high return opening,
and a lower eastern wing. The upper western escape opening retains its rounded head.
Two recessed fire escapes have open flights, treads, landings, support posts and
railings. Roof guardrails, television aerials, cream drainpipes, a small dish and
the prominent angular pale duct follow the visible features. The broad west
return is plain rendered masonry rather than decorative street stone.

The entrance close-ups resolve the **No 124 LORD STREET / ENTRANCE TO FLATS**
plaque, three fielded black door panels, brass kickplate and handle, two shallow
recessed steps, white handrails and intercom. Its flat splayed stone arch now has
a tall central keystone, and the separate upper window has crossed glazing bars
inside a rectangular border. Only the legible address plaque is transcribed;
small intercom labels and the door sticker remain unreadable.

Rear projections, floor heights and stair dimensions are visual calibrations,
not surveyed measurements. Lower stair bases are partially concealed by other
buildings in the photographs; their simple continuation is explicitly estimated.
The yard, surrounding red-brick outbuildings, private rooms and hidden roof
connections are not inferred as surveyed architecture. Local screenshot names,
Google attribution and displayed dates are recorded in `research/references.json`;
reference pixels remain private and are not texture inputs. White-brick bond and
variation are generated by `prepare.py`.

LOD decisions preserve the stepped envelopes, real openings, duct and open
escape structure at all three levels. Treads, stringers, landing plates and main
rails are deliberately inexpensive geometry: a solid bounding box would destroy
the stair recesses and silhouette. Walk retains the thinner balusters, pipes and
roof cross-bracing; District omits those small fittings. Fine platform grating is
Detail only. Rear sash prototypes share the existing District panel bake, while
the address plaque uses the existing Walk/District sign bake. No global mesh
decimation is introduced.

Use **Rear elevation**, **Rear stairs**, **Rear roof** and **Flats entrance** in
the viewer. Master renders include `rear.png`, `rear-oblique.png`,
`rear-stairs.png` and `flats-door.png`. Validation checks every rear window's
visibility, as well as three rear wings, two stair recesses, two escape assemblies,
the duct and address plaque. Existing street-window, roof and bounds checks remain.

## Screenshot correction pass publication budgets

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| detail | 256,119 | 15,135,356 | 1,552,866 |
| walk | 82,671 | 7,575,216 | 1,294,664 |
| district | 25,715 | 4,157,068 | 855,914 |

The east rear gable meets the recess at 15.00 m, with a 300 mm underside return
between their offset planes. Horizontal and rising-oblique ray checks guard
against the previously open 100 mm band and a missing soffit. Its vertical top
shares only an edge with the roof deck, avoiding a duplicate horizontal cap.

User review and `screenshot-20261022-103827.png` show shallow applied pilasters,
with their bases close to the grey skirt face. Pilaster depth is reduced at all
three levels so the base projects 0.06 m rather than 0.38 m; shaft, flutes and
capital relief scale together while width and height remain unchanged. This
projection is a visual estimate, not a measured dimension. The skirt is unchanged.


### Rear escape correction (22 October 2026)

Fresh November 2020 Street View angles from 1 and 2 Glebe Place show narrow,
parallel flights running along the recess depth and rising towards projecting
outer platforms. They replace the mistaken wide flights across the facade.
The former full landing plates cut through the flights; these are now U-shaped
landings with open stair wells and a separate side return route. Railings leave
the heads and feet clear. The lower run reaches the local ground datum via an
estimated half landing instead of ending suspended 1.4 m above it.

The .85 m flight width, 3.30 m run, .85 m outer platform and concealed return
route are visual estimates, not a surveyed stair plan. Adjacent roofs obscure
the base. Curved rail transitions are simplified to straight members. Main
flights, open landings, supports and rails remain at every LoD; fine balusters
remain at Detail/Walk and surface grating at Detail only. Geometry rays now
check open wells, clear return routes and clear stair mouths, alongside the
existing rear-window and roof-seam tests. Publication figures above include this correction and all three packages pass validation.


### Recessed joinery and entrance sign (22 October 2026)

The supplied Lord Street close-up and retained official exterior photographs show
slimmer painted frames than the first model. Perimeter frames are now 65 mm
(previously 100 mm), shop dividers 40 mm (60 mm), and fine sash glazing bars
18 mm (27 mm). Frames sit inside the stone reveal rather than projecting as a
white surround. These are visually calibrated proportions, not surveyed sizes.
The same authored geometry supplies Detail/Walk and the rebaked District panels.

The corner PREZZO sign now sits behind the masonry face and ahead of the dark
fanlight. Its whole rectangular receiver fits inside the curved arch, avoiding
the previous panel crossing the stone hood. Validation tests the recess, curved
clearance and all street window fronts. All three exported levels were reviewed
in entrance, shopfront and upper-sash close-ups; 26 window/relief bake checks pass.
Fresh browser verification was attempted but the session stalled after its idle
restart, so this correction relies on the recorded existing photographs.

The rear duct was rechecked against the supplied November 2020 Glebe Place
close-up (screenshot-20261022-104014.png, retained privately). Its offset follows
the wall plane; the previous extra alleyward bend and independently twisted
box segments were removed. A single closed mitered shell now forms the elbow.
Widths and exact wall offsets remain visually estimated.

The corner lantern snag (64f5fd) replaces the brass-coloured boxes using two
private closeups supplied by the user. Dark weathered metal frames surround
recessed glazing and ivory bulb forms; hipped caps, raised vents, finials and
tapered lower bowls define the silhouette. These are visual estimates, not a
manufacturer identification. Hardware is retained at Detail/Walk and omitted
at District under the existing publication policy. No photo pixels are embedded.
