# 6–12 London Street

The Halifax/Post & Packing dividing pier has one granite lower face, with the
dark shop surround continuing above it. A duplicate coplanar dark pier caused
flickering in the viewer; the frontage ray checks now cover that shared face.

`southport.london-street.london-street-6-12` owns the continuous red-brick building between Prezzo’s narrow London Street terminal bay and Glebe Place. Halifax occupies nine of its twelve upper bays; number six occupies the other three. The architectural asset therefore covers the whole block, rather than treating the bank shop unit as a separate building.

The front follows verified August 2024 Street View: two rows of twelve sash windows, a hood over every third first-floor window, shallow segmental second-floor heads, dentilled eaves, granite shop piers, recessed bank entrance, two ATMs, blue fascia and the number-six shop/office frontage. The Halifax and Post & Packing names represent that dated evidence, not a statement about current trading. There are no interiors.

November 2020 Glebe Place panoramas establish the side glazing return, small side casements/louvre, mixed rear windows and security bars, external brick chimney, lower service roofs, glazed rooflight, open guardrail and caged ladder. Overhead imagery establishes the hipped roof end and rear service notch. Exact pitches, dimensions, concealed rear wall positions and heights are visually estimated. Later conversion work is not reconstructed without current imagery. The missing rear wing of the adjoining Lord Street terrace remains a separate follow-up.

The metric frame matches London Square: origin 53.6486555, -3.0043401 and site yaw 43.5293°. The north end meets Prezzo at site Y -41.2; the Glebe return is at Y -63.5. OSM maps the enclosing urban block, not individual ownership divisions. Ground is owned by the London Square and Glebe Place public-realm assets, with a shared estimated .7845 m pavement datum.

At the rear, the northern boundary steps back around Prezzo's projecting wings
and both escape stairs. The original rectangular party wall and uncut roof
incorrectly occupied those wells. Three explicit planar roof slopes now form a
closed shell, with a cutout above the low rear rooflight court. The court eave
sits higher on the rear pitch than the full-depth southern eave; wall returns,
vents and gutters follow those actual roof levels. Setback coordinates are
estimated from retained aerial/rear imagery and coordinated with the existing
Prezzo model. A fresh Google 3D review remains pending because the browser
profile was locked during this repair.

## Levels and review

Architecture, roof, shopfront and rear stream independently. Wall apertures, roof shape, hood spacing and entrance recess remain authored geometry at all levels. Walk preserves sash depth; District replaces repeated window modules with baked panels. Both reduced levels bake signs onto simple receivers. District omits dentils, small joints, controls and minor pipes. No global decimation is used. Texture caps are 512 px at Walk and 256 px at District.

Build with `python3 tools/project.py build southport.london-street.london-street-6-12`; add `--stage render` for front, roof, side, rear and shopfront inspection images. The validator checks all 24 front windows are unobscured, the bank door recess, registration bounds, packed maps and finite UV meshes. The research catalogue records exact URLs, capture dates and remaining uncertainty. Reference screenshots stay outside Git.

Roof validation requires manifold edges and checks 1,677 rays against the
declared slopes/cutouts. Every triangle, including pipes and wall returns, is
checked against both neighbouring stair-clearance volumes. The viewer's
“Prezzo stair clearance” bookmark shows the two buildings together.


## Rear court and side-window correction

The November 2020 Glebe photographs were rechecked against the generated rear
and side elevations. The pair of side windows now use plain casements with a
narrow top transom, distinct from the front sashes. Upper bricked openings align
with those casements. The recessed court wall now holds all eight visible mixed
openings: four upper windows, three lower barred windows and the larger barred
opening below the chimney-side window. The southern projection is blank above
its low service wing; the previous misplaced trio has been removed.

The rear eave is lowered to calibrate the two-storey courtyard proportions, while
the front eave/ridge and the neighbouring staircase cutouts remain fixed. Chimney
and rooflight positions follow the corrected window grouping. These rear heights
and offsets remain estimates. Fresh Maps screenshot attempts stalled, so this
pass uses the retained dated Street View and aerial references explicitly.

Regression checks retain all 1,677 roof rays, manifold roof tests and triangle-level
stair clearances, and add visibility/registration checks for the eight court
windows and two side casements. All levels rebake the changed window modules.

The rebuilt Detail, Walk and District GLBs were reviewed in rear, side and roof
comparisons. Their roof silhouette and material colour stay consistent; only
small fittings and baked sash depth simplify. The normal front composition is
preserved. The exact rear pitch still needs confirmation when live imagery is
available; the reconstruction does not claim a surveyed roof profile.

## Independent southern deck review

A second comparison with the retained Google aerial and November 2020 Glebe
panorama found the southern flat service deck still covered by the main hip.
The pitched roof now stops at the recessed upper rear line throughout the south
end, exposing the pale deck through to Glebe Place. The upper brick return closes
to the actual hip underside; hip flashing and drainage stop at that roof edge.
The southern side wall steps down to the flat deck. This matches the visible
roof arrangement, while the exact setback width and elevations remain estimates.

The two windows on the lower southern rear wing are now wide, shallow barred
casements, matching the ground view instead of repeating a narrow portrait unit.
Their sizes and sill heights remain visually calibrated. A validation ray checks
that the southern deck is exposed at three positions, in addition to the existing
closed-roof, window-clearance and neighbouring-stair checks.

A saved rear snag exposed a triangular opening where the wall crossed the hip
seam. Wall tops now split at roof-plane intersections instead of connecting
only endpoint heights. Fifty-nine horizontal rays follow the rear eave to catch
missing closure. The retained aerial supports the overall hip and exposed lower
service deck; exact pitch and setback dimensions remain estimates.

## Current frontage details

Private snag photographs e6c96e and 588176 establish the paired Halifax machines
and number-six entrances. Each machine has a white backboard, upper information
display, hooded/sloping screen, paired button rows, green card guide, two lower
slots and projecting keypad shelf. The blue identity panel carries authored
Halifax/cash-machine lettering; unreadable screen instructions are omitted.
The machines' coarse frames and recesses survive all levels; controls remain at
Detail/Walk and omit at District, while sign lettering bakes to panels.

Continuous soffits and glazing heads close the fascia recess. Number six has a
separate glazed shop door and black four-panel offices door with two letterboxes,
a knob, overlight, threshold and granite jambs. Temporary letting boards and
interiors are excluded. Sizes are calibrated estimates from the supplied photos.
Ray checks sample the previous fascia and doorway gaps in the assembled building.
