# Reasoned LOD construction and baking

An LOD is a different representation of a building, not a percentage of its polygons. Start with the volumes, openings and silhouette that remain visible at the intended scale. Decide what each feature contributes, then choose its representation. Textures can carry appearance; they cannot restore a missing silhouette, an open arcade, parallax or cast-shadow geometry.

## Make four explicit choices

| Strategy | Use it when | Examples |
| --- | --- | --- |
| **Omit** | The feature is insignificant at the intended scale and does not define the silhouette or a recognisable colour patch. | Small fittings, hidden backing, bevels and minor ironwork. Record the omission; do not let it vanish accidentally. |
| **Replace** | A simpler authored shape describes the visible envelope better than collapsing the detailed mesh. Bake onto that shape. | Bounding box for a plain pedestal, shallow panel for wall-mounted carving, solid disc for engraved lettering, tapered prism for an obelisk, roof wedges and wall volumes for a building. |
| **Generator controls** | The topology has a known construction and detail can be removed without losing its dimensions or important profiles. | Fewer rings on a tapered shaft, fewer radial segments, flute geometry replaced by a normal map, simpler moulding profiles, fewer window subdivisions. |
| **Decimate** | Irregular geometry has no better simple construction and measured/visual tests show collapse preserves the needed form. | Selected organic relief or masonry surfaces. It is an explicit choice, never a fallback for unclassified parts. |

Use combinations within a building and change strategies between levels. A facade may retain window recess geometry nearby, use solid wall panels with baked windows farther away, and merge with a coarse building volume at long range. Keep through-openings and recognisable negative space as geometry until they truly disappear on screen. A whole colonnade is not a solid box: keep its roof, end chambers and coarse columns separated.

For bounding-volume proxies, author the envelope deliberately. An automatic axis-aligned box is appropriate only for a genuinely box-like part. Roofs, spires, arches and tapered monuments need corresponding proxy shapes. Keep the original origin, dimensions and placement. Bake source features onto their actual replacement surface; do not bake independent feature atlases and leave the expensive geometry in place.

## Working command

The current pilot supports opaque dielectric parts and records deliberate omissions. It uses background Blender, with no additional MCP or paid tool.

```sh
python tools/project.py build southport.london-square.war-memorial
python tools/project.py lod southport.london-square.war-memorial
python tools/check_lods.py build/southport.london-square.war-memorial/lods
chafa build/southport.london-square.war-memorial/lods/comparison.png
chafa build/southport.london-square.war-memorial/lods/comparison-oblique.png
```

A matching master build is required. Editing lod.json or the baking helper does not require rebuilding the master; changing a geometry generator does. Work runs in lod-work/ and replaces lods/ only after all checks succeed. Failed work and logs remain for diagnosis; the next run clears failed work. Do not overlap writers for one asset. The master is never overwritten by LOD generation.

## Recipe contract

Add lod.json beside asset.json. Every target has an exact source object, a stable ID, a review direction and an **action with a reason at every level**. There is no global geometry ratio. Texture sizes belong to levels; shape/detail controls belong to individual actions.

Supported actions:

- `omit`: no GLB, image or material allocation. The manifest retains the decision and reason.
- `replace`: `box` uses the local bounds and a six-face atlas; `panel` uses the front face of the bounds with planar UVs; `lathe` uses an explicit profile and segment count. A panel is only suitable for a wall-mounted surface; it has no back or thickness. The disc adapter splits front/back/side UV regions.
- `generator`: `heightfield` resamples asset-local numeric relief data into a regular grid; `module:function` calls an asset generator with `(name, settings, asset_directory)` and expects a Blender object in local source coordinates. The memorial's column_geometry.py is a tested example shared by master and LOD builds.
- `decimate`: an explicit per-component ratio and UV strategy. The tests demonstrated why this is unsuitable as a universal default: it damaged lettering and produced folded relief faces.

Each non-omitted action declares a UV layout and projection cage distance and sampled-error limit in metres (these may inherit from its target). Values are design budgets for a feature, not universal defaults. Planar UVs require a front-facing heightfield. Source surfaces and a proxy can differ substantially by design: the distant relief panel intentionally gives up physical depth. Its larger allowed geometric error must be considered when choosing a future viewing threshold.

Use `scope: component-pilot` for incomplete coverage. `scope: asset` currently checks every object in the memorial's numbered export collections; a new building workflow needs its own explicit export-selection adapter. Unsupported material channels fail instead of silently losing glass, emission, alpha or metalness. The current pilot is not a full town-ready publisher.

## Bake contract

Isolate source/replacement pairs, evaluate source modifiers, triangulate targets before baking, and retain that triangulation through export. Source UVs may tile; target atlas UVs must not overlap. Do not let huge numbers of tiny UV islands consume the atlas padding budget: choose planar, box or cylindrical layouts where the feature permits them.

Bake base colour without direct/indirect lighting, tangent-space +Y normal, and roughness. Colour is sRGB; normal/roughness are non-colour. Export normals, UVs and tangents; glTF packs roughness into its material texture. The current opaque stone adapter fixes metalness at zero and rejects unsupported materials. These conventions follow Blender's [selected-to-active baking documentation](https://docs.blender.org/manual/en/latest/render/cycles/baking.html), tested with Blender 5.0.1.

Projection distances are feature-specific. Too small misses carving; too large can hit the back or another face. Non-uniform source transforms and steep relief need particular care. Valid-length normal pixels are only a heuristic, not proof that rays hit the intended surface. Normal maps cannot supply ambient occlusion or cast shadows lost with geometry; do not hide those limits by baking directional illumination into base colour.

## Completion and review

1. Plan component decisions while authoring each building. State why a part is omitted, replaced, parameterised or decimated. Add matching implementation/recipe controls as the feature is built.
2. Keep master validation passing. Build all declared levels and review front **and oblique** comparisons, at intended projected sizes. Check openings, roofline, silhouette, seams, lettering, texture density and changes between levels.
3. Record unique and placed triangles, texture sizes, file bytes, bounds, transforms and approximation measurements. The validator reads actual GLBs and embedded textures; it does not trust Blender-side counts alone.
4. Reuse prototypes deliberately. Shared geometry does not automatically imply shareable baked appearance. Avoid an atlas per repeated column when expanding this pilot to the complete scene. Shared baking, atlasing and instance assembly need a separate adapter.
5. Include source recipes, reasoning and review findings in the PR. Generated GLBs/maps/renders stay out of Git. A new building is not LOD-complete while components are unclassified; document any agreed deferral explicitly.

The manifest records decisions, source/recipe/baker hashes, Blender version, bounds, file sizes, textures and sampled distances. GLBs retain placement with glTF Y-up conversion; report bounds are Blender world Z-up metres. Sampled distances are not conservative error bounds. Do not infer guaranteed screen-space switching distances from them. Compression, aggregate instance assembly, screen-space thresholds and publication remain subsequent stages.
