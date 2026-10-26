"""Pier-local metric surfaces; shared by independently streamed pier sections."""
import math
import numpy as np

class Faces:
    def __init__(self): self.items=[]
    def face(self,name,p,mat='blue',part='structure',cage=.1,weight=1):
        self.items.append(dict(name=name,vertices=[tuple(v) for v in p],material=mat,part=part,cage_m=cage,weight=weight))
    def box(self,name,a,b,mat='blue',part='structure',omit=(),**kw):
        x,y,z=a;X,Y,Z=b
        v=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
        for side,ix in [('bottom',(0,3,2,1)),('south',(0,1,5,4)),('end',(1,2,6,5)),('north',(2,3,7,6)),('start',(3,0,4,7)),('top',(4,5,6,7))]:
            if side not in omit:self.face(name+' '+side,[v[i] for i in ix],mat,part,**kw)
    def tube(self,name,a,b,r,mat='blue',part='fittings',segments=8,cap=True,cage=.1,weight=.3,r2=None):
        a,b=np.array(a,float),np.array(b,float);u=b-a;u/=np.linalg.norm(u)
        n=np.cross(u,[0,0,1] if abs(u[2])<.9 else [0,1,0]);n/=np.linalg.norm(n);v=np.cross(u,n);rr=r if r2 is None else r2
        A=[a+r*(math.cos(i*math.tau/segments)*n+math.sin(i*math.tau/segments)*v) for i in range(segments)]
        B=[b+rr*(math.cos(i*math.tau/segments)*n+math.sin(i*math.tau/segments)*v) for i in range(segments)]
        for i in range(segments):
            j=(i+1)%segments;self.face(name+' side '+str(i),[A[i],A[j],B[j],B[i]],mat,part,cage,weight)
        if cap:self.face(name+' start',list(reversed(A)),mat,part,cage,weight);self.face(name+' end',B,mat,part,cage,weight)
    def beam(self,name,a,b,width,depth,mat='blue',part='structure',cap=True,**kw):
        a,b=np.array(a,float),np.array(b,float);u=b-a;u/=np.linalg.norm(u)
        n=np.cross(u,[0,0,1] if abs(u[2])<.9 else [0,1,0]);n/=np.linalg.norm(n);v=np.cross(u,n)
        rings=[[p+n*i*width/2+v*j*depth/2 for i,j in [(1,1),(-1,1),(-1,-1),(1,-1)]]for p in [a,b]]
        A,B=rings
        for i in range(4):j=(i+1)%4;self.face(name+' side '+str(i),[A[i],A[j],B[j],B[i]],mat,part,**kw)
        if cap:self.face(name+' start',list(reversed(A)),mat,part,**kw);self.face(name+' end',B,mat,part,**kw)
    def path_tube(self,name,points,r,mat='ivory',part='fittings',segments=6,**kw):
        """Continuous swept rings avoid coplanar overlaps at curved rod joints."""
        pts=[np.array(p,float) for p in points];normal=np.cross(pts[1]-pts[0],pts[-1]-pts[0])
        if np.linalg.norm(normal)<1e-8:normal=np.array([1.,0,0])
        normal/=np.linalg.norm(normal);rings=[]
        for i,p in enumerate(pts):
            tangent=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];tangent/=np.linalg.norm(tangent);v=np.cross(tangent,normal);v/=np.linalg.norm(v)
            rings.append([p+r*(math.cos(j*math.tau/segments)*normal+math.sin(j*math.tau/segments)*v)for j in range(segments)])
        for i,(a,b) in enumerate(zip(rings,rings[1:])):
            for j in range(segments):k=(j+1)%segments;self.face(f'{name} {i} {j}',[a[j],a[k],b[k],b[j]],mat,part,**kw)
