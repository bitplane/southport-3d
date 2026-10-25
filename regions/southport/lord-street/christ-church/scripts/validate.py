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

# The cafe has a real glazed opening, a round corner and a separate lower porch.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
front=bpy.data.objects['Envelope cafe front']
for u,h in [(1.1,1.4),(2.3,1.4),(4.2,1.4),(2.5,2.6)]:
    origin=front.matrix_world@Vector((u,h,2))
    direction=front.matrix_world.to_3x3()@Vector((0,0,-1))
    hit,p,n,i,ob,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=4)
    assert hit and ob.name.startswith('Window cafe glazing'),('Cafe glazing blocked',u,h,ob.name if hit else None)
assert len([o for o in objects if o.name.startswith('Envelope cafe curved brick')])==24
cap=bpy.data.objects['Roof cafe rounded flat'];porch=bpy.data.objects['Roof cafe entrance canopy']
assert max(v.co.z for v in porch.data.vertices)<min(v.co.z for v in cap.data.vertices),'Porch ridge must remain below cafe cap'
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
for name in ('Envelope rear cross gable','Envelope cafe west return','Envelope rear long wall','Envelope cafe porch return'):
    ob=bpy.data.objects[name];ob.data.calc_loop_triangles()
    for t in ob.data.loop_triangles:
        triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(name)
# The full published audit also retains sub-0.0001 m² export slivers.
errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
assert not errors,errors[:8]
print('Rear hall corner surface ownership passed')

# The cafe-side front shoulder must close every strip below the sloping roof.
# A former rectangular wall left a triangular opening up to 1.1 m high.
shoulder=bpy.data.objects['Envelope cafe porch return']
inv=shoulder.matrix_world.inverted()
for x in (-89.65,-90.2,-91.0,-92.0,-93.0):
    hit,top,n,i=roof.ray_cast(Vector((x,-29.65,20)),Vector((0,0,-1)),distance=20)
    assert hit,('Missing shoulder roof',x)
    for drop in (.18,.35,.7):
        origin=inv@Vector((x,-28,top.z-drop))
        direction=inv.to_3x3()@Vector((0,-1,0))
        assert shoulder.ray_cast(origin,direction,distance=3)[0],('Open cafe roof shoulder',x,drop)
    assert not shoulder.ray_cast(inv@Vector((x,-28,top.z+.02)),direction,distance=3)[0],('Shoulder above roof',x)
assert abs(max((side.matrix_world@v.co).y for v in side.data.vertices)+29.9)<1e-5
print('Cafe shoulder closes the sloping roof without changing its silhouette')

# Tower quoins retain their exposed relief but stop at the masonry face.
# Their former 7 mm embedded ends overlapped the tower's corner end caps.
quoins=[o for o in objects if o.name.startswith('Fine tower quoin')]
assert len(quoins)==312
for ob in quoins:
    assert abs(min(v.co.z for v in ob.data.vertices))<1e-6,ob.name
    assert abs(max(v.co.z for v in ob.data.vertices)-.063)<1e-6,ob.name
print('All 312 tower quoins meet masonry without embedded corner faces')

# Porch supports meet the timber beam and roof; a former 60mm gap left the
# canopy floating. The measured aerial plan is narrow and projects outward.
canopy=bpy.data.objects['Roof cafe entrance canopy']
verts=[canopy.matrix_world@v.co for v in canopy.data.vertices]
assert abs(max(v.x for v in verts)-min(v.x for v in verts)-2.9)<1e-4
assert abs(max(v.y for v in verts)-min(v.y for v in verts)-4.9)<1e-4
beam=bpy.data.objects['Trim porch cross beam']
assert abs(max(v.co.z for v in beam.data.vertices)-min(v.z for v in verts))<1e-4
for capital in [o for o in objects if o.name.startswith('Trim porch pier capital')]:
 assert abs(max(v.co.z for v in capital.data.vertices)-min(v.co.z for v in beam.data.vertices))<1e-4
for pier in [o for o in objects if o.name.startswith('Pier cafe porch')]:
 assert abs(max(v.co.z for v in pier.data.vertices)-(.58+2.72))<1e-4
assert any('timber' in m.name.lower() for m in canopy.data.materials),'Missing timber gable/soffit'
print('Cafe porch plan and continuous support levels verified')
boards=[o for o in objects if o.name.startswith('Trim porch recessed gable board')]
assert len(boards)>=5,'Missing recessed horizontal gable boarding'
assert all(max(v.co.y for v in o.data.vertices)<-24.8 for o in boards),'Gable infill must sit behind verge'
check_porch=[o for o in objects if o.name.startswith(('Roof cafe entrance canopy','Trim porch','Pier cafe porch'))]
from coplanar import check_blender
check_blender(check_porch)
print('Complete porch roof, boarding, fascia and support overlap check passed')

connector=bpy.data.objects['Envelope cafe connector']
for x in (-89.50,-84.45):
 assert connector.ray_cast(Vector((x,-28,1.5)),Vector((0,-1,0)),distance=3)[0],('Open connector jamb seam',x)
print('Porch backing joins both adjacent walls without light slots')

# Changed wing prototypes: glazing stays inside an actual masonry aperture;
# the door centre stile must reach its pointed head rather than float below it.
from coplanar import check_blender
wings=[o for o in objects if o.name.startswith('Window Gothic wing')]
doors=[o for o in objects if o.name.startswith('Door wing pointed')]
assert len(wings)==4 and len(doors)==2
# One complete wing prototype includes component interfaces; the opposite wing
# instances the same window family and mirrors the door/wall construction.
check_blender([bpy.data.objects[n] for n in (
    'Envelope Gothic wing','Window Gothic wing inner','Window Gothic wing outer',
    'Door wing pointed','Trim wing blind tracery')])
for ob in [o for o in objects if o.name.startswith('Envelope Gothic wing')]:
    check_blender([ob])
    sign=1 if sum(v.co.x for v in ob.data.vertices)>0 else -1
    for u,h in [(sign*7.65,1.6),(sign*7.65,5.5),(sign*4.25,4.5)]:
        assert not ob.ray_cast(Vector((u,h,2)),Vector((0,0,-1)),distance=3)[0],('Filled wing opening',ob.name,u,h)
for ob in doors:
    centre=(min(v.co.x for v in ob.data.vertices)+max(v.co.x for v in ob.data.vertices))/2
    hit,p,n,i=ob.ray_cast(Vector((centre,2.75,1)),Vector((0,0,-1)),distance=2)
    assert hit and ob.data.polygons[i].material_index==1,'Door stile stops short of pointed head'
print('Four wing window and two doorway prototypes: coplanar ownership and open masonry verified')
