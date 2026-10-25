# 118–122 Lord Street

The lower shop terrace immediately southwest of Prezzo is the next asset towards
Christ Church. Its stable ID is `southport.london-square.lord-street-118-122`;
shop names are reference appearances, not the asset identity. Select **118–122
Lord Street — shop terrace** in the viewer.

The exterior includes six recessed narrow upper windows, a panelled stone
frontage, parapet and flat roof, polished green-grey shopfront piers, recessed
entrances, aluminium/dark glazing bars, Mamma Mia’s awning, projecting signs and the tall
right-hand ATM housing. The frontages represent Sam Thai, Mamma Mia and The Bugle
Tap. Names and readable exterior telephone/sign lettering are authored geometry at Detail and baked
panels farther away. Unreadable menu notices are omitted. Glass is opaque; no
interiors, patrons or photographic shop-window textures are included.

## Evidence and placement

The January 2018 ground panorama and January 2025 aerial establish the upper
facade and roof silhouette. Close photographs resolve Sam Thai's blue bands,
Mamma Mia's high transom sign/awning, and the Bugle Tap's August 2026 appearance.
The latter supersedes older right-hand shop signage. URLs, dates and attribution
are recorded in the asset's `research/references.json`; photographic references
remain private. The listing's 1966 construction date is a listing claim, not an
independently verified historical finding.

The building shares Prezzo's origin/yaw and estimated 0.58 m base. It meets the
Prezzo party-wall edge at site X -32.225 and extends to X -50.8, with its street
face at Y -23.6. Dimensions, exact shop subdivisions, rear depth and roof service
features are estimates rather than survey measurements. The right-hand shop
frontage is interpreted from the newer oblique Bugle Tap photograph. Hidden rear
walls are plain envelopes. The public-realm asset extends the pavement approach
to meet these doors; this building owns no ground mesh.

## Second exterior audit

The three shopfronts now have independent joinery layouts. Mamma Mia has one
broad lower display pane, its row of short transom lights, pale lower-window
lettering, a deeper right doorway with burgundy panel and moulding, and the
awning telephone/name panels and supporting arms. Sam Thai has two main panes,
upper and lower blue name bands, its door-header number and continuous fascia
strip light. Bugle has folding-leaf joints, a doorway inset from the right with a
separate right sidelight, the fixed fascia and a sparse unlit festoon. The
previous generic door placement and invented Bugle fabric awning are removed.
The ATM has a hood, control recess, screen, keypad and lower bin.

Green-grey brecciated stone is an authored procedural interpretation, with
mineral patches and pale fractures at metric scale. It uses no photograph
pixels. The undated Mamma Mia photo shows a cream pier, while the adjoining Sam
Thai and 2026 Bugle photos show green stone: the retained green frontage remains
a mixed-date interpretation. Typeface, veining, hinges and frame profiles are
approximate. A tighter ground-panorama review confirms the six upper openings
but cannot resolve their exact bars. Rear elevations and roof fittings remain
explicit estimates; no invented facade ornament or interiors were added.

The audit also replaced overlapping upper-window rail joints and roof-coping
corners with meeting edges. Window/door openings remain physically recessed.
Close render and viewer presets now cover each individual shop as well as the
front, oblique terrace and roof views.

## LOD and validation

Three parts separate architecture, roof and shopfront. Detail retains the full
architectural source; Walk retains its existing feature policies and baked signs.
District uses the independent envelope described below, with major recesses and
the awning kept geometric and fine features carried by shared atlases. Historical
District measurements and review notes below refer to the previous recipe.

Measured after the second exterior audit, including all three streaming parts:

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 39,120 | 3,771,032 | 506,024 |
| Walk | 5,292 | 1,612,952 | 1,030,382 |
| District | 1,976 | 594,340 | 295,393 |

These are the three terrace parts only. Most Detail triangles are sign glyphs;
the simpler terrace achieves a much larger geometry reduction than Prezzo.
Bakes are unlit base colour, tangent normal and roughness, not photographs.

Checks validate finite geometry, UVs, packed authored maps, registered bounds,
six visible upper windows, three recessed doors, unobstructed sign centres and
visible display-pane samples, including Mamma Mia’s unsplit pane and Bugle’s
right sidelight.
The existing package hook checks base-colour/roughness coverage of the window
bake. Generated render views cover the front, oblique, shopfronts and roof.

```sh
python3 tools/project.py build southport.london-square.lord-street-118-122
python3 tools/project.py publish
python3 tools/project.py build southport.london-square.lord-street-118-122 --stage render
chafa build/southport.london-square.lord-street-118-122/renders/contact-sheet.png
```

## Agreed direction of travel

Continue southwest along this side of Lord Street: the larger British Heart
Foundation frontage next, then Christ Church and its garden. After this side is
reviewed, return to the buildings along London Street toward Chapel Street /
Hoghton Street to finish the block. This is a work sequence, not a claim those
buildings are already modelled; each needs its own reference and boundary pass.

The browser review also found isotropic mip filtering blurred long baked signs.
Device-limited anisotropic filtering (up to 16) restores legible main names at
Walk/District in the comparison views without changing the GLBs. This applies to
all streamed assets, including Prezzo. Lower-capability GPUs can remain softer;
rectangular sign atlases are a future optimisation. All 107 terrace meshes are classified at every level, with all nine GLBs
validated after the second audit. The post-export window coverage check passes.
The revised package retains the same geographic registration and three parts.

The coordinated three-building publication passed all nine GLBs for this asset
and its bake checks. Browser review covered automatic close-up Detail and forced
Walk/District front and oblique views. All 31 combined scene parts loaded without
asset errors. Thirteen Python tests and the viewer policy test pass.

The Glebe Place rear snag exposed a coplanar roof-slab end on the outside rear
wall. The slab now stops behind the wall's inner face. Rear-facing probes through
the full slab-height strip require the wall to be the visible surface; this
removes the flickering strip without changing the estimated rear envelope.

## Independent surface audit

The retained close Mamma Mia reference and all three exported viewing levels
were checked from front, roof and Glebe Place. The earlier rear slab separation
remains effective; the plain hidden rear is still an explicitly estimated
envelope. Existing main openings, recessed doors and roof silhouette are retained.

The sloping Mamma Mia awning and ATM hood previously used two opposing faces
at identical coordinates. They now have thin closed shells (18 mm fabric
allowance and 15 mm hood allowance, both estimates) so double-sided rendering
does not rely on duplicate coplanar surfaces. Validation checks closed edges,
positive signed volume and absence of duplicate triangles. The awning stays
at all levels; the small ATM hood follows the existing Detail/Walk fittings
policy (omitted at District). Lettering typefaces, green stone pattern and service roof features
remain interpretations rather than exact reproductions.

Full builds and validators passed after the audit. Re-published Detail, Walk
and District GLBs were rendered from front, close and roof/rear viewpoints;
colour and major silhouettes remain stable. A combined Walk comparison with
public-realm ground checked the frontage and entrance approaches. Live browser
inspection was unavailable; these checks used imported exported GLBs.

The Glebe Place rear now follows the four private images attached to snag
9648072a74f14fbfac2ad9c4483b92d7, including a Street View frame dated November
2020. Orange brick, an upper rear range, a lower flat-roofed service annex,
asymmetric white/dark windows, metal service doors, two external stair runs,
condensers and drainpipes are observed. The annex depth to site Y -49 m, floor
heights and exact bay positions are visually estimated, not surveyed. Temporary
bins, parked vehicles, tiny warning text and hidden interiors are omitted.
Simple wall, window, door and stair solids remain at all LoDs; fine rails,
pipework and fan faces follow the existing Fine-detail rule. Brickwork uses
an authored metric repeating map; none of the reference pixels is distributed.

## Fixed-budget District envelope

The independent District mesh preserves the panelled upper frontage, parapet,
stepped service annex, three recessed shop doors and Mamma Mia awning. Its two
escape stairs have a fixed 19 treads each; fine rails, projecting shop signs and
small service fittings are omitted. No deep door soffit is invented where the
source has an open transom assembly. Windows, sign lettering and brick/panel
appearance use shared 512×256 architecture/shopfront and 256×256 roof atlases.
The recipe retains the researched dimensions and their uncertainty. The owner
handles visual acceptance following automated geometry/bake/budget checks.

Checked District export: **596 triangles, 255,340 bytes including textures and
5,303,691 bytes estimated GPU memory**, down from 5,212 triangles, 1,020,948
bytes and 9,254,868 GPU bytes. Receiver overlap scan passes; actual architecture
and shopfront coverage exceeds 99.8%, with valid normal maps and export budgets.
The appearance guard now accepts checked whole-part envelope maps and remains
a declared validation dependency on cached publications. Visual acceptance is
left to the owner.

Door recesses include a continuous head return between the side jambs and the
recessed leaf. The fascia does not substitute for that soffit. Upward ray probes
cover three depths of each head; the District envelope also closes the opening
at its head. This prevents the wall cavity showing above the Bugle Tap entrance.
