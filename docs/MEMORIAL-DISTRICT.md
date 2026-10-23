# War memorial District envelope pilot

The replacement is authored independently in the memorial's `scripts/district.py`.
It reads the documented site layout, dimensional specification and shaft envelope;
it never counts or simplifies the detailed mesh's vertices. Detail and Walk retain
their existing feature policies. Regional aggregation and impostors remain deferred.

The obelisk uses a tapered square shaft, simplified stepped base and cornice, and
pyramid. Reliefs, engraved letters and masonry are projected onto this envelope.
The colonnades retain sixteen distinct columns each, stepped roofs, open central
porticos, four side window apertures per colonnade, and the chamber entrances.
Columns have eight radial sides and three profile intervals, with simple square
abaci. Flutes and small mouldings become normal-map detail. Broad steps and
chamber plinths retain their different shapes. The four clustered lamps retain
five globes each, and the eight colonnade lamps retain one globe each. Tiny cast
feet, scrolls, rails and mouldings are not separately represented at District.

Repeated columns and lamp surfaces explicitly share atlas keys within each part.
Only one representative is baked per key: overlapping instances are not all
allowed to write the same UV island. Shared-key geometry must be congruent.
This bounds atlas use independently of repeated detailed meshes; repeated weathering
is an accepted approximation. Non-repeated carvings and inscriptions keep their
own receiving surfaces. Source-part isolation prevents accidentally projecting a
neighbouring building or the other colonnade onto a receiver.

Atlas budgets are 256×512 for the obelisk, 512×512 for each colonnade and 256×128
for the clustered lamps, each with colour, tangent normals and roughness. Baking
supersamples each dimension four times, area-averages colour in linear space,
checks source normals before averaging, and renormalises the result. Projected
receivers have split face normals so cages do not round building corners.

Tiny modern metallic obelisk lights and grille fittings are explicitly excluded
from the bake, consistent with the previous District omission policy. The current
adapter supports opaque dielectric materials; unsupported metallic inputs fail
unless a justified omission is recorded. They are never silently converted to
stone. Retaining metal appearance on an important future feature will require a
metalness adapter or separate material.

Hard budgets: 7,000 placed triangles, 2,000,000 total GLB bytes, and 14 MiB estimated
GPU resources. All four GLBs and embedded maps count towards these limits.
Coverage/normal tests and nondegenerate receivers are technical checks, not proof
of visual equivalence. Matching-camera front, end, roof and distant views remain
required. Small engraved text is not intended to be legible at District distance;
Detail retains the original geometry and Walk retains its prior representations.

The migration also separates portable material preparation from legacy export.
Master construction now prepares and packs shaders/UVs. Export reads that master
without resaving it. Generated research manifests are checked stage outputs and
survive subsequent snapshots. Existing structural, inscription, globe-count and
embedded-surface checks still apply to the detailed master/export.

Private baselines and screenshots are under `../output/memorial-district-pilot/`.
The generated comparison can be recreated with:

```sh
python3 tools/create_lod_review.py --asset southport.london-square.war-memorial \
  --baseline ../output/memorial-district-pilot/before
```

Its URL is `/reviews/southport.london-square.war-memorial/index.html` on the local
viewer. Switch versions without moving the camera; inspect wireframe and disable
normal maps to distinguish physical shape from baked relief. This is a review
page, not an additional town-viewer LoD.

## Published technical result

| District version | Placed triangles | GLB bytes including maps | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Previous | 348,682 | 35,420,136 | 59,286,190 |
| Independent envelope | 5,716 | 1,905,508 | 11,688,140 |

The four output parts are 144 obelisk triangles, 1,822 per colonnade and 1,928
clustered-lamp triangles. Four atlas materials replace per-feature maps. Checked
master/export/validation stages were reused on the final packaging run; packaging
took 9m40s and peaked at approximately 3.1 GiB child RSS (GNU time). The corrected
master migration, legacy structural/embedded-map checks, projection checks and
actual exported budgets pass. Detail/Walk policies are unchanged; regenerating
Boolean geometry can alter triangulation slightly, so byte identity is not claimed.

Visual acceptance is assigned to the user by their explicit instruction. No new
manual visual review or silhouette comparison is claimed for this memorial pilot.
The old District package is retained privately for same-camera comparison.
