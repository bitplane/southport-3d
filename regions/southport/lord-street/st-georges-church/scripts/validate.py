"""Check roof closure, architectural counts and real doorway/window clearance."""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-church.blend'))
mesh=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in mesh)
assert all(math.isfinite(c) for o in mesh for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in mesh if o.name.startswith('Window stone nave')])==10
assert len([o for o in mesh if o.name.startswith('Window stone bell')])==6
assert len([o for o in mesh if o.name.startswith('Buttress nave')])==12
assert len([o for o in mesh if o.name.startswith('Pinnacle crocketed')])==4
assert len([o for o in mesh if o.name.startswith('Lucarne gabled body')])==8
for name in ['Roof nave closed shell','Roof broach spire closed','Roof rear hall closed shell']:
    ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
    assert all(e.is_manifold for e in bm.edges),(name,'unclosed roof edge')
    bm.free()
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
probes=0
for ob in mesh:
    if ob.name.startswith('Glazing panel'):
        # Probe away from a lead line; first hit must be the glazing itself,
        # not a solid wall accidentally left behind the frame.
        panel_width=max(v.co.x for v in ob.data.vertices)-min(v.co.x for v in ob.data.vertices)
        origin=ob.matrix_world@Vector((panel_width*.07,.71,1.5))
        direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
        hit,p,n,idx,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
        assert hit and target==ob,(ob.name,'obscured glazing',target.name if target else None)
        probes+=1
# The principal recessed door is physically visible below its gable canopy.
origin=Vector((D['centre_x']+.055,D['tower_front_y']+2,D['base_z']+1.4))
hit,p,n,idx,target,matrix=bpy.context.scene.ray_cast(deps,origin,Vector((0,-1,0)),distance=3)
assert hit and target.name=='Door main leaf',('Blocked porch',target.name if target else None)
# Ray-sample both nave slopes. Exactly two shell hits: exterior and underside.
roof=bpy.data.objects['Roof nave closed shell'];samples=0
for dx in [D['nave_width']/2*f for f in (-.9,-.7,-.5,-.3,.3,.5,.7,.9)]:
    for i in range(6):
        y=D['rear_y']+(min(D['nave_front_y'],D['tower_back_y'])-D['rear_y'])*(i+.5)/6
        origin=Vector((D['centre_x']+dx,y,30));hits=[]
        for _ in range(4):
            hit,p,n,idx=roof.ray_cast(origin,Vector((0,0,-1)),distance=30)
            if not hit:break
            hits.append((p.z,n.z));origin=p+Vector((0,0,-.0001))
        assert len(hits)==2 and hits[0][1]>0 and hits[1][1]<0,(dx,y,hits)
        samples+=1
points=[ob.matrix_world@v.co for ob in mesh for v in ob.data.vertices]
assert 47<max(p.z for p in points)<49
assert min(p.x for p in points)>157 and max(p.x for p in points)<180
# OSM 51826176 describes the combined church/hall envelope, not the nave
# alone. Its rear edge is about 15 m ahead of the supermarket's rear wall.
assert -54<min(p.y for p in points)<-50, 'Church/hall intrudes into rear parking'
assert max(p.y for p in points)<-14
assert D['nave_front_y']-D['rear_y']<23, 'Nave includes the hall footprint'
assert D['rear_hall']['bounds_xy'][3]<D['rear_y']
# Hood mould width + buttress width must fit a bay without intersections.
for ob in [o for o in mesh if o.name.startswith('Window stone nave')]:
    xs=[v.co.x for v in ob.data.vertices]
    assert max(xs)-min(xs)+.92 < (D['nave_front_y']-D['rear_y'])/5
report={'meshes':len(mesh),'window_probes':probes,'roof_samples':samples,'checks':['finite UV meshes and packed maps','10 nave windows and 6 paired bell windows','4 pinnacles and 8 lucarnes','closed roof/spire','unobscured recessed glazing and main doorway','two-hit roof slopes','registered footprint and height bounds']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Roof cannot cross the tower footprint, and the rear belfry face stays blank.
for dx in [-2,-1,0,1,2]:
 hit,p,n,i=roof.ray_cast(Vector((D['centre_x']+dx,D['tower_back_y']+.2,30)),Vector((0,0,-1)),distance=30)
 assert not hit,'Nave roof inside tower'
back=bpy.data.objects['Envelope tower back']
for u in [D['tower_width']/2-1.14,D['tower_width']/2+1.14]:
 origin=back.matrix_world@Vector((u,18,1))
 direction=(back.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,p,n,i=back.ray_cast(back.matrix_world.inverted()@origin,(back.matrix_world.inverted().to_3x3()@direction).normalized(),distance=2)
 assert hit,'Invented rear belfry aperture'
assert len([o for o in mesh if o.name.startswith('Buttress weathering')])==12

# The repeated nave/bell tracery must not contain coincident front/back jambs.
import os,sys
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from coplanar import overlaps
from components import arch_ring,foil
from southport3d.geometry import Mesh
seen=set()
for ob in mesh:
 if not ob.name.startswith(('Window stone nave','Window stone bell','Window stone front-flank')) or ob.data.name in seen:continue
 seen.add(ob.data.name);ob.data.calc_loop_triangles()
 triangles=[[tuple(ob.data.vertices[i].co) for i in t.vertices] for t in ob.data.loop_triangles]
 assert not overlaps(triangles,[ob.name]*len(triangles),min_area=1e-5),ob.name
# Open-bottom arch strips still need closed end caps; closed foils need no seam caps.
for kind in ('arch-with-sill','arch-open-bottom','foil'):
 m=Mesh('Regression '+kind)
 if kind=='foil':foil(m,0,0,.32,4)
 else:arch_ring(m,.825,2.45,5.75,sill=kind=='arch-with-sill')
 ob=m.finish([]);bm=bmesh.new();bm.from_mesh(ob.data)
 assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(kind,'Open or inverted profile')
 assert bm.calc_volume(signed=True)>0,(kind,'Inward profile')
 bm.free();data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
print('Repeated tracery has no coplanar overlaps; arch and foil shells are closed')

# The enlarged wall apertures stop behind the stone surrounds without removing
# the narrow visible wall strip between the first and second moulding orders.
wall_names=('Envelope nave south','Envelope nave north','Envelope front gable',
            'Envelope tower front','Envelope tower south','Envelope tower north')
wall_objects=[bpy.data.objects[n] for n in wall_names];ownership_probes=0
for ob in mesh:
 if ob.name.startswith('Window stone nave'):radius,bottom=.825,2.45
 elif ob.name.startswith('Window stone front-flank'):radius,bottom=.94,5.25
 elif ob.name.startswith('Window stone bell'):radius,bottom=.89,15.45
 else:continue
 outward=(ob.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
 candidates=[w for w in wall_objects if (w.matrix_world.to_3x3()@Vector((0,0,1))).normalized().dot(outward)>.999 and abs((w.matrix_world.inverted()@ob.matrix_world.translation).z)<1e-4]
 assert len(candidates)==1,(ob.name,'Missing coplanar wall owner')
 wall=candidates[0];inverse=wall.matrix_world.inverted();direction=(inverse.to_3x3()@(-outward)).normalized()
 for sign in (-1,1):
  point=ob.matrix_world@Vector((sign*(radius+.08),bottom+.6,1))
  assert not wall.ray_cast(inverse@point,direction,distance=2)[0],(ob.name,'Masonry inside surround')
  point=ob.matrix_world@Vector((sign*(radius+.175),bottom+.6,1))
  assert wall.ray_cast(inverse@point,direction,distance=2)[0],(ob.name,'Missing wall between mouldings')
  point=ob.matrix_world@Vector((sign*(radius+.08),bottom+.6,1))
  hit,p,n,i,target,matrix=bpy.context.scene.ray_cast(deps,point,-outward,distance=2)
  assert hit and target==ob,(ob.name,'Surround failed to cover wall opening',target.name if hit else None)
 ownership_probes+=1
assert ownership_probes==18
print('18 window surrounds cover their wall apertures; inter-order wall strips retained')
