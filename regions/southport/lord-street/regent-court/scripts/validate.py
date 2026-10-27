import bpy,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from batch import digest
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/regent-court.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(v) for p in o.data.vertices for v in p.co),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-9,(o.name,'degenerate')
assert digest(obs)==(bpy.context.scene['source_surface_digest'],bpy.context.scene['source_triangle_count'])
print('Original family-specific surface ownership validated before batching; triangle digest preserved after reload.')
