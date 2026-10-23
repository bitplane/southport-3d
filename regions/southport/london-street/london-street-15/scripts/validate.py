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
assert len(windows) == 5, [o.name for o in windows]
for o in windows:
    origin = o.matrix_world @ Vector((.21, .13, 1.5))
    direction = (o.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    hit, p, n, i, found, m = scene.ray_cast(deps, origin, direction, distance=2)
    assert hit and found == o, (o.name, found.name if found else None)

# The two photographed oriels have matching front windows; the centre is
# genuinely recessed. Check exported master geometry, not only recipe values.
left = bpy.data.objects['Window first floor left']
right = bpy.data.objects['Window first floor right']
def width(obj):
    return max(v.co.x for v in obj.data.vertices) - min(v.co.x for v in obj.data.vertices)
assert abs(width(left) - width(right)) < .001
assert abs(left.matrix_world.translation.x - right.matrix_world.translation.x) < .001
# Sample across the small attic aperture: the roof/bargeboard must clear it.
attic = bpy.data.objects['Window bay top storey']
for u in (-.30, 0, .30):
    for v in (-.17, 0, .17):
        origin = attic.matrix_world @ Vector((u, v, 1.5))
        direction = (attic.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        hit, p, n, i, found, m = scene.ray_cast(deps, origin, direction, distance=2)
        assert hit and found == attic, ('attic occluded', u, v, found and found.name)
centre = bpy.data.objects['Envelope first floor centre recess']
assert centre.matrix_world.translation.x - left.matrix_world.translation.x > .45

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
assert min(p.x for _, p in points) > D['front_x'] - 1.4, 'projects too far over the pavement'
# Highest point is the gable finial: no chimney exists on this building.
assert D['base_z']+D['ridge_height'] < max(p.z for _,p in points) < D['base_z']+D['ridge_height']+.2
assert not any('chimney' in o.name.lower() for o in meshes)

# The alley stays open: only roof overhangs/eave brackets sit above it, and a
# ray from the pavement runs its length to the estimated rear closure.
for name, p in points:
    if name.startswith(('Rear alley', 'Envelope alley rear end')):
        continue
    if name=='Shop alley panelled return':
        assert p.y >= D['south_y']-.10, (name,tuple(p),'panel projects into alley')
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

# The narrow roof is a lean-to against NatWest, not a pitched strip with a
# middle ridge. Its central run rises monotonically towards the party wall.
roof=bpy.data.objects['Roof north bay clay shell']
for x in (8.5,9.2,10.0):
    heights=[]
    for t in (.1,.3,.5,.7,.9):
        y=D['north_y']-D['bay_width']+t*(D['bay_width']-.02)
        hit,p,n,i=roof.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),distance=20)
        assert hit,('Missing lean-to roof',x,y)
        heights.append(p.z)
    assert all(b>a+.1 for a,b in zip(heights,heights[1:])),heights
assert 'Roof north bay ridge tiles' not in bpy.data.objects
assert all('Window first floor '+side+' return' in bpy.data.objects for side in ('left','right'))

# Equal roof pitches and short measured plan depth, independent of facade trim.
roof=bpy.data.objects['Roof main clay shell']
xs=[v.co.x for v in roof.data.vertices]
assert abs(max(xs)-min(xs)-D['main_roof_depth'])<.001
ycentre=D['north_y']-D['gable_centre']
for offset in (.7,1.8,3.0):
    heights=[]
    for sign in (-1,1):
        hit,p,n,i=roof.ray_cast(Vector((8.0,ycentre+sign*offset,20)),Vector((0,0,-1)),distance=20)
        assert hit
        heights.append(p.z)
    assert abs(heights[0]-heights[1])<.001,heights
assert len([o for o in meshes if o.name.startswith('Rear rooflight ')])==9
# Arc edges must close at oblique as well as perpendicular viewing angles.
for a,b in D['arches']:
    radius=((b-a)**2/4+D['arch_rise']**2)/(2*D['arch_rise'])
    half=math.asin((b-a)/2/radius)
    for k in range(1,20):
        angle=-half+2*half*k/20
        u=(a+b)/2+(radius-.095)*math.sin(angle)
        h=D['arch_spring']+D['arch_rise']-radius+(radius-.095)*math.cos(angle)
        for oblique in (-.6,0,.6):
            target=Vector((u,h,-.22))
            origin=target+Vector((oblique,0,1.2))
            direction=(target-origin).normalized()
            hit,p,n,i,found,m=scene.ray_cast(deps,shop@origin,(shop.to_3x3()@direction).normalized(),distance=1.5)
            assert hit and (shop.inverted()@p).z > -.30,(u,h,oblique,found and found.name)

# Reported adjoining surfaces have separate ownership (large-overlap regression).
import sys,os
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
triangles=[];labels=[]
for name in ('Envelope short north party wall', 'Shop entrance porch'):
 ob=bpy.data.objects[name];ob.data.calc_loop_triangles()
 for t in ob.data.loop_triangles:
  points=[tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]
  # The 0.01 m² common bottom patch is buried at z=.62, below the
  # .785 m pavement/porch floor. The map-wide audit still records it.
  if all(abs(p[2]-D['bury_z'])<1e-5 for p in points):continue
  triangles.append(points);labels.append(name)
# The full published audit still records sub-centimetre-square rounding slivers.
errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
assert not errors,errors[:8]
print('Reported wall/return surface ownership verified')

# Roof-side and red-wing corners must not duplicate their end-wall skins.
for pair in [('Envelope north roof rear wall','Envelope short north party wall'),
             ('Envelope red wing alley wall','Envelope red wing rear wall')]:
 triangles=[];labels=[]
 for name in pair:
  ob=bpy.data.objects[name];ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(name)
 errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
 assert not errors,(pair,errors[:8])
print('Rear wall corner ownership passed')
