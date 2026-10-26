"""Check finite nondegenerate geometry, real facade apertures and open yard."""
import bpy,math,os,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/willow-grove.blend'));s=bpy.context.scene;bpy.context.view_layer.update()
obs=[o for o in s.objects if o.type=='MESH'];tris=0
for o in obs:
 assert o.data.uv_layers and o.data.polygons,o.name
 o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 for v in o.data.vertices:assert all(math.isfinite(x) for x in v.co)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate')
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
deps=bpy.context.evaluated_depsgraph_get();n=0
for bay in D['bay_centres']:
 for off in D['light_offsets']:
  for z in (6.1,9.8):
   hit,at,normal,i,o,m=s.ray_cast(deps,T@Vector((D['front_left']+bay+off,-1,z)),(T.to_3x3()@Vector((0,1,0))).normalized(),distance=2)
   assert hit and o.name.startswith('Architecture lord'),(bay,off,z,o.name if o else None);n+=1
for u in D['boots_bays']:
 for z in (6.5,11.2):
  hit,at,normal,i,o,m=s.ray_cast(deps,T@Vector((-1,D['wing_start']+u+.15,z)),(T.to_3x3()@Vector((1,0,0))).normalized(),distance=2)
  assert hit and o.name.startswith('Architecture nevill'),(u,z,o.name if o else None);n+=1
for y in (39,44,49):
 hit,*_=s.ray_cast(deps,T@Vector((14.5,y,1)),Vector((0,0,1)),distance=20);assert not hit,('yard filled',y)
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Shell ')])
check_blender([o for o in obs if o.name.startswith('Courtyard') or o.name=='Shell rear'])
rooflight_bars=[o for o in obs if o.name.startswith('Rooflight bars')]
assert rooflight_bars
check_blender(rooflight_bars)
# Horizontal rays just above the hip must hit the stack, not pass through an
# air gap beneath it. The old 13.55 m master base fails all three probes.
right=D['front_left']+D['front_width']
roof_at_outer=D['front_eaves']+(D['front_ridge']-D['front_eaves'])*.05/2.6
for y in (6.3,6.9,7.5):
 hit,at,normal,i,o,m=s.ray_cast(deps,T@Vector((right+.5,y,roof_at_outer+.08)),(T.to_3x3()@Vector((-1,0,0))).normalized(),distance=1.5)
 assert hit and o.name=='Architecture roof',('detached chimney',y,o.name if hit else None)
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from roof_controls import chimney_bounds
lo,hi=chimney_bounds(D)
assert lo[2]<roof_at_outer and hi[2]==16.75
from district import surfaces
coarse=[p for face in surfaces(ROOT)['roof'] if face['name'].startswith('chimney ') for p in face['vertices']]
assert coarse and abs(min(p[2] for p in coarse)-(D['base_z']+lo[2]))<1e-6,'District chimney base differs'
report={'triangles':tris,'aperture_probes':n,'yard_probes':3,'chimney_contact_probes':3,'phase':D['phase']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Correctly registered courtyard windows/vents are apertures, not wall overlays.
for name,p,direction in [('backing window',(14.2,D['wing_end']+1,5.8),(0,-1,0)),('side vent',(16.0,40.5,6.0),(1,0,0))]:
 ray=(T.to_3x3()@Vector(direction)).normalized();hit,at,normal,face,ob,mat=s.ray_cast(deps,T@Vector(p),ray,distance=2)
 assert hit and not ob.name.startswith(('Shell','Courtyard shells')),(name,ob.name if hit else None)
 assert normal.dot(ray)<-.5,(name,normal)
print('Two registered courtyard aperture probes passed')
