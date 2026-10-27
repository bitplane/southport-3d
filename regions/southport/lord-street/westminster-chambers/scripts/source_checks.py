import bpy,math,os,sys
from pathlib import Path

def validate():
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   assert o.data.polygons and o.data.uv_layers
   assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 import os,sys
 sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
 from coplanar import check_blender,overlaps
 check_blender([bpy.data.objects['Envelope front wing']])
 prototype=[]
 for prefix,n in [('Window polygonal bay glazing',10),('Trim bay base panel',5),('Trim bay horizontal',20),('Trim bay upper mullion',5),('Trim bay stile',6),('Trim bay cap',2)]:
  items=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefix)]
  assert len(items)>=n,(prefix,len(items))
  prototype+=items[:n]
 check_blender(prototype+[bpy.data.objects['Envelope front wing']])
 all_bays=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Window polygonal bay glazing','Trim bay horizontal','Trim bay upper mullion','Trim bay upper light rail','Trim bay crown moulding','Trim bay base panel','Trim bay stile','Trim bay cap'))]
 check_blender(all_bays+[bpy.data.objects['Envelope front wing']])
 check_blender([bpy.data.objects['Roof front wing']])
 turret=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Envelope turret facet','Window turret glazing','Trim turret band'))]
 check_blender(turret)
 crown=bpy.data.objects['Roof turret crown']
 check_blender([crown])
 # Every cap facet must face up and outward, otherwise the District bake
 # encodes inverted tangent normals even when coverage is complete.
 from mathutils import Vector
 centre=Vector((-266.24-1.2-.0367*1.2,-25.45-1.2,0))
 for face in crown.data.polygons:
  radial=face.center-centre;radial.z=0
  assert face.normal.z>0 and face.normal.dot(radial)>0, ('Inward turret crown face',face.index)
 check_blender([bpy.data.objects['Veranda openwork brackets']])
 veranda=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Veranda ')]
 check_blender(veranda)
 balconies=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Balcony ')]
 check_blender(balconies)
 shop=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Shop ')]
 check_blender(shop+[bpy.data.objects['Envelope front wing']])
 sashes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Window front','Window side','Trim front','Trim side','Trim segmental sash head'))]
 # Sill-top and wall-reveal share only their designed boundary. Float32 after
 # the site shear creates sub-1e-5 m² contact residue at that boundary; allow
 # only that named pair and inspect all other positive-area overlaps strictly.
 triangles=[];labels=[]
 for ob in sashes+[bpy.data.objects['Envelope front wing']]:
  ob.data.calc_loop_triangles()
  for tri in ob.data.loop_triangles:
   triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in tri.vertices]);labels.append(ob.name)
 findings=overlaps(triangles,labels)
 errors=[e for e in findings if not (e[2]<1e-5 and 'Envelope front wing' in e[:2] and any(n.startswith('Trim side sash sill') for n in e[:2]))]
 assert not errors,errors[:12]
 print('Sash/reveal ownership: %d named numerical contacts under 1e-5 m²'% (len(findings)-len(errors)))
 check_blender(all_bays+[bpy.data.objects['Roof front wing']])
 gables=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Roof Dutch gable','Trim Dutch gable coping','Trim gable curved band'))]
 check_blender(gables+[bpy.data.objects['Roof front wing']])

 dormers=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Roof front dormer casing','Roof side dormer casing'))]
 check_blender(dormers+[bpy.data.objects['Roof front wing']])

 # Diagnostic full trim and balcony interface ownership before batching.
 trim=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Trim ','Balcony '))]
 tris=[];owners=[]
 for ob in trim:
  ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   tris.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices]);owners.append(ob.name)
 findings=overlaps(tris,owners)
 
 assert not findings, ('Trim/balcony coplanar overlaps',findings[:12])
 print('All trim and balcony surfaces have single ownership')
