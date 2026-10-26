# Agent instructions

Read the target `asset.json`, its evidence records and assigned brief. Use README
for initial orientation, not every task. Use the model-southport skill for
modelling; CLAUDE.md points here too. Read only task-relevant references below,
not the full documentation or historical review directory.

## Working rules

- Use metres and preserve documented geographic origins/orientations. Keep
  building recipes under `regions/<town>/<area>/<asset>/`. Extract shared helpers
  only when their interface is useful independently of one building.
- Use `tools/project.py` for isolated builds and checked publication. Run at most
  **one Blender process per agent**, normally `--threads 4`; different agents may
  build/render/bake different assets concurrently. There is no global Blender
  slot. Keep per-asset and catalog locks; direct scripts bypass them. Blender
  commands require `--python-exit-code 1`.
- Keep images, browser state, credentials and generated models/textures/renders
  out of Git. Record source links, attribution, dates and uncertainty. Numeric
  relief fields are intentional source, not licence-free substitutes for the
  original works; see [RIGHTS.md](RIGHTS.md).
- Use `master`. Do not push or publish without authorization; existing user
  authorization persists. Local viewer publication does not deploy a website.
  Scope commits to owned files in the shared workspace.
- Stage intended source and run `python3 tools/project.py check`. Geometry changes
  require full asset build/validation, reference comparisons and affected renders;
  review exported levels and neighbouring seams before claiming completion.
- Browser sessions expire after five idle minutes, including child browsers.
  Reopen and continue after expiry; close owned browsers when finished. Keep
  browser calls sequential within each session.

## Task references

- **Modelling:** [MODELLING-WORKFLOW.md](docs/MODELLING-WORKFLOW.md). Establish
  roads, footprints, access gaps and placeholders first. Orbit actual 3D imagery,
  gather each modelled elevation, record measurements/missing coverage and compare
  main shapes before ornament. Existing code and attractive renders are not
  evidence. Preserve estimates and deferrals; never invent unreadable lettering.
- **Surface ownership:** use that workflow's checks during design, before repeated
  components and publication. Add scoped regressions; a wall-only or successful
  build check does not certify the whole asset against z-fighting.
- **LoDs:** [LOD-PIPELINE.md](docs/LOD-PIPELINE.md). Make per-feature choices and a
  separate fixed-budget District envelope whose topology/atlas size does not grow
  with Detail ornament. Declare budgets, omissions and projection groups.
- **Publication:** [VIEWER.md](docs/VIEWER.md). Classify meshes exactly once,
  preserve the coordinate frame and check Detail/Walk/District in the assembled
  viewer. Use the catalog pipeline, not building-specific viewer branches.
- **Ground/furniture:** [PUBLIC-REALM.md](docs/PUBLIC-REALM.md) and, for heights,
  [ELEVATION.md](docs/ELEVATION.md). Use bounded named surfaces and rough editable
  slopes, not raster draping. Keep bridge decks and lower paths distinct; separate
  ground ownership from buildings/furniture. Share generators, not site positions.
- **Snags:** [SNAGS.md](docs/SNAGS.md). Inspect and exclusively claim with
  `tools/snags.py`; resolve only after the fix is built, reviewed and locally
  published. Queue/photos default to `../snags/`, outside Git.
- **Environment/build internals:** consult [SETUP.md](docs/SETUP.md),
  [ARCHITECTURE.md](docs/ARCHITECTURE.md) and
  [INCREMENTAL-BUILDS.md](docs/INCREMENTAL-BUILDS.md) when needed.

## Reviews and documentation

Process worker checkpoints promptly; release accepted stages and give specific
corrections. Workers continue independent work while awaiting review. Keep asset
notes about current evidence, decisions, limitations and reproducible checks;
update existing sections rather than append repair diaries. Commit history and
ignored output hold chronology and transient logs. Preserve evidence dates.
Task-specific `docs/reviews/` briefs are not global onboarding requirements.

The owner permits `claude -p` outside the sandbox for read-only code/plan reviews.
Do not request that permission again or duplicate a review already started by the
user. It does not authorize edits, pushes or publication by Claude, and does not
override runtime restrictions.
