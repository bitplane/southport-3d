"""Curved memorial-garden return opposite Christ Church; private photo c6a972.

Plan radii, heights and planting volumes are visual estimates in the site frame.
"""
import math
from southport3d.geometry import Mesh
from southport3d.road import parallel


def grade(y):return -.0075-.022*max(-36,min(36,y))


def kerb_curve():
    return [(-41,-14.8)]+[(-63.5+2.5*math.cos(a),-12.3+2.5*math.sin(a)) for a in [-math.pi/2-i*math.pi/2/16 for i in range(17)]]+[(-66,21)]


def wall_curve():
    return [(-58,-12.3)]+[(-60.5+3*math.cos(a),-9.3+3*math.sin(a)) for a in [-math.pi/2-i*math.pi/2/20 for i in range(21)]]+[(-63.5,-5.3)]


def curved_wall(level='detail',name='Garden curved return'):
    m=Mesh(name);path=wall_curve()
    # Continuous band shells share vertices, with end caps only at the two ends.
    for lo,hi,width in [(0,.35,.36),(.35,.43,.40),(.96,1.10,.43)]:
        left=parallel(path,width/2);right=parallel(path,-width/2)
        verts=[]
        for a,b in zip(left,right):
            verts.extend([(a[0],a[1],grade(a[1])+lo),(b[0],b[1],grade(b[1])+lo),(a[0],a[1],grade(a[1])+hi),(b[0],b[1],grade(b[1])+hi)])
        faces=[]
        for i in range(len(path)-1):
            k=4*i;j=k+4;faces.extend([(k,j,j+1,k+1),(k+2,k+3,j+3,j+2),(k,k+2,j+2,j),(k+1,j+1,j+3,k+3)])
        faces.extend([(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)])
        m.add(verts,faces)
    lengths=[math.dist(a,b) for a,b in zip(path,path[1:])];total=sum(lengths)
    def at(distance):
        for a,b,length in zip(path,path[1:],lengths):
            if distance<=length:return (a[0]+(b[0]-a[0])*distance/length,a[1]+(b[1]-a[1])*distance/length)
            distance-=length
        return path[-1]
    piers=[4.2,8.2,total]
    profile=[(.43,.12),(.47,.12),(.51,.085),(.55,.075),(.59,.105),(.66,.115),(.74,.09),(.82,.065),(.91,.065),(.94,.105),(.96,.105)]
    if level=='walk':profile=[profile[i] for i in [0,1,3,5,7,8,10]]
    if level=='district':profile=[(.43,.10),(.66,.11),(.85,.065),(.96,.10)]
    for i in range(1,int(total/.43)):
        t=i*total/int(total/.43)
        if min(abs(t-p) for p in [0]+piers)<.30:continue
        x,y=at(t);m.lathe((x,y),[(grade(y)+z,r) for z,r in profile],{'detail':16,'walk':8,'district':4}[level])
    for t in piers:
        x,y=at(t);m.box((x,y,grade(y)+.53),(.38,.46,1.06));m.box((x,y,grade(y)+1.10),(.47,.50,.08))
    return m


def shrubs(level='detail',name='Garden corner shrubs'):
    m=Mesh(name);n,rings={'detail':(10,6),'walk':(7,4),'district':(5,3)}[level]
    for x,y in [(-58.5,-11.2),(-60.2,-11.0),(-61.7,-10.0),(-62.3,-8.2),(-62.3,-6.3)]:
        for dx,dy,h,r in [(0,0,1.0,1.05),(.30,-.12,1.55,.55),(-.3,.18,1.43,.55)]:
            if level=='district' and dx:continue
            q=Mesh('foliage');q.ellipsoid((x+dx,y+dy,grade(y)+h),(r,r*.75,r*.70),segments=n,rings=rings)
            # Shared ellipsoid winding is inward; correct this closed foliage shell.
            q.faces=[tuple(reversed(f)) for f in q.faces]
            m.add(q.vertices,q.faces,0 if dx==0 else 1)
    return m


def taxi_letters(x,y):
    # Road-marking strokes, rather than font outlines with many tiny triangles.
    letters={'T':[(0,.8,.5,.8),(.25,0,.25,.8)],'A':[(0,0,.25,.8),(.25,.8,.5,0),(.12,.35,.38,.35)],'X':[(0,0,.5,.8),(0,.8,.5,0)],'I':[(0,0,.5,0),(.25,0,.25,.8),(0,.8,.5,.8)],'S':[(.5,.8,0,.8),(0,.8,0,.4),(0,.4,.5,.4),(.5,.4,.5,0),(.5,0,0,0)]}
    result=[]
    for i,c in enumerate('TAXIS'):
        for a,b,c,d in letters[c]:
            # Text runs along the lane and reads towards Lord Street.
            a,b,c,d=x+b-.4,y+a+i*.65-1.55,x+d-.4,y+c+i*.65-1.55
            length=math.hypot(c-a,d-b);nx,ny=-(d-b)/length*.045,(c-a)/length*.045
            result.append([(a-nx,b-ny),(c-nx,d-ny),(c+nx,d+ny),(a+nx,b+ny)])
    return result


def build_corner(ctx,materials):
    C=ctx['collections'];fp='sw-garden-furniture'
    curved_wall().finish(materials,C[fp])
    green=[ctx['mat']('Corner shrub dark',(.075,.14,.035)),ctx['mat']('Corner shrub leaf',(.16,.25,.07))]
    shrubs().finish(green,C[fp])
    from garden_front import globe_lamp
    ob=globe_lamp(name='Garden globe lamp curved return').finish(materials,C[fp]);ob.location=(-63.5,-5.3,grade(-5.3)+1.14)
    # Low wall and planter bowls continue along the side of the garden.
    from southport3d.landscape import capped_wall
    capped_wall([(-63.5,-5.3,grade(-5.3)),(-63.5,17.8,grade(17.8))],.42,.34,'Wall low garden return').finish([materials[0]],C[fp])
    for y in [0,12]:
        m=Mesh('Street return planter bowl');z=grade(y)+.42
        m.lathe((-63.5,y),[(z,.16),(z+.15,.20),(z+.25,.40),(z+.48,.57),(z+.52,.56),(z+.46,.48),(z+.30,.31)],24)
        m.finish([materials[0]],C[fp])


def build_lod(name,settings,asset_dir):
    return {'wall':curved_wall,'shrubs':shrubs}[settings['kind']](settings['level'],name).finish([])
