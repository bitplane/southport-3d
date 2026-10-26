"""Partition intersecting coplanar moulding faces, preserving source UVs.

Pier capitals own a common plane before continuous cornices. This removes
buried duplicate backs as well as visible coplanar faces; nothing is displaced.
"""
import numpy as np
from coplanar import overlaps
from southport3d.planar import subtract,area

def partition(objects):
 triangles=[];labels=[];records=[]
 for oi,ob in enumerate(objects):
  ob.data.calc_loop_triangles()
  for t in ob.data.loop_triangles:
   xyz=np.array([tuple(ob.data.vertices[i].co) for i in t.vertices]);uv=np.array([tuple(ob.data.uv_layers.active.data[i].uv) for i in t.loops])
   triangles.append(xyz);labels.append(len(records));records.append((oi,xyz,uv,t.material_index))
 hits=overlaps(triangles,labels);cutters={}
 for a,b,size in hits:
  # Stable construction order owns each shared plane. Later boxes are cut.
  cutters.setdefault(max(a,b),set()).add(min(a,b))
 changed={records[i][0] for i in cutters};new={i:([],[],[],[]) for i in changed}
 for index,(oi,xyz,uv,material) in enumerate(records):
  if oi not in changed:continue
  normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);axis=int(np.argmax(abs(normal)));axes=[k for k in range(3) if k!=axis];poly=xyz[:,axes].tolist();pieces=[poly]
  for winner in sorted(cutters.get(index,())):
   cut=triangles[winner][:,axes].tolist()
   if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(cut,cut[1:]+cut[:1]))<0:cut.reverse()
   pieces=[q for pp in pieces for q in subtract(pp,cut)]
  a=xyz[0,axes];ab=xyz[1,axes]-a;ac=xyz[2,axes]-a;matrix=np.column_stack((ab,ac))
  verts,faces,uvs,mats=new[oi]
  for pp in pieces:
   if area(pp)<1e-9:continue
   # Fan triangles of convex clipping fragments retain original normal.
   for j in range(1,len(pp)-1):
    ps=[pp[0],pp[j],pp[j+1]];vv=[];tt=[]
    for p in ps:
     t=np.linalg.solve(matrix,np.asarray(p)-a);vv.append(xyz[0]+t[0]*(xyz[1]-xyz[0])+t[1]*(xyz[2]-xyz[0]));tt.append(uv[0]+t[0]*(uv[1]-uv[0])+t[1]*(uv[2]-uv[0]))
    if np.dot(np.cross(vv[1]-vv[0],vv[2]-vv[0]),normal)<0:vv.reverse();tt.reverse()
    if np.linalg.norm(np.cross(np.float32(vv[1])-np.float32(vv[0]),np.float32(vv[2])-np.float32(vv[0])))<2e-10:continue
    base=len(verts);verts.extend(vv);uvs.extend(tt);faces.append((base,base+1,base+2));mats.append(material)
 for oi,(verts,faces,uvs,mats) in new.items():
  ob=objects[oi];mesh=ob.data;materials=list(mesh.materials);mesh.clear_geometry();mesh.from_pydata(verts,[],faces);mesh.update()
  while mesh.uv_layers:mesh.uv_layers.remove(mesh.uv_layers[0])
  layer=mesh.uv_layers.new(name='Partitioned authored UV')
  for p,material in zip(mesh.polygons,mats):
   p.material_index=material
   for li in p.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index]
 return {'candidate_pairs':len(hits),'partitioned_triangles':len(cutters),'objects':len(changed)}
