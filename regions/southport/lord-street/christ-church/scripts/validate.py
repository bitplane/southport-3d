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
assert len([o for o in objects if o.name.startswith('Roundel diamond')])==3
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
(ROOT/'research/validation.json').write_text(json.dumps({'objects':len(objects),'triangles':triangles,'checks':['four open tower elevations','eight pointed bell windows','three roundel windows','open main doorway','closed tower roof deck','five modern side windows','finite UV meshes','site bounds','packed authored maps']},indent=2))
print('Christ Church geometry, openings, roof deck and site bounds passed',triangles)

# The cafe has a real glazed opening, a round corner and a separate raised porch.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
front=bpy.data.objects['Envelope cafe front']
for u,h in [(1.1,1.4),(2.3,1.4),(4.2,1.4),(2.5,2.6)]:
    origin=front.matrix_world@Vector((u,h,2))
    direction=front.matrix_world.to_3x3()@Vector((0,0,-1))
    hit,p,n,i,ob,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=4)
    assert hit and ob.name.startswith('Window cafe glazing'),('Cafe glazing blocked',u,h,ob.name if hit else None)
assert len([o for o in objects if o.name.startswith('Envelope cafe curved brick')])==24
cap=bpy.data.objects['Roof cafe rounded flat'];porch=bpy.data.objects['Roof cafe entrance canopy']
assert min(v.co.z for v in porch.data.vertices)>max(v.co.z for v in cap.data.vertices)+.1
assert max(v.co.x for v in porch.data.vertices)<min(v.co.x for v in cap.data.vertices)-.1
# Close the formerly exposed hall side above the lower flat annex.
side=bpy.data.objects['Envelope cafe west return']
for y in [-32,-40,-50,-59]:
    inv=side.matrix_world.inverted()
    assert side.ray_cast(inv@Vector((-85,y,6.8)),inv.to_3x3()@Vector((-1,0,0)),distance=8)[0],('Hall side gap',y)

# Roundel apertures remain open in the masonry; the stair belongs on the cafe side.
for o in objects:
    if o.name.startswith('Envelope tower') and not o.name.endswith('back'):
        assert not o.ray_cast(Vector((0,13.1,2)),Vector((0,0,-1)),distance=4)[0]
turret=bpy.data.objects['Turret octagonal stair']
assert min(v.co.x for v in turret.data.vertices)>-102.69,'Stair turret moved to the wrong side'
assert not any(o.name.startswith('Clock ') for o in objects)


# Supplied rear/garden photographs show a cross-gable, never a terminal hip.
import bmesh
roof=bpy.data.objects['Roof main cross gabled hall']
bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges),'Open cross-roof junction'
bm.free()
for x in (-113.5,-108,-101,-92):
    hit,p,n,i=roof.ray_cast(Vector((x,-56.65,20)),Vector((0,0,-1)),distance=20)
    assert hit and abs(p.z-10.78)<.02,('Lost transverse ridge',x,p.z if hit else None)
for x in (-110,-103,-95):
    for y in (-60,-55,-45,-32):
        hit,p,n,i=roof.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),distance=20)
        assert hit,('Missing roof slope',x,y)
assert len([o for o in objects if o.name.startswith('Window modern rear side')])==6
back=bpy.data.objects['Envelope rear cross gable']
for u,z in [(4.55,2.5),(4.55,7.75),(2.55,4.1),(6.55,4.1)]:
    assert not back.ray_cast(Vector((u,z,2)),Vector((0,0,-1)),distance=4)[0],('Rear gable opening filled',u,z)

# Roof endcap must not cover the photographed round light or brick gable.
assert not roof.ray_cast(Vector((-120,-56.65,8.33)),Vector((1,0,0)),distance=10)[0], 'Slate cap obscures rear roundel'

# Shared annex seam: the flat roof meets the return wall instead of leaving a
# light strip, and the gable wall has no vertices above the roof underside.
annex=bpy.data.objects['Envelope annex return']
assert abs(min(v.co.x for v in annex.data.vertices)+89.55)<1e-5
assert all(abs(min(v.co.x for v in o.data.vertices)+89.55)<1e-5 for o in flat)
for v in side.data.vertices:
    p=side.matrix_world@v.co
    if p.z<6:continue
    hit,top,n,i=roof.ray_cast(Vector((p.x-.01,p.y,20)),Vector((0,0,-1)),distance=20)
    assert hit and p.z<=top.z-.159, ('Wall penetrates roof shell',tuple(p),top.z if hit else None)

# Rear elevation corners have one owner, including their exposed end caps.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
triangles=[];labels=[]
for name in ('Envelope rear cross gable','Envelope cafe west return','Envelope rear long wall'):
    ob=bpy.data.objects[name];ob.data.calc_loop_triangles()
    for t in ob.data.loop_triangles:
        triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(name)
# The full published audit also retains sub-0.0001 m² export slivers.
errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
assert not errors,errors[:8]
print('Rear hall corner surface ownership passed')

# Tower quoins retain their exposed relief but stop at the masonry face.
# Their former 7 mm embedded ends overlapped the tower's corner end caps.
quoins=[o for o in objects if o.name.startswith('Fine tower quoin')]
assert len(quoins)==312
for ob in quoins:
    assert abs(min(v.co.z for v in ob.data.vertices))<1e-6,ob.name
    assert abs(max(v.co.z for v in ob.data.vertices)-.063)<1e-6,ob.name
print('All 312 tower quoins meet masonry without embedded corner faces')
