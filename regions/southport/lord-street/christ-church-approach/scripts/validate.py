"""Ground, access, furniture contacts and affected surface ownership."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'tools'),str(REPO/'lib')]
from datum import grade
from coplanar import check_blender
from components import tree,hedge,bench
from southport3d.street import furniture
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());R=json.loads((ROOT/'research/geometry-report.json').read_text())
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ground=[o for o in obs if o.name.startswith('Surface ')];vertical=[o for o in ground if 'edging'in o.name]
assert ground and len(obs)>len(ground)
triangles=0
for ob in obs:
 assert ob.data.uv_layers
 assert all(math.isfinite(c)for v in ob.data.vertices for c in v.co)
 ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles)
 for t in ob.data.loop_triangles:
  a,b,c=(ob.data.vertices[i].co for i in t.vertices);assert(b-a).cross(c-a).length>1e-10,(ob.name,t.index)
assert triangles<24000,triangles

def hits(x,y):
 out=[]
 for o in ground:
  hit,p,n,index=o.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
  if hit and n.z>.2:out.append((p.z,o.name))
 return out

def one(x,y):
 h=hits(x,y);assert len(h)==1,(x,y,h);return h[0]
# Open TownHall footpath, church-side court and Corporation route all reach
# the handovers. Sampling offsets avoid shared triangle-edge ambiguity.
access=0
for y in range(-104,-30):
 x=-129.3 if y>-70 else-127.0
 z,name=one(x+.013,y+.317);assert abs(z-grade(x,y+.317))<3e-5,(x,y,z,name);access+=1
for x,y in [(-116,-45),(-117,-55),(-121,-62),(-125,-68),(-123,-65)]:
 z,name=one(x,y);assert abs(z-grade(x,y))<3e-5,(x,y,z,name);access+=1
for x,y in [(-123,-37),(-123.5,-49),(-123.8,-29.2)]:
 z,name=one(x,y);assert 'grass'in name and .07<=z-grade(x,y)<=.451,(x,y,z,name)
for x,y in [(-125,-17.99),(-130,-125),(-108,-40),(-100,-90)]:assert not hits(x,y),(x,y,'adjacent owner or building floor duplicated')
# Retained cross-approach is paved and clear; neither lawn nor wall closes it.
for x in [-127.3,-125,-122,-119]:
 z,name=one(x,-22.4);assert 'grass'not in name,(x,name)
assert max(y for x,y in D['wall']['xy'])<=-25.5,'wall blocks cross-path'
assert max(y for x,y in D['lawn'])<=-26,'raised lawn blocks cross-path'
# Footprint and station surface exclusions are exact, not hidden lower layers.
from mathutils.geometry import tessellate_polygon
polygons=[json.loads((REPO/D['building_source']).read_text())['mapped_footprint']]
for path in D['block_plans']:polygons += [b['footprint']for b in json.loads((REPO/path).read_text())['blocks']]
polygons += json.loads((REPO/D['station_ground_source']).read_text())['ground_polygons']
exclusions=0
for q in polygons:
 pts=[Vector((x,y,0))for x,y in q]
 for tri in tessellate_polygon([pts]):
  tri=[pts[i]if isinstance(i,int)else i for i in tri];x=sum(p.x for p in tri)/3;y=sum(p.y for p in tri)/3
  assert not hits(x,y),(x,y,'excluded footprint has floor');exclusions+=1
# Bases meet their declared ground; trees/benches on raised turf use its level.
for row in R['placements']:
 x,y=row['xy'];h=hits(x,y)
 if not h:
  # The photographed bin stands on the retained TownHall-side garden path.
  assert row['kind']=='bin' and -136<x<-127.9 and -29.72<y<-17.8,row
  z,name=grade(x,y),'adjoining church-gardens paving'
 else:z,name=one(x,y)
 matches=[o for o in obs if o.name.startswith('Furniture '+row['kind']+' ')and abs(o.location.x-x)<1e-4 and abs(o.location.y-y)<1e-4]
 assert len(matches)==1,(row,matches)
 assert abs(matches[0].location.z-z)<.025,(row,z,matches[0].location.z)
# Check support footprints as well as origins: a hedge on a sloping margin
# can have a correct centre while its outer base visibly floats.
support_samples=0
for ob in obs:
 if ob.name.startswith('Furniture hedge '):supports=[(x,y,0)for x in [-.5,.5]for y in [-.375,.375]]
 elif ob.name.startswith('Furniture bench '):supports=[(x,y,0)for x in [-.72,.72]for y in [-.275,.275]]
 else:continue
 for local in supports:
  p=ob.matrix_world@Vector(local);z,name=one(p.x,p.y)
  assert abs(p.z-z)<.03,(ob.name,tuple(p),z,'floating support footprint');support_samples+=1
# Coarse families preserve silhouettes while reducing the fixed detail budget.
family_counts={}
for kind in ['bench','bollard','bin','tree','hedge']:
 factory={'tree':tree,'hedge':hedge,'bench':bench}.get(kind);counts=[]
 for level in ['detail','walk','district']:
  m=factory(level)if factory else furniture(kind,level);counts.append(sum(len(f)-2 for f in m.faces))
 assert counts[0]>counts[1]>counts[2],(kind,counts);family_counts[kind]=counts
# Regress the exact coarse-family defect found only in the published District
# timber end caps. Check prototypes at every level as well as placed Detail.
for level in ['detail','walk','district']:
 ob=bench(level,'Audit bench '+level).finish([]);check_blender([ob]);bpy.data.objects.remove(ob,do_unlink=True)
# Every changed mesh: ground, walls, board, repeated furniture and landscape.
# Any findings are reviewed rather than exempted by material or object family.
check_blender(obs)
report={'objects':len(obs),'triangles':triangles,'access_samples':access,'excluded_surface_samples':exclusions,'placements':len(R['placements']),'support_samples':support_samples,'family_triangles':family_counts,'ownership_check':'All new meshes including wall/coping, noticeboard, repeated bench/bin/post/tree/hedge prototypes and their ground interfaces. Existing garden handover tested separately and exported neighbouring assets audited.','limitations':D['limits']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
