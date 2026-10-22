"""Facade-specific masonry and mouldings, authored from exterior observations."""
import math
from southport3d.geometry import Mesh


def subtract_rect(rect,cut):
    x0,y0,x1,y1=rect;a,b,c,d=cut
    a,b,c,d=max(a,x0),max(b,y0),min(c,x1),min(d,y1)
    if a>=c or b>=d:return [rect]
    return [r for r in [(x0,y0,a,y1),(c,y0,x1,y1),(a,y0,c,b),(a,d,c,y1)] if r[2]-r[0]>.006 and r[3]-r[1]>.006]


def stone(m,rect,out=.018,depth=.025,bevel=.003,material=0):
    """Chamfered slab, with no coplanar surface overlay on the envelope."""
    x0,y0,x1,y1=rect
    if x1-x0<.018 or y1-y0<.018:return
    b=min(bevel,(x1-x0)/5,(y1-y0)/5)
    vs=[(x0,y0,out-depth),(x1,y0,out-depth),(x1,y1,out-depth),(x0,y1,out-depth),
        (x0,y0,out-b),(x1,y0,out-b),(x1,y1,out-b),(x0,y1,out-b),
        (x0+b,y0+b,out),(x1-b,y0+b,out),(x1-b,y1-b,out),(x0+b,y1-b,out)]
    fs=[(3,2,1,0),(8,9,10,11)]
    for i in range(4):j=(i+1)%4;fs.extend([(i,j,j+4,i+4),(i+4,j+4,j+8,i+8)])
    m.add(vs,fs,material)


def coursed_surface(length,openings,name):
    m=Mesh(name);course=.39;block=.92
    for row in range(39):
        y0=.70+row*course;y1=min(15.10,y0+course)
        if y0>=15.10:break
        for col in range(-1,int(length/block)+1):
            x0=max(0,col*block+(row%2)*block/2);x1=min(length,(col+1)*block+(row%2)*block/2)
            if x1<=x0:continue
            rects=[(x0+.002,y0+.002,x1-.002,y1-.002)]
            for cut in openings:rects=[r for rect in rects for r in subtract_rect(rect,cut)]
            for rect in rects:stone(m,rect,material=(row*7+col*3)%4)
    return m


def rusticated_corner(length,openings,spring,radius):
    m=Mesh('Rustication corner')
    for row in range(38):
        y0=.05+row*.40;y1=min(15.10,y0+.375)
        if y0>=15.1:break
        cuts=list(openings)
        if y0<spring+radius:
            half=radius if y0<spring else math.sqrt(max(0,radius*radius-(y0-spring)**2))
            cuts.append((length/2-half-.005,0,length/2+half+.005,spring+radius))
        # Two or three large ashlar blocks per course, restrained joint rhythm.
        breaks=[0,length*.5,length] if row%2 else [0,length*.28,length*.72,length]
        for a,b in zip(breaks,breaks[1:]):
            rects=[(a+.006,y0,b-.006,y1)]
            for cut in cuts:rects=[r for r0 in rects for r in subtract_rect(r0,cut)]
            for rect in rects:stone(m,rect,.085,.10,.012)
    return m


def arch_stones(cx,spring,inner,outer,name='Dressings arch voussoirs'):
    m=Mesh(name);n=13
    for i in range(n):
        a=math.pi*i/n+.008;b=math.pi*(i+1)/n-.008;r=outer+(.10 if i==n//2 else 0)
        vertices=[]
        for depth in [.01,.15]:
            vertices.extend([(cx+rad*math.cos(t),spring+rad*math.sin(t),depth) for rad,t in [(inner,a),(r,a),(r,b),(inner,b)]])
        m.add(vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    for side in [-1,1]:
        for row in range(8):
            a=.10+row*.4;b=min(spring,a+.375)
            stone(m,(cx+side*(inner+outer)/2-(outer-inner)/2,a,cx+side*(inner+outer)/2+(outer-inner)/2,b),.15,.14,.008)
    return m


def architrave(width,height,name,sill=True):
    m=Mesh(name);w=width/2;h=height/2
    for off,thick,out in [(.04,.04,.085),(.10,.045,.12),(.16,.045,.085)]:
        for x in [-w-off,w+off]:m.box((x,0,out),(thick,height+.12,.065))
        m.box((0,h+off,out),(width+2*off+thick,thick,.065))
    if sill:stone(m,(-w-.17,-h-.15,w+.17,-h-.03),.18,.20,.012)
    return m


def cornice_ring(poly,z0,profile,name):
    """A continuous mitred street sweep; no overlapping facade end caps."""
    from mathutils import Vector
    directions=[]
    for i,p in enumerate(poly):
        before=Vector(poly[i-1]);here=Vector(p);after=Vector(poly[(i+1)%len(poly)])
        t0=(here-before).normalized();t1=(after-here).normalized();n0=Vector((t0.y,-t0.x));n1=Vector((t1.y,-t1.x))
        directions.append((n0+n1)/(1+n0.dot(n1)))
    m=Mesh(name)
    for edge in [1,2,3]:
        j=edge+1
        vs=[]
        for idx in [edge,j]:
            for z,out in profile:
                q=Vector(poly[idx])+directions[idx]*out;vs.append((q.x,q.y,z0+z))
        n=len(profile);fs=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        if edge==1:fs.append(tuple(reversed(range(n))))
        if edge==3:fs.append(tuple(range(n,2*n)))
        m.add(vs,fs)
    return m


def london_menu_stonework():
    """Interpreted framed relief and pendant from the small corner photograph.

    Local XY permits a normal-map panel bake. No heraldic identity or lettering
    is asserted: the photograph resolves the masses, not the carved subject.
    """
    from components import rectangle_frame
    m=Mesh('Relief London menu stonework')
    # Continuous shallow backing gives the two reduced-level receivers coverage.
    m.box((0,.0125,.0295),(1.28,1.605,.035))
    # Raised square frame, with an inset field and stepped projecting mouldings.
    for w,h,b,out,d in [(1.16,.91,.075,.095,.075),(1.03,.78,.035,.139,.035),(.94,.69,.024,.115,.025)]:
        rectangle_frame(m,0,.30,w,h,b,out,d,0)
    stone(m,(-.64,.755,.64,.815),.18,.15,.01)
    stone(m,(-.62,-.19,.62,-.12),.18,.15,.01)
    # Central raised cartouche-like mass and shallow branching strokes. Subject
    # is deliberately abstract pending a close photograph, rather than invented arms.
    def relief_polygon(points,out,back=.055):
        n=len(points);v=[(x,y,z) for z in [back,out] for x,y in points]
        m.add(v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    relief_polygon([(-.12,.43),(-.14,.24),(0,.13),(.14,.24),(.12,.43)],.14)
    for sign in [-1,1]:
        m.tube([(sign*(.10+.28*t),.23+.20*t+.045*math.sin(t*math.pi),.12) for t in [i/20 for i in range(21)]],.035,0,8,.6)
        for j in range(3):
            x=sign*(.19+j*.075);y=.29+j*.055
            relief_polygon([(x,y),(x+sign*.035,y+.13),(x+sign*.075,y+.10),(x+sign*.025,y-.025)],.135)
    # Pendant below the square: broad shoulders and a pointed, shield-like bottom.
    relief_polygon([(-.27,-.24),(-.25,-.54),(0,-.68),(.25,-.54),(.27,-.24)],.145)
    m.tube([(-.27,-.24,.16),(-.25,-.54,.16),(0,-.68,.16),(.25,-.54,.16),(.27,-.24,.16)],.024,0,8,.65)
    for sign in [-1,1]:
        m.tube([(sign*(.26+.21*t),-.39-.055*math.sin(t*math.pi),.115) for t in [i/16 for i in range(17)]],.041,0,8,.6)
    return m
