"""Check registration, clear apertures and closed roof shell."""
from pathlib import Path
import json,math
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-14-16.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
windows=[o for o in meshes if o.name.startswith('Window front')]
assert len(windows)==6
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows:
 origin=o.matrix_world@Vector((.2,0,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==o,(o.name,found.name if found else None)
roof=bpy.data.objects['Roof front slope'];bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges);bm.free()
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert -27.2<min(v.x for v in points)<-26.2
assert -12.2<max(v.x for v in points)<-11
assert min(v.y for v in points)>-81.3 and max(v.y for v in points)<-68.3
assert 10.8<max(v.z for v in points)<11.6
report={'mesh_objects':len(meshes),'front_windows':len(windows),'checks':'Finite UV meshes, packed procedural maps, mapped bounds, six unobscured window apertures, closed pitched roof shell.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
