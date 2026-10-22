# 118–122 Lord Street

The lower shop terrace immediately southwest of Prezzo is the next asset towards
Christ Church. Its stable ID is `southport.london-square.lord-street-118-122`;
shop names are reference appearances, not the asset identity. Select **118–122
Lord Street — shop terrace** in the viewer.

The exterior includes six recessed narrow upper windows, a panelled stone
frontage, parapet and flat roof, polished green-grey shopfront piers, recessed
entrances, aluminium/dark glazing bars, awnings, projecting signs and the small
right-hand ATM housing. The frontages represent Sam Thai, Mamma Mia and The Bugle
Tap. Names and readable main lettering are authored geometry at Detail and baked
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

## LOD and validation

Three parts separate architecture, roof and shopfront. Their inexpensive walls,
openings, parapets, glazing frames and awning profiles remain at all levels.
Walk replaces sign glyphs with baked panels. District also replaces six repeated
upper windows with one shared baked prototype and omits tiny handles/fascia
lamps. Texture caps are 512 for Walk and 256 for District. No global decimation.

| Level | Placed triangles | GLB bytes including textures | Embedded image bytes |
| --- | ---: | ---: | ---: |
| Detail | 24,364 | 2,269,628 | 247,286 |
| Walk | 1,876 | 721,488 | 481,430 |
| District | 1,156 | 375,184 | 163,198 |

These are the three terrace parts only. Most Detail triangles are sign glyphs;
the simpler terrace achieves a much larger geometry reduction than Prezzo.
Bakes are unlit base colour, tangent normal and roughness, not photographs.

Checks validate finite geometry, UVs, packed authored maps, registered bounds,
six visible upper windows, three recessed doors and unobstructed sign centres.
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
rectangular sign atlases are a future optimisation. All 100 terrace meshes are
classified at each level, with all nine GLBs validated. The post-export window
coverage check passes, and repeated publication reuses all four asset packages.
