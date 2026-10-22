# Agent instructions

Read README.md and the relevant asset.json before changing a building. Use the model-southport skill for research/modelling work. CLAUDE.md points to these same instructions.

Use metres and retain each asset's documented coordinate origin and orientation. Keep construction source under regions/<town>/<area>/<asset>/; move reusable primitives into lib/southport3d only when their interface is useful independently of one building. The memorial currently uses a compatibility shim for geometry imports.

Use tools/project.py for ordinary builds. It copies inputs into build/ so report-writing scripts cannot overwrite source recipes. Build/export/render operations write the same Blender file: run them sequentially for a given asset. Blender commands must use --python-exit-code 1 so script failures propagate.

Do not commit downloaded reference images, page captures, browser profiles, credentials, generated textures, Blender files or GLBs. Keep source links, attribution, dates and uncertainty in the asset's research records. Numeric relief source surfaces are intentional source assets, not licence-free substitutes for the works they depict; see RIGHTS.md.

Run python tools/project.py check after staging intended files. For geometry changes, run a full asset build and inspect affected renders. Preserve the distinction between observed dimensions and estimates. Interiors and missing memorial names are deferred until supporting evidence arrives.

Use master. Do not push or publish unless requested. LOD generation and the viewer are future work; do not describe them as implemented.
