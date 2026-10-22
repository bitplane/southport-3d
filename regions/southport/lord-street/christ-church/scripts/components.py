"""Christ Church's pointed openings and relief, in face XY with outward Z."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract


def rect(x0, y0, x1, y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def pointed(x, bottom, spring, radius, steps=16):
    # Two circular arcs of radius 2r centred on opposite jambs.
    right=[(x-radius+2*radius*math.cos(i*math.pi/3/steps),spring+2*radius*math.sin(i*math.pi/3/steps)) for i in range(steps+1)]
    left=[(2*x-p[0],p[1]) for p in right[::-1]]
    return [(x-radius,bottom),(x+radius,bottom)]+right+left[1:]


def clipped(poly, holes):
    regions=[poly]
    for hole in holes:
        regions=[p for region in regions for p in subtract(region,hole)]
    return regions


def wall(name, polygon, holes, thickness=.42):
    mesh=Mesh(name)
    for p in clipped(polygon,holes):mesh.outline(p,-thickness,0)
    return mesh


def arch_ring(mesh, x, bottom, spring, radius, width=.12, depth=.12, forward=.12, steps=16, material=0):
    inner=pointed(x,bottom,spring,radius,steps)
    # Offset the jamb and follow the same two-centre shape for the hood mould.
    outer=pointed(x,bottom,spring,radius+width,steps)
    for i in range(2,len(inner)-1):
        mesh.outline([inner[i],outer[i],outer[i+1],inner[i+1]],forward-depth,forward,material)
    for side in [-1,1]:
        mesh.box((x+side*(radius+width/2),(bottom+spring)/2,forward-depth/2),(width,spring-bottom,depth),material)


def ring(mesh,x,y,r,t,forward=.1,steps=32,material=0):
    for i in range(steps):
        a=2*math.pi*i/steps;b=2*math.pi*(i+1)/steps
        mesh.outline([(x+r*math.cos(a),y+r*math.sin(a)),(x+(r+t)*math.cos(a),y+(r+t)*math.sin(a)),(x+(r+t)*math.cos(b),y+(r+t)*math.sin(b)),(x+r*math.cos(b),y+r*math.sin(b))],forward-.10,forward,material)


def gothic_window(name,width=1.8,bottom=0,spring=2.5,kind='glass',steps=16):
    """Opaque glazing is deliberately recessed; keep stone frame independent."""
    m=Mesh(name);r=width/2
    m.outline(pointed(0,bottom,spring,r,steps),-.28,-.24,1 if kind!='blocked' else 0)
    for w,dep,out in [(.12,.22,.12),(.08,.12,.21)]:
        arch_ring(m,0,bottom,spring,r,w,dep,out,steps)
        r+=w+.035
    m.box((0,bottom-.09,.06),(width+.5,.18,.32),0)
    r=width/2
    # Central mullion and two subsidiary lancets lead into a geometric roundel.
    m.box((0,(bottom+spring+.12)/2,-.02),(.10,spring+.12-bottom,.24),0)
    sub=r*.47
    for side in [-1,1]:
        arch_ring(m,side*r*.5,bottom,spring-.18,sub,.055,.14,.02,max(8,steps//2))
    circle_r=r*.34;cy=spring+r*.84
    ring(m,0,cy,circle_r,.055,.025,steps*2)
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        ring(m,math.cos(angle)*circle_r*.47,cy+math.sin(angle)*circle_r*.47,circle_r*.44,.026,.03,steps)
    if kind=='louvre':
        for y in [bottom+.18+i*.35 for i in range(int((spring-bottom)/.35)+1)]:
            # Sloping blades sit behind the mullion; actual gaps read at close range.
            for side in [-1,1]:
                x=side*r*.5;w=r-.14
                m.add([(x-w/2,y-.08,-.19),(x+w/2,y-.08,-.19),(x+w/2,y+.07,-.05),(x-w/2,y+.07,-.05)],[(0,1,2,3)],2)
    return m


def leadwork(name,width,bottom,spring,steps=16):
    """Fine diamond leading; separate detail-only mesh over recessed glazing."""
    m=Mesh(name);outline=pointed(0,bottom,spring,width/2,steps)
    # The lead lattice stops below tracery, with deterministic small glass hues.
    r=width/2
    for side in [-1,1]:
        for y in [bottom+.15+i*.32 for i in range(int((spring-bottom)/.32))]:
            for x in [-r+.10+i*.28 for i in range(int((width-.12)/.28))]:
                end=(x+.20,y+.26,-.215)
                if end[0]<r-.06 and end[1]<spring-.2:
                    m.tube([(x,y,-.215),end],.009,sides=4)
                    m.tube([(x+.20,y,-.215),(x,y+.26,-.215)],.009,sides=4)
        break
    return m


def clock(name,radius=.69,segments=48):
    m=Mesh(name)
    m.outline([(-radius*1.43,0),(0,-radius*1.43),(radius*1.43,0),(0,radius*1.43)],-.05,.045,0)
    m.outline([(radius*math.cos(i*2*math.pi/segments),radius*math.sin(i*2*math.pi/segments)) for i in range(segments)],.05,.075,1)
    ring(m,0,0,radius,.055,.12,segments,2)
    for i in range(12):
        a=i*math.pi/6
        m.tube([(radius*.80*math.sin(a),radius*.80*math.cos(a),.13),(radius*.91*math.sin(a),radius*.91*math.cos(a),.13)],.014,sides=4,material=2)
    m.tube([(0,0,.15),(-radius*.45,radius*.38,.15)],.025,sides=6,material=2)
    m.tube([(0,0,.16),(radius*.70,radius*.16,.16)],.018,sides=6,material=2)
    ring(m,0,0,.08,.025,.17,20,2)
    return m


def roof(name,x0,x1,y0,y1,eaves,ridge,hip=0):
    """Closed planar hipped roof, y-axis ridge, with a real underside."""
    mesh=Mesh(name);xm=(x0+x1)/2
    mesh.add([(x0,y0,eaves),(x1,y0,eaves),(x1,y1,eaves),(x0,y1,eaves),(xm,y0+hip,ridge),(xm,y1-hip,ridge)],[(3,2,1,0),(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)])
    return mesh


def build_lod(name,settings,asset_directory):
    """Regenerate known Gothic curves; preserve jambs, depth and pierced tracery."""
    if settings['kind']=='clock':
        mesh=clock(name,segments=24 if settings['level']=='walk' else 12)
    else:
        mesh=gothic_window(name,settings['width'],settings['bottom'],settings['spring'],settings.get('window_kind','glass'),steps=8 if settings['level']=='walk' else 4)
    return mesh.finish([])
