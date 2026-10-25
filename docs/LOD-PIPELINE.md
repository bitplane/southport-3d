# Reasoned LOD construction and baking

An LOD is a different representation of a building, not a percentage of its polygons. Start with the volumes, openings and silhouette that remain visible at the intended scale. Decide what each feature contributes, then choose its representation. Textures can carry appearance; they cannot restore a missing silhouette, an open arcade, parallax or cast-shadow geometry.

## Default for new buildings and the current rollout

Retain Detail for close inspection and Walk for exploration. **Replace District**
with an independently authored, fixed-budget envelope; do not add another permanent
per-building LoD. Existing per-feature District recipes are legacy intermediate
representations until converted. Distant block/district aggregation is a separate,
future tier that replaces multiple individual assets together.

Plan the envelope when establishing the footprint and main roof/openings. Finalise
it against the reviewed detailed model, sharing dimensional inputs where useful
but not inheriting the detailed mesh topology. New ornament changes baked appearance,
not envelope face counts or texture sizes. Significant roof/footprint/opening changes
require revisiting the envelope. Avoid replacing each tiny source object with its
own box: that scales with detail, duplicates textures and creates intersections.
A polygonal bay should be one coordinated envelope with adjoining faces.

Provisional per-building triangle targets, to be tested at intended screen sizes:

| Type | District triangles | Typical maximum atlas dimension |
| --- | ---: | ---: |
| Simple shop/unit | 100–500 | 256–512 |
| Ornate corner building | 500–1,500 | 512–1,024 |
| Large church/landmark | 1,000–3,000 | 512–1,024 |

These are design targets, not a mandate to damage a silhouette. A multi-building
ensemble may have a justified larger combined budget (the memorial is capped at
7,000). Each asset declares enforced triangle, total GLB-byte and estimated GPU
budgets. Include all embedded maps and duplicated part resources. Texture memory
and material/draw-call counts matter even when triangle counts are tiny. Prefer
one bounded atlas material per streaming part, with shared appearance only where
it is justified. Keep source texture resolution independent of exported atlas size.

Before launching a bake, calculate the atlas memory floor: the current three-map
RGBA colour/normal/roughness set with mipmaps costs approximately `16 × width ×
height` bytes per part. Sum all parts and allow additional space for mesh buffers;
a compressed GLB can be much smaller than its decoded GPU allocation. A budget
below that floor cannot pass, regardless of how simple the mesh is.

Use geometry for negative spaces, roof outline, large projections and distinct
columns. Use low-sided tapered cylinders with coarse capitals for isolated round
columns, rectangular prisms for square piers, and surface bakes for shallow attached
features. Do not fill an open colonnade or courtyard just to meet a budget. Surface
normal maps cannot restore missing silhouettes, through-openings or cast shadows.
Height/parallax mapping is optional future work, not a prerequisite for this pipeline.

Declare receiving surfaces and source groups explicitly. Keep unrelated buildings
and nearby opposite surfaces out of the projection group. Choose cages for the
actual feature depths; record any unsupported-material omissions. Bake colour
without illumination, normal and roughness, then supersample/downsample carefully
so thin frames and glyph strokes fade consistently. Validate receiver coverage,
finite/valid normals before and after filtering, nondegenerate geometry and actual
exported costs. Passing those checks does not certify architectural fidelity.

Ordinarily compare matching front, oblique, roof and rear views and actual viewing
transitions. For the current rollout, the user explicitly owns visual acceptance:
retain technical checks, publish each finished asset, provide measured before/after
costs, and leave visual acceptance pending the user's review. Do not spend long
render/browser passes on every asset or claim those comparisons happened. New
architectural modelling still follows the evidence workflow.

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

## Streaming assembly

The commands above retain the original component experiment. For the complete viewer build, use `python tools/project.py publish` and the [publication contract](VIEWER.md). publication.json groups compatible instances, classifies every exported object, retains explicit architectural envelopes where appropriate, and assembles Detail/Walk/District streaming parts. Spatial streaming cells are implemented; merged regional LoDs remain deferred.

For long shop signs, inspect the result in the actual viewer as well as the bake
PNG. Stretching a square atlas over a thin panel creates unequal texel density;
isotropic mip filtering can erase otherwise sharp letters. The viewer now uses
device-limited anisotropic filtering (up to 16). Check both front and oblique
views and retain this sampling policy in other viewers. Rectangular sign atlases
would also reduce wasted texture allocation in a future packing pass.


## Fixed District envelope pilot

BHF now replaces its previous District model using an optional `district_envelope`
publication recipe. Its generator returns authored quad surfaces per streaming
part, in asset coordinates. The shared `tools/blender_envelope.py` packs aspect-
correct, non-overlapping rectangles into fixed-size atlases, projects the selected
source onto split-normal receivers, supersamples and area-downsamples colour,
normal and roughness maps. Sharp corners do not share inflated cage normals.
Normals use glTF tangent-space +Y; colour is averaged in linear space. Source
material support is currently opaque dielectric only. Height/parallax maps are
not implemented. One material per part bounds draw calls independently of detail.

The replacement must cover every part. Source meshes still pass complete rule
classification; the whole-envelope recipe supersedes District per-object actions.
Explicit triangle, total download and estimated GPU budgets fail publication if
exceeded. Detail and Walk use the existing recipes. Inputs, generators and bakes
are traced/cached through the ordinary package stage. Failed bakes leave the last
published catalog intact. Receiver pixel coverage and valid normals are only
heuristics; inspect front, oblique, roof and rear comparisons at the intended
screen size, not just close screenshots or a successful build.

Establish a verified footprint, roof and large openings first. Author the envelope
from those dimensions, never from an automatically simplified detailed mesh.
Adding windows, lettering or mouldings must not add envelope topology or enlarge
atlases. Test this independence. Rebake appearance when detailed surfaces change;
review the envelope when major geometry changes. Preserve negative spaces and
silhouette with geometry, even when their surfaces are baked. Record omissions,
projection distances, budgets, before/after costs and actual visual comparisons.
BHF establishes the facade case; the memorial exercises open colonnades and shared columns. This is not automatic quality certification for other buildings.

`tools/create_lod_review.py --asset ID --baseline DIRECTORY` generates a private
local review page from the previous package and current checked package. Switch
models without moving the camera; compare wireframe and normal maps. Generated
review GLBs/images/pages stay outside Git. See BHF's asset documentation for the
first measured result. Regional aggregation and impostors remain separate work.

The [memorial pilot](MEMORIAL-DISTRICT.md) records the second fixed-envelope result,
including shared column atlas islands and explicit metallic-fitting omissions.

For new envelope generators, `blender_envelope.Surfaces` supplies small quad,
triangle, box and hip helpers. These consume authored dimensions, not detailed
mesh topology. A face can set `cage_m` below its part's maximum for tightly spaced
features such as chimney pots; use this to prevent rays crossing neighbouring
features. Reflected local coordinate frames must reverse winding after the
geographic transform. Preserve courtyards and recesses explicitly instead of
baking them onto a filled bounding box.

Preflight every part's receiver geometry, source material support and triangle
budget before beginning texture bakes. The shared baker now does this for the
whole asset, so a malformed late part fails immediately rather than after earlier
parts have spent minutes baking. Coplanar overlap reports remain candidates to
inspect; a valid UV layout or normal bake does not prove that adjacent envelopes
have only one visible surface.

## Repeatable envelope rollout

1. Save the existing package manifest and District GLBs outside Git for the
   before/after comparison. Read the researched layout and current source shape;
   this pass does not silently correct or reinterpret architectural estimates.
2. Author `scripts/district.py` using verified dimensions and bounded topology.
   Configure `district_envelope` groups, cages, omissions and fixed budgets in
   `publication.json`. Retain Detail/Walk policies.
3. Build the master, then run the shared preflight without rendering or baking:

   ```sh
   python3 tools/project.py build ASSET_ID --stage all --threads 8
   blender -b --factory-startup --threads 8 --python-exit-code 1 \
     --python tools/blender_envelope.py -- \
     --asset regions/southport/AREA/ASSET \
     --output ../output/ASSET-envelope-preflight.json
   ```

   This uses the baker's actual material, geometry, budget and atlas preparation,
   then samples projection rays. Investigate named faces with misses; do not
   increase a cage blindly, since it may hit an unrelated surface. Tiny-grid ray
   sampling is diagnostic and does not replace actual bake coverage/normal checks.
   Rebuild the master after architectural source changes before trusting the probe.
   Inspect coplanar candidates as well; the projection test does not detect them.
4. Publish only that asset with `python3 tools/project.py publish --asset ASSET_ID
   --threads 8`. Package validation still checks actual exported costs and bakes.
   Wait for the catalog lock if another agent is publishing; do not delete locks.
5. Generate the owner's comparison page with `python3 tools/create_lod_review.py
   --asset ASSET_ID --baseline BASELINE_DIRECTORY`, record measured results and
   omissions in the building document, then stage intended source, run `check`
   and commit. Owner visual acceptance remains pending until actually received.

Practical lessons from the rollout:

- Repeated painted columns should share atlas islands when their shapes and
  appearance agree. A genuine metric prototype avoids tiny differences from
  geographic warping; test congruency after float32 conversion, not just in Python
  doubles. Do not share islands across different lettering or material patterns.
- A long plain beam can force every island to become tiny in an aspect-correct
  atlas. Lower its `weight` relative to important surfaces, or split it at real
  structural spans. Verify usable interior pixels before paying for a bake.
- Transparent glass and metallic materials need explicit treatment; the current
  envelope baker supports opaque dielectric surfaces. Preserve open canopy/arcade
  geometry and document distant omissions instead of projecting a solid sheet.
- Respect local coordinate frames and winding, especially mirrored facades and
  frames whose second coordinate is height. Several false overlaps came from
  applying world-axis box-face exclusions to these local frames.
- Build valleys from a few authored roof volumes or analytic planes. Remove
  numerical degenerate triangles before exporting; never inherit the detailed
  roof's decorative tessellation. Clip shared boundaries so one visible surface
  owns each location.
- Compare actual GLB and GPU totals across all three levels. A per-sign bake can
  make Walk use more memory than Detail even while its triangle count falls.
  Retain inexpensive glyph geometry or use a bounded shared atlas when separate
  textures cost more than the geometry they replace.
- Migrate asset-specific appearance guards when replacing per-feature bakes.
  Require complete envelope map coverage/normal checks instead of obsolete
  per-window prototypes. Declare each `publication_checks` script under
  `build_inputs.validate` as well, so a guard change refreshes the isolated
  runtime script even when the master and package are reused.
- Source snapshots must stay fixed throughout packaging. Coordinate shared-tool
  edits between active bakes; an otherwise successful bake is rejected if its
  inputs change. Failed packages leave the previous published catalog intact.

### Straight-sided component bake cages

For a shallow architectural box replacement, inspect the baked border from an
oblique angle: an automatic cage around welded box corners can project sideways
and curve otherwise straight mullions. A baked `replace`/`box` action with `box`
UVs can opt into `"bake_projection": "face-normal"`. This gives each receiver face
its own vertices before triangulation, preserving the closed geometric envelope,
12 triangles and atlas layout while preventing averaged corner ray directions.
It does not increase texture resolution or retain the detailed source mesh.
Use this for planar architectural faces, not smooth cylindrical forms. The
Blender regression is `tests/blender_bake_projection.py`; also inspect a real
prototype bake and the assembled exported Walk asset. Unchanged actions retain
the existing projection behaviour.
