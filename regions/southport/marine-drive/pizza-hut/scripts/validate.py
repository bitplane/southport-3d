import bpy,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pizza-hut.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(v) for p in o.data.vertices for v in p.co),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-9,(o.name,'degenerate')
roof=bpy.data.objects['Roof lower 0'];assert all(p.normal.z>0 for p in roof.data.polygons), 'roof normals must face up for district projection'
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Wall ')])
check_blender([o for o in obs if o.name.startswith('Frame front ')])
check_blender([o for o in obs if o.name.startswith(('Frame side ', 'Side reveal '))])
print('Checked finite geometry, triangles, wall ownership and front and side frames with side reveals; roof interfaces and remaining joinery require visual review.')
