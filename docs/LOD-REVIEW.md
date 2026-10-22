# LOD pilot review — 2026-10-22

The recipe was built with Blender 5.0.1 and all eight emitted GLBs passed independent checks for geometry counts, coordinate transforms, UV/normal/tangent attributes, opaque PBR materials, embedded image dimensions and file hashes. The omitted fixture produces no GLB or texture. Front and 25-degree oblique comparisons were generated.

| Component | Master triangles | LOD1 triangles | LOD2 triangles | LOD2 GLB KiB |
| --- | ---: | ---: | ---: | ---: |
| doric-column | 38,168 | 3,288 | 604 | 598.6 |
| victory | 252,681 | 88,722 | 2 | 664.6 |
| wwii-inscription | 44,382 | 572 | 284 | 396.4 |
| pedestal | 5,860 | 1,172 | 12 | 537.0 |
| cornice-light | 1,048 | 0 | 0 | 0.0 |

These are per-prototype component results, not totals for the full memorial. One baked column could represent many instances only after checking material/prototype reuse. Textures dominate the small proxies: the uncompressed PNG-in-GLB output is a workflow proof, not a final whole-town bandwidth budget.

## Observations

- Columns retain their base, taper, capital and square abacus. The distant mesh omits flute geometry; the normal map restores its lighting pattern. Small bevels and a neck annulus disappear.
- The regular-grid relief avoids the folded faces found with additional collapse decimation. A 96×160 trial failed the configured 40 mm sampled-error limit; 160×280 passed with about 18 mm maximum sampled error.
- The distant two-triangle relief keeps the rectangular wall-mounted footprint and baked carved contours but loses physical depth, parallax, occlusion and cast shadows. Its maximum sampled distance is about 125 mm, explicitly allowed by the distant representation. It must not be substituted at close range.
- The circular inscription proxy removes boolean lettering topology while preserving the insert outline. Smaller textures soften the lettering; a close reading view must use higher detail.
- The pedestal box preserves its mass and silhouette, with shallow joints in the baked surface. At 512px some fine joints soften and procedural microtexture remains visible.
- The small cornice light is deliberately omitted at both tested reduced levels; this is a reasoned omission, not a bake failure.

## Limits and next steps

The sample-distance metric is not a conservative bound, and no screen-space switching thresholds have been calibrated. Review views show intended approximations; they do not certify appearance at arbitrary distance or grazing angle. Full colonnade/obelisk proxy assembly, merged facade atlases, repeated-instance sharing, metal/glass adapters, compression and viewer integration remain outstanding. The pilot establishes the contract and tested mechanisms; it does not mark whole-memorial LOD coverage complete.

Master build/export/validation also passed after extracting column_geometry.py. The original master parameter values and existing geometry tolerances were retained.
