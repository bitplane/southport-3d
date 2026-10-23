import json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-place-terrace.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in meshes if o.name.startswith('Bay white gable')])==6
assert len([o for o in meshes if o.name.startswith('Door recessed timber')])==3
assert len([o for o in meshes if o.name.startswith('Assembly bay ')])==54
assert len([o for o in meshes if o.name.startswith('Assembly sash ')])==99
roofs=[o for o in meshes if o.name.startswith('Roof ')]
assert len(roofs)==10
for ob in roofs:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),(ob.name,'open edge');bm.free()
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();probes=0
for ob in meshes:
 if ob.name.startswith('Assembly bay ') and 'storey 0' not in ob.name:
  xs=[v.co.x for v in ob.data.vertices];u=(min(xs)+max(xs))/2
  ray=ob.matrix_world@Vector((u,1.4,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=.85)
  assert hit and target==ob,(ob.name,'Blocked glazing',target.name if target else None)
  assert 'glass' in target.data.materials[target.data.polygons[i].material_index].name.lower(),(ob.name,'Ray missed actual glass')
  probes+=1
assert probes==36
sash_probes=0
for ob in meshes:
 if ob.name.startswith('Assembly sash '):
  height=2.52 if ob.name.startswith('Assembly sash front') else 1.9
  ray=ob.matrix_world@Vector((.1,height*.7,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=.85)
  assert hit and target==ob,(ob.name,'Blocked sash',target.name if target else None)
  assert 'glass' in target.data.materials[target.data.polygons[i].material_index].name.lower(),ob.name
  sash_probes+=1
assert sash_probes==99
pts=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert 69<min(p.x for p in pts)<74 and 107<max(p.x for p in pts)<112
assert -57<min(p.y for p in pts)<-49 and -23<max(p.y for p in pts)<-16
assert 20<max(p.z for p in pts)<22
report={'meshes':len(meshes),'closed_roofs':len(roofs),'glazing_probes':probes,'sash_probes':sash_probes,'checks':['Finite UV meshes and packed authored textures','Six polygonal bays,90 leaded transoms and three recessed entrances','Closed main,oriel and rear wing roofs','Registered site envelope']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Repeated rails meet their stiles without overlapping the visible faces.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
for prefixes in [('Window main side frame','Window main side transom'),
                 ('Window attic stile','Window attic rail')]:
 triangles=[];labels=[]
 for ob in meshes:
  if not ob.name.startswith(prefixes):continue
  ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(ob.name)
 assert triangles,prefixes
 errors=overlaps(triangles,labels,min_area=1e-4)
 assert not errors,(prefixes,errors[:8])
print('Repeated window rail/stile surface ownership passed')

# Triple-sash strip union keeps all openings and the original outer bounds.
oriels=[o for o in meshes if o.name.startswith('Window attic oriel frame')]
assert len(oriels)==4
# Undo the documented site shear only for checks in the authored frame.
# Check the actual saved mesh, not a freshly generated substitute.
from mathutils import Matrix
d=json.loads((ROOT/'research/layout.json').read_text());angle=math.radians(d['local_rotation_degrees'])
rotation=Matrix.Rotation(angle,3,'Z')
registered=Matrix(((math.cos(angle),d['north_basis'][0],0),
                   (math.sin(angle),d['north_basis'][1],0),(0,0,1)))
ob=oriels[0].copy();ob.data=oriels[0].data.copy()
r=ob.matrix_world.to_3x3();undo=(r.inverted()@registered@rotation.inverted()@r).inverted()
for v in ob.data.vertices:v.co=undo@v.co
ob.data.update()
bm=bmesh.new();bm.from_mesh(ob.data)
assert all(e.is_manifold and e.is_contiguous for e in bm.edges),'Open/inverted oriel frame'
assert bm.calc_volume(signed=True)>0
bm.free()
assert abs(max(v.co.x for v in ob.data.vertices)-1.0175)<1e-5
assert abs(min(v.co.y for v in ob.data.vertices)-11.6225)<1e-5
assert abs(max(v.co.y for v in ob.data.vertices)-13.3075)<1e-5
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[p.vertices[:] for p in ob.data.polygons])
for x in (-.67,0,.67):
 for y in (11.9,12.9):
  assert tree.ray_cast(Vector((x,y,.2)),Vector((0,0,-1)),.4)[0] is None,('Filled oriel pane',x,y)
 for y in (11.65,12.45,13.28):
  p,n,i,distance=tree.ray_cast(Vector((x,y,.2)),Vector((0,0,-1)),.4)
  assert p is not None and abs(p.z)<1e-5 and n.z>.99,('Missing/inverted oriel rail',x,y)
ob.data.calc_loop_triangles()
triangles=[[tuple(ob.data.vertices[i].co) for i in t.vertices] for t in ob.data.loop_triangles]
assert not overlaps(triangles,[ob.name]*len(triangles),min_area=1e-6)
print('Oriel union: closed outward shell, original bounds, open panes and no duplicate faces')

mesh=ob.data;bpy.data.objects.remove(ob);bpy.data.meshes.remove(mesh)

# Masonry backing must not duplicate the timber's exposed inner reveal.
seen=set()
for ob in meshes:
 if not ob.name.startswith('Assembly sash ') or ob.data.name in seen:continue
 seen.add(ob.data.name);ob.data.calc_loop_triangles();triangles=[];labels=[]
 for t in ob.data.loop_triangles:
  mat=ob.data.materials[t.material_index].name
  if mat not in ('Historic red water shot brick','Ivory painted timber'):continue
  triangles.append([tuple(ob.data.vertices[i].co) for i in t.vertices]);labels.append(mat)
 errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
 assert not errors,(ob.name,errors[:8])
print('Sash backing leaves timber reveals unobscured',len(seen),'prototypes')

# Once the wall is cut around each panel, its exposed border must still be brick.
for ob in meshes:
 if not ob.name.startswith('Assembly sash '):continue
 w,h=(1.12,2.52) if ob.name.startswith('Assembly sash front') else (1.0,1.9)
 for x in (-w/2-.12,w/2+.12):
  ray=ob.matrix_world@Vector((x,h*.55,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=.85)
  assert hit and target==ob,('Uncovered sash border',ob.name,x,target.name if hit else None)
  assert target.data.materials[target.data.polygons[i].material_index].name=='Historic red water shot brick',(ob.name,'Border lost masonry')
print('All sash panels cover their enlarged wall openings')

# Stepped head blocks have one surface across their overlapping corners.
seen=set()
for ob in meshes:
 if not ob.name.startswith('Assembly sash ') or ob.data.name in seen:continue
 seen.add(ob.data.name);ob.data.calc_loop_triangles()
 triangles=[[tuple(ob.data.vertices[i].co) for i in t.vertices] for t in ob.data.loop_triangles
            if ob.data.materials[t.material_index].name=='Terracotta dressings']
 assert not overlaps(triangles,[ob.name]*len(triangles),min_area=1e-4),ob.name
print('Repeated terracotta head surfaces have no coplanar overlap')

# Check actual bay prototypes in their authored frames after undoing site shear.
# Lead crossings and exposed arch faces have one owner; spandrels leave glazing clear.
seen=set();transom_probes=0
for source in meshes:
 if not source.name.startswith('Assembly bay '):continue
 lights=3 if ' front ' in source.name else 1
 length=2.46 if lights==3 else math.hypot((3.45-2.46)/2,1.08)
 top=2.12 if 'storey 0' in source.name else 2.35
 r=source.matrix_world.to_3x3();undo=(r.inverted()@registered@rotation.inverted()@r).inverted()
 verts=[undo@v.co for v in source.data.vertices]
 tree=BVHTree.FromPolygons(verts,[p.vertices[:] for p in source.data.polygons])
 lw=(length-.16)/lights-.045
 for k in range(lights):
  u=.08+(k+.5)*(length-.16)/lights
  p,n,i,distance=tree.ray_cast(Vector((u+lw*.1,top+.35,.2)),Vector((0,0,-1)),.5)
  assert p is not None and source.data.materials[source.data.polygons[i].material_index].name=='Leaded transom glass',(source.name,'Obscured transom',k)
  transom_probes+=1
 if source.data.name in seen:continue
 seen.add(source.data.name);source.data.calc_loop_triangles()
 lead_tri=[];front_tri=[];boundary_tri=[];boundary_labels=[]
 for t in source.data.loop_triangles:
  mat=source.data.materials[t.material_index].name
  tri=[verts[i] for i in t.vertices]
  if mat=='Dark lead came':lead_tri.append(tri)
  if mat in ('Ivory painted timber','Leaded transom glass'):
   boundary_tri.append(tri);boundary_labels.append(mat)
  n=(tri[1]-tri[0]).cross(tri[2]-tri[0]).normalized()
  if mat=='Ivory painted timber' and n.z>.99:front_tri.append(tri)
 assert not overlaps(lead_tri,['lead']*len(lead_tri),min_area=1e-6),source.name
 assert not overlaps(front_tri,['arch']*len(front_tri),min_area=1e-5),source.name
 assert not [hit for hit in overlaps(boundary_tri,boundary_labels,min_area=1e-5) if hit[0]!=hit[1]],source.name
assert transom_probes==90
print('90 clear bay transoms; lead crossings and exposed arch faces have no overlap')
