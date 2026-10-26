import bpy,json,math,os,sys
from pathlib import Path
from plan import D,W,L,world
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(REPO/'tools'));sys.path.insert(0,str(REPO/'lib'))
from coplanar import check_blender
from southport3d.elevation import Elevations
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/funland.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];n=0
for o in obs:
 assert o.data.uv_layers,o.name;o.data.calc_loop_triangles();n+=len(o.data.loop_triangles)
 for v in o.data.vertices:assert all(math.isfinite(x)for x in v.co)
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-10,(o.name,t.index)
check_blender(obs)
surface=Elevations(REPO/'regions/southport/elevation/nevill.json').surface('nevill-pavement');checks=[]
for x,y in [(0,0),(W,0),(0,L),(W,L)]:
 p=world((x,y,0));ground=surface.height(*p[:2]);assert p[2]>=ground-.02 and p[2]-ground<.3;assert D['base']+D['footing']<ground;checks.append({'point':p,'ground':ground,'floor_gap':p[2]-ground})
# Carousel retains level roof/floor but enclosure footing seats below rough grade.
from plan import canopy_ring
for q in canopy_ring(D['carousel']['radius']*.79,-.25,48):
 p=world(q);assert p[2]<surface.height(*p[:2]),('carousel footing',p)
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':n,'coplanar':'All exported source meshes, shell, roofs, parapet, glazing, repeated trim, lettering and carousel included','supports':checks},indent=2));print('Funland validated',n)
