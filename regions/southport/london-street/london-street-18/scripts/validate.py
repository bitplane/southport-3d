"""Check real front openings, roof closure and neighbour registration."""
from pathlib import Path
import json,math
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-18.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
windows=[o for o in meshes if o.name.startswith('Window front')];assert len(windows)==8
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows:
 origin=o.matrix_world@Vector((.2,0,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==o,(o.name,found.name if found else None)
for name in ['Roof main hip shell','Roof rear wing shell']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data)
 assert all(e.is_manifold for e in bm.edges),name;bm.free()
D=json.loads((ROOT/'research/layout.json').read_text());p=D['registration_pivot'];reg=Matrix.Translation((*p,0))@Matrix.Rotation(D['registration_radians'],4,'Z')@Matrix.Translation((-p[0],-p[1],0))
points=[reg.inverted()@o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>D['south_y']-.1
assert max(v.y for v in points)<D['north_y']+.1
assert min(v.x for v in points)>D['rear_x']-.1
assert 12.8<max(v.z for v in points)<13.1
report={'mesh_objects':len(meshes),'front_windows':len(windows),'checks':'Finite UV meshes, packed authored maps, eight unobscured upper window apertures, two manifold roof shells, bounds respecting neighbour division.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
