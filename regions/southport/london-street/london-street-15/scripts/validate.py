"""Check apertures, closed roofs, footprint registration and the open side alley."""
from pathlib import Path
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
repo = Path(os.environ['SOUTHPORT_REPO_ROOT'])
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'models/london-street-15.blend'))
D = json.loads((ROOT / 'research/layout.json').read_text())
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source == 'FILE')
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()

# Every leaded window is the first thing a ray from the street meets.
windows = [o for o in meshes if o.name.startswith('Window ')]
assert len(windows) == 4, [o.name for o in windows]
for o in windows:
    origin = o.matrix_world @ Vector((.21, .13, 1.5))
    direction = (o.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    hit, p, n, i, found, m = scene.ray_cast(deps, origin, direction, distance=2)
    assert hit and found == o, (o.name, found.name if found else None)

# Shop arches are closed by glazing/joinery within half a metre of the face.
shop = bpy.data.objects['Shop rendered arcade'].matrix_world
for a, b in D['arches']:
    for u in [a + .2, (a + b) / 2 + .05, b - .2]:
        for h in [.2, 1.2, D['arch_spring'] + .3]:
            hit, p, n, i, found, m = scene.ray_cast(
                deps, shop @ Vector((u, h, 1)), (shop.to_3x3() @ Vector((0, 0, -1))).normalized(), distance=1.5)
            assert hit, (u, h, 'open shop arch')

for name in ['Roof main clay shell', 'Roof north bay clay shell']:
    bm = bmesh.new()
    bm.from_mesh(bpy.data.objects[name].data)
    assert all(e.is_manifold for e in bm.edges), name
    bm.free()

points = [(o.name, o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
natwest = json.loads((repo / 'regions/southport/london-square/natwest/research/layout.json').read_text())
assert max(p.y for _, p in points) <= natwest['rear_y'] - .01, 'intrudes into NatWest'
assert min(p.y for _, p in points) >= D['alley_south_y'] - 1e-4, 'crosses into William Hill'
assert max(p.x for _, p in points) <= D['rear_x'] + 1e-4
assert min(p.x for _, p in points) > D['front_x'] - 1.2, 'projects too far over the pavement'
# Ridge at about 11m; the stack and pots stand about 2.2m above it.
assert 11.9 < max(p.z for _, p in points) < 13.5

# The alley stays open: only roof overhangs/eave brackets sit above it, and a
# ray from the pavement runs its length to the estimated rear closure.
for name, p in points:
    if name.startswith(('Rear alley', 'Envelope alley rear end')):
        continue
    # Facing timbers may stand 6cm proud above the shop storey; nothing else
    # enters the alley below the eaves.
    if p.y < D['south_y'] - .1 or (p.y < D['south_y'] - 1e-3 and p.z < D['base_z'] + 3.4):
        assert p.z > D['base_z'] + 5.5, (name, tuple(p), 'obstructs the side alley')
mid = (D['south_y'] + D['alley_south_y']) / 2
for h in (.3, 1.0, 1.7):
    origin = Vector((D['front_x'] - 1, mid, D['base_z'] + h))
    hit, p, n, i, found, m = scene.ray_cast(deps, origin, Vector((1, 0, 0)), distance=40)
    assert hit and found.name.endswith(('alley rear end', 'Rear alley timber gate')), (h, found and found.name)
    assert p.x > D['rear_x'] - .5, (h, p.x)

# Remaining placeholder boxes must not overlap this building or its alley.
placeholders = json.loads((repo / 'regions/southport/london-street/east-side-placeholders/research/layout.json').read_text())
for block in placeholders['blocks']:
    (x0, x1), (y0, y1) = block['x'], block['y']
    overlap = min(x1, D['rear_x']) - max(x0, D['front_x']), min(y1, D['north_y']) - max(y0, D['alley_south_y'])
    assert min(overlap) < 1e-4, ('placeholder overlaps 15 London Street', block['name'])

report = {
    'mesh_objects': len(meshes),
    'leaded_windows': len(windows),
    'checks': 'Finite UV meshes, packed authored maps, unobscured leaded windows, closed shop arches, '
              'two manifold clay roof shells, NatWest/William Hill/placeholder clearance, open side alley.',
}
(ROOT / 'research/validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(report)
