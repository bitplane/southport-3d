"""K6 exterior, calibrated to the November 2020 kiosk beside NatWest.

XY is the front elevation; +Z faces the street. Material slots: red, black,
glazing, ivory sign, crown ochre, handle metal. Hidden fittings are not invented.
"""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh


def roof_height(x,z):
    return 2.54-.08*((x/.46)**2+(z/.46)**2)


def kiosk(level='detail',name='Kiosk boundary telephone'):
    m=Mesh(name)
    detail=level=='detail'; close=level!='district'
    n={'detail':16,'walk':10,'district':6}[level]
    # Square plinth, solid rear and independent glazed elevations. No glass cube.
    m.box((0,.055,0),(.91,.11,.91),1)
    m.box((0,1.10,-.402),(.78,2.0,.07),0)
    for x in [-.405,.405]:
        for z in [-.405,.405]:
            m.box((x,1.14,z),(.085,2.06,.085),0)
            m.box((x,.16,z),(.097,.12,.097),0)
    # Compound convex roof: arched on all four sides, not a barrel extrusion.
    vs=[(-.46+.92*i/n,roof_height(-.46+.92*i/n,-.46+.92*j/n),-.46+.92*j/n)
        for j in range(n+1) for i in range(n+1)]
    count=len(vs);vs += [(x,y-.035,z) for x,y,z in vs]
    fs=[]
    for j in range(n):
        for i in range(n):
            a=j*(n+1)+i;f=(a,a+n+1,a+n+2,a+1)
            fs.extend([f,tuple(k+count for k in reversed(f))])
    edge=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
    fs += [(a,b,b+count,a+count) for a,b in zip(edge,edge[1:]+edge[:1])]
    m.add(vs,fs,0)
    # Each face has its own head casting and inset enamel name panel.
    for side in range(4):
        q=Mesh('K6 elevation');angle=side*math.pi/2
        q.box((0,2.115,.408),(.82,.11,.075),0)
        q.box((0,2.235,.416),(.82,.19,.065),0)
        q.box((0,2.235,.454),(.64,.115,.012),3)
        # Raised sign surround follows the actual casting, with a recessed centre.
        for x in [-.335,.335]:q.box((x,2.235,.466),(.026,.145,.026),0)
        for y in [2.163,2.307]:q.box((0,y,.466),(.696,.024,.026),0)
        arc=[(-.445,2.325),(.445,2.325)]+[(.445-.89*i/n,roof_height(.445-.89*i/n,.46)-.033) for i in range(n+1)]
        q.outline(arc,.378,.438,0)
        # Crown emblem: band, lobed arches, orb and cross. Relief is interpreted
        # from the photographed gold silhouette; fine heraldry is not surveyed.
        crown=[(-.065,2.335),(.065,2.335),(.078,2.365),(.063,2.402),(.025,2.415),(0,2.433),(-.025,2.415),(-.063,2.402),(-.078,2.365)]
        q.outline(crown,.443,.450,4)
        if close:
            for y in [2.34,2.352]:q.box((0,y,.454),(.13,.009,.009),4)
            for cx,rx in [(-.032,.037),(.032,.037),(0,.028)]:
                pts=[(cx+rx*math.cos(a),2.36+.045*math.sin(a),.455) for a in [math.pi*i/(10 if detail else 5) for i in range((10 if detail else 5)+1)]]
                q.tube(pts,.0045,material=4,sides=6 if detail else 4)
            q.box((0,2.427,.456),(.009,.035,.012),4)
            q.box((0,2.432,.456),(.028,.008,.012),4)
        if side!=2:
            # Eight rows of wide centre panes flanked by narrow margin lights.
            q.box((0,1.185,.392),(.626,1.73,.016),2)
            for x in [-.356,.356]:q.box((x,1.16,.426),(.072,1.84,.065),0)
            q.box((0,.23,.425),(.78,.22,.07),0)
            q.box((0,2.065,.425),(.78,.10,.07),0)
            for x in [-.225,.225]:q.box((x,1.185,.426),(.019,1.73,.038),0)
            for j in range(9):q.box((0,.32+j*1.73/8,.426),(.64,.019,.038),0)
            if detail:
                # Small stepped beads around the pane field and timber door.
                for x in [-.319,.319]:q.box((x,1.185,.450),(.012,1.76,.012),0)
                for y in [.307,2.063]:q.box((0,y,.449),(.65,.012,.012),0)
            if side==0 and close:
                # Recessed oval metal cup pull, rather than an external bar.
                q.box((.358,1.12,.464),(.047,.13,.012),5)
                q.box((.358,1.12,.472),(.024,.083,.008),1)
                q.tube([(.341,1.07,.48),(.339,1.12,.486),(.341,1.17,.48)],.006,material=5,sides=6)
                for y in [.47,1.18,1.93]:q.box((-.388,y,.46),(.026,.074,.022),0)
        else:
            if close:
                for x in [-.34,.34]:q.box((x,1.14,.446),(.025,1.8,.012),0)
                for y in [.25,1.12,2.03]:q.box((0,y,.446),(.70,.025,.012),0)
        if detail:
            # Small ventilation slots below the cornice, visible on original casting.
            for x in [-.26,-.13,0,.13,.26]:q.box((x,2.105,.449),(.085,.008,.004),1)
        q.transform(Matrix.Rotation(angle,4,'Y'))
        for f,idx in zip(q.faces,q.indices):m.add([q.vertices[i] for i in f],[tuple(range(len(f)))],idx)
    return m
