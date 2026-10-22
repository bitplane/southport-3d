"""Check identity, registration and exposed windows rather than mesh counts alone."""
from pathlib import Path
import json
import math
import os
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from roof import roof_height
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-6-12.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
assert all(obj.data.polygons and obj.data.uv_layers for obj in meshes)
assert all(math.isfinite(x) for obj in meshes for v in obj.data.vertices for x in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
windows=[obj for obj in meshes if obj.name.startswith('Window front ')]
assert len(windows)==24, len(windows)
points=[obj.matrix_world@v.co for obj in meshes for v in obj.data.vertices]
assert -31<min(v.x for v in points)<-29
assert -9.5<max(v.x for v in points)<-8.8
assert min(v.y for v in points)>-64 and max(v.y for v in points)<-41
assert 12<max(v.z for v in points)<14
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
for obj in windows:
    origin=obj.matrix_world@Vector((.23,.23,1))
    direction=(obj.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and found==obj,(obj.name,found.name if found else None)
# Ground entrance remains set back from the display panes, not a wall filling it.
doors=[obj for obj in meshes if obj.name.startswith('Shop recessed door leaf')]
assert len(doors)==2
assert all(max((obj.matrix_world@v.co).x for v in obj.data.vertices)<D['front_x']-.5 for obj in doors)
# No coincident exterior faces on the Glebe wall or its corner cap. These
# samples exposed overlapping return boxes as black patches in the render.
shared_pier_u=(D['north_y']-D['south_y'])/D['upper_bays']*D['halifax_bays']+.10
for origin,direction in [(Vector((D['front_x']+1,D['south_y']+shared_pier_u,D['base_z']+1.1)),Vector((-1,0,0))),
                         (Vector((-28,D['south_y']-1,D['base_z']+2)),Vector((0,1,0))),
                         (Vector((D['front_x']+1,D['south_y']+.16,D['base_z']+6.6)),Vector((-1,0,0)))]:
    distances=[]
    for obj in meshes:
        inverse=obj.matrix_world.inverted()
        hit,p,n,index=obj.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized())
        if hit:
            distances.append(((obj.matrix_world@p-origin).length,obj.name))
    distances.sort()
    assert distances and sum(abs(distance-distances[0][0])<1e-5 for distance,name in distances)==1,distances[:3]
roof=bpy.data.objects['Roof hipped slate envelope']
bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges),'Open roof edge'
bm.free()
roof_probes=0
for ix in range(1,40):
    x=D['rear_x']+ix*.5
    for iy in range(1,44):
        y=D['south_y']+iy*.5
        excluded=any(a<x<b and c<y<d for a,b,c,d in D['roof_cutouts'])
        hit,p,n,index=roof.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),distance=20)
        assert hit!=excluded,('Roof coverage',x,y,hit,excluded)
        if hit:
            assert abs(p.z-roof_height(D,x,y))<1e-4 and n.z>0,('Non-planar roof fold',p,n)
            hit,q,n,index=roof.ray_cast(p+Vector((0,0,-.0001)),Vector((0,0,-1)),distance=20)
            assert hit and abs(p.z-q.z-.14)<1e-4 and n.z<0,('Roof underside',p,q,n)
        roof_probes+=1

def clip_axis(poly,axis,bound,lower):
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp=(p[axis]-bound)*(1 if lower else -1)
        dq=(q[axis]-bound)*(1 if lower else -1)
        if dp>=0:result.append(p)
        if (dp>=0)!=(dq>=0):result.append(p+(q-p)*(dp/(dp-dq)))
    return result

# Keep the entire clearance volumes free, including walls and minor pipes,
# not just roof vertices. Large triangles can span a well without a vertex in it.
for box in D['stair_clearance_boxes']:
    low=(box[0],box[2],box[4]);high=(box[1],box[3],box[5])
    for obj in meshes:
        verts=[obj.matrix_world@v.co for v in obj.data.vertices]
        if any(max(v[k] for v in verts)<=low[k] or min(v[k] for v in verts)>=high[k] for k in range(3)):continue
        for face in obj.data.polygons:
            poly=[verts[i] for i in face.vertices]
            if any(max(v[k] for v in poly)<=low[k] or min(v[k] for v in poly)>=high[k] for k in range(3)):continue
            for k in range(3):
                poly=clip_axis(poly,k,low[k],True)
                poly=clip_axis(poly,k,high[k],False)
            area=sum((poly[i]-poly[0]).cross(poly[i+1]-poly[0]).length/2 for i in range(1,len(poly)-1)) if len(poly)>2 else 0
            assert area<1e-7,('Neighbour escape stair obstructed',obj.name,box,area)
report={'objects':len(meshes),'front_windows':len(windows),'roof_probes':roof_probes,'checks':'Finite UV meshes, packed maps, registered extent, 24 unobscured front windows, recessed double entrance, closed planar roof shell, open rear court and both neighbour stair wells'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)

# Every observed court window belongs to the recessed rear wall, not the south
# projection; inspect glazing rays as well as mesh counts so walls cannot fill it.
service_windows=[o for o in meshes if o.name.startswith('Window rear casement')]
assert len(service_windows)==8
assert all(abs(o.matrix_world.translation.x-D['upper_rear_x'])<1e-6 for o in service_windows)
side_windows=[o for o in meshes if o.name.startswith('Window Glebe casement')]
assert len(side_windows)==2
for obj in service_windows+side_windows:
    origin=obj.matrix_world@Vector((.13,.12,1))
    direction=(obj.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,p,n,i,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and found==obj,(obj.name,'service window obscured',found.name if found else None)
assert D['rear_eaves_height']<D['eaves_height']-1.5,'Lost lower rear roof level'
print('Eight courtyard windows, two plain Glebe casements and lower rear eave checked')

# The aerial's pale southern service deck is exposed, not buried in pitched slate.
for y in [-57.5,-60,-62.5]:
 origin=Vector((-27.5,y,20))
 hit,p,n,i,found,matrix=bpy.context.scene.ray_cast(deps,origin,Vector((0,0,-1)),distance=20)
 assert hit and found.name.startswith('Roof south wing flat deck'),('Southern deck obscured',y,found.name if found else None)

# Follow the hip intersection along the rear wall, rather than checking its ends.
for i in range(1,60):
 y=D['south_y']+.36+i*((-55.7)-(D['south_y']+.36))/60
 x=D['upper_rear_x'];z=roof_height(D,x,y)-.18
 wall=bpy.data.objects['Envelope southern rear upper return']
 hit,p,n,index=wall.ray_cast(Vector((x-1,y,z)),Vector((1,0,0)),distance=1.1)
 assert hit,('Gap under rear hip',y,z)
print('Rear wall closes to both roof planes across the hip seam')

# Sample the previously open strip under the fascia and beside number-six door.
xf=D['front_x'];ys=D['south_y'];base=D['base_z'];width=D['north_y']-ys
for u,h in [(1.6,3.08),(4.9,3.08),(8.3,3.08),(11.7,3.08),(15,3.08),(width-1.39,1.2),(width-.78,2.9)]:
    hit,p,n,i,found,matrix=bpy.context.scene.ray_cast(deps,Vector((xf+1,ys+u,base+h)),Vector((-1,0,0)),distance=2)
    assert hit and found.name.startswith('Shop '),('Open frontage gap',u,h,found.name if hit else None)

# The new soffit must stay behind the retail sign's upper blank margin.
sign=bpy.data.objects['Sign Post and Packing']
origin=sign.matrix_world@Vector((.30,.18,1))
direction=sign.matrix_world.to_3x3()@Vector((0,0,-1))
hit,p,n,i,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
assert hit and found==sign,('Retail sign obscured by soffit',found.name if hit else None)
