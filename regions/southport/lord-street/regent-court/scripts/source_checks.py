import bpy,math,os,sys
from pathlib import Path

def validate():
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  assert o.data.polygons and o.data.uv_layers,o.name
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co),o.name
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   a,b,c=[o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-9,(o.name,'degenerate')
 
 import os,sys
 sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
 from coplanar import check_blender
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 check_blender([o for o in meshes if o.name.startswith(('Wall span','Wall sill','Wall head','Core masonry','End wall'))])
 check_blender([o for o in meshes if o.name.startswith(('Window vertical','Window horizontal','Window mullion','Window pale sill'))])
 check_blender([o for o in meshes if o.name.startswith(('Podium end skin','Podium rear skin','Service wall','Service parapet'))])
 check_blender([o for o in meshes if o.name.startswith('Fine balcony')])
 check_blender([o for o in meshes if o.name.startswith(('Door frame','Door rail','Roof lantern rib','Roof lantern ridge'))])
 check_blender([o for o in meshes if o.name.startswith(('Roof band','Roof deck','Roof access','Roof opening edge','Roof opening return'))])
 print('Audited tower wall skins and window frames separately; podium, railings and roof interfaces remain subject to visual and published audit.')
