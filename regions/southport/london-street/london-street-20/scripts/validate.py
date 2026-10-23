"""Check real front openings, roof closure and neighbour registration."""
from pathlib import Path
import json,math
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-20.blend'))
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
for name in ['Roof common main shell']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data)
 assert all(e.is_manifold for e in bm.edges),name;bm.free()
D=json.loads((ROOT/'research/layout.json').read_text());p=D['registration_pivot'];reg=Matrix.Translation((*p,0))@Matrix.Rotation(D['registration_radians'],4,'Z')@Matrix.Translation((-p[0],-p[1],0))
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
# Check the actual authored cross-section, not just matching layout settings.
roof=bpy.data.objects['Roof common main shell']
rv=[reg.inverted()@roof.matrix_world@v.co for v in roof.data.vertices]
section={tuple(round(v[i],4) for i in range(3)) for v in rv if abs(v.y-D['north_y'])<.001}
xe=D['front_x']-.20;xb=D['front_x']-D['main_depth']+.15
expected={(round(x,4),round(D['north_y'],4),round(z,4)) for x,h in [(xe,10.40),(xb,10.40),((xe+xb)/2,D['ridge_height'])] for z in [D['base_z']+h,D['base_z']+h-.14]}
assert section==expected,(section,expected)
infill=bpy.data.objects['Shop entrance dividing infill']
centre=sum((v.co for v in infill.data.vertices),Vector())/len(infill.data.vertices)
origin=infill.matrix_world@(centre+Vector((0,0,1)))
direction=(infill.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
assert hit and found==infill,'Shop entrance dividing strip must close the aperture'
report={'mesh_objects':len(meshes),'front_windows':len(windows),'checks':'Finite UV meshes, packed authored maps, eight unobscured upper window apertures, manifold common roof shell, bounds respecting neighbour division.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Cornice courses and pilasters form one closed masonry surface. Separate
# coplanar end caps caused the reported flicker at the neighbouring frontage.
body=bpy.data.objects['Envelope classical cream front']
bm=bmesh.new();bm.from_mesh(body.data)
assert all(e.is_manifold for e in bm.edges),'Open cornice/masonry union'
bm.free()
assert not any(o.name.startswith(('Trim facade moulding','Trim frieze','Trim end pilaster','Trim pilaster capital','Trim pilaster foot')) for o in meshes)
# Probe the upper two projected courses, including the formerly fighting end.
assert len(body.data.materials)==1 and body.data.materials[0].name=='Pale painted render'
assert all(p.material_index==0 for p in body.data.polygons)
for u in (.02,.3,3.75,7.48):
 for h,depth in [(10.43,.26),(10.61,.305)]:
  hit,p,n,i=body.ray_cast(Vector((u,h,1)),Vector((0,0,-1)),distance=2)
  assert hit and abs(p.z-depth)<.001,('Lost cornice profile',u,h,tuple(p) if hit else None)

for u in (1,2.5,3.75,5):
 hit,p,n,i=body.ray_cast(Vector((u,7.5,1)),Vector((0,0,-1)),distance=2)
 assert hit and abs(p.z)<.001,("Missing rendered wall",u)
