"""Occulo-specific classical profiles; face coordinates are right, up, outward."""
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

def column(u,bottom=8.95,top=15.75,detail=True):
    m=Mesh('Column fluted')
    # Roman Doric base/echinus, slender entasis and 24 concave flutes.
    profile=[(bottom,.59),(bottom+.08,.59),(bottom+.13,.52),(bottom+.20,.55),(bottom+.27,.49),(bottom+.32,.46)]
    m.lathe((u,-.24),profile,64)
    shaft=Mesh('shaft');h=top-bottom
    profile=[(bottom+.32,.455),(bottom+.40,.45),(bottom+h*.3,.448),(bottom+h*.6,.424),(top-.45,.39),(top-.38,.39)]
    shaft.lathe((u,-.24),profile,192 if detail else 48,flutes=24 if detail else 0,flute_depth=.046 if detail else 0)
    m.add(shaft.vertices,shaft.faces)
    m.lathe((u,-.24),[(top-.38,.40),(top-.31,.41),(top-.27,.42),(top-.22,.48),(top-.10,.53),(top-.06,.53)],64)
    # Lathe is Z-up; rotate into face-space without reflecting normals.
    m.vertices=[(x,z,-y) for x,y,z in m.vertices]
    m.box((u,top-.025,.24),(1.15,.11,1.12))
    return m

def balustrade(u,z,width=2.18,detail=True):
    m=Mesh('Balustrade')
    m.box((u,z+.08,.40),(width+.15,.16,.65))
    m.box((u,z+.79,.40),(width+.20,.14,.66))
    for sign in (-1,1):m.box((u+sign*(width/2-.09),z+.45,.40),(.18,.66,.58))
    count=7
    for j in range(count):
        x=u-width/2+.32+j*(width-.64)/(count-1)
        n=Mesh('baluster');n.lathe((x,-.42),[(z+.16,.055),(z+.21,.075),(z+.28,.065),(z+.38,.095),(z+.46,.085),(z+.54,.042),(z+.64,.055),(z+.70,.07)],20 if detail else 10)
        m.add([(x,Z,-y) for x,y,Z in n.vertices],n.faces)
    return m

def ball(m,centre,radii,segments=16,rings=8):
    # Single pole vertices, avoiding the zero-area cap triangles of UV spheres.
    x,y,z=centre;rx,ry,rz=radii;v=[(x,y,z+rz)]
    for i in range(1,rings):
        a=math.pi*i/rings
        for j in range(segments):
            b=math.tau*j/segments;v.append((x+rx*math.sin(a)*math.cos(b),y+ry*math.sin(a)*math.sin(b),z+rz*math.cos(a)))
    v.append((x,y,z-rz));last=len(v)-1
    f=[(0,1+j,1+(j+1)%segments) for j in range(segments)]
    for i in range(rings-2):
        for j in range(segments):a=1+i*segments+j;b=1+i*segments+(j+1)%segments;f.append((a,a+segments,b+segments,b))
    f.extend((last,1+(rings-2)*segments+(j+1)%segments,1+(rings-2)*segments+j) for j in range(segments));m.add(v,f)

def leaf(m,x,y,out,length,angle=0,width=.09):
    # Lanceolate carved leaf with a raised centre vein and curved edges.
    dx,dy=math.sin(angle),math.cos(angle);ox,oy=math.cos(angle),-math.sin(angle)
    n=16;verts=[]
    for i in range(n+1):
        t=i/n;w=width*math.sin(math.pi*t)*(1+.22*math.sin(8*math.pi*t));bend=.04*math.sin(math.pi*t)
        for s in (-1,0,1):verts.append((x+dx*length*t+ox*w*s,y+dy*length*t+oy*w*s,out+bend+(.045*math.sin(math.pi*t) if s==0 else 0)))
    # End rows collapse to a point: use explicit triangles at tips.
    for i in range(n):
        for j in range(2):
            a=i*3+j;b=a+1;c=b+3;d=a+3
            pts=[verts[k] for k in (a,b,c,d)]
            if i==0:m.add([pts[0],pts[2],pts[3]],[(0,1,2)])
            elif i==n-1:m.add([pts[0],pts[1],pts[2]],[(0,1,2)])
            else:m.add(pts,[(0,1,2,3)])

def scroll(m,x,y,out,rx=.25,ry=.25,sign=1):
    pts=[]
    for i in range(45):
        a=math.tau*1.35*i/44;r=1-.88*i/44
        pts.append((x+sign*rx*r*math.cos(a),y+ry*r*math.sin(a),out+.035*math.sin(a)))
    m.tube(pts,.035,sides=8)

def mask(u,z,scale=1):
    m=Mesh('Relief lion mask')
    # Mane clusters, brow, muzzle and recessed dark mouth are separately modelled.
    for i in range(14):
        a=math.tau*i/14
        ball(m,(u+math.cos(a)*.19*scale,z+math.sin(a)*.23*scale,.22),(.075*scale,.11*scale,.075),12,6)
    ball(m,(u,z,.25),(.17*scale,.21*scale,.13),20,10)
    for sign in (-1,1):
        ball(m,(u+sign*.09*scale,z+.07*scale,.35),(.07*scale,.045*scale,.05),12,6)
        ball(m,(u+sign*.065*scale,z-.09*scale,.37),(.075*scale,.07*scale,.06),12,6)
    ball(m,(u,z-.015*scale,.40),(.045*scale,.07*scale,.05),12,6)
    m.tube([(u-.08*scale,z-.15*scale,.36),(u,z-.19*scale,.38),(u+.08*scale,z-.15*scale,.36)],.025,sides=8)
    return m

def tympanum(u,z,variant=0):
    m=Mesh('Relief tympanum')
    # Three distinguishable observed families: central shield, vase/garlands,
    # and intertwined vertical scrollwork. Fine carving is an interpretation.
    if variant%2==0:
        shield=[(u-.19,z+.12),(u+.19,z+.12),(u+.16,z-.19),(u,z-.32),(u-.16,z-.19)]
        m.outline(shield,-.15,.12)
        m.tube([(x,y,.16) for x,y in shield+[shield[0]]],.025,sides=8)
        for sign in (-1,1):
            scroll(m,u+sign*.31,z+.02,.10,.25,.18,sign)
            m.tube(smooth_path([(u+sign*.28,z+.25,.08),(u+sign*.60,z+.18,.12),(u+sign*.77,z-.22,.08),(u+sign*1.05,z-.25,.02)],7),.045,sides=8)
        m.box((u,z+.29,.07),(.32,.10,.17))
    else:
        for sign in (-1,1):scroll(m,u+sign*.24,z+.05,.13,.28,.25,sign)
        m.tube(smooth_path([(u-.12,z-.31,.16),(u+.15,z-.12,.18),(u-.13,z+.11,.18),(u+.13,z+.31,.12)],10),.045,sides=8)
    for sign in (-1,1):
        for j in range(8):
            a=.3+j*.14;x=u+sign*(.35+j*.07);y=z-.20+j*.038
            leaf(m,x,y,.06,.24+.05*math.sin(j),sign*(.7+j*.16),.065)
    return m

def cartouche(u,z):
    m=Mesh('Relief entrance cartouche')
    # Oval escutcheon and layered rolled surround seen above the entrance hood.
    outline=[(u+.28*math.cos(math.tau*i/40),z+.47*math.sin(math.tau*i/40)) for i in range(40)]
    m.outline(outline,.18,.41)
    for rx,ry,out,r in [(.28,.47,.44,.035),(.32,.52,.37,.045),(.35,.55,.31,.025)]:
        m.tube([(u+rx*math.cos(math.tau*i/64),z+ry*math.sin(math.tau*i/64),out) for i in range(65)],r,sides=10)
    # Small tower-like crest at the top; the worn monogram is deliberately not guessed.
    m.box((u,z+1.01,.30),(.28,.25,.16))
    for x in (-.105,0,.105):m.box((u+x,z+1.17,.31),(.065,.10,.18))
    for x in (-.065,.065):
        m.box((u+x,z+1.01,.40),(.025,.08,.025))
    for sign in (-1,1):
        scroll(m,u+sign*.37,z+.53,.36,.23,.26,sign)
        scroll(m,u+sign*.29,z-.40,.34,.19,.26,-sign)
        pts=smooth_path([(u+sign*.40,z+.25,.30),(u+sign*.48,z-.35,.24),(u+sign*.85,z-.80,.20),(u+sign*.95,z-1.02,.08)],10)
        m.tube(pts,.07,sides=10)
        for j,p in enumerate(pts[::3]):
            leaf(m,p[0],p[1],p[2]+.03,.22,sign*(.6+j*.09),.075)
            leaf(m,p[0],p[1],p[2]+.02,.18,-sign*(.5+j*.08),.065)
    for j in range(5):leaf(m,u+(j-2)*.10,z+.65,.27,.48,(j-2)*.34,.10)
    return m
