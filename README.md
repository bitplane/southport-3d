# Southport 3D

A source-built, detailed model of Southport, UK, starting with the War Memorial in London Square. The aim is to capture individual buildings, shop fronts and architectural details, and eventually stream them through a town-wide web viewer.

The memorial asset contains the obelisk, two colonnades and clustered lamps. A separate [public-realm asset](docs/PUBLIC-REALM.md) adds patterned paving, carriageways, gardens and street furniture, extending along London Street to Chapel Street/Hoghton Street. The adjoining [Prezzo building at 128 Lord Street](docs/PREZZO.md) is the first shopfront/building test of the same pipeline. The adjoining [118–122 Lord Street terrace](docs/LORD-STREET-118-122.md) continues towards Christ Church with Sam Thai, Mamma Mia and Bugle Tap frontages. Exterior proportions, lettering and reliefs are researched reconstructions with documented estimates. Interiors and further names await photographs. A local browser viewer streams Detail, Walk and District representations from a source-built catalog. The detailed master supports close inspection; reduced levels use explicit feature decisions and shared baked prototypes. Regional tiles and public hosting are deferred.

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
