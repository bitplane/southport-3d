"""Fixed-budget corner envelope, independent of joinery and ornament topology."""
import json
from blender_envelope import Surfaces
from corner_plan import frame,roof_faces,world,clip

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());p=d['corner_footprint'];s=Surfaces(['architecture','roof','shopfront','rear'],lambda q:world(d,q));e=d['wall_height']
 for i,a in enumerate(p):
  b=p[(i+1)%len(p)];a,u,n,w=frame(p,i)
  # Use the same physical ownership at every LoD. Architecture owns masonry
  # piers and the plain corner, not only the wall above the fascias.
  def Q(t,z,dep=0):return (a[0]+u[0]*t+n[0]*dep,a[1]+u[1]*t+n[1]*dep,z)
  f=next((f for f in d['facades'] if f['edge']==i),None)
  holes=[(a,b,.15,3.2) for a,b,name in f['shops']] if f else [(.2,w-.2,0,3.12)] if i==1 else []
  xs=sorted(set([0,w]+[v for h in holes for v in h[:2]]));zs=sorted(set([0,e]+[v for h in holes for v in h[2:]]))
  s.part='architecture' if i<4 else 'rear'
  for a0,b0 in zip(xs,xs[1:]):
   for lo,hi in zip(zs,zs[1:]):
    if any(a<(a0+b0)/2<b and z<(lo+hi)/2<Z for a,b,z,Z in holes):continue
    s.quad('masonry '+str(i),[Q(b0,lo),Q(a0,lo),Q(a0,hi),Q(b0,hi)])
  # Real opening reveals prevent side views through different-level parts.
  for a0,b0,lo,hi in holes:
   s.quad('left reveal',[Q(a0,lo),Q(a0,lo,-.25),Q(a0,hi,-.25),Q(a0,hi)])
   s.quad('right reveal',[Q(b0,lo,-.25),Q(b0,lo),Q(b0,hi),Q(b0,hi,-.25)])
  s.part='shopfront'
  for a0,b0,lo,hi in holes:s.quad('shop glazing '+str(i),[Q(b0,lo,-.12),Q(a0,lo,-.12),Q(a0,hi,-.12),Q(b0,hi,-.12)])
  for a0,b0,name in (f['shops'] if f else [(.175,w-.175,'57')] if i==1 else []):
   s.quad('fascia '+str(i),[Q(b0,3.22,.10),Q(a0,3.22,.10),Q(a0,3.94,.10),Q(b0,3.94,.10)])
 for f in d['facades']:
  a,u,n,w=frame(p,f['edge']);s.part='architecture'
  for c,r in f['gables']:
   q=lambda v,z:(a[0]+u[0]*v,a[1]+u[1]*v,z)
   s.triangle('gable '+str(c),[q(c+r,e),q(c-r,e),q(c,d['ridge_height'])])
 s.part='roof';x,X,y,Y=d['roof_room']['bounds']
 for name,vs in roof_faces(d):
  # Remove the invisible flat receiver under the raised room.
  pieces=[vs]
  if name.startswith('inner'):
   poly=[q[:2] for q in vs];pieces=[];inside=poly
   for fn in [lambda q:q[0]-x,lambda q:X-q[0],lambda q:q[1]-y,lambda q:Y-q[1]]:
    out=clip(inside,lambda q,fn=fn:-fn(q))
    if out:pieces.append([(a,b,e) for a,b in out])
    inside=clip(inside,fn)
  for poly in pieces:
   if len(poly)==4:s.quad(name,poly)
   else:
    for k in range(1,len(poly)-1):s.triangle(name,[poly[0],poly[k],poly[k+1]])
 s.box('room',(x,y,e),(X,Y,d['roof_room']['height']+.08))
 cx,cy=-15.7,-127.9;z=d['ridge_height']+.45
 s.box('clock skirt',(cx-.55,cy-.55,z-.7),(cx+.55,cy+.55,z))
 s.box('clock case',(cx-.59,cy-.59,z),(cx+.59,cy+.59,z+1.07))
 for a,b in [((-1,-1),(1,-1)),((1,-1),(1,1)),((1,1),(-1,1)),((-1,1),(-1,-1))]:
  s.triangle('clock cap',[(cx+a[0]*.62,cy+a[1]*.62,z+1.07),(cx+b[0]*.62,cy+b[1]*.62,z+1.07),(cx,cy,z+1.65)])
 return s.result
