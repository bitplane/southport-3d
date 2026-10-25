"""Check ground ownership, profile planes and separate platform/rail levels."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from datum import grade
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=0;probes=0
for o in obs:
 assert o.data.uv_layers and all(math.isfinite(c)for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);normal=(b-a).cross(c-a)
  assert normal.length>1e-9,(o.name,'degenerate')
  if 'kerb' in o.name or o.name.startswith(('Structure cutting edge','Structure platform edges')):continue
  assert normal.z>0,(o.name,'ground facing down')
  p=(a+b+c)/3
  expected=0 if o.name.startswith('Ground rail-ground') else .65 if o.name=='Ground platform-ground' else .09 if o.name.startswith('Structure running rails') else grade(p.x,p.y)-(.12 if o.name.endswith(('asphalt','yellow','white')) else 0)
  assert abs(p.z-expected)<.0003,(o.name,list(p),expected)
  probes+=1
assert triangles<D['budgets']['triangles_per_level'],triangles
check_blender(obs)
# Rail cutting is below the independent existing Eastbank bridge profile.
assert grade(-334,-602)>4.5
assert any(o.name=='Ground platform-ground'for o in obs)
assert any(o.name=='Ground rail-ground'for o in obs)
report={'triangles':triangles,'profile_probes':probes,'checks':['finite nondegenerate upward ground','authored profile at triangle interiors','separate platform and railway heights','same-facing coplanar surface ownership','fixed triangle budget'],'limits':['Ground heights are provisional, not surveyed. Rail fan has simple running strips, no signalling or third-rail engineering.']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
