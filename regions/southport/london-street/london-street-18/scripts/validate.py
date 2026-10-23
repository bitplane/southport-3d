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
# Scan the exterior aperture: panels/returns must close it within the front
# half-metre, rather than rays escaping to an unrelated rear wall.
front=bpy.data.objects['Envelope four-bay rendered front'].matrix_world
for u,h in [(u,h) for u in [.42,1.52,1.86,2.2,4.0,6.22,7.3,7.65] for h in [.1,1.3,2.73,2.82,3.63]]:
 hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,front@Vector((u,h,1)),(front.to_3x3()@Vector((0,0,-1))).normalized(),distance=1.55)
 assert hit,(u,h,'Open shopfront or fascia')
points=[reg.inverted()@o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>D['south_y']-.1
assert max(v.y for v in points)<D['north_y']+.1
assert min(v.x for v in points)>D['rear_x']-.1
assert 12.8<max(v.z for v in points)<13.1
# Common ridge/eaves section must match the adjoining unit's source dimensions.
other='20' if D['north_y']==-80.25 else '18'
repo=Path(__import__('os').environ['SOUTHPORT_REPO_ROOT'])
nd=json.loads((repo/'regions/southport/london-street'/('london-street-'+other)/'research/layout.json').read_text())
for field in ['front_x','main_depth','ridge_height','base_z','registration_pivot','registration_radians']:assert D[field]==nd[field],field
assert (D['south_y']==nd['north_y'] if other=='20' else D['north_y']==nd['south_y'])
report={'mesh_objects':len(meshes),'front_windows':len(windows),'checks':'Finite UV meshes, packed authored maps, eight unobscured upper window apertures, two manifold roof shells, bounds respecting neighbour division.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Rear wing corners have one owner, including their exposed end caps.
import os,sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
triangles=[];labels=[]
for name in ('Envelope rear wing north','Envelope rear wing south','Envelope rear service end'):
 ob=bpy.data.objects[name];ob.data.calc_loop_triangles()
 for t in ob.data.loop_triangles:
  triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(name)
errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
assert not errors,errors[:8]
print('Rear wing corner ownership passed')
