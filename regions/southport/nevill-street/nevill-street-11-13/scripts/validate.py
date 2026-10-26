"""Mechanical checks complement reference and assembled-export review."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-11-13.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.matrix_world@o.data.vertices[i].co for i in t.vertices)
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate triangle')
 if o.get('closed_shell'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00012)
  assert all(e.is_manifold for e in bm.edges),(o.name,'open roof shell')
  assert bm.calc_volume(signed=True)>0,(o.name,'inward roof');bm.free()
check_blender([o for o in obs if o.name.startswith(('Shell ','Architecture ','Glazing '))])
# Fine carvings and arrises are also checked. Only the decorative iron loops
# have welded intersections; native exported audit records their three tiny
# groups separately, rather than exempting the facade or all fine detail.
fine=[]
for o in obs:
 if not o.name.startswith('Fine '):continue
 mesh=o.data.copy();tmp=bpy.data.objects.new('Regression '+o.name,mesh);bm=bmesh.new();bm.from_mesh(mesh)
 remove=[f for f in bm.faces if mesh.materials[f.material_index].name=='Black painted wrought iron']
 bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(mesh);bm.free();fine.append(tmp)
check_blender([o for o in obs if o.name.startswith(('Shell ','Architecture ','Glazing '))]+fine)
for o in fine:
 mesh=o.data;bpy.data.objects.remove(o);bpy.data.meshes.remove(mesh)
# Openings must genuinely pass through street brick into separate glazing.
d=json.loads((ROOT/'research/layout.json').read_text());x,y,z=d['origin'];bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();probes=0
# Sample the interiors and edges of every pane at both storeys. A single
# centre ray missed pilasters and capitals clipping the edges of the glazing.
windows=[(u,w,4.35,2.58,2 if w<.7 else 3) for u,w in d['first_windows']]
windows += [(u,1.06,8.18,2.43,3) for u in d['upper_windows']]
for u,w,bottom,height,cols in windows:
 for col in range(cols):
  left=u-w/2+.045+col*(w-.09)/cols+.010
  right=u-w/2+.045+(col+1)*(w-.09)/cols-.010
  for row in range(4):
   low=bottom+.045+row*(height-.09)/4+.012
   high=bottom+.045+(row+1)*(height-.09)/4-.012
   for fx in (.15,.5,.85):
    for fz in (.15,.5,.85):
     q=left+(right-left)*fx;zz=low+(high-low)*fz
     if zz<4.54:continue  # The observed balcony ledge masks the bottom of this storey.
     p=Vector((x+.0135*q+.55,y+q+.02087*.55,z+zz))
     direction=Vector((-1,-.02087,0)).normalized()
     hit,point,n,i,o,M=bpy.context.scene.ray_cast(deps,p,direction,distance=1)
     while hit and o.data.materials[o.data.polygons[i].material_index].name=='Black painted wrought iron':
      p=point+direction*.001
      hit,point,n,i,o,M=bpy.context.scene.ray_cast(deps,p,direction,distance=1)
     assert hit and o.name.startswith('Glazing '),(u,zz,q,o.name if o else None,o.data.materials[o.data.polygons[i].material_index].name if o else None,list(point))
     probes+=1
# The previous closed-slab/coplanar tests accepted warped roofs and arbitrary
# pentagonal back caps. Check the actual interface contract as well as solidity.
from plan import attachments,attachment_faces,attachment_cheeks,roof_height,world,hip_ridge_segments
from mathutils.bvhtree import BVHTree
junctions=[]
for spec in attachments(d):
 name,centre,half,front,eave,peak,fall=spec
 ob=bpy.data.objects['Shell roof '+('central gable hood' if name=='central gable' else name)]
 tree=BVHTree.FromObject(ob,deps);contacts=[]
 for label,points in attachment_faces(d,spec):
  a,b,c=map(Vector,points[:3]);normal=(b-a).cross(c-a).normalized()
  assert max(abs((Vector(p)-a).dot(normal)) for p in points)<1e-5,(label,'warped roof plane')
  for P,Q in zip(points,points[1:]+points[:1]):
   if all(abs(p[2]-.07-roof_height(d,p[0],p[1]))<1e-7 for p in (P,Q)):
    for t in (0.,.25,.5,.75,1.):
     p=tuple(P[k]+t*(Q[k]-P[k]) for k in range(3))
     assert abs(p[2]-.07-roof_height(d,p[0],p[1]))<1e-7,(label,'valley leaves hip')
     for dz in (0.,-.07):
      q=Vector(world(d,(p[0],p[1],p[2]+dz)));hit=tree.find_nearest(q)
      assert hit[0] is not None and hit[3]<.0002,(label,'export-source roof does not meet hip',hit[3])
     contacts.append(p)
  assert all(p[2]-.07>=roof_height(d,p[0],p[1])-1e-7 for p in points),(label,'roof penetrates exposed hip')
 assert contacts and max(p[1] for p in contacts)>front+.5,(name,'missing return into hip')
 assert any(p[0]<centre-.05 for p in contacts) and any(p[0]>centre+.05 for p in contacts),(name,'missing side valley')
 for label,points in attachment_cheeks(d,spec):
  for p in points:
   lower=roof_height(d,p[0],p[1]);upper=eave-fall*(p[1]-front)-.07
   assert upper>=lower-1e-7,(label,'inverted cheek')
   assert min(abs(p[2]-lower),abs(p[2]-upper))<1e-7,(label,'detached cheek boundary')
 junctions.append({'name':name,'contact_samples':len(contacts),'rear_contact_m':max(p[1] for p in contacts)})

for A,B in hip_ridge_segments(d):
 for t in (.01,.25,.5,.75,.99):
  u,v,z=(A[k]+t*(B[k]-A[k]) for k in range(3))
  for name,c,h,v0,e,peak,fall in attachments(d):
   if c-h<=u<=c+h and v>=v0:
    roof=peak-abs(u-c)*(peak-e)/h-fall*(v-v0)
    assert roof<z-.10,(name,'hip cap crosses dormer junction')

# Independent District receivers must meet the cheeks at the omitted slab's
# underside; using the detailed top surface here opened visible 7 cm slots.
from district import surfaces
from mathutils import Matrix
ox,oy,oz=d['origin']
inverse=Matrix(((.0135,-1,0,ox),(1,-.02087,0,oy),(0,0,1,oz),(0,0,0,1))).inverted()
receivers=surfaces(ROOT)['roof']
for name,c,h,v0,e,peak,fall in attachments(d):
 returns=[f for f in receivers if f['name'].startswith(name+' stone front return ')]
 assert len(returns)==4,(name,'District missing front depth returns')
 pitches=[f for f in receivers if f['name'].startswith(name+' ') and ' pitch ' in f['name']]
 assert pitches,(name,'District missing roof')
 for face in pitches:
  for point in face['vertices']:
   p=inverse@Vector(point)
   expected=peak-abs(p.x-c)*(peak-e)/h-fall*(p.y-v0)-.07
   assert abs(p.z-expected)<.00003,(name,'District roof detached from cheek plane')

assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
report={'triangles':triangles,'roof_junctions':junctions,'window_probes':probes,'checks':['finite float32 geometry','nondegenerate triangles','closed outward hip roof','planar dormer pitches and sampled actual mesh to hip valley contacts','District roof/cheek attachment and front depth returns','hip caps stop at dormer junctions','real street window apertures','all architectural meshes and non-iron ornament overlap regression','packed authored textures'],'limitations':['Decorative iron-loop welds remain subject to the exported audit; three tiny self-overlap groups are recorded in review.json. Other architecture and ornament are checked together.']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
