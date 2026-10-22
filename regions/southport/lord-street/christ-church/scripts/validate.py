"""Geometric regression checks for actual openings, roof deck and site frame."""
import json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/christ-church.blend'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:
    assert o.data.uv_layers and o.data.polygons,o.name
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
assert len([o for o in objects if o.name.startswith('Envelope tower')])==4
assert len([o for o in objects if o.name.startswith('Louvre paired')])==8
assert len([o for o in objects if o.name.startswith('Clock diamond')])==3
assert len([o for o in objects if o.name.startswith('Window modern hall')])==5
flat=[o for o in objects if o.name.startswith('Roof modern annex flat')]
assert len(flat)==3,'Missing stepped flat annex roofs'
assert len([o for o in objects if o.name.startswith('Window annex rooflight')])==15
assert all(max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)<.19 for o in flat),'Annex roof became pitched'
assert not any(o.name.startswith('Roof modern annex') and 'flat' not in o.name for o in objects)
# Cast through the wall surfaces themselves: openings cannot be pasted on masonry.
for o in objects:
    if not o.name.startswith('Envelope tower'):continue
    for x,y in [(-1.05,16.0),(1.05,16.0),(0,8.2)]:
        hit=o.ray_cast(Vector((x,y,2)),Vector((0,0,-1)),distance=4)[0]
        assert not hit,(o.name,'opening filled',x,y)
front=bpy.data.objects['Envelope tower front']
assert not front.ray_cast(Vector((0,1.2,2)),Vector((0,0,-1)),distance=4)[0]
deck=bpy.data.objects['Roof tower lead deck']
assert deck.ray_cast(Vector((-102.69,-26.4,30)),Vector((0,0,-1)),distance=20)[0],'Missing tower roof face'
world=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
assert min(v.x for v in world)>-116 and max(v.x for v in world)<-75
assert min(v.y for v in world)>-73 and max(v.y for v in world)<-21
assert 22<max(v.z for v in world)<25,'Lost present-day tower silhouette'
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
triangles=sum(len(p.vertices)-2 for o in objects for p in o.data.polygons)
(ROOT/'research/validation.json').write_text(json.dumps({'objects':len(objects),'triangles':triangles,'checks':['four open tower elevations','eight pointed bell windows','three clocks','open main doorway','closed tower roof deck','five modern side windows','finite UV meshes','site bounds','packed authored maps']},indent=2))
print('Christ Church geometry, openings, roof deck and site bounds passed',triangles)
