"""Metric seam, coverage and navigable-route checks for the Nevill corridor."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
publication=json.loads((Path(__import__('os').environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/nevill-street/public-realm/publication.json').read_text())
assert all(part.get('ground') is True for part in publication['parts']), 'Every corridor part must participate in viewer ground following'
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes and all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>=36-1e-5
assert max(v.y for v in points)<317
# The existing square owns everything except its open 12m road neck below Y41.
assert all(-6-1e-5<=v.x<=6+1e-5 for v in points if v.y<41-1e-5)
seam=[v for v in points if abs(v.y-36)<1e-5];assert seam
assert all(abs(v.z-(-.9195))<1e-5 for v in seam)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def sample(x,y):
 hit,p,n,idx,ob,m=bpy.context.scene.ray_cast(deps,Vector((x,y,20)),Vector((0,0,-1)),distance=30)
 assert hit,(x,y,'ground hole')
 return p.z,ob
# Route centre samples are deliberately spaced independently of construction rows.
for y in range(37,248,3):
 stations=D['stations_y_centre_halfwidth_left_right'];centre=0
 for a,b in zip(stations,stations[1:]):
  if y<=b[0]:
   t=max(0,(y-a[0])/(b[0]-a[0]));centre=a[1]+(b[1]-a[1])*t;break
 sample(centre,y)
for x,y in [(-7,60),(7,60),(-8,130),(7,130),(-22,221),(7,221),(-18,248),(-9,270),(-11,280),(-11,300),(-9,310)]:sample(x,y)
# Adjacent streaming parts must share exactly the same surface height.
for y in [95,185,248.07]:
 for x in ([0] if y<200 else [-18]):
  za,_=sample(x,y-.002);zb,_=sample(x,y+.002);assert abs(za-zb)<.002,(x,y,za,zb)
# Exported triangles must retain nonzero area after Blender's float32 conversion.
# In particular, tiny paint-cutout fragments must not collapse during snapping.
minimum_triangle_area=float('inf')
for ob in meshes:
 ob.data.calc_loop_triangles()
 for tri in ob.data.loop_triangles:
  a,b,c=(ob.data.vertices[i].co for i in tri.vertices)
  triangle_area=(b-a).cross(c-a).length/2
  assert triangle_area>1e-10,(ob.name,tri.index,'collapsed float32 triangle')
  minimum_triangle_area=min(minimum_triangle_area,triangle_area)
conform=json.loads((ROOT/'research/conform.json').read_text())
assert conform['inserted_edge_junctions']>0,'Street clipping should share paint/base edge junctions'

report={'minimum_triangle_area_m2':minimum_triangle_area,'joined_edge_junctions':conform['inserted_edge_junctions'],'ground_parts':len(publication['parts']),'objects':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'checks':'finite meshes, UVs, packed authored maps, no ownership overlap south of seam, square road elevation, continuous route and three part seams','uncertainty':'Mapped registration with estimated widths and grade; checks establish geometric continuity, not survey accuracy.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)
