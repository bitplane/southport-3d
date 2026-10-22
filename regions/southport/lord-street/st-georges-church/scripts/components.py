"""St George's Gothic profiles, in facade XY and outward Z, measured in metres."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract

CURVE_SCALE = 1.0


def rectangle(x0, y0, x1, y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def pointed(radius, bottom, spring, cx=0, steps=18):
    """Two-centred equilateral arch, CCW and convex for planar clipping."""
    steps=max(4,round(steps*CURVE_SCALE))
    right=[(cx-radius+2*radius*math.cos(i*math.pi/3/steps),
            spring+2*radius*math.sin(i*math.pi/3/steps)) for i in range(steps+1)]
    left=[(2*cx-x,y) for x,y in reversed(right[:-1])]
    return [(cx-radius,bottom),(cx+radius,bottom)]+right+left


def regions(poly, holes):
    result=[poly]
    for hole in holes:
        result=[part for p in result for part in subtract(p,hole)]
    return result


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


def arch_ring(mesh, radius, bottom, spring, width=.15, out=.12, depth=.25, cx=0, material=0, steps=18, sill=True):
    inner=pointed(radius,bottom,spring,cx,steps)
    outer=pointed(radius+width,bottom-width if sill else bottom,spring,cx,steps)
    for i in range(len(inner)):
        if i==0 and not sill: continue
        j=(i+1)%len(inner)
        mesh.outline([inner[i],outer[i],outer[j],inner[j]],out-depth,out,material)


def circle_band(mesh, x, y, radius, width=.07, out=.05, depth=.13, steps=32, material=0):
    steps=max(8,round(steps*CURVE_SCALE))
    for i in range(steps):
        a=math.tau*i/steps;b=math.tau*(i+1)/steps
        mesh.outline([(x+radius*math.cos(a),y+radius*math.sin(a)),
                      (x+(radius+width)*math.cos(a),y+(radius+width)*math.sin(a)),
                      (x+(radius+width)*math.cos(b),y+(radius+width)*math.sin(b)),
                      (x+radius*math.cos(b),y+radius*math.sin(b))],out-depth,out,material)


def foil(mesh,x,y,radius,lobes=4,out=.10,width=.045,material=0):
    pts=[]
    steps=max(4,round(16*CURVE_SCALE))
    for i in range(lobes*steps+1):
        a=math.tau*i/(lobes*steps)
        r=radius*(.80+.20*math.cos(lobes*a))
        pts.append((x+r*math.cos(a),y+r*math.sin(a),out))
    mesh.tube(pts,width,sides=max(4,round(6*CURVE_SCALE)),material=material)


def window_surround(name,radius,bottom,spring,lights=3,style=0,louvres=False):
    mesh=Mesh(name)
    arch_ring(mesh,radius,bottom,spring,.16,.18,.32)
    arch_ring(mesh,radius+.19,bottom-.11,spring,.09,.23,.27)
    mesh.box((0,bottom-.17,.15),(radius*2+.58,.22,.64))
    # Main outer hood mould is lifted off the wall and returns into carved stops.
    arch_ring(mesh,radius+.32,bottom+.24,spring,.075,.26,.12,sill=False)
    lightwidth=2*radius/lights
    tracerybase=spring-.45
    for i in range(1,lights):
        x=-radius+i*lightwidth
        mesh.box((x,(bottom+tracerybase)/2,.015),(.11,tracerybase-bottom,.23))
    for i in range(lights):
        x=-radius+(i+.5)*lightwidth
        arch_ring(mesh,lightwidth*.43,bottom,tracerybase,.065,.06,.16,cx=x,steps=12,sill=False)
    cy=spring+radius*.80
    circle_band(mesh,0,cy,radius*.35,.065,.07,.18,24)
    foil(mesh,0,cy,radius*.30,3 if style%2 else 4,out=.09,width=.035)
    if lights==3:
        for sign in (-1,1):
            circle_band(mesh,sign*radius*.53,spring+radius*.32,radius*.18,.045,.065,.14,20)
    return mesh


def diamond_leads(name,width,height):
    mesh=Mesh(name)
    # Full, shallow receiver is isolated from the stone surrounds for baking.
    mesh.box((0,height/2,-.23),(width,height,.035),0)
    spacing=.24
    for sign in (-1,1):
        for i in range(-int(height/spacing)-2,int(width/spacing)+3):
            x0=-width/2+i*spacing
            pts=[]
            for y in (0,height):
                x=x0+sign*y
                if -width/2<=x<=width/2:pts.append((x,y,-.203))
            for x in (-width/2,width/2):
                y=(x-x0)/sign
                if 0<=y<=height:pts.append((x,y,-.203))
            if len(pts)>=2 and sum((pts[0][k]-pts[1][k])**2 for k in range(3))>1e-8:
                mesh.tube(pts[:2],.009,sides=4,material=1)
    return mesh


def pinnacles(name,height=3.0,detail=True):
    mesh=Mesh(name)
    mesh.box((0,0,.20),(.48,.48,.40))
    mesh.rect_profile((0,0),[(.40,.40,.40),(.90,.40,.40),(1.0,.53,.53),(1.10,.42,.42),(height-.25,.02,.02)])
    if detail:
        for z in (1.2,1.55,1.9,2.25):
            if z>height-.3:continue
            spread=.22*(height-z)/(height-1)+.03
            for angle in range(4):
                a=angle*math.pi/2
                mesh.ellipsoid((spread*math.cos(a),spread*math.sin(a),z),(.085,.085,.115),segments=8,rings=5)
    mesh.lathe((0,0),[(height-.3,.06),(height-.20,.12),(height-.08,.06),(height,.015)],segments=8)
    return mesh


def reduced_window(name,settings,asset_directory):
    """Same measured tracery/profile, fewer curve samples for distant LoDs."""
    global CURVE_SCALE
    previous=CURVE_SCALE
    try:
        CURVE_SCALE=settings['curve_scale']
        mesh=window_surround(name,settings['radius'],settings['bottom'],settings['spring'],settings['lights'],settings['style'])
        return mesh.finish([])
    finally:
        CURVE_SCALE=previous


def reduced_pinnacle(name,settings,asset_directory):
    """Keep the complete tapered finial body; omit small foliage at distance."""
    return pinnacles(name,height=3.4,detail=False).finish([])
