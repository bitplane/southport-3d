# Published mesh overlap audit

Run the audit against the current local publication:

```sh
python3 tools/audit_published_coplanar.py
```

Requires the existing Python dependencies and a C++17 compiler (`g++`). The
wrapper compiles the small BVH scanner into the output directory. No new Python
packages are required. It reads the published GLBs, verifies their catalog hashes
and triangle counts, applies nested node transforms and catalog placement exactly
as the viewer does, and accounts for mirrored-instance front-face winding. It
never edits or republishes geometry.

Results are generated outside source control in `build/coplanar-audit/`:

- `report.md`: counts, asset queues and the largest candidates.
- `detail.json`, `walk.json`, `district.json`: every grouped finding, exact GLB
  hashes, source node and primitive IDs, triangle examples, surface normals and
  viewer-coordinate locations.
- `catalog.json`: the exact publication snapshot audited.

Use `--output PATH` to preserve a dated run, or `--levels detail` to audit one
level. Run against a stable publication. A missing or changed resource fails the
scan rather than silently skipping it. A run interrupted between levels has only
partial coverage; check the report's level table.

The native scanner uses an AABB hierarchy to find candidate triangle pairs and
then tests parallel normals, distances to both planes and positive-area polygon
intersection. It avoids the small detector's rounded-normal buckets, which can
split nearly equal normals at bucket boundaries. Regression tests compare the
scanner with `tools/coplanar.py` and check transformed, nested and mirrored GLB
instances.

## Using the repair queue

For prevention during new modelling, follow the required
[surface ownership checks](MODELLING-WORKFLOW.md#surface-ownership-checks).
The map-wide audit supplements asset validators; it does not replace prototype
checks, exported-LoD review or inspection of the assembled viewer.

Start with roof, facade and pavement joins that are visible from normal browsing
positions. Use the finding's GLB node name to locate the corresponding generator.
`near_viewer_xyz` is in East/up/south metres and locates the overlap's bounding
boxes; it is an inspection target, not a guaranteed point inside the overlap.
Review the actual model and relevant references before changing dimensions.

A finding is an overlapping primitive pair, potentially containing many triangle
pairs. The same physical defect can appear at all three levels. Pair-area sums
are not union areas and must not be presented as square metres of visible damage.
A single primitive may overlap itself; these findings are retained.

Buried wall bottoms, internal joins, layered carvings and coincident hidden
surfaces can be legitimate or invisible. Confirm visibility before prioritising
or changing them. Fix surface ownership or construction rather than moving faces
by an arbitrary epsilon. Record accepted hidden overlaps with a narrow reason if
we later introduce a regression baseline; never blanket-ignore an entire asset.

After a repair, rebuild, inspect affected views and levels, publish locally when
authorised, and rerun this audit. Compare source node pairs and resource hashes;
numeric finding IDs are ranks within a run and can change when results change.

## Coverage limits

The scanner reads `catalog.json` asset packages. The viewer now renders a 3D Tiles
hierarchy, including merged distant content. A catalog audit alone does not prove
that generated tile content is equivalent or that parent/child replacements are
never rendered together. Check the actual tileset and runtime separately when
investigating flicker after renderer or hierarchy changes.

Each viewing level is scanned as a complete map, including overlaps between
separate assets and parts. Mixed-LoD combinations are not enumerated. The scan
checks same-facing surfaces only; opposite-facing surfaces are excluded even
when a material is double-sided. It does not perform occlusion testing, find
ordinary non-coplanar intersections, or simulate depth-buffer precision at every
camera distance. It therefore reports potential geometric causes of z-fighting,
not every possible flicker and not a list of confirmed visible bugs.

Thresholds are recorded in the report: 20 micrometres of plane separation,
1 square millimetre of overlap, and normal dot product at least 0.99999999.
Triangles below the area threshold do not contribute findings. Degenerate-face
and manifold audits are separate tasks.
