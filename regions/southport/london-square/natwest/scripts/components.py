"""Bank-specific architectural profiles, in local face XY with outward Z."""
import math
from southport3d.geometry import Mesh, smooth_path
from southport3d.planar import subtract


def rectangle(x0,y0,x1,y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def arch_outline(x,bottom,spring,radius,steps=32):
    return [(x-radius,bottom),(x+radius,bottom)]+[
        (x+radius*math.cos(math.pi*i/steps),spring+radius*math.sin(math.pi*i/steps))
        for i in range(steps+1)]


def cut_regions(poly, openings):
    pieces=[poly]
    for hole in openings:
        pieces=[fragment for piece in pieces for fragment in subtract(piece,hole)]
    return pieces


def wall(name,width,height,openings,ashlar=False,start=0):
    m=Mesh(name)
    if not ashlar:
        for poly in cut_regions(rectangle(start,0,width,height),openings):m.outline(poly,-.42,0)
    else:
        for row in range(math.ceil(height/.4)):
            y=row*.4
            for col in range(-1,math.ceil(width/1.2)+1):
                x=col*1.2+(row%2)*.6
                a,b=max(.008,x+.008),min(width-.008,x+1.192)
                if b<=a:continue
                for poly in cut_regions(rectangle(a,y+.008,b,min(height,y+.392)),openings):
                    m.outline(poly,.001,.019,(row+col)%3)
    return m


def arc(m,x,y,inner,outer,start=0,end=math.pi,depth=.2,out=.10,steps=48,material=0):
    for i in range(steps):
        a=start+(end-start)*i/steps;b=start+(end-start)*(i+1)/steps
        m.outline([(x+inner*math.cos(a),y+inner*math.sin(a)),
                   (x+outer*math.cos(a),y+outer*math.sin(a)),
                   (x+outer*math.cos(b),y+outer*math.sin(b)),
                   (x+inner*math.cos(b),y+inner*math.sin(b))],out-depth,out,material)


def upper_window(name,width=2.45,height=3.45,narrow=False,hood_extra=1.02):
    m=Mesh(name);w=width/2;h=height/2
    m.box((0,0,-.22),(width,height,.045),1)
    for side in (-1,1):
        for x,ww,dep in [(side*(w+.10),.20,.18),(side*(w+.24),.09,.26)]:
            m.box((x,0,dep/2),(ww,height+.28,dep),0)
        m.box((side*(w-.035),0,-.10),(.07,height,.10),2)
    for y in (-h,h):
        m.box((0,y+.015,.08),(width+.48,.15,.25),0)
        m.box((0,y,-.09),(width,.065,.12),2)
    transom=h-.88
    m.box((0,transom,-.025),(width,.15,.22),0)
    m.box((0,transom-.09,-.075),(width,.035,.08),2)
    if not narrow:
        m.box((0,0,-.01),(.17,height,.25),0)
        for x in (-.11,.11):m.box((x,0,-.08),(.025,height,.07),2)
    m.box((0,-h-.16,.17),(width+.68,.18,.51),0)
    if narrow:
        arc(m,0,h+.23,width*.50,width*.50+.12,depth=.20,out=.24)
        m.outline([(width*.5,h+.23),(-width*.5,h+.23)]+[(width*.5*math.cos(math.pi-i*math.pi/24),h+.23+width*.5*math.sin(math.pi-i*math.pi/24)) for i in range(25)],.0,.07)
        m.box((0,h+.23,.16),(width+.36,.11,.38))
    else:
        for y,ww,hh,dd in [(h+.21,width+.65*hood_extra/1.02,.16,.28),(h+.37,width+.91*hood_extra/1.02,.13,.39),(h+.48,width+hood_extra,.09,.48)]:
            m.box((0,y,dd/2),(ww,hh,dd))
        for side in (-1,1):
            x=side*(w+.27)
            m.outline([(x-.12,h-.33),(x+.12,h-.33),(x+.15,h+.34),(x-.15,h+.34)],.03,.26)
            for yy in [h-.25,h-.12,h+.02]:m.box((x,yy,.29),(.21,.045,.1))
    return m



def low_side_window(name, width=.96, height=2.15):
    """Single tall light and compact head, observed under the blind London St niche.

    These are not miniature cross-windows. Their centres are only1.66m apart,
    so the wide upper-storey cornice would overlap the neighbouring head.
    """
    m=Mesh(name);w=width/2;h=height/2
    m.box((0,0,-.22),(width,height,.045),1)
    for side in (-1,1):
        m.box((side*(w+.075),0,.065),(.15,height+.22,.20),0)
        m.box((side*(w-.027),0,-.10),(.054,height,.10),2)
    for y in (-h,h):
        m.box((0,y,-.09),(width,.055,.12),2)
    m.box((0,-h-.105,.12),(width+.36,.15,.34),0)
    # Narrow individual lintel and small ends; no central mullion or transom.
    for y,ww,hh,dd in [(h+.07,width+.26,.12,.22),
                        (h+.18,width+.42,.10,.30)]:
        m.box((0,y,dd/2),(ww,hh,dd),0)
    for side in (-1,1):
        x=side*(w+.11)
        m.outline([(x-.075,h-.22),(x+.075,h-.22),
                   (x+.09,h+.10),(x-.09,h+.10)],.02,.22)
    return m


def arched_window(name,radius=1.2,bottom=1.4,spring=3.7,large=False):
    m=Mesh(name);r=radius
    m.outline(arch_outline(0,bottom,spring,r),-.30,-.24,1)
    if radius < 1.4 and bottom > 1:
        m.outline([(r*math.cos(math.pi*i/32),spring+r*math.sin(math.pi*i/32)) for i in range(33)],-.235,-.22,2)
    for side in (-1,1):
        x=side*(r+.12)
        m.box((x,(bottom+spring)/2,.065),(.24,spring-bottom,.23))
        m.box((side*(r-.045),(bottom+spring)/2,-.12),(.07,spring-bottom,.12),2)
        for z in (bottom-.08,spring):m.box((x,z,.15),(.40,.14,.36))
    m.box((0,bottom-.13,.12),(2*r+.6,.17,.40))
    m.box((0,spring,-.10),(2*r,.09,.14),2)
    arc(m,0,spring,r,r+.14,out=.15)
    arc(m,0,spring,r+.18,r+.29,out=.20)
    if large:arc(m,0,spring,r+.34,r+.48,out=.30)
    # Radial joints and alternating recessed voussoirs remain real profiles.
    for i in range(13):
        a=math.pi*i/13+.016;b=math.pi*(i+1)/13-.016
        arc(m,0,spring,r+.15,r+.30,a,b,out=.18,steps=3)
    m.outline([(-.13,spring+r-.14),(.13,spring+r-.14),(.23,spring+r+.47),(-.23,spring+r+.47)],.10,.36)
    return m


def gable(name,spread=1.0):
    m=Mesh(name)
    # Steep curved shoulders lead to a narrow terminal aedicule, not a triangle.
    # Spread narrows only the lower shoulders; the oculus and aedicule keep size.
    side=[(x*spread if y<16 else x,y) for x,y in
          [(2.82,12.55),(2.55,13.35),(2.15,14.10),(1.70,14.85),
           (1.25,15.65),(.92,16.35),(.76,17.05),(.72,18.18)]]
    outline=[(-x,y) for x,y in reversed(side)]+side
    hole=[(.68*math.cos(math.tau*i/48),14.35+.68*math.sin(math.tau*i/48)) for i in range(48)]
    # Triangulate the concave shoulder before convex clipping around the oculus.
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in outline]]):
        for poly in cut_regions([outline[v] if isinstance(v,int) else (v.x,v.y) for v in tri],[hole]):m.outline(poly,-.30,.10)
    for sign in (-1,1):
        m.tube([(sign*x,y,.16) for x,y in side],.115,sides=8)
    for y in (12.65,13.25,15.55,16.45):
        w=5.20*spread if y<13.5 else 2.75*spread if y<16 else 1.65
        m.box((0,y,.17),(w,.10,.20))
    for r,out in [(.71,.22),(.82,.18),(.91,.15)]:arc(m,0,14.35,r,r+.075,0,math.tau,out=out,depth=.15,steps=64)
    m.box((0,17.42,.16),(1.07,1.40,.30))
    m.box((0,17.43,.33),(.64,1.06,.07))
    for x in (-.63,.63):m.box((x,17.43,.25),(.17,1.50,.35))
    for y,w,h in [(16.60,1.38,.18),(16.77,1.56,.12),(18.15,1.55,.15),(18.30,1.65,.12)]:m.box((0,y,.22),(w,h,.48))
    arc(m,0,18.30,.60,.78,out=.27,depth=.30)
    m.outline([(-.6,18.3),(.6,18.3)]+[(.6*math.cos(a),18.3+.6*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]],.01,.10)
    return m


def foliage(name):
    m=Mesh(name)
    # Interpreted leaves follow the observed paired sprays around the oculus.
    for side in (-1,1):
        stem=[(side*x,y,.26) for x,y in [(.12,13.15),(.75,13.25),(1.22,13.75),(1.35,14.40),(1.28,15.0)]]
        m.tube(smooth_path(stem,5),.045,sides=6)
        for i in range(7):
            t=i/6;x=.72+.63*math.sin(t*1.65);y=13.25+t*1.9
            for direction in (-1,1):
                tip=(side*(x+direction*.43),y+.42,.29)
                base=(side*x,y,.25)
                mid=(side*(x+direction*.22),y+.24,.38)
                m.add([base,(mid[0]-.11,mid[1],.27),tip,(mid[0]+.11,mid[1],.27),mid],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
        for cx,cy in [(side*.65,13.2),(side*1.25,13.3)]:
            pts=[]
            for i in range(45):
                t=i/44*math.tau*1.35;r=.29*(1-i/52)
                pts.append((cx+r*math.cos(t),cy+r*math.sin(t),.28))
            m.tube(pts,.045,sides=6)
    # Small projecting pendant below the window and carved console above it.
    m.outline([(-.16,13.25),(.16,13.25),(.10,12.65),(0,12.35),(-.1,12.65)],.20,.34)
    for x in (-.35,-.18,0,.18,.35):
        m.tube([(x,16.70,.34),(x*.8,16.48,.43),(x*.35,16.25,.3)],.055,sides=6)
    return m


def parapet(name,width):
    m=Mesh(name)
    for y in (.05,.58):m.box((0,y,0),(width,.10,.22))
    for i in range(max(1,round(width/.95))):
        count=max(1,round(width/.95));cx=-width/2+(i+.5)*width/count
        for sign in (-1,1):
            pts=[]
            for j in range(33):
                t=j/32*math.tau*1.15;r=.23*(1-j/45)
                pts.append((cx+sign*(.19+r*math.cos(t)),.30+r*math.sin(t),0))
            m.tube(pts,.047,sides=6)
        m.tube([(cx-.36,.12,0),(cx,.52,0),(cx+.36,.12,0)],.045,sides=6)
    return m


def urn(name):
    m=Mesh(name)
    # Lathe along local Y (facade vertical).
    m.lathe((0,0),[(0,.18),(.12,.24),(.20,.12),(.37,.13),(.65,.27),(.88,.30),(1.0,.22),(1.08,.31),(1.18,.12),(1.28,.06)],segments=24)
    m.vertices=[(x,z,-y) for x,y,z in m.vertices]
    return m


def finial(name):
    m=Mesh(name)
    # Heraldic seated-animal silhouette; facial carving remains interpreted.
    m.box((0,.06,0),(.52,.12,.48))
    m.ellipsoid((0,.36,0),(.21,.30,.18),segments=12,rings=8)
    m.ellipsoid((0,.67,-.02),(.15,.19,.15),segments=12,rings=8)
    m.ellipsoid((0,.70,.15),(.12,.08,.12),segments=12,rings=6)
    for x in (-.15,.15):
        m.tube([(x,.50,.10),(x,.21,.17),(x,.12,.24)],.07,sides=8)
        m.ellipsoid((x*.7,.81,0),(.06,.09,.055),segments=8,rings=6)
    m.tube([(.16,.30,-.08),(.29,.16,-.10),(.37,.24,-.07),(.31,.40,-.06)],.045,sides=6)
    return m


def partition_window(mesh):
    """Keep stone profiles in geometry; bake only the shallow glazing assembly."""
    parts=[]
    for stone in (True,False):
        indices=[i for i,mat in enumerate(mesh.indices) if (mat==0)==stone]
        used=sorted({v for i in indices for v in mesh.faces[i]})
        lookup={old:new for new,old in enumerate(used)}
        result=Mesh(('Trim surround '+mesh.name) if stone else mesh.name)
        result.vertices=[mesh.vertices[v] for v in used]
        result.faces=[tuple(lookup[v] for v in mesh.faces[i]) for i in indices]
        result.indices=[mesh.indices[i] for i in indices]
        parts.append(result)
    return parts
