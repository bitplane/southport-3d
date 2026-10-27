"""Semantic export batching with a reproducible surface identity audit."""
import bpy, hashlib

def digest(objects):
 rows=[]
 for ob in objects:
  ob.data.calc_loop_triangles()
  for tri in ob.data.loop_triangles:
   v=[tuple(round(float(c),5) for c in ob.matrix_world@ob.data.vertices[i].co) for i in tri.vertices]
   v=min(tuple(v[i:]+v[:i]) for i in range(3))
   mat=ob.data.materials[ob.data.polygons[tri.polygon_index].material_index]
   rows.append((mat.name, v))
 rows.sort()
 return hashlib.sha256(repr(rows).encode()).hexdigest(),len(rows)

def batch(collection):
 groups={}
 for ob in list(collection.objects):
  if ob.type!='MESH':continue
  assert len(ob.data.materials)==1,ob.name
  key=(ob.name.split(' ',1)[0],ob.data.materials[0].name)
  groups.setdefault(key,[]).append(ob)
 for (family,material),objects in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0]
  if len(objects)>1:bpy.ops.object.join()
  objects[0].name=family+' batch '+material
