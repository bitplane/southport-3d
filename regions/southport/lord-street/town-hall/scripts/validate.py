from pathlib import Path
import bpy,json,math,os,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib'),str(REPO/'tools')]
from shapes import transform
from staircase import flight,baluster_points
from coplanar import check_blender
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];n=0
for ob in obs:
 ob.data.calc_loop_triangles();n+=len(ob.data.loop_triangles)
 for t in ob.data.loop_triangles:
  a,b,c=[ob.matrix_world@ob.data.vertices[i].co for i in t.vertices];assert all(math.isfinite(v)for p in [a,b,c]for v in p);assert(b-a).cross(c-a).length>1e-10,(ob.name,'degenerate')
checks={'shell':[o for o in obs if o.name.startswith('Shell')],'joinery':[o for o in obs if o.name.startswith('Joinery')],'stair_treads':[o for o in obs if o.name.startswith('Stair tread')],'roof_slopes':[o for o in obs if o.name.startswith('Roof')]}
for name,selected in checks.items():check_blender(selected)
for x,y in [(13,22),(14,32)]:
 hit,*_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(transform(D,(x,y,5))),Vector((0,0,1)),distance=30);assert not hit,('court obstructed',x,y)
# Connected central landing and clear head-height route into the open porch.
deps=bpy.context.evaluated_depsgraph_get();start=Vector(transform(D,(D['front_width']/2,-4.5,4.2)));end=Vector(transform(D,(D['front_width']/2,-.35,4.2)));direction=end-start
hit,*_=s.ray_cast(deps,start,direction.normalized(),distance=direction.length);assert not hit,'porch access blocked by railing'
for y in [-4.5,-3.12,-2.5]:
 hit,loc,*_=s.ray_cast(deps,Vector(transform(D,(D['front_width']/2,y,4))),Vector((0,0,-1)),distance=4)
 assert hit and abs(loc.z-(2.8+D['floor_z']))<.01,('disconnected entrance landing',y,loc.z)
# Test actual exported-source surfaces beneath and above each spindle. The
# grouped stair object includes the seat and rail, but not the spindle mesh.
def contact(ob,p,direction):
 hit,where,normal,index=ob.ray_cast(Vector(p),Vector(direction),distance=.03)
 assert hit,(ob.name,p,direction,'missing physical contact')
 return where
st=D['stair'];x0=D['porch']['x0'];x1=D['porch']['x1'];yf=-st['front'];yb=-st['back'];stairs=bpy.data.objects['Stair porch'];seat_count=0
for a,b,r in [(st['x0'],x0,True),(x1,st['x1'],False)]:
 _,segments=flight(st,a,b,r)
 for yy in [yf,yb]:
  mid=yy+(-.11 if yy==yf else .11)
  for x,z in baluster_points(st,segments):
   p=transform(D,(x,mid,z));contact(stairs,(p[0],p[1],p[2]+.01),(0,0,-1))
   contact(stairs,(p[0],p[1],p[2]+.84),(0,0,1));seat_count+=1
wall=bpy.data.objects['Stair central retaining wall'];rail=bpy.data.objects['Balcony rail']
for j in range(1,st['landing_balusters']+1):
 x=x0+j*(x1-x0)/(st['landing_balusters']+1);p=transform(D,(x,yf+.002,2.8))
 contact(wall,(p[0],p[1],p[2]+.01),(0,0,-1));contact(rail,(p[0],p[1],p[2]+.84),(0,0,1));seat_count+=1
assert n<160000,n
report={'phase':D['phase'],'triangles':n,'objects':len(obs),'coplanarity':{k:len(v)for k,v in checks.items()},'court_probes':2,'baluster_seat_and_rail_contacts':seat_count,'limits':'Scoped shell, joinery, roof and stair checks; exported full and neighbouring surface checks reported separately.'};(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
