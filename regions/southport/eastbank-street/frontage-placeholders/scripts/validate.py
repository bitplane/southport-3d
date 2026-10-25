"""Footprint, floor contact, closed volume and fixed budget checks."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())

obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==sum(not b['replace_with'] for b in D['blocks'])
sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from datum import grade
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
  assert abs(min(v.co.z for v in matches)-grade(x,y))<1e-4,(o.name,'floating base')
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-9
assert triangles<D['budgets']['triangles_per_level'],triangles
sys.path.insert(0,str(REPO/'tools'));from coplanar import check_blender
check_blender(obs)
sys.path.insert(0,str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts'))
from plan_geometry import Plan
import itertools
P=Plan();new=D['blocks'];old=[b for f in D['existing_block_plans']for b in json.loads((REPO/f).read_text())['blocks']]
polys={id(b):P.polygons([b['footprint']]) for b in new+old}
for a,b in itertools.chain(itertools.combinations(new,2),itertools.product(new,old)):
 ts=P.triangles(P.intersection(polys[id(a)],polys[id(b)]))
 overlap=sum(abs(sum(x*y2-x2*y for (x,y),(x2,y2) in zip(t,t[1:]+t[:1])))/2 for t in ts)
 assert overlap<.001,(a['id'],b['id'],'positive-area footprint overlap',overlap)
sys.path.insert(0,str(REPO/'lib'))
from southport3d.road import parallel
roads=json.loads((REPO/'regions/southport/eastbank-street/public-realm/research/layout.json').read_text())['roads']
for r in roads:
 road=P.polygons([parallel(r['points'],-r['width']/2)+list(reversed(parallel(r['points'],r['width']/2)))])
 for b in new:
  ts=P.triangles(P.intersection(road,polys[id(b)]))
  overlap=sum(abs(sum(x*y2-x2*y for (x,y),(x2,y2) in zip(t,t[1:]+t[:1])))/2 for t in ts)
  assert overlap<.001,(r['id'],b['id'],'road blocked by placeholder',overlap)
P.close()
report={'blocks':len(obs),'triangles':triangles,'checks':'Closed positive volumes; exact retained footprint vertices; shared street grade; finite UV float32 geometry; no same-facing coplanar overlap; under declared 20000 triangle fixed envelope budget','limitation':'Geometry checks do not establish architectural or survey fidelity.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
