import bpy,math,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pavilions.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==6
triangles=0
for o in obs:
 assert o.data.uv_layers,o.name
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(o.name,t.index)
assert triangles<120000,triangles
# Canopy and wall footing skirts extend below the existing bounded street datum.
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.elevation import Elevations
datum=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/lord-corridor.json').surface('lord-corridor-pavement')
for b in json.loads((ROOT/'research/layout.json').read_text())['pavilions']:
 p=b['footprint'];cx=sum(x for x,y in p)/len(p);cy=sum(y for x,y in p)/len(p)
 for x,y in p:
  dx=x-cx;dy=y-cy;distance=math.hypot(dx,dy)
  for a,c in ((x,y),(x+.48*dx/distance,y+.48*dy/distance)):
   assert b['base_m']-.18<=datum.height(a,c)+.001,(b['id'],a,c,'floating footing')

sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
# A receiver facing inward bakes the dark backing rather than the visible
# windows, even when projection coverage reports success.
from district import surfaces
from mathutils import Vector
shapes=surfaces(ROOT)
for b in json.loads((ROOT/'research/layout.json').read_text())['pavilions']:
 p=b['footprint'];cx=sum(x for x,y in p)/len(p);cy=sum(y for x,y in p)/len(p)
 for face in shapes[b['id']]:
  v=list(map(Vector,face['vertices']));normal=(v[1]-v[0]).cross(v[3]-v[0]);centre=sum(v,Vector())/len(v)
  if face['name'].startswith('wall '):assert normal.x*(centre.x-cx)+normal.y*(centre.y-cy)>0,(b['id'],face['name'],'inward receiver')
  if face['name'].startswith('roof '):assert normal.z>0,(b['id'],face['name'],'inverted roof')
for side in ('north','south'):check_blender([o for o in obs if o.name.endswith(side)])
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':triangles,'checks':'Finite nondegenerate mesh and UV; all pavilion faces pass same-facing coplanar audit at Blender float32 precision. Cross-asset contacts and visual fidelity remain separate.'},indent=2)+'\n')
