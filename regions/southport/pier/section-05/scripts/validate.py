from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
import bpy,math,json
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pier.blend'))
count=0
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ob.data.calc_loop_triangles()
 for t in ob.data.loop_triangles:
  a,b,c=[ob.data.vertices[i].co for i in t.vertices]
  assert all(math.isfinite(v) for p in (a,b,c) for v in p)
  assert (b-a).cross(c-a).length>1e-10,(ob.name,'degenerate')
  count+=1
assert count<160000,count
print('Pier triangles',count)
