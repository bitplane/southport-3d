"""Metric facade and canopy generators for the St George's Place store."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract


def rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def roundtop(width,bottom,top,radius,steps=12):
    """Flat topped opening with quarter-circle upper shoulders, CCW."""
    w=width/2;r=min(radius,w)
    pts=[(-w,bottom),(w,bottom),(w,top-r)]
    for i in range(1,steps+1):
        a=i*math.pi/2/steps;pts.append((w-r+r*math.cos(a),top-r+r*math.sin(a)))
    for i in range(steps+1):
        a=math.pi/2+i*math.pi/2/steps;pts.append((-w+r+r*math.cos(a),top-r+r*math.sin(a)))
    return pts


def wall(name,poly,holes,thickness=.48):
    """Conforming facade shell with reveals only on true boundary edges."""
    from southport3d.conform import conform
    def clean(points):
        out=[]
        for p in points:
            if not out or sum((p[k]-out[-1][k])**2 for k in range(2))>1e-16:out.append(p)
        if len(out)>1 and sum((out[0][k]-out[-1][k])**2 for k in range(2))<1e-16:out.pop()
        return out
    poly=clean(poly);holes=[clean(h) for h in holes]
    shapes=[poly]
    for hole in holes:shapes=[p for q in shapes for p in subtract(q,hole)]
    edges=[(a,b) for ring in [poly]+holes for a,b in zip(ring,ring[1:]+ring[:1])]
    def on_boundary(a,b):
        midpoint=((a[0]+b[0])/2,(a[1]+b[1])/2)
        for c,d in edges:
            v=(d[0]-c[0],d[1]-c[1]);length2=v[0]**2+v[1]**2
            if length2<1e-14:continue
            t=((midpoint[0]-c[0])*v[0]+(midpoint[1]-c[1])*v[1])/length2
            error=sum((midpoint[k]-c[k]-t*v[k])**2 for k in range(2))
            if -.00001<=t<=1.00001 and error<1e-12:return True
        return False
    m=Mesh(name);limits=(min(p[0] for p in poly),max(p[0] for p in poly))
    for shape in shapes:
        shape=clean(shape)
        if len(shape)<3:continue
        n=len(shape);verts=[(x,y,z) for z in (-thickness,0) for x,y in shape]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        for i,(a,b) in enumerate(zip(shape,shape[1:]+shape[:1])):
            shared_corner=any(abs(a[0]-x)<1e-7 and abs(b[0]-x)<1e-7 for x in limits)
            if on_boundary(a,b) and not shared_corner:faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
        m.add(verts,faces)
    return conform({'wall':m})[0]['wall']


def ring(name,width,bottom,top,radius,border=.10,depth=.15,steps=12):
    inner=roundtop(width,bottom,top,radius,steps)
    outer=roundtop(width+2*border,bottom-border,top+border,radius+border,steps)
    m=Mesh(name)
    for i in range(len(inner)):
        j=(i+1)%len(inner);m.outline([inner[i],outer[i],outer[j],inner[j]],-.08,depth)
    return m


def column(name,segments=16):
    m=Mesh(name)
    m.lathe((0,0),[(0,.16),(.12,.17),(.18,.13),(.58,.13),(.68,.18),(.74,.15),(1.00,.10),(1.06,.12)],segments=segments,material=0)
    m.lathe((0,0),[(1.06,.09),(3.5,.067),(3.55,.12),(3.66,.13),(3.72,.20),(3.82,.20),(3.88,.12),(4.25,.095)],segments=segments,material=1)
    m.box((0,0,4.28),(.22,.22,.18),1)
    return m


def column_lod(name,settings,asset_directory):return column(name,settings['segments']).finish([])


def bracket(name,detail=True):
    m=Mesh(name)
    # Plane XY (X span, Y up), outward Z; curved knee sits beneath trellis.
    for sign in (-1,1):
        pts=[]
        for i in range(13 if detail else 6):
            a=(i/(12 if detail else 5))*math.pi/2
            pts.append((sign*(.9-.9*math.cos(a)),3.44+.9*math.sin(a),0))
        m.tube(pts,.035,sides=6 if detail else 4)
        m.tube([(0,3.42,0),(0,4.33,0),(sign*.95,4.33,0)],.04,sides=6 if detail else 4)
        if detail:
            for x,y,r in ((.17,4.14,.10),(.43,4.22,.065)):
                m.tube([(sign*(x+r*math.cos(i*math.tau/24)),y+r*math.sin(i*math.tau/24),0) for i in range(25)],.026,sides=5)
    return m


def bracket_lod(name,settings,asset_directory):return bracket(name,False).finish([])


def ring_lod(name,settings,asset_directory):
    args={k:v for k,v in settings.items() if k!='steps'}
    return ring(name,steps=settings['steps'],**args).finish([])
