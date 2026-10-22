"""Reusable, metric street furniture with explicit silhouette/detail controls.

Material slots: dark iron, zinc, pale edging, yellow, red lens, amber lens,
green lens, timber, glass. Site positions and evidence belong to asset recipes.
"""
import math
from mathutils import Matrix
from .geometry import Mesh


def furniture(kind, level='detail', name=None):
    m=Mesh(name or kind);n={'detail':24,'walk':12,'district':6}[level];fine=level=='detail';coarse=level=='district'
    if kind=='bollard':
        m.rect_profile((0,0),[(0,.28,.28),(.96,.16,.16)] if coarse else [(0,.28,.28),(.09,.27,.27),(.88,.18,.18),(.96,.16,.16)],0)
        if fine:
            for i in range(25):
                z=.13+i*.03;w=.27-(z-.09)*.09/.79
                for side in (-1,1):m.box((0,side*(w/2+.002),z),(w,.008,.006),0)
    elif kind=='bench':
        for x in (-.72,.72):
            m.box((x,0,.23),(.065,.55,.46),0);m.box((x,.24,.69),(.05,.06,.55),0)
            m.tube([(x,-.28,.62),(x,-.28,.70),(x,.23,.70)],.025,0,max(4,n//2))
        slats=1 if coarse else 5
        for i in range(slats):m.box((0,-.22+(i+.5)*.46/slats,.47),(1.9,.46/slats-(.012 if not coarse else 0),.05),7)
        for i in range(1 if coarse else 3):m.box((0,.245,.63+i*.105),(1.9,.055,.31 if coarse else .085),7)
        if fine:
            for x in (-.72,.72):
                for y in (-.16,.16):m.ellipsoid((x,y,.500),(.012,.012,.004),1,8,4)
    elif kind=='bin':
        m.lathe((0,0),[(0,.28),(.08,.30),(.80,.30),(.86,.32),(.94,.27),(1.0,.20)],n,0)
        if not coarse:
            for k in range(4):
                a=k*math.pi/2;part=Mesh('bin opening');part.box((0,-.302,.73),(.25,.012,.15),8);part.transform(Matrix.Rotation(a,4,'Z'));m.add(part.vertices,part.faces,8)
        if fine:
            for i in range(20):
                a=i*math.tau/20;m.tube([(.302*math.cos(a),.302*math.sin(a),.1),(.302*math.cos(a),.302*math.sin(a),.62)],.006,1,4)
    elif kind in ('signal','pedestrian'):
        pedestrian=kind=='pedestrian';height=2.75 if pedestrian else 3.7
        m.lathe((0,0),[(0,.065),(.12,.065),(height,.045)],n,1)
        z=2.4 if pedestrian else 3.05;h=.67 if pedestrian else 1.05
        m.box((0,-.07,z),(.48,.065,h+.12),2);m.box((0,-.145,z),(.39,.16,h),0)
        lens_z=[z+.16,z-.16] if pedestrian else [z+.32,z,z-.32]
        for k,zz in enumerate(lens_z):
            # Unlit coloured lenses; no invented live traffic phase.
            m.ellipsoid((0,-.233,zz),(.12,.022,.12),4+(k if not pedestrian else k*2),n,max(3,n//2))
            if not coarse:
                m.box((0,-.28,zz+.125),(.27,.15,.018),0)
                for side in (-1,1):m.box((side*.13,-.28,zz+.07),(.015,.15,.11),0)
        if pedestrian:
            m.box((0,-.10,1.05),(.16,.14,.27),3);m.box((0,-.177,1.05),(.12,.016,.22),0)
            if not coarse:m.ellipsoid((0,-.19,1.0),(.025,.012,.025),2,n,4)
            if fine:
                # Simple standing/walking glyphs, not text or a claimed equipment model.
                for zz,idx in [(z+.16,4),(z-.16,6)]:
                    m.ellipsoid((0,-.26,zz+.055),(.021,.008,.021),idx,8,4)
                    m.tube([(0,-.26,zz+.03),(0,-.26,zz-.02),(-.035,-.26,zz-.07)],.012,idx,4)
                    m.tube([(0,-.26,zz-.02),(.035,-.26,zz-.07)],.012,idx,4)
        elif fine:
            m.box((0,.06,2.8),(.18,.05,.5),1)
    elif kind=='streetlight':
        m.lathe((0,0),[(0,.18),(.3,.18),(.6,.09),(5.5,.055)],n,1)
        steps=16 if fine else 8 if not coarse else 4
        path=[(0,0,5.4)]+[(0,-1.05+1.05*math.cos(i*math.pi/2/steps),5.4+1.05*math.sin(i*math.pi/2/steps)) for i in range(steps+1)]
        m.tube(path,.05,1,max(4,n//2));m.ellipsoid((0,-1.1,6.35),(.23,.36,.12),0,n,max(3,n//2))
        m.ellipsoid((0,-1.1,6.29),(.19,.28,.05),2,n,max(3,n//2))
    else:raise ValueError('Unknown street furniture family: '+kind)
    return m


def sagging_chain(points, height=.55, sag=.16, radius=.012, segments=12):
    """Continuous low-sided cable approximation; individual links deliberately omitted."""
    m=Mesh('chain')
    for a,b in zip(points,points[1:]):
        path=[]
        for i in range(segments+1):
            t=i/segments;path.append((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t+height-4*sag*t*(1-t)))
        m.tube(path,radius,1,4)
    return m


def guardrail(points, height=1.0, picket_pitch=.16):
    m=Mesh('guardrail')
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b);count=max(1,round(length/picket_pitch))
        for i in range(count+1):
            p=[a[k]+(b[k]-a[k])*i/count for k in range(3)]
            m.tube([p,[p[0],p[1],p[2]+height]],.014,0,4)
        for h in (.15,height):m.tube([(a[0],a[1],a[2]+h),(b[0],b[1],b[2]+h)],.023,0,6)
    return m
