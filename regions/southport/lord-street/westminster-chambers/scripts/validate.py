from pathlib import Path
import bpy,math,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from batch import digest
bpy.ops.wm.open_mainfile(filepath=str(R/'models/westminster-chambers.blend'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
actual,count=digest(objects)
assert actual==bpy.context.scene['source_surface_digest'], 'Export surfaces differ from checked source'
assert count==bpy.context.scene['source_triangle_count']
print('Batch surface identity:',count,'triangles',actual,'objects',len(objects))
