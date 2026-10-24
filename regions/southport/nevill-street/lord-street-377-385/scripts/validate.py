"""Validate finite exports and aperture/corner/canopy invariants."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lord-street-377-385.blend'));bpy.context.view_layer.update();s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate export')
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
deps=bpy.context.evaluated_depsgraph_get();probes=0
for side,bays in [('front',D['front_bays']),('side',D['side_bays'])]:
 for b in bays:
  for z in (6.2,10.2):
   u=b['u']+.22;pos=(u,-1,z) if side=='front' else (-1,u,z);direction=(0,1,0) if side=='front' else (1,0,0)
   hit,p,n,i,obj,m=s.ray_cast(deps,T@Vector(pos),(T.to_3x3()@Vector(direction)).normalized(),distance=2)
   assert hit and obj.users_collection[0].name=='frontage',(side,u,z,obj.name if obj else None)
   probes+=1
# The four Ionic shafts must physically project from the wall. These probes
# remain meaningful after semantic batching, unlike counting named objects.
for u in (10.5,14.0):
 hit,p,n,i,obj,m=s.ray_cast(deps,T@Vector((-1.5,u,8)),(T.to_3x3()@Vector((1,0,0))).normalized(),distance=2)
 assert hit and (T.inverted()@p).x<-.45,('missing projected shaft',u)
for u in (.45,D['radius']*math.pi/2-.45):
 a=math.pi+u/D['radius'];nx,ny=math.cos(a),math.sin(a);r=D['radius'];pos=(r+(r+1.5)*nx,r+(r+1.5)*ny,8)
 hit,p,n,i,obj,m=s.ray_cast(deps,T@Vector(pos),(T.to_3x3()@Vector((-nx,-ny,0))).normalized(),distance=2)
 local=T.inverted()@p if hit else Vector((r,r,8))
 assert hit and math.hypot(local.x-r,local.y-r)>r+.45,('missing corner shaft',u)
# The pavement remains a through-space below the canopy, and the missing corner
# column from the 2017 refurbishment must not be invented at the outer radius.
for pos in [(-1.5,8,1.6),(6,-1.5,1.6)]:
 hit,*_=s.ray_cast(deps,T@Vector(pos),Vector((0,0,1)),distance=1.3);assert not hit,('filled arcade',pos)
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'));from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Shell ')])
report={'triangles':triangles,'aperture_probes':probes,'phase':D['phase'],'limitations':'Height ±1m; lightwell position ±1.5m; hidden rear windows deferred; canopy glazing uses opaque dielectric approximation.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
