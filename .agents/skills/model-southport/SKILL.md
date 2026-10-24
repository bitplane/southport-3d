---
name: model-southport
description: Research, construct and review individual Southport buildings or memorial details using this repository's metric Blender source workflow. Use for building modelling and architectural corrections, not general repository maintenance.
---

Read AGENTS.md, docs/ARCHITECTURE.md and the target asset manifest. Keep building-specific recipes with the building; shared primitives belong in lib/southport3d.

Follow the required evidence and comparison stages in docs/MODELLING-WORKFLOW.md. Before detailed geometry, orbit Google Maps 3D from several directions to understand the footprint, roof sections and neighbouring context; gather views of every modelled elevation and search Maps place photos, Mapillary, web/images and Wikimedia/heritage sources where relevant. Record missing coverage and actual access failures. Save measurement inputs and an elevation/roof evidence coverage record, not just source links. Compare basic model shapes against matching reference viewpoints before adding ornament. Existing code is not architectural evidence.

With the southport-browser MCP, make browser calls one at a time; parallel calls race, so a screenshot can run before the wait meant to precede it. Wait a few seconds after navigating before the first screenshot. Google shows a consent page in every fresh session: choose "Reject all". In Street View, turn with arrow keys or browser_mouse_drag_xy, zoom with browser_mouse_wheel, and read heading, pitch and field of view from the URL. Session output is temporary; copy anything worth keeping outside the repository.

Work from footprint and height through elevations, columns/mouldings, entrances and distinctive ornament. Preserve architectural identity before adding surface noise. For the memorial, interiors and missing names are deferred; never invent lettering to fill unreadable areas.

Use the isolated tools/project.py build workflow. Existing relief NPZ files are source depth fields; regenerating them may require local photographs, while ordinary builds do not. Keep Blender file writers sequential. Review affected close-ups and an overview for scale, silhouette and placement. The render stage accepts --views with full view identifiers (for example, 43_obelisk_wwii).

Plan Detail/Walk feature choices and a separately authored District envelope; read docs/LOD-PIPELINE.md for budgets, projection groups and the working BHF/memorial examples. Coarse topology and atlas dimensions must stay fixed when fine detail is added. Reuse verified dimensions, preserve silhouettes and meaningful openings, and bake onto the actual replacement surfaces. Prefer shared atlases to one bake per window/sign. Record omissions and incomplete coverage. Integrate all three levels through publication.json and the ordinary checked publisher; regional aggregation is a separate farther-distance representation.

Completion requires recorded reference-versus-model comparisons, including roof/rear coverage and the assembled neighbourhood; passing builds alone is insufficient. Publish staged progress when requested, keeping provisional areas and unresolved discrepancies explicit. Stage intended source, run the source check, and report build/validation results plus unresolved estimates. Do not add reference images or generated outputs to Git. See docs/SETUP.md for browser MCP setup and RIGHTS.md for source provenance.

For an LoD-only rollout where the user explicitly takes visual acceptance, keep
automated mesh/bake/budget checks and publish reviewable increments; do not claim
unperformed visual checks or impose a long render/browser review on each asset.
This exception does not waive evidence gathering for new architecture or permit
changing major dimensions to simplify baking. Each agent may run one Blender job concurrently with other agents. Retain
per-asset writer locks and the catalog publication lock; see the concurrency
policy in docs/MODELLING-WORKFLOW.md.
