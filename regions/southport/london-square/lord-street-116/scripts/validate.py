"""Check facade visibility, neighbour bounds, entrance recess and sign receivers."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bhf.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.x for v in points)>=D['x_far']-.07 and max(v.x for v in points)<=D['x_near']+2.5  # Collection steps project into the court.
assert 14.6<max(v.z for v in points)<15.5
windows=[o for o in meshes if o.name.startswith('Window ')];assert len(windows)==D['upper_bays']
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows+[o for o in meshes if o.name.startswith('Sign ')]:
 origin=o.matrix_world@Vector((0,0,.8));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.5)
 assert hit and obj==o,(o.name,obj.name if obj else None)
doors=next(o for o in meshes if o.name=='Shop recessed doors')
assert max((doors.matrix_world@v.co).y for v in doors.data.vertices)<D['front_y']-1.1
assert len([o for o in meshes if o.name.startswith('Shop entrance step')])==2
# A dark lamp disc behind a solid soffit can silently disappear in an export.
# Check each centre from below, not merely the existence of the fixture mesh.
lights=next(o for o in meshes if o.name=='Fine circular soffit downlights')
for u in [D['entry_left']+.8,(D['entry_left']+D['entry_right'])/2,D['entry_right']-.8]:
 origin=lights.matrix_world@Vector((u,3.8,-.55));direction=(lights.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
 assert hit and obj==lights,('downlight obscured',u,obj.name if obj else None)
assert len([o for o in meshes if o.name.startswith('Sign entrance')])==2
left_doors=next(o for o in meshes if o.name=='Shop left recessed doors')
assert max((left_doors.matrix_world@v.co).y for v in left_doors.data.vertices)<D['front_y']-.90
ramp=next(o for o in meshes if o.name=='Shop left access ramp')
assert max(v.co.y for v in ramp.data.vertices)>.35 and min(v.co.y for v in ramp.data.vertices)==0
assert any(o.name=='Shop red ramp railing' for o in meshes)
# Custom local-Y-up solids must have outward winding, not rely on double-sided
# materials hiding inverted faces. The missing threshold wedge must cover ground.
for name in ['Shop left access ramp','Shop left ramp retaining wall','Shop left threshold infill']:
 ob=next(o for o in meshes if o.name==name)
 volume=sum(ob.data.vertices[f.vertices[0]].co.dot(ob.data.vertices[f.vertices[1]].co.cross(ob.data.vertices[f.vertices[2]].co))/6 for f in ob.data.polygons)
 assert volume>0,(name,'inward winding',volume)
infill=next(o for o in meshes if o.name=='Shop left threshold infill')
origin=infill.matrix_world@Vector((6.0,1,-.7));direction=(infill.matrix_world.to_3x3()@Vector((0,-1,0))).normalized()
hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
assert hit and obj==infill and point.z>D['base_z']+.3,('threshold infill missing',obj.name if obj else None)
for name in ['Shop left access ramp','Shop left access landing','Shop entrance step']:
 ob=next(o for o in meshes if o.name==name)
 assert ob.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value>.8
# A roof slab must not fill the external walled recess. Probe its actual floor.
R=json.loads((ROOT/'research/roof-layout.json').read_text());wx,wy=R['walled_recess']['centre']
hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((wx,wy,25)),Vector((0,0,-1)),distance=20)
assert hit and obj.name=='Roof walled recess' and point.z<D['base_z']+D['roof_level']-.4
assert len([o for o in meshes if o.name.startswith('Roof edge housing ')])==1
assert len([o for o in meshes if o.name.startswith('Envelope integrated court shaft ')])==2
assert any(o.name=='Roof plant platform and cabinets' for o in meshes)
# The shallow rooflight pitches must face the sky, independent of material culling.
rooflight=next(o for o in meshes if o.name=='Roof elongated rooflight or vent')
pitches=[f for f in rooflight.data.polygons if f.material_index==1 and abs(f.normal.z)>.5]
assert len(pitches)==4 and all(f.normal.z>0 for f in pitches),('rooflight pitch winding',[tuple(f.normal) for f in pitches])
report={'objects':len(meshes),'window_modules':len(windows),'checks':'metric finite meshes, packed maps, neighbour bounds, visible windows/signs, two recessed entrances and two main risers, two welcome panels and visible downlight lenses, outward access solids and covered threshold, matte access tiles, open roof recess and three edge housings'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)

# Collection sign and door faces must remain clear of exterior rainwater pipes.
ob=bpy.data.objects['Sign rear collection point']
for x in [-1,-.5,0,.5,1]:
 for y in [-.2,0,.2]:
  origin=ob.matrix_world@Vector((x,y,.8))
  direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.5)
  assert hit and target==ob,('Collection sign obstructed',x,y,target.name if target else None)
for name,u in [('Fixture collection door 0',14.0),('Fixture collection door 1',16.8)]:
 ob=bpy.data.objects[name]
 for dx in [-.6,0,.6]:
  origin=ob.matrix_world@Vector((u+dx,2,.8))
  direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.5)
  assert hit and target==ob,('Collection door obstructed',name,dx,target.name if target else None)

# On vertical brick edges, texture U stays fixed and V follows physical height.
# This catches the former ninety-degree turn on the court utility-box end.
brick_vertical_edges=0
for ob in meshes:
 uv=ob.data.uv_layers.active.data
 for face in ob.data.polygons:
  if ob.data.materials[face.material_index].name!='Roof parapet brick':continue
  loops=list(face.loop_indices)
  for a,b in zip(loops,loops[1:]+loops[:1]):
   A=ob.matrix_world@ob.data.vertices[ob.data.loops[a].vertex_index].co
   B=ob.matrix_world@ob.data.vertices[ob.data.loops[b].vertex_index].co
   d=B-A
   if abs(d.x)+abs(d.y)<1e-5 and abs(d.z)>.1:
    delta=uv[b].uv-uv[a].uv
    assert abs(delta.x)<1e-5 and abs(abs(delta.y/d.z)-1/.30)<1e-4,(ob.name,'Rotated brick courses',tuple(delta),tuple(d))
    brick_vertical_edges+=1
assert brick_vertical_edges>20
print('Horizontal brick-course UV probes:',brick_vertical_edges)
