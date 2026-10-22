import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/terrace.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.x for v in points)>D['x_far']-.2 and max(v.x for v in points)<D['x_near']+.2
assert 12<max(v.z for v in points)<13
windows=[o for o in meshes if o.name.startswith('Window ')];assert len(windows)==6
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows:
 origin=o.matrix_world@Vector((.2,.2,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and obj==o,(o.name,obj.name if obj else None)
# Door must remain recessed from display panes, at every authored unit.
for shop in D['shops']:
 ob=next(o for o in meshes if o.name.startswith('Shop recessed door '+shop['id']))
 assert max((ob.matrix_world@v.co).y for v in ob.data.vertices)<D['front_y']-.30
report={'objects':len(meshes),'upper_windows':6,'checks':'finite metric meshes, packed maps, bounds, six visible window openings and three recessed door positions'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)

# Fascia lettering must sit in front of its awning, not be hidden by the valance.
for ob in [o for o in meshes if o.name.startswith('Sign ')]:
 origin=ob.matrix_world@Vector((0,0,.8));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
 assert hit and found==ob,(ob.name,'obscured by',found.name if found else None)
print('All sign centres visible from their authored front')

# Actual display panes must be visible, including Mamma Mia's unsplit main pane
# and Bugle's independent right sidelight (generic frontage once obscured these).
for ob in [o for o in meshes if o.name.startswith('Shop display ')]:
 centre=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
 sample_x=centre.x if 'mamma-mia' in ob.name else (centre.x+min(v.co.x for v in ob.data.vertices))/2
 origin=ob.matrix_world@Vector((sample_x,1.75,1))
 direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==ob,(ob.name,'display blocked by',found.name if found else None)
print('All four display panes visible, including the unsplit Mamma pane and Bugle right sidelight')

# No roof skin may share the exposed rear wall plane (Glebe Place view).
slab=bpy.data.objects['Roof slab']
assert min((slab.matrix_world@v.co).y for v in slab.data.vertices)>D['rear_y']+.30
for x in [D['x_far']+1,(D['x_far']+D['x_near'])/2,D['x_near']-1]:
 for z in [D['base_z']+D['roof_level']-.10,D['base_z']+D['roof_level'],D['base_z']+D['roof_level']+.10]:
  hit,point,normal,index,ob,matrix=bpy.context.scene.ray_cast(deps,Vector((x,D['rear_y']-2,z)),Vector((0,1,0)),distance=3)
  assert hit and ob.name=='Envelope rear and party walls',(x,z,ob.name if ob else None)
print('Glebe rear wall owns the full roof-level strip without coplanar slab faces')

# Thin awning/hood surfaces need closed, outward shells rather than opposing
# triangles at identical coordinates; double-sided materials conceal that defect.
for name in ['Awning mamma-mia','Fine ATM controls']:
 ob=bpy.data.objects[name];seen=set();edges={}
 for f in ob.data.polygons:
  key=tuple(sorted(tuple(round(x,7) for x in ob.data.vertices[i].co) for i in f.vertices))
  assert key not in seen,(name,'duplicate surface triangle')
  seen.add(key)
  for a,b in zip(f.vertices,(*f.vertices[1:],f.vertices[0])):
   edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
 assert all(n==2 for n in edges.values()),(name,'open sheet')
 # Each independent primitive is closed; summed signed volume must be positive.
 volume=sum(ob.data.vertices[f.vertices[0]].co.dot(ob.data.vertices[f.vertices[1]].co.cross(ob.data.vertices[f.vertices[2]].co))/6 for f in ob.data.polygons)
 assert volume>0,(name,'inward shell',volume)
print('Awning and ATM hood have closed non-duplicate outward surfaces')
