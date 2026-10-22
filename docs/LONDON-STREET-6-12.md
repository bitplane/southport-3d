# 6–12 London Street

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
