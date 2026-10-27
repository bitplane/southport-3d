"""Check finite export geometry and single ownership at roads, islands and seams."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from datum import grade
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
triangles=0;trees=[]
for o in obs:
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 assert all(math.isfinite(v) for p in o.data.vertices for v in p.co),o.name
 for t in o.data.loop_triangles:
  a,b,c=(o.data.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate float32 face')
  if not o.name.endswith(' kerb') and not o.name.startswith(('Fountain ','Garden ')):
   centre=(a+b+c)/3;expected=grade(centre.x,centre.y)-(.12 if o.name.endswith(' asphalt') else 0)
   assert abs(centre.z-expected)<1e-4,(o.name,t.index,'terrain plane erased',centre.z,expected)
 assert o.data.uv_layers,o.name
 if not o.name.startswith('Garden '):trees.append((o.name,BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)))
garden=[o for o in obs if o.name.startswith('Garden ')]
assert len(garden)>=50,len(garden)
for o in garden:
 assert abs(o.location.z-grade(o.location.x,o.location.y))<1e-5,(o.name,'floating')
assert triangles<D['budgets']['triangles_per_level'],triangles
probes=[(-234,-6.5,'garden-paving'),(-219,-2.5,'pattern'),(-221,-20.1,'pattern'),(-221,8.1,'pattern'),(-160.9,-20.1,'pattern'),(-160.9,8.1,'pattern'),(-185.7,9.1,'pattern'),(-210,12,'paving'),(-179.9,-2.5,'Fountain middle'),(-150,-12,'paving'),(-136.01,26,'asphalt'),(218.01,26,'asphalt'),(-701.3,31.9,'asphalt'),(390,24,'asphalt'),(-745.9,17.1,'lawn'),(546,19,'lawn'),(-180,40,'paving'),(280,40,'paving')]
for x,y,kind in probes:
 hits=[name for name,tree in trees if 'kerb' not in name and tree.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),100)[0] is not None]
 assert len(hits)==1 and kind in hits[0],(x,y,kind,hits)
# Existing central ground and Nevill own these points, not this extension.
for x,y in [(-224,-2.5),(0,26),(-100,10),(180,15),(0,55),(-60,44),(20,43)]:
 hits=[name for name,tree in trees if tree.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),100)[0] is not None];assert not hits,(x,y,hits)
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
for kind in ('bench','balustrade','column','globe','tree'):
 check_blender([next(o for o in garden if o.name.startswith('Garden '+kind+' '))])
check_blender([o for o in garden if o.name in ('Garden balustrade -214 16.4','Garden balustrade -210 16.4')])
# The photographed wide tongue stays level, and its provisional treads rise in
# order from the bounded ground. This does not establish surveyed access levels.
tongue=next(tree for name,tree in trees if name=='Fountain tongue')
a=tongue.ray_cast(Vector((-185.7,-10.4,20)),Vector((0,0,-1)),100)[0]
b=tongue.ray_cast(Vector((-185.7,-7.2,20)),Vector((0,0,-1)),100)[0]
assert a and b and abs(b.z-a.z)<1e-5,(a,b)
steps=[]
for i in range(3):
 tree=next(t for name,t in trees if name=='Fountain approach-'+str(i))
 p=tree.ray_cast(Vector((-185.7,-14.4+i,20)),Vector((0,0,-1)),100)[0]
 assert p,(i,'missing tread');steps.append(p.z)
assert all(abs((b-a)-.14)<1e-5 for a,b in zip(steps,steps[1:])),steps
check_blender([o for o in obs if (('section-05' in o.name or 'section-06' in o.name) and not o.name.endswith(' kerb')) or o.name.startswith('Fountain ')])
report={'triangles':triangles,'objects':len(obs),'checks':'Finite float32 nondegenerate triangles; UVs; budget; running road, roundabout island, pavement and ownership-exclusion probes. Open edges are intentional on ground tiles. Full coplanar audit is a separate assembled review.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
