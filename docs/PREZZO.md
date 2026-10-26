# Prezzo, 128 Lord Street

Source: `regions/southport/london-square/prezzo/`.

## Evidence, registration and limits

The asset shares London Square's WGS84 origin and 43.5293-degree site frame.
OSM way 371203985 describes the whole block, not this individual property.
Estimated lot limits, heights and the 0.58 m local floor datum are recorded in
`research/layout.json`; dimensions have not been surveyed. Public-realm assets
own the pavement approach, with no duplicate building-owned ground.

Evidence includes January 2025 Google aerial imagery, January 2018 street
panoramas, davidsong's July 2019 Mapillary sequence, official Prezzo and property
exterior photographs, and supplied November 2020 Glebe Place Street View.
URLs, attribution, private capture names and limitations are in
`research/references.json`. Reference pixels are not distributed or used as maps.
Branding follows those references rather than a verified current inventory.

Street ornament is an interpreted geometric approximation, not an exact carving
reproduction. Rear projections, stair bases, roof connections and metric heights
remain visually calibrated estimates. Glazing is opaque; interiors, surrounding
outbuildings and illegible text are not invented.

## Street elevations

Five principal Lord Street upper bays, three London Street bays and a chamfered
arched entrance define the frontage. Narrow terminal bays beyond the main cornice
have three slimmer upper windows and recessed entrances. The Lord Street terminal
bay is approximately 1.8 m wide; the London bay extends to site Y=-41.2.

Detail includes bevelled ashlar, corner rustication, radial entrance stones,
layered window mouldings, interpreted keystones, six-over-six sashes, fluted
Ionic-style pilasters, profiled bases/cornices, dentils and eaves brackets.
Pilaster bases project about 0.06 m beyond the grey skirt; widths and heights
are independent of that shallow relief. Painted perimeter frames are estimated
at 65 mm, shop dividers 40 mm and fine glazing bars 18 mm, recessed within stone.

The London Street bay away from the corner has two three-light glazing registers,
a broad stone spandrel and a recessed apron; the corner-adjacent bay remains
full-height glazing. First-floor surrounds continue into inset aprons down to
the belt course; higher floors retain projecting sills. Pilasters stand clear
of the glazing edges.

The menu occupies a shallow dark wall pocket with a smaller framed display below.
Above it, a framed relief and shield-like pendant reproduce the visible outline
and shallow branching marks. The carved subject and menu copy remain unresolved.
The corner PREZZO sign sits behind the masonry face, ahead of the fanlight and
entirely inside the curved arch. Corner lanterns have dark metal frames, recessed
glass, ivory bulb forms, hipped caps, vents, finials and tapered bowls; their
manufacturer and exact dimensions are unknown.

The legible flats plaque reads “No 124 LORD STREET / ENTRANCE TO FLATS”. The
entrance has a splayed flat arch and tall keystone, three fielded black door
panels, brass kickplate/handle, two shallow recessed steps, white rails and
intercom. Its upper window has crossed bars inside a rectangular border.
Intercom labels and the door sticker are unreadable.

## Roof and rear

The mansard covers the three street faces, with vertical party/rear gables,
nine dormers and face-local slate courses parallel to each eave. Dormers have
open cheeks, recessed glazing and lead caps/sill flashings. Six placed chimney
stacks comprise three capped stacks and three terracotta-pot groups. Lord Street
rows run along site Y; the London Street row follows X. Estimated pot counts are
five per Lord Street group and four on London Street; concealed flues are unknown.

November 2020 rear views establish three stepped masses: a broad white-brick wing
with paired wide/narrow sashes, a taller central wing with windows on perpendicular
faces and a high return opening, and a lower eastern wing. The upper western
escape opening has a rounded head. The broad west return is plain render.
Guardrails, aerials, drainpipes, a dish and an angular pale duct follow visible
features. The duct elbow is a single closed mitred shell; offsets remain estimated.

Two recessed fire escapes have narrow parallel flights along the recess depth,
U-shaped landings, open wells, supports and rails. Estimated dimensions are 0.85 m
flight width, 3.30 m run and 0.85 m outer platform. A concealed lower return reaches
the local ground through an estimated half landing. Adjacent roofs hide the bases;
curved rail transitions are simplified. The east rear gable meets the recess at
15.00 m, with a 300 mm underside return between offset planes.

## Viewing levels

Architecture, roof and shopfront are separate publication parts. Detail retains
fine masonry, joinery, carving, fittings and grating. Walk reduces pilaster
sampling, omits fine skins/beads and bakes lettering and the menu relief while
retaining the main openings, stairs, rails and window geometry.

District uses the independent `scripts/district.py` envelope. It retains the
chamfer, three recessed street entrances, mansard, dormers, chimney groups and
stepped rear wings. Landing slabs and six broad treads per flight preserve the
open escape wells; fine rails, aerials and hardware are omitted. Fine appearance
projects into shared architecture 512×512, roof 512×256 and shopfront 512×128
atlas sets. Metallic lanterns are excluded from the dielectric bake.

Recorded District export: 940 triangles, 492,920 download bytes including textures
and 7,438,424 estimated GPU bytes. Use generated package reports for current
counts after changes. The owner handles visual acceptance for this LoD rollout;
automated geometry, coverage, normal-map and budget checks remain required.

## Construction and checks

Cornices are continuous mitred sweeps. `surface_cleanup.py` clips same-facing
coplanar patches without moving or decimating them, preserving material ownership.
Party-wall ends remain inside street faces; ground-contact underside caps are
omitted where the public realm supplies the floor. Triangulation precedes UVs.

Build/render with `tools/project.py build southport.london-square.prezzo`
and `--stage render`; publish with `--asset southport.london-square.prezzo`.
Renders include entrance, pilasters, stonework, london-menu, london-ground,
rear, rear-oblique, rear-stairs and flats-door views.

Validation checks finite geometry, UVs, textures, bounds, expected feature counts,
window/sign visibility, dormer panes, pilaster clearance, recessed aprons, rear
openings, escape wells/routes, gable soffit and sign/arch clearance. Surface
cleanup regressions cover union area, materials, winding and idempotence.

`check_package.py` runs even for reused packages. Full-panel window bakes require
95% colour/roughness coverage; relief receivers require 99.5% colour coverage
inside their UV rectangle. Cage depth must reach the recessed backing: valid
normal pixels alone do not prove a successful colour bake. Review exported
levels in the assembled neighbourhood; numerical checks cannot certify every
view or rendering device.
