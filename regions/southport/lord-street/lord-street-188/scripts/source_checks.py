"""Validate authored meshes before any semantic batching."""
import bpy,math,os,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps

def validate():
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=[];labels=[]
 for ob in obs:
  ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   p=[ob.matrix_world@ob.data.vertices[i].co for i in t.vertices]
   assert all(math.isfinite(x)for v in p for x in v)
   assert (p[1]-p[0]).cross(p[2]-p[0]).length>1e-9,(ob.name,'degenerate')
   triangles.append([tuple(v)for v in p]);labels.append(ob.name)
 assert len(triangles)<70000
 issues=overlaps(triangles,labels);assert not issues,issues[:20]
 scene=bpy.context.scene;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 for point in ((455,-33.5,1),(455,-65,1)):
  hit,*_=scene.ray_cast(deps,Vector(point),Vector((0,0,1)),distance=40);assert not hit,('gap',point)
 print('AUTHORING_CHECK',len(obs),len(triangles),'no degenerate/coplanar and two open gaps',flush=True)
