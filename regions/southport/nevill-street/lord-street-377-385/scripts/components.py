"""Local classical facade and curved frontage construction, in metres."""
import math
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(poly,holes):
    out=[poly]
    for hole in holes:out=[q for p in out for q in subtract(p,hole)]
    return out

def arch(u,lo,spring,rx,ry,n=32):
    return [(u-rx,lo),(u+rx,lo)]+[(u+rx*math.cos(math.pi*i/n),spring+ry*math.sin(math.pi*i/n)) for i in range(n+1)]

def ring(m,u,z,rx,ry,t,back,front,start=0,end=math.pi,n=40):
    vertices=[]
    for i in range(n+1):
        a=start+(end-start)*i/n
        for out in (back,front):
            for r,R in ((rx,ry),(rx+t,ry+t)):vertices.append((u+r*math.cos(a),z+R*math.sin(a),out))
    faces=[]
    for i in range(n):
        a=4*i;b=a+4
        faces.extend([(a+2,a+3,b+3,b+2),(a,b,b+1,a+1),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    faces.extend([(0,1,3,2),(4*n+2,4*n+3,4*n+1,4*n)])
    m.add(vertices,faces)

def path_profile(m,path,profile):
    """Sweep height/outset profile along (x,y,outward-x,outward-y) samples."""
    n=len(profile);verts=[(x+nx*out,y+ny*out,z) for x,y,nx,ny in path for z,out in profile]
    faces=[]
    for i in range(len(path)-1):
        for j in range(n-1):faces.append((i*n+j,(i+1)*n+j,(i+1)*n+j+1,i*n+j+1))
    m.add(verts,faces)

def outline(W,D,R,n=24,well=None):
    p=[(R,0),(W,0),(W,D)]
    if well:
        a,b=well['x'];lo,hi=well['y'];p.extend([(b,D),(b,lo),(a,lo),(a,D)])
    p.extend([(0,D),(0,R)])
    p.extend([(R+R*math.cos(math.pi+math.pi*.5*i/n),R+R*math.sin(math.pi+math.pi*.5*i/n)) for i in range(1,n)])
    return p
