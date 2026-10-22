# Agent instructions

Read README.md and the relevant asset.json before changing a building. Use the model-southport skill for research/modelling work. CLAUDE.md points to these same instructions.

Use metres and retain each asset's documented coordinate origin and orientation. Keep construction source under regions/<town>/<area>/<asset>/; move reusable primitives into lib/southport3d only when their interface is useful independently of one building. The memorial currently uses a compatibility shim for geometry imports.

Use tools/project.py for ordinary builds. It copies inputs into build/ so report-writing scripts cannot overwrite source recipes. Build/export/render operations write the same Blender file: run them sequentially for a given asset. Blender commands must use --python-exit-code 1 so script failures propagate.

Do not commit downloaded reference images, page captures, browser profiles, credentials, generated textures, Blender files or GLBs. Keep source links, attribution, dates and uncertainty in the asset's research records. Numeric relief source surfaces are intentional source assets, not licence-free substitutes for the works they depict; see RIGHTS.md.

Run python tools/project.py check after staging intended files. For geometry changes, run a full asset build and inspect affected renders. Preserve the distinction between observed dimensions and estimates. Interiors and missing memorial names are deferred until supporting evidence arrives.

Plan LODs while constructing each feature. Read docs/LOD-PIPELINE.md: each component/level needs a reasoned omit, replace, generator or decimate decision. Start distant models from simple envelopes while preserving major openings and silhouette. Global decimation ratios are not a substitute for these decisions. Add generator controls and replacement geometry as the feature is authored, then run the declared baked levels and inspect front/oblique comparisons. Any incomplete coverage must be explicit.

Use master. Do not push or publish unless requested. A baked component-LOD pilot exists; full-building LOD coverage, publication and the viewer remain future work. Do not overstate coverage.
