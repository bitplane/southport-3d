"""Check the shared geographic seam, walkable extent and exported topology."""
from pathlib import Path
import bpy,json,math,os
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
recipe=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/promenade/marine-parade-junction/publication.json').read_text());assert all(p.get('ground') is True for p in recipe['parts'])
points=[v.co for o in meshes for v in o.data.vertices];assert all(math.isfinite(c) for v in points for c in v)
assert min(v.x for v in points)>=22-.0002 and max(v.x for v in points)<=85+.0002
assert min(v.z for v in points)>=2.08-.0002 and max(v.z for v in points)<=2.2+.0002
assert all(o.data.uv_layers for o in meshes);assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def ground(x,y,z):
 hit,p,*_=bpy.context.scene.ray_cast(deps,Vector((x,y,20)),Vector((0,0,-1)),distance=30)
 assert hit,(x,y,'ground hole');assert abs(p.z-z)<.001,(x,y,p.z,z)
# An exact boundary column must match the earlier Nevill tile's road height.
for y in [273,276,280,284]:ground(22.001,y,2.08)
for p in [(29,282),(45,287),(65,291),(80,299),(29,307),(33,306)]:ground(*p,2.08)
for p in [(40,275),(70,283),(76,310)]:ground(*p,2.2)
# Independently sample both sides of each turning kerb in the finished scene.
# A stray cap over paving fails because its road-side probe stays at footway
# height; a cap inside asphalt fails on its pavement-side probe.
kerb_samples=0
for a,b in json.loads((ROOT/'research/turning-kerbs.json').read_text()):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
 for t in [.1,.3,.5,.7,.9]:
  x,y=a[0]+dx*t,a[1]+dy*t
  ground(x+nx*.09,y+ny*.09,2.2)
  ground(x-nx*.15,y-ny*.15,2.08)
  kerb_samples+=1
assert kerb_samples>0
# Refuges must stay raised while their pedestrian cut-throughs remain open.
ground(33.3,296,2.2);ground(66,293.27,2.2);ground(32.8,302,2.08);ground(56.7,291,2.08)
triangles=0
for o in meshes:
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for tri in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in tri.vertices);assert (b-a).cross(c-a).length>1e-10
report={'turning_kerb_boundary_samples':kerb_samples,'objects':len(meshes),'triangles':triangles,'checks':'finite packed meshes, float32 triangles, ground flags, exact X22 road seam, route and footway samples','limits':'Widths and levels estimated; geometric checks do not establish survey accuracy.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)
