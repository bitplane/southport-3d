# Southport 3D

A detailed, source-built reconstruction of Southport, UK, for exploring the town
in a browser and reusing its architecture in other projects. The aim is to capture
its varied buildings, shopfronts, streets and public spaces, building out the town
one area at a time.

The model is researched from street-level photographs, aerial imagery and mapping.
Evidence, capture dates and uncertain dimensions are recorded alongside each
asset. This is a reconstruction, not a surveyed digital twin; coverage and detail
vary across the map.

## How it works

Python recipes generate metric Blender geometry. Each asset has detailed and
walking-distance versions plus a separately designed, fixed-budget distant
representation. A spatial streaming viewer selects models as you orbit the town
or walk through it. Local live updates show newly published work, and a snag
collector saves camera positions, marked areas, comments and reference photos
for review.

Work starts with roads, footprints, access gaps and placeholder volumes, then
replaces them with researched architecture. Contributions can come from people
or coding agents using the same build and review workflow.

## Build and explore

Install Blender and Liberation Serif, then set up Python dependencies. See
[setup](docs/SETUP.md) for tested versions, browser research tools and SSH use.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 tools/project.py list
python3 tools/project.py check
```

Choose an asset ID from the list:

```sh
python3 tools/project.py build <asset-id> --threads 4
python3 tools/project.py build <asset-id> --stage render --threads 4
python3 tools/project.py publish --asset <asset-id> --threads 4
python3 tools/serve.py
```

Open http://localhost:8765. Publication generates local files; it does not upload
or deploy a public website. Public hosting remains future work. See the
[viewer guide](docs/VIEWER.md) for controls, port forwarding and publication.

## Repository layout

- `regions/`: geographic asset directories with manifests, evidence and recipes.
- `lib/southport3d/`: reusable geometry and spatial helpers.
- `tools/`: build, validation, publication, viewer server and research tooling.
- `docs/`: workflow references and current asset notes.
- `.agents/skills/`: modelling guidance shared with supported coding agents.

Source recipes, JSON and intentional numeric relief data belong in Git. Blender
scenes, GLBs, textures and renders are generated under ignored build/output
folders. Reference photographs and browser state stay private and outside Git;
research records link to their sources. Ordinary builds use the checked-in
source; regenerating some relief data requires privately held photographs.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md) and
[RIGHTS.md](RIGHTS.md). Keep evidence distinct from estimates, review models
against their references and neighbours, and validate every viewing level.
The default branch is `master`.

Use the [architecture guide](docs/ARCHITECTURE.md) for code organisation,
[modelling workflow](docs/MODELLING-WORKFLOW.md) for reconstruction and review,
[LoD pipeline](docs/LOD-PIPELINE.md) for reduced assets, and
[roadmap](docs/ROADMAP.md) for planned work. Discover buildings through
`tools/project.py list` and their manifests rather than a duplicate README inventory.
