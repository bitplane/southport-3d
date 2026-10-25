"""Photo-led exterior relief; dimensions are visually calibrated estimates."""
import math
from southport3d.geometry import Mesh,face_matrix
from components import arch_ring,ring,pointed,clipped,tracery_solid


def wing_detail(finish,box,tr,sign,a,b,inner,outer,stone,wood,glass,metal):
    # Two tiers of blind panels, with the upper tier rising under the outer gable.
    m=Mesh('Trim wing blind tracery')
    for dx in [-1.43,-.78,.78,1.43]:
        if abs(dx)>1:
            arch_ring(m,outer+dx,4.35,6.18,.29,.045,.09,.10,12)
        arch_ring(m,outer+dx,6.82,9.04-abs(dx)*.87,.29,.045,.09,.10,12)
    arch_ring(m,outer,8.63,9.47,.22,.045,.09,.10,12)
    # Blind panels stop at the full dressed window surround. They must not
    # cross its glazing or share exposed front faces with its arch mouldings.
    outline=pointed(outer,4.17,6.75,1.215)
    pieces=[]
    for face in m.faces:
        points=[m.vertices[i] for i in face]
        if all(abs(p[2]-.10)<1e-7 for p in points):
            polygon=[(p[0],p[1]) for p in points]
            signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
            if signed<0:polygon.reverse()
            pieces.extend(clipped(polygon,[outline]))
    m=Mesh('Trim wing blind tracery')
    tracery_solid(m,pieces,back=.01,front=.10)
    finish(m,mats=[stone],transform=tr)
    # Recessed stone panels below the inner glazing are clearly visible.
    m=Mesh('Trim inner window apron')
    for dx in [-.5,.5]:
        m.box((inner+dx,3.12,.025),(.85,.65,.10))
        for sx in [-.46,.46]:m.box((inner+dx+sx,3.03,.09),(.06,.58,.10))
    m.box((inner,2.73,.07),(2.30,.13,.22));finish(m,mats=[stone],transform=tr)
    # Quatrefoil spandrels above the paired side doors.
    m=Mesh('Ornament side door spandrels')
    for dx in [-.63,.63]:
        ring(m,outer+dx,2.84,.17,.025,.19,24)
        for k in range(4):
            a=k*math.pi/2
            ring(m,outer+dx+.07*math.cos(a),2.84+.07*math.sin(a),.065,.016,.20,16)
    finish(m,mats=[stone],transform=tr)
    # Wall globe lights beside the doors, with their visible dark equatorial band.
    m=Mesh('Fine side doorway lights')
    for dx in [-1.28,1.28]:
        m.box((outer+dx,2.58,.06),(.12,.23,.13),0)
        m.ellipsoid((outer+dx,2.64,.23),(.14,.14,.14),segments=12,rings=6,material=1)
        ring(m,outer+dx,2.64,.139,.018,.245,24,0)
    finish(m,mats=[metal,glass],transform=tr)


def tower_detail(finish,box,cx,front,z0,tw,stone,wallstone):
    for x in [cx-tw/2-.20,cx+tw/2+.20]:
        tr=face_matrix((x,front+.6,z0),(0,1,0))
        m=Mesh('Buttress sloped weatherings')
        # Sloping plinth offsets, rather than a stack of flat shelves.
        for h,w,d in [(.55,1.30,.52),(1.10,1.12,.44),(1.48,.90,.34)]:
            m.add([(-w/2,h,0),(w/2,h,0),(w/2,h+.20,-d),(-w/2,h+.20,-d),(-w/2,h-.08,-d),(w/2,h-.08,-d)],[(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2),(2,5,4,3)])
        finish(m,mats=[stone],transform=tr)
        m=Mesh('Trim buttress gabled niches')
        for h,w in [(7.0,.56),(14.0,.47),(19.7,.40)]:
            m.outline([(-w,h),(w,h),(0,h+1.15)],-.13,.10)
            arch_ring(m,0,h+.04,h+.36,w*.55,.045,.11,.16,12)
            for side in [-1,1]:
                m.tube([(side*w,h,.14),(0,h+1.15,.14)],.055,sides=6)
            m.box((0,h+1.21,.1),(.10,.26,.14))
        finish(m,mats=[stone],transform=tr)
        m=Mesh('Ornament buttress crocket buds')
        for h,w in [(7.0,.56),(14.0,.47),(19.7,.40)]:
            for side in [-1,1]:
                for t in [.18,.43,.68]:m.ellipsoid((side*w*(1-t),h+1.15*t,.20),(.08,.10,.07),segments=8,rings=4)
        finish(m,mats=[stone],transform=tr)
