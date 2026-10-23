"""Check actual openings, gable count and footprint registration."""
import json
import math
import os
import sys
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.planar import area, halfplane
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/natwest.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
# Compare in linear colour space: PNG pixels are encoded sRGB, shader values
# are linear. The lower-level wall must match the omitted Detail stone skins.
image=next(im for im in bpy.data.images if im.name.startswith('sandstone'))
pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
rgb=pixels.reshape(-1,4)[:,:3]
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4).mean(axis=0)
ashlar=np.array(bpy.data.materials['Sandstone relief 1'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3])
assert np.max(np.abs(linear-ashlar))<.02,('LoD sandstone albedo mismatch',linear,ashlar)
assert len([o for o in meshes if o.name.startswith('Gable ')])==3
assert len([o for o in meshes if o.name.startswith('Window oculus')])==3
assert len([o for o in meshes if o.name.startswith('Balcony rails')])==3
assert len([o for o in meshes if o.name.startswith('ATM metal')])==2
assert len([o for o in meshes if o.name.startswith('Chimney stack')])==4
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for ob in meshes:
    if not ob.name.startswith(('Window cross','Window narrow','Window oculus')):continue
    probe=.30 if ob.name.startswith(('Window cross','Window narrow')) else 0
    origin=ob.matrix_world@Vector((probe,0,1))
    direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and target==ob,(ob.name,'window obscured by',target.name if target else None)
# Two single-pane lower windows: a cross-window generator previously introduced
# extra mullions and intersecting oversized hoods in this narrow pair.
low_windows=[o for o in meshes if o.name.startswith('Window low side')]
assert len(low_windows)==2
for ob in low_windows:
    origin=ob.matrix_world@Vector((0,0,1))
    direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and target==ob and ob.data.polygons[index].material_index==1,('Lower single light obstructed',ob.name)
for ob in meshes:
    if ob.name.startswith('Trim surround Window low side'):
        assert max(abs(v.co.x) for v in ob.data.vertices)<.82, 'Adjacent lower window heads overlap'
# Three Lord Street hoods must fit between their3.35m centres.
front_heads=[o for o in meshes if o.name.startswith('Trim surround Window cross lord')]
assert len(front_heads)==3
assert all(max(abs(v.co.x) for v in o.data.vertices)<3.35/2 for o in front_heads), 'Upper hoods overlap'
points=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert min(p.x for p in points)>D['x_min']-1.3
assert max(p.x for p in points)<33.2  # Boundary stops at Posting House; kiosk trim projects 2 cm.
assert min(p.y for p in points)>D['rear_y']-.5
assert max(p.y for p in points)<D['front_y']+1.5
# Wall backing must close the strip between cornice and open parapet.
for origin,direction,prefix in [
    (Vector((D['x_max']-8,D['front_y']+1,D['base_z']+12.50)),Vector((0,-1,0)),'Envelope lord'),
    (Vector((D['x_min']-1,D['front_y']-14,D['base_z']+12.50)),Vector((1,0,0)),'Envelope london')]:
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and target.name.startswith((prefix,'Ashlar ')),('Open parapet footing',target.name if hit else None)
# The inner deck must stay below the pitched perimeter; no huge solid roof slab.
hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,Vector((24,-40,25)),Vector((0,0,-1)),distance=25)
assert hit and point.z<12,(target.name,point)
# Open sheets and overlapping hip/gable surfaces previously passed the ordinary
# finite-mesh tests. Require one closed roof and exactly one upward roof skin.
roof=bpy.data.objects['Roof joined slate']
bm=bmesh.new();bm.from_mesh(roof.data)
assert all(e.is_manifold for e in bm.edges), 'Open or non-manifold roof edge'
bm.free()
roof_samples=0
for ix in range(1,45):
    x=D['x_min']+.3+ix*.5
    for iy in range(1,57):
        y=D['front_y']-.3-iy*.5
        if x>D['x_max']-.1 or y<D['rear_y']+.1:continue
        if x>D['x_min']+D['roof_ranges']['side_width']-.05 and y<D['front_y']-D['roof_ranges']['front_depth']+.05:continue
        origin=Vector((x,y,25));hits=[]
        for _ in range(5):
            hit,point,normal,index=roof.ray_cast(origin,Vector((0,0,-1)),distance=25)
            if not hit:break
            hits.append((point.z,normal.z));origin=point+Vector((0,0,-.0001))
        assert len(hits)==2 and hits[0][1]>0 and hits[1][1]<0,(x,y,hits)
        roof_samples+=1
# Detect positive-area coplanar overlap on the external building envelope.
# Shared edges are allowed; duplicate outer wall/deck skins are not.
for axis,value in [(0,D['x_min']),(0,D['x_max']),(1,D['front_y']),(1,D['rear_y'])]:
    axes=[i for i in range(3) if i!=axis];surfaces=[]
    for ob in meshes:
        if not ob.name.startswith(('Envelope ','Roof ')):continue
        for face in ob.data.polygons:
            vertices=[ob.matrix_world@ob.data.vertices[i].co for i in face.vertices]
            if any(abs(v[axis]-value)>1e-5 for v in vertices):continue
            poly=[(v[axes[0]],v[axes[1]]) for v in vertices]
            signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))
            if signed<0:poly.reverse()
            if area(poly)>1e-7:surfaces.append((ob.name,poly))
    for i,(name,poly) in enumerate(surfaces):
        for other,cutter in surfaces[i+1:]:
            if name==other:continue
            if any(max(p[k] for p in poly)<=min(p[k] for p in cutter)+2e-5 or
                   max(p[k] for p in cutter)<=min(p[k] for p in poly)+2e-5 for k in range(2)):continue
            overlap=poly
            for a,b in zip(cutter,cutter[1:]+cutter[:1]):
                overlap=halfplane(overlap,a,b)
            assert area(overlap)<1e-5,('Coplanar exterior skins',name,other,axis,value,area(overlap))
report={'meshes':len(meshes),'roof_samples':roof_samples,'checks':'finite metric meshes, packed maps, three gables/oculi and balconies, two ATMs, four stacks, unobscured main glazing and oculi, footprint limits, lower internal deck, closed roof and single visible skin, no coplanar exterior envelopes'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)

# A short saddle must disappear into the hip, not end as an exposed vertical step.
end=D['front_y']-D['roof_ranges']['corner_saddle_depth']
for face in roof.data.polygons:
 points=[roof.data.vertices[i].co for i in face.vertices]
 if all(abs(p.y-end)<1e-4 for p in points) and abs(face.normal.z)<.08:
  assert face.area<.02 or max(p.z for p in points)<D['base_z']+12.40,('Exposed corner saddle endcap',face.area)

# Cash-machine apertures must expose the inset screen, not uncut ashlar.
for ob in [o for o in meshes if o.name.startswith('ATM screen') and not o.name.startswith('ATM screen hood')]:
    origin=ob.matrix_world@Vector((-.115,.08,1))
    direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and target==ob, ('ATM screen obscured',target.name if hit else None)
assert len([o for o in meshes if o.name.startswith('Door wall handrail')])==2
steps=[o for o in meshes if o.name.startswith('Trim entrance step')]
assert len(steps)==4
assert sorted(round(max(v.co.y for v in o.data.vertices),2) for o in steps)==[.14,.28,.42,.56]

# Kiosk regressions: a square compound cap, eight margin-glazed rows on three
# faces, solid rear and stable dimensions at every viewing level.
sys.path.insert(0,str(ROOT/'scripts'))
from kiosk import kiosk
from mathutils.bvhtree import BVHTree
counts=[]
for level in ['detail','walk','district']:
    model=kiosk(level)
    tree=BVHTree.FromPolygons(model.vertices,model.faces)
    counts.append(sum(len(f)-2 for f in model.faces))
    assert abs(max(v[1] for v in model.vertices)-2.54)<1e-6
    for axis in [0,2]:
        assert .459<max(v[axis] for v in model.vertices)<.50
    for rotation in [0,math.pi/2,3*math.pi/2]:
        from mathutils import Matrix
        frame=Matrix.Rotation(rotation,4,'Y')
        for j in range(8):
            for x in [0,-.275,.275]:
                origin=frame@Vector((x,.32+(j+.5)*1.73/8,.6))
                point,normal,index,distance=tree.ray_cast(origin,frame@Vector((0,0,-1)),.3)
                assert index is not None and model.indices[index]==2,(level,j,x,'K6 pane obscured')
    point,normal,index,distance=tree.ray_cast(Vector((0,1,-.6)),Vector((0,0,1)),.3)
    assert index is not None and model.indices[index]==0,(level,'K6 rear must be solid')
    top=tree.ray_cast(Vector((0,3,0)),Vector((0,-1,0)))[0].y
    for x,z in [(.40,0),(0,.40)]:
        edge=tree.ray_cast(Vector((x,3,z)),Vector((0,-1,0)))[0].y
        assert top-edge>.05,(level,'K6 roof became a barrel or flat cap')
assert counts[0]>counts[1]>counts[2],counts
print('K6 roof, glazing, solid back and LOD reductions checked',counts)

# The larger entrance hood replaces the outer window arch moulding.
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import overlaps
hood=bpy.data.objects['Trim main entrance hood']
# Find its colocated arched opening by frame origin, not Blender suffix order.
arch=min((o for o in meshes if o.name.startswith('Window arch')),
         key=lambda o:(o.matrix_world.translation-hood.matrix_world.translation).length)
triangles=[];labels=[]
for ob in (hood,arch):
    ob.data.calc_loop_triangles()
    for t in ob.data.loop_triangles:
        triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);labels.append(ob.name)
errors=[hit for hit in overlaps(triangles,labels,min_area=1e-4) if hit[0]!=hit[1]]
assert not errors,errors[:8]
print('Entrance hood/window moulding ownership passed')
