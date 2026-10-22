# LOD audit: memorial construction

Measured from the evaluated Blender master on 2026-10-22:

| Quantity | Count |
| --- | ---: |
| Exportable placed objects | 310 |
| Distinct source mesh/curve datablocks | 179 |
| Triangles counted once per datablock | 2,476,229 |
| Triangles across placed instances | 9,443,854 |
| One fluted column | 38,168 |
| All 32 columns | 1,221,376 |
| Southport arms relief | 348,795 |
| Victory figure | 252,681 |
| WWII circular insert with engraved lettering | 44,382 |

The unique count is grouped by source datablock in this master; it is not a general GPU memory estimate. Modifiers, material splits, UV seams, exporter behaviour and node instancing can change costs. The generated inventory lists individual objects and evaluated triangles. Count both unique geometry and placed triangles when reporting performance.

## Mechanisms and suitable uses

| Source | Existing mechanism | LOD treatment |
| --- | --- | --- |
| `lib/southport3d/geometry.py` | Explicit lathe segments, tube sides, ring sections, ellipsoid rings, text resolution and bevels | Parameterise these at the feature/caller level, with explicit reasons for which controls change. Preserve profile changes and silhouette; never globally divide every segment count. |
| `build_memorial.py:column` | Shared mesh for 32 columns; 160 shaft segments, 65 longitudinal profile rings, 20 flutes | Strong reuse opportunity. The shared column_geometry generator now exposes axial rings, radial segments, flutes and small mouldings. Master defaults preserve the original mesh; distant shafts retain the taper and capital while moving flutes to normal maps. |
| `sculpt_surface.py:simplify_relief` | Collapse modifier plus sampled error checks against source NPZ surfaces | Already reduces master reliefs, not a distance LOD. Keep its master tolerances unchanged. Additional LOD reduction needs separate tolerances and high-to-low normal baking. |
| `reliefs.py`, relief NPZ files | Dense continuous carving surfaces; repeated ornaments share meshes | Retain depth and outline in low mesh; transfer fine surface shading into tangent normals. A flat card loses parallax and silhouette. |
| `wwii_roundel.py`, `engrave` | Geometry cut-outs for lettering, circular insert and separate radial reeding | Test lettering through a normal bake. Retain high detail where readable. The pilot insert excludes the separate surrounding reeding. |
| `ornamental_lamps.py` | Many explicit 48+ segment lathes, decorative mesh parts | Simplify curved profiles and remove tiny fixtures by distance. Metal/glass need a separate material adapter; the current baker rejects them. |
| `shaft_masonry.py`, `pedestal_joints.py`, `colonnade_envelope.py` | Individual blocks, recessed joints, carved profiles and bevelled edges | Keep envelope, openings, roof edges and cornices. Transfer shallow joints/bevel shading to maps only when their silhouettes remain acceptable. |
| `export_assets.py` | 512px procedural stone bakes on a plane, metre-scale projected UVs | Portable materials already exist. These tiled/overlapping UVs are unsuitable as unique target atlases; new LOD meshes receive non-overlapping atlas UVs. |
| `obelisk_surfaces.py`, `exterior_weathering.py` | Authored UV surfaces and location-dependent material colour/roughness | Bake evaluated materials, not bare unweathered recipes. Reusing an atlas across instances may repeat weathering or use the wrong location; inspect before sharing. |

## Implemented experiment

`lod.json` defines two levels with a reasoned action per component: generator controls for columns, a sampled heightfield then a flat envelope panel for Victory, replacement discs for lettering, decimation then a bounding box for the pedestal, and deliberate omission of a small light fixture. The reusable baker evaluates source modifiers, builds the chosen replacement, triangulates, assigns an appropriate atlas, bakes colour/normal/roughness, exports GLBs and measures sampled surface error. A separate reader verifies the exported GLB geometry, transforms, embedded textures and file hashes. Review images compare master, reduced geometry without its normal map, and the baked result.

This is a component pilot, not complete memorial LOD coverage. It establishes the repeatable contract before extending to every component. Full-building export, additional building-envelope generators, shared prototype/instance baking, draw-call reduction, KTX2/mesh compression, conservative screen-space error bounds and streaming remain future work. The column construction was extracted into a shared master/LOD generator with its original master settings preserved; master geometry thresholds remain unchanged.

For future buildings, declare LOD components while designing their geometry, reuse prototypes deliberately, and run the recipe as part of completion. See [the working pipeline](LOD-PIPELINE.md).

## Whole-memorial representation plan

These are design decisions to implement beyond the component pilot, not claims of full coverage:

| Feature | Intermediate representation | Distant representation and reason |
| --- | --- | --- |
| Obelisk | Tapered shaft, stepped base, major cornices; reduced surface detail | Tapered prism and a few stepped volumes. Bake masonry, inscriptions and panels into faces; keep the pointed top and characteristic outline. |
| Colonnade roofs and end chambers | Preserve major mouldings, door/window openings and roof shape | Compound roof/wall volumes. Do not fill the open arcade or spaces between columns with a bounding box. |
| Columns | Fewer axial rings and flute-aware radial samples | Coarse tapered cylinders plus base/capital/abacus. Retain count and spacing; flute shading moves to normals. |
| Sculptures and decorative plaques | Coarse relief geometry with baked fine carving | Wall-mounted envelope panels or decoration baked into the parent wall atlas; no independent deep relief when subpixel. |
| Lettering | Retain readable master cuts at close range | Solid receiving surface plus colour/normal maps; drop text-specific geometry. |
| Bevels, mortar and shallow mouldings | Reduce bevel/profile sampling | Bake shading where useful; omit subpixel grooves. Keep large cornices that affect silhouette/shadow. |
| Lamps | Coarse poles and broad lantern shapes with appropriate metal/glass materials | Keep distinctive clustered silhouettes if visible; remove brackets, fasteners and tiny fittings. |
| Hidden/internal detail | Exclude from exterior publication where never visible | Omit; do not allocate invisible triangles or atlas space. |

For an ordinary building, start with massing volumes and roof forms, then decide whether doors, windows, bays, awnings and shop signs still affect outline, openings or identity. Bake facade detail onto those volumes. Geometry hierarchy and semantic feature boundaries should make those decisions possible without rediscovering the building after completion.

The measured results and visual limitations are recorded in [LOD-REVIEW.md](LOD-REVIEW.md).
