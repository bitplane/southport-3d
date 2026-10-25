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


def tracery_solid(mesh,polygons,back=-.15,front=.025,material=0,disjoint=False):
    """Union planar moulding strokes before extruding their exposed boundary.

    No internal fragment caps or coincident stroke faces at branching points.
    """
    from collections import Counter
    from southport3d.planar import area
    import southport3d.conform as conform_module
    def clean(poly):
        result=[]
        for p in poly:
            if not result or math.dist(p,result[-1])>1e-9:result.append(p)
        if len(result)>1 and math.dist(result[0],result[-1])<1e-9:result.pop()
        return result
    pieces=[]
    for polygon in polygons:
        pending=[polygon]
        for existing in ([] if disjoint else pieces):
            pending=[clean(p) for candidate in pending for p in subtract(candidate,existing) if area(p)>1e-8]
            if not pending:break
        pieces.extend(pending)
    skin=Mesh('tracery skin')
    for p in pieces:skin.add([(*v,0) for v in p],[tuple(range(len(p)))])
    old_grid,old_tol=conform_module.GRID,conform_module.TOLERANCE
    try:
        conform_module.GRID=1e-6;conform_module.TOLERANCE=2e-6
        skin=conform_module.conform({'skin':skin})[0]['skin']
    finally:
        conform_module.GRID=old_grid;conform_module.TOLERANCE=old_tol
    counts=Counter();directed={}
    for face in skin.faces:
        points=[skin.vertices[i] for i in face]
        for a,b in zip(points,points[1:]+points[:1]):
            key=tuple(sorted((a,b)));counts[key]+=1;directed[key]=(a,b)
        mesh.add([(x,y,front) for x,y,z in points],[tuple(range(len(points)))],material)
        mesh.add([(x,y,back) for x,y,z in points],[tuple(reversed(range(len(points))))],material)
    for edge,count in counts.items():
        if count!=1:continue
        a,b=directed[edge]
        mesh.add([(a[0],a[1],back),(b[0],b[1],back),(b[0],b[1],front),(a[0],a[1],front)],[(0,1,2,3)],material)


def wing_wall(name,polygon,holes):
    """Continuous wall skins and true reveal boundaries, without fragment caps."""
    m=Mesh(name)
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    triangles=tessellate_polygon([[Vector((x,y,0)) for x,y in polygon]])
    pieces=[p for triangle in triangles for p in clipped([polygon[v] if isinstance(v,int) else (v.x,v.y) for v in triangle],holes)]
    tracery_solid(m,pieces,back=-.42,front=0,disjoint=True)
    return m


def wing_door(name,x):
    m=Mesh(name)
    m.outline(pointed(x,0,1.85,.68),-.34,-.30,2)
    arch_ring(m,x,0,1.85,.68,.13,.40,.10)
    inner=pointed(x,0,1.85,.60,24);outer=pointed(x,0,1.85,.675,24)
    timber=[rect(x-.675,0,x-.60,1.85),rect(x+.60,0,x+.675,1.85)]
    timber += [[inner[i],outer[i],outer[i+1],inner[i+1]] for i in range(2,len(inner)-1)]
    timber += [rect(x-.0525,0,x+.0525,1.85+math.sqrt(3)*.60)]
    for side in [-1,1]:
        c=x+side*.326
        # Lower panels terminate at 1 m rail (~33% of doorway height).
        m.box((c,.50,-.2825),(.547,.87,.025),1)
        for h in [.065,.97]:timber.append(rect(c-.2735,h-.065,c+.2735,h+.065))
        for dx in [-.235,.235]:timber.append(rect(c+dx-.03,.13,c+dx+.03,.905))
    # All timber faces are a single union; curved head and centre stile join.
    tracery_solid(m,timber,back=-.27,front=-.16,material=1)
    for side in [-1,1]:m.box((x+side*.96,1.535,.085),(.12,3.07,.17))
    m.box((x,3.15,.085),(2.04,.16,.17))
    return m


def wing_window(name,width=2,bottom=0,spring=2.5,steps=16):
    """Paired elongated upper lights, traced from supplied close front photos.

    Unlike the tower, these wings have no circular roundel. The two long
    upper lights branch from the cusped heads of the lower pair.
    """
    m=Mesh(name);r=width/2
    m.outline(pointed(0,bottom,spring,r,steps),-.28,-.24,1)
    for radius,w,depth,out in [(r,.10,.38,.10),(r+.135,.075,.12,.17)]:
        arch_ring(m,0,bottom,spring,radius,w,depth,out,steps)
    m.box((0,bottom-.09,.03),(width+.42,.18,.30))
    # Mullion joins the central branching point, with no floating end.
    branch=spring+.12
    strokes=[rect(-.0525,bottom,.0525,branch)]
    # Cubic segments give the characteristic trefoil shoulders of each light.
    def curve(points,radius=.044):
        out=[]
        for a,b,c,d in zip(points[0::3],points[1::3],points[2::3],points[3::3]):
            for j in range(steps):
                t=j/steps;u=1-t
                out.append((r*(u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0]),
                            spring+r*(u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]),-.055))
        out.append((r*points[-1][0],spring+r*points[-1][1],-.055))
        for a,b in zip(out,out[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
            nx,ny=-dy/length*radius,dx/length*radius
            strokes.append([(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)])
        # Rounded joints are part of the union, not overlaid disks.
        for x,y,z in out:
            strokes.append([(x+radius*math.cos(j*math.tau/8),y+radius*math.sin(j*math.tau/8)) for j in range(8)])
    for sign in [-1,1]:
        def trace(points,rad=.044):curve([(sign*x,y) for x,y in points],rad)
        trace([(0,.12),(.04,.39),(.19,.49),(.29,.48),(.18,.61),(.30,.79),(.46,.67),(.56,.82),(.76,.59),(.64,.48),(.81,.49),(.93,.31),(.94,.02)])
        # Elongated top lights share the narrow centre stem at the apex.
        trace([(.13,.79),(.05,1.00),(.12,1.36),(.17,1.52),(.28,1.45),(.46,1.25),(.48,1.10),(.52,.92),(.40,.79),(.29,.82),(.22,.75),(.17,.75),(.13,.79)],.038)
        # Upper cusp and short central stem connect to the main head.
    curve([(0,.12),(0,.52),(0,1.12),(0,1.66)],.043)
    tracery_solid(m,strokes)
    return m


def wing_leadwork(name,width,bottom,spring):
    """Continuous diagonal strips clipped inside each lower glazed light."""
    m=Mesh(name);r=width/2
    # Glazing owns the back; 8 mm lead sits on its front. Crossing strips have
    # distinct back/front depths, reflecting lapped lead without coplanar faces.
    for sign in [-1,1]:
        x0,x1=sorted((sign*.065,sign*(r-.055)))
        y0,y1=bottom+.035,spring+.06
        for slope in [-1.45,1.45]:
            for k in range(-35,36):
                intercept=bottom+k*.33
                candidates=[]
                for x in [x0,x1]:
                    y=slope*x+intercept
                    if y0<=y<=y1:candidates.append((x,y))
                for y in [y0,y1]:
                    x=(y-intercept)/slope
                    if x0<x<x1:candidates.append((x,y))
                if len(candidates)==2:
                    z=-.224 if slope<0 else -.215
                    m.tube([(*p,z) for p in candidates],.006,sides=4)
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


def roundel(name,radius=.69,segments=48):
    """Recessed four-spoke glazing in an open diamond surround, not a clock."""
    m=Mesh(name)
    diamond=[(-radius*1.43,0),(0,-radius*1.43),(radius*1.43,0),(0,radius*1.43)]
    circle=[(radius*math.cos(i*2*math.pi/segments),radius*math.sin(i*2*math.pi/segments)) for i in range(segments)]
    for polygon in clipped(diamond,[circle]):m.outline(polygon,-.08,.08,0)
    m.outline(circle,-.23,-.20,1)
    ring(m,0,0,radius,.065,.10,segments,0)
    for a in range(4):
        angle=a*math.pi/2
        m.tube([(.25*math.cos(angle),.25*math.sin(angle),-.045),(radius*math.cos(angle),radius*math.sin(angle),-.045)],.035,sides=6,material=0)
    ring(m,0,0,.22,.055,-.015,segments//2,0)
    for i,p in enumerate(diamond):m.tube([(*p,.11),(*diamond[(i+1)%4],.11)],.045,sides=6)
    return m


def roof(name,x0,x1,y0,y1,eaves,ridge,hip=0):
    """Closed planar hipped roof, y-axis ridge, with a real underside."""
    mesh=Mesh(name);xm=(x0+x1)/2
    mesh.add([(x0,y0,eaves),(x1,y0,eaves),(x1,y1,eaves),(x0,y1,eaves),(xm,y0+hip,ridge),(xm,y1-hip,ridge)],[(3,2,1,0),(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)])
    return mesh


def build_lod(name,settings,asset_directory):
    """Regenerate known Gothic curves; preserve jambs, depth and pierced tracery."""
    if settings['kind']=='roundel':
        mesh=roundel(name,segments=24 if settings['level']=='walk' else 12)
    elif settings.get('window_kind')=='wing':
        mesh=wing_window(name,settings['width'],settings['bottom'],settings['spring'],steps=8)
    else:
        mesh=gothic_window(name,settings['width'],settings['bottom'],settings['spring'],settings.get('window_kind','glass'),steps=8 if settings['level']=='walk' else 4)
    return mesh.finish([])
