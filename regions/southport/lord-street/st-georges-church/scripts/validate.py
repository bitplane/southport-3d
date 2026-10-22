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
assert len([o for o in mesh if o.name.startswith('Window stone bell')])==8
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
        origin=ob.matrix_world@Vector((.23,.71,1.5))
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
for dx in (-8,-6,-4,-2,2,4,6,8):
    for y in (-26,-30,-35,-40,-45,-50):
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
assert min(p.y for p in points)>-70 and max(p.y for p in points)<-14
report={'meshes':len(mesh),'window_probes':probes,'roof_samples':samples,'checks':['finite UV meshes and packed maps','10 nave windows and 8 paired bell windows','4 pinnacles and 8 lucarnes','closed roof/spire','unobscured recessed glazing and main doorway','two-hit roof slopes','registered footprint and height bounds']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
