# Southport 3D

A source-built, detailed model of Southport, UK, starting with the War Memorial in London Square. The aim is to capture individual buildings, shop fronts and architectural details, and eventually stream them through a town-wide web viewer.

The memorial asset contains the obelisk, two colonnades and clustered lamps. A separate [public-realm asset](docs/PUBLIC-REALM.md) adds patterned paving, carriageways, gardens and street furniture, extending along London Street to Chapel Street/Hoghton Street. The adjoining [Prezzo building at 128 Lord Street](docs/PREZZO.md) is the first shopfront/building test of the same pipeline. The adjoining [118–122 Lord Street terrace](docs/LORD-STREET-118-122.md) continues towards Christ Church with Sam Thai, Mamma Mia and Bugle Tap frontages. The [British Heart Foundation at 116 Lord Street](docs/BRITISH-HEART-FOUNDATION.md) continues the frontage to the church edge. Exterior proportions, lettering and reliefs are researched reconstructions with documented estimates. Interiors and further names await photographs. A local browser viewer streams Detail, Walk and District representations from a source-built catalog. The detailed master supports close inspection; reduced levels use explicit feature decisions and shared baked prototypes. Regional tiles and public hosting are deferred.

The [Lord Street church gardens](docs/LORD-STREET-GARDENS.md) add Christ Church’s lawns, walls and approaches and the St George’s hedge garden, with road/pavement joins coordinated across neighbouring assets. [Christ Church](docs/CHRIST-CHURCH.md) and [St George’s Church](docs/ST-GEORGES-CHURCH.md) now add their researched exterior architecture, including the modern annexes and rear hall.

The [Nevill Street corridor](docs/NEVILL-STREET.md) continues the roads and pavements from the monument to the Promenade crossing and Funland frontage, with mapped registration and estimated widths and levels. The [Nevill block plan](docs/NEVILL-BLOCK-PLAN.md) adds provisional footprint/height volumes on both street sides to Funland, with checked open forecourts and rear access. The [Marine Parade junction extension](docs/MARINE-PARADE-JUNCTION.md) continues northeast along the Promenade through the next junction, with crossing refuges informed by July 2026 Street View.

The [Occulo Lounge / former Waterstones building](docs/OCCULO-LOUNGE.md) replaces the Nevill Street corner placeholder with its Portland-stone arcades, fluted columns, carved entrance and flat roof. Beside it, [Coffee King / The Old Bank at 365 Lord Street](docs/COFFEE-KING.md) adds the red-granite colonnade and surveyed pitched roof, reserving the passage to Parkinson Books for a later courtyard survey.

The [Lord Street block plan](docs/LORD-STREET-BLOCK-PLAN.md) extends both frontages and the road/landscape canvas between the Duke Street and Leicester Street roundabouts, using provisional replaceable building volumes.

The [NatWest bank at 130 Lord Street](docs/NATWEST.md) adds the opposite corner: sandstone street elevations, Dutch gables, pierced parapets and intersecting slate roofs.

The adjoining [Posting House and 132 Lord Street](docs/POSTING-HOUSE.md) continue that frontage, with the [Sainsbury’s building](docs/SAINSBURYS.md) farther along the existing street canvas. [6–12 London Street](docs/LONDON-STREET-6-12.md) adds Halifax and the adjoining frontage beside Glebe Place. Each asset has independent source, evidence records and three viewing levels; hidden surfaces and visually estimated dimensions remain documented limitations.

## Build

Requires Python with NumPy/Pillow, Blender (tested with 5.0.1), and Liberation Serif. See [setup](docs/SETUP.md).

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python tools/project.py list
python tools/project.py check
python tools/project.py build southport.london-square.war-memorial
python tools/project.py build southport.london-square.war-memorial --stage render
```

Builds go into `build/southport.london-square.war-memorial/`, including models, PNG renders, reports and logs. The default build prepares textures, builds geometry, exports GLBs and validates them. Rendering is a separate step. No reference photographs are needed to rebuild the current master.

See the [LOD audit](docs/LOD-AUDIT.md) and [reasoned LOD workflow](docs/LOD-PIPELINE.md) for choosing omissions, replacements, generator controls and selective decimation.

## Explore in your browser

```sh
python tools/project.py publish
python tools/serve.py
```

Open http://localhost:8765. Use orbit or walking controls, and View settings to compare levels. See [viewer setup, SSH forwarding and adding buildings](docs/VIEWER.md). Publication here creates a local static package; it does not upload or deploy it.

## Source layout

- `regions/southport/london-square/war-memorial/`: asset manifest, construction scripts, measurement recipes and numeric relief surfaces.
- `lib/southport3d/`: shared geometry helpers; building-specific construction stays with its asset.
- `tools/`: build runner and optional browser MCP setup.
- `.agents/skills/`: modelling workflow, also exposed to Claude through `.claude/skills`.
- `docs/`: [setup](docs/SETUP.md), [architecture](docs/ARCHITECTURE.md) and [roadmap](docs/ROADMAP.md).

Python, JSON and numeric NPZ relief data are source. Blender scenes, GLBs, textures and renders are generated outputs. Historical sculpting scripts may need privately acquired photographs to regenerate relief source data. Reference images, browser profiles and caches are excluded; the source catalogue contains links and attribution.

Read [contribution instructions](CONTRIBUTING.md), [agent instructions](AGENTS.md) and [rights/provenance](RIGHTS.md) before contributing. The default branch is `master`. The `memorial-source-baseline` tag preserves the imported construction source before the shared-library extraction.
