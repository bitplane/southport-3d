"""Posting House redevelopment: aerial roof plan and photographed raised garden.

Roof widths come from block-review/measurements.json. Heights and concealed
basement construction are estimates; this is an exterior reconstruction.
"""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh
from components import rect, wall, sash


def build_courtyard(g):
    front=g['front']; finish=g['finish']; box=g['box']; instance=g['instance']
    brick=g['brick']; glass=g['glass']; white=g['white']
    metal=g['material']('Courtyard pale zinc roof',(.48,.52,.54))
    rail=g['material']('Courtyard blue grey metal',(.16,.28,.36))
    render=g['material']('Courtyard light render',(.75,.75,.68))
    paving=g['material']('Courtyard concrete flags',(.34,.35,.33))
    turf=g['material']('Courtyard artificial lawn',(.24,.32,.10))
    wood=g['material']('Courtyard weathered timber',(.30,.25,.17))
    soil=g['material']('Courtyard planter soil',(.065,.045,.025))
    foliage=g['material']('Courtyard shrubs',(.12,.22,.065))

    def b(name,c,s,mat=render,part='rear-range',frame=front):
        return box(name,c,s,part,mat,frame)

    # Broad flat warehouse roof, then the narrower pitched attic strip seen
    # from the courtyard. The previous eight-metre solid extrusion was wrong.
    outside=front@Matrix.Translation((0,0,-44.4))@Matrix.Rotation(-math.pi/2,4,'Y')
    holes=[rect(44.4-d-.85,z-1.075,44.4-d+.85,z+1.075)
           for d in [21.2,25.8,30.4,35,39.6] for z in [3.1,6.9,10.6]]
    finish(wall('Envelope warehouse street wall',rect(0,0,26.5,13.7),holes),
           'rear-range',[brick],outside)
    for d in [21.2,25.8,30.4,35,39.6]:
        for z in [3.1,6.9,10.6]:
            instance('warehouse-sash',sash('Glazing warehouse',1.7,2.15),
                     outside@Matrix.Translation((44.4-d,z,0)),'rear-range',[glass,white])
    b('Roof warehouse broad pale flat',(5.5,13.8,-31.15),(11,.20,26.5),metal,'roof')
    m=Mesh('Roof warehouse courtyard pitch')
    m.add([(u,z,-d) for dz in [0,-.18] for u,z,d in
           [(10.8,13.9+dz,17.9),(16.1,12.6+dz,17.9),
            (16.1,12.6+dz,44.4),(10.8,13.9+dz,44.4)]],
          [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    finish(m,'roof',[metal],front)
    end=front@Matrix.Translation((16.1,0,-44.4))@Matrix.Rotation(math.pi,4,'Y')
    finish(wall('Envelope warehouse roof end',[(0,12.6),(5.3,12.6),(5.3,13.9)],[]),
           'rear-range',[brick],end)

    # Inner face faces west; local X runs back towards the historic building.
    inner=front@Matrix.Translation((15.5,0,-17.9))@Matrix.Rotation(math.pi/2,4,'Y')
    centres=[9.1,15.8,22.5]
    holes=[rect(x-2.4,z-1.12,x+2.4,z+1.12) for x in centres for z in [4.5,7.9,11.1]]
    finish(wall('Envelope warehouse garden wall',rect(0,2.7,26.5,12.6),holes),
           'rear-range',[brick],inner)
    for x in centres:
        for z in [4.5,7.9,11.1]:
            instance('warehouse-garden',sash('Window warehouse garden',4.8,2.24),
                     inner@Matrix.Translation((x,z,0)),'rear-range',[glass,white])
        for z in [6.72,9.92]:
            b('Balcony courtyard deck',(x,z,.64),(5.4,.15,1.4),rail,frame=inner)
            m=Mesh('Balcony courtyard balustrade')
            for y in [.35,.7,1.05]:
                m.tube([(x-2.7,z+y,1.31),(x+2.7,z+y,1.31)],.025,sides=6)
            for xx in [x-2.7,x-1.35,x,x+1.35,x+2.7]:
                m.tube([(xx,z,1.31),(xx,z+1.1,1.31)],.03,sides=6)
            finish(m,'rear-range',[rail],inner)
    # One rendered stair/access tower at the historic end, not two free-standing
    # pyramid bays halfway along the garden. Its roof is a shallow metal hip.
    tf=front@Matrix.Translation((16.3,0,-17.9))@Matrix.Rotation(math.pi/2,4,'Y')
    tholes=[rect(.6,z-.7,1.65,z+.7) for z in [4.5,7.9,11.3]]
    finish(wall('Envelope courtyard access tower face',rect(0,2.7,5.8,14.7),tholes),
           'rear-range',[render],tf)
    for z in [4.5,7.9,11.3]:
        instance('tower-small',sash('Window courtyard tower',1.05,1.4),
                 tf@Matrix.Translation((1.125,z,0)),'rear-range',[glass,white])
    for d in [17.9,23.7]:b('Envelope courtyard tower return',(13.65,8.7,-d),(5.3,12,.25))
    m=Mesh('Roof courtyard tower shallow hip')
    m.add([(10.6,14.75,-17.5),(16.7,14.75,-17.5),(16.7,14.75,-24.1),
           (10.6,14.75,-24.1),(13.65,15.35,-20.8)],
          [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)])
    finish(m,'roof',[metal],front)

    # Raised basement roof garden. The service lane remains outside its west
    # retaining wall. Photo 15 shows paving, artificial lawn and timber squares.
    level=2.7
    b('Envelope courtyard basement roof',(22.4,level-.18,-31.15),(13.8,.36,26.5),paving,'courtyard-ground')
    b('Envelope courtyard west retaining wall',(29.05,1.95,-31.15),(.5,3.9,26.5),brick)
    b('Trim courtyard retaining coping',(29.05,3.96,-31.15),(.65,.12,26.5),paving)
    b('Envelope courtyard lawn',(25.0,level+.025,-33.6),(7.5,.05,21.6),turf,'courtyard-ground')
    for d in [27.8,37.6]:
        b('Envelope courtyard timber square',(24.2,level+.055,-d),(5.1,.06,3.5),wood,'courtyard-ground')
        for j in range(27):
            b('Detail courtyard deck joints',(21.7+j*.19,level+.088,-d),(.012,.005,3.5),soil)
    # Flag grid is fine relief only; courtyard proportions survive every LOD.
    for d in [24+i*.6 for i in range(34)]:
        b('Detail courtyard paving joint',(19.6,level+.012,-d),(3.8,.012,.015),soil)
    for u in [17.8+i*.6 for i in range(7)]:
        b('Detail courtyard paving joint',(u,level+.012,-34),( .015,.012,20),soil)
    for u,d,w,dep in [(27.8,25.8,1.3,1.3),(27.8,31.4,1.3,1.3),(27.8,37,1.3,1.3),
                       (21.3,26,1.35,1.35),(21.3,33,1.35,1.35),(21.3,40,1.35,1.35),
                       (18,29,.65,2.7),(18,36,.65,2.7)]:
        for hh in [.15,.37,.59]:
            b('Trim courtyard planter boards',(u,level+hh,-d),(w,.20,dep),wood)
        b('Envelope courtyard planter soil',(u,level+.7,-d),(w-.12,.06,dep-.12),soil)
        m=Mesh('Ornament courtyard shrub')
        m.ellipsoid((u,level+1,-d),(w*.49,.6,dep*.48),segments=10,rings=6)
        finish(m,'rear-range',[foliage],front)
    # Metal pergola/trellis along the boundary, observed in the garden photo.
    m=Mesh('Balcony courtyard boundary frame')
    for d in [24,28,32,36,40,44]:
        m.tube([(28.7,level,-d),(28.7,level+2,-d)],.035,sides=6)
        m.tube([(28.7,level+2,-d),(26.9,level+2,-d)],.035,sides=6)
    m.tube([(28.7,level+2,-24),(28.7,level+2,-44)],.035,sides=6)
    finish(m,'rear-range',[rail],front)

    # Historic rear's low extension supports the terrace above the garden doors.
    b('Roof historic rear terrace',(23,5.1,-20.45),(12,.18,5.1),paving,'courtyard-ground')
    ef=front@Matrix.Translation((29,0,-23.0))@Matrix.Rotation(math.pi,4,'Y')
    for x in [1.5,4.5,7.5,10.5]:
        instance('garden-door',sash('Window garden extension',2.95,2.2),
                 ef@Matrix.Translation((x,3.8,0)),'rear-range',[glass,rail])
    for u in [17,29]:b('Envelope garden extension return',(u,3.9,-20.45),(.18,2.4,5.1))
    m=Mesh('Balcony historic terrace rails')
    for a,bound in [(17,25.5),(26.5,29)]:
        for z in [5.5,6.15]:m.tube([(a,z,-23),(bound,z,-23)],.025,sides=6)
        count=round((bound-a)/.25)
        for j in range(count+1):m.tube([(a+j*(bound-a)/count,5.2,-23),(a+j*(bound-a)/count,6.2,-23)],.018,sides=6)
    finish(m,'rear-range',[white],front)
    # Exterior spiral from the garden to the terrace, visible in photo 15 and
    # the heritage rear photograph. Treads belong to walkable ground; rails do not.
    steps=13;cx,cz=26.0,-23.9
    m=Mesh('Envelope courtyard spiral treads');handrail=[]
    for j in range(steps):
        angle=-math.pi*1.5+2*math.pi*(j+1)/steps
        z=level+(5.1-level)*(j+1)/steps
        a,bound=angle-2*math.pi/steps,angle
        plan=[(cx+r*math.cos(t),cz+r*math.sin(t)) for r,t in [(.08,a),(.72,a),(.72,bound),(.08,bound)]]
        verts=[(x,y,d) for y in [z-.07,z] for x,d in plan]
        m.add(verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        handrail.append((cx+.76*math.cos(angle),z+1.0,cz+.76*math.sin(angle)))
    finish(m,'courtyard-ground',[metal],front)
    b('Envelope courtyard stair landing',(26,5.06,-23.1),(1.0,.08,.7),metal,'courtyard-ground')
    m=Mesh('Balcony courtyard spiral rails')
    m.tube([(cx,level,cz),(cx,6.1,cz)],.06,sides=10)
    m.tube(handrail,.025,sides=6)
    for x,z,d in handrail:m.tube([(x,z-1,d),(x,z,d)],.018,sides=6)
    finish(m,'rear-range',[white],front)
