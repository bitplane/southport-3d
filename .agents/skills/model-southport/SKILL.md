---
name: model-southport
description: Research, construct and review individual Southport buildings or memorial details using this repository's metric Blender source workflow. Use for building modelling and architectural corrections, not general repository maintenance.
---

Read AGENTS.md, docs/ARCHITECTURE.md and the target asset manifest. Keep building-specific recipes with the building; shared primitives belong in lib/southport3d.

Study the site from multiple directions using available Street View, Mapillary, aerial/3D views and supplementary image searches. Record source-page URLs, attribution and capture dates where known. Keep downloaded evidence outside tracked source. Distinguish measured dimensions, visually calibrated proportions and guessed hidden surfaces.

With the southport-browser MCP, make browser calls one at a time; parallel calls race, so a screenshot can run before the wait meant to precede it. Wait a few seconds after navigating before the first screenshot. Google shows a consent page in every fresh session: choose "Reject all". In Street View, turn with arrow keys or browser_mouse_drag_xy, zoom with browser_mouse_wheel, and read heading, pitch and field of view from the URL. Session output is temporary; copy anything worth keeping outside the repository.

Work from footprint and height through elevations, columns/mouldings, entrances and distinctive ornament. Preserve architectural identity before adding surface noise. For the memorial, interiors and missing names are deferred; never invent lettering to fill unreadable areas.

Use the isolated tools/project.py build workflow. Existing relief NPZ files are source depth fields; regenerating them may require local photographs, while ordinary builds do not. Keep Blender file writers sequential. Review affected close-ups and an overview for scale, silhouette and placement. The render stage accepts --views with full view identifiers (for example, 43_obelisk_wwii).

Before treating a new building as complete, read docs/LOD-PIPELINE.md and record a reasoned action for every component at every intended level: omit, replace with a simple envelope, adjust the generator, or decimate selectively. Design feature boundaries and generator controls while authoring the master. Preserve major silhouettes and through-openings; bake facade/carving/text detail onto simpler receiving surfaces. Test front and oblique views. Mark incomplete coverage explicitly; the memorial has a complete streaming assembly recipe as well as the earlier component pilot. Read docs/VIEWER.md and add publication.json with exact coverage, transforms and all three working levels. Run the publication command and inspect the building in the viewer before treating its LOD work as complete.

Stage intended source, run the source check, and report build/validation results plus unresolved estimates. Do not add reference images or generated outputs to Git. See docs/SETUP.md for browser MCP setup and RIGHTS.md for source provenance.
