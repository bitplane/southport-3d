"""Anchor Street face-space construction helpers; face coordinates are right, up, outward."""
import math
from southport3d.geometry import Mesh, smooth_path
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(poly,holes):
    result=[poly]
    for hole in holes:result=[q for p in result for q in subtract(p,hole)]
    return result

def ellipse_arch(u,bottom,spring,radius,rise,steps=32):
    return [(u-radius,bottom),(u+radius,bottom)]+[(u+radius*math.cos(math.pi*i/steps),spring+rise*math.sin(math.pi*i/steps)) for i in range(steps+1)]

def arc(m,u,z,rx,ry,thickness,out=.15,depth=.18,steps=40,start=0,end=math.pi):
    # Continuous ring skin, without radial internal caps that shimmer in WebGL.
    v=[]
    for i in range(steps+1):
        a=start+(end-start)*i/steps
        for d in (out-depth,out):
            for x,y in ((rx,ry),(rx+thickness,ry+thickness)):
                v.append((u+x*math.cos(a),z+y*math.sin(a),d))
    f=[]
    for i in range(steps):
        a=4*i;b=a+4
        f.extend([(a+2,a+3,b+3,b+2),(a,b,b+1,a+1),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    if abs(end-start-math.tau)>1e-6:f.extend([(0,1,3,2),(4*steps+2,4*steps+3,4*steps+1,4*steps)])
    m.add(v,f)

def moulding(m,left,right,z,profile):
    """Continuous extruded stepped profile; profile points are elevation/outset."""
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(profile,profile[1:]+profile[:1]))<0:profile=list(reversed(profile))
    n=len(profile);v=[(u,z+y,depth) for u in (left,right) for y,depth in profile]
    m.add(v,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])

def beam(m,a,b,width,depth):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);ox=-dy/length*width/2;oy=dx/length*width/2
    m.outline([(a[0]-ox,a[1]-oy),(b[0]-ox,b[1]-oy),(b[0]+ox,b[1]+oy),(a[0]+ox,a[1]+oy)],a[2]-depth/2,a[2]+depth/2)
