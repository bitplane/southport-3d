"""Check upper openings, closed roof and the shared 24 boundary."""
from pathlib import Path
import json,math,os
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-gabled-bay.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
windows=[o for o in meshes if o.name.startswith('Window upper sash')];assert len(windows)==2
for o in windows:
 origin=o.matrix_world@Vector((.2,.2,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==o,(o.name,found.name if found else None)
for o in meshes:
 if o.name.startswith(('Roof continuous pitched shell','Envelope roof end infill','Roof rear flat deck','Envelope cream front gable')):
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;bm.free()
D=json.loads((ROOT/'research/layout.json').read_text());p=D['registration_pivot'];reg=Matrix.Translation((*p,0))@Matrix.Rotation(D['registration_radians'],4,'Z')@Matrix.Translation((-p[0],-p[1],0))
points=[reg.inverted()@o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>D['south_y']-.05
assert max(v.y for v in points)<D['north_y']+.05
assert min(v.x for v in points)>D['rear_x']-.05
assert 9.9<max(v.z for v in points)<10.2
repo=Path(os.environ['SOUTHPORT_REPO_ROOT']);nd=json.loads((repo/'regions/southport/london-street/london-street-24/research/layout.json').read_text())
for f in ['front_x','base_z','registration_pivot','registration_radians']:assert D[f]==nd[f],f
assert D['north_y']==nd['south_y']
# Joined wall edges must not leave coplanar end caps on a visible rear plane.
for o in meshes:
 if o.name.startswith('Envelope party'):
  assert min((reg.inverted()@o.matrix_world@v.co).x for v in o.data.vertices)>D['front_x']-D['main_depth']+.35
 if o.name.startswith('Envelope rear store'):
  assert min((reg.inverted()@o.matrix_world@v.co).x for v in o.data.vertices)>D['rear_x']+.35
stiles=[o for o in meshes if o.name.startswith('Shop display stile')]
assert len(stiles)==3,'Two display panes share one centre stile'
report={'mesh_objects':len(meshes),'upper_windows':2,'checks':'Finite UV meshes; packed authored textures; two unobscured sashes; closed pitch/deck/endwall; shared 24boundary and geographic registration.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Manifold alone does not prove consistent winding: every roof side faces out.
roof=bpy.data.objects['Roof continuous pitched shell'];bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_contiguous for e in bm.edges),'Roof shell has reversed side faces'
assert bm.calc_volume(signed=True)>0,'Roof shell faces inward'
bm.free()
for name in ['Trim rear low coping.001','Trim brick pier foot.001']:
 o=bpy.data.objects[name];assert max((reg.inverted()@o.matrix_world@v.co).y for v in o.data.vertices)<=D['north_y']+1e-5,(name,'Crosses 24 boundary')

# Felt owns the wall-top strips while the outer brick profile is unchanged.
import sys
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
deck=bpy.data.objects['Roof rear flat deck']
for name in ('Envelope rear store north','Envelope rear store south','Envelope rear loading wall'):
 wall=bpy.data.objects[name];triangles=[];labels=[]
 for ob in (deck,wall):
  ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(ob.name)
 assert not [h for h in overlaps(triangles,labels,min_area=1e-4) if h[0]!=h[1]],name
 # Both upper outside corners remain: subtraction must not lower the wall.
 pts=[reg.inverted()@wall.matrix_world@v.co for v in wall.data.vertices]
 assert abs(max(v.z for v in pts)-(D['base_z']+3.42))<1e-4,name
# Loading-door aperture remains clear after the wall-top subtraction.
wall=bpy.data.objects['Envelope rear loading wall']
hit,*_=wall.ray_cast(Vector((2.4,1.1,1)),Vector((0,0,-1)),distance=2)
assert not hit,'Rear loading opening filled by wall-top repair'
print('Rear deck/wall faces have single ownership; outer wall height and loading opening retained')
