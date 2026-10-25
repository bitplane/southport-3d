"""Footprint, floor contact, closed volume and fixed budget checks."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())

obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==sum(not b['replace_with'] for b in D['blocks'])
sys.path.insert(0,str(ROOT/'scripts'))
from datum import grade,SURFACE

triangles=0
for block in D['blocks']:
 if block['replace_with']:continue
 o=bpy.data.objects['Massing '+block['id']];bm=bmesh.new();bm.from_mesh(o.data)
 assert all(e.is_manifold for e in bm.edges),(o.name,'open volume')
 assert bm.calc_volume(signed=True)>0,(o.name,'inverted volume');bm.free()
 assert o.data.uv_layers and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 for x,y in block['footprint']:
  matches=[v for v in o.data.vertices if abs(v.co.x-x)<1e-4 and abs(v.co.y-y)<1e-4]
  assert len(matches)==2,(o.name,'footprint changed',x,y)
  assert min(v.co.z for v in matches)<=grade(x,y)-.049,(o.name,'floating base')
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-9
assert triangles<12000,triangles
sys.path.insert(0,str(REPO/'tools'));from coplanar import check_blender
check_blender(obs)
report={'blocks':len(obs),'triangles':triangles,'checks':'Closed positive volumes; exact retained footprint vertices; shared street grade; finite UV float32 geometry; no same-facing coplanar overlap; under 12000 triangles','limitation':'Geometry checks do not establish architectural or survey fidelity.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
