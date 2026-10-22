"""Photograph-led boundary and red kiosk beside the bank; dimensions estimated."""
import math
from southport3d.geometry import Mesh
from components import wall, rectangle, arc


def kiosk(level='detail', name='Kiosk boundary telephone'):
    # Local XY is the front elevation, +Z faces the pavement.
    m=Mesh(name)
    m.box((0,.045,0),(.88,.09,.88),1)
    m.box((0,1.22,0),(.74,2.32,.74),2)
    for x in [-.40,.40]:
        for z in [-.40,.40]:m.box((x,1.20,z),(.09,2.3,.09),0)
    for y,h in [(.15,.18),(2.14,.13),(2.36,.12)]:
        m.box((0,y,0),(.88,h,.88),0)
    # A shallow curved crown, shared silhouette at every LoD.
    steps={'detail':20,'walk':12,'district':6}[level]
    crown=[(-.44,2.42),(.44,2.42)]+[(.44*math.cos(i*math.pi/steps),2.42+.16*math.sin(i*math.pi/steps)) for i in range(steps+1)]
    m.outline(crown,-.44,.44,0)
    # Front and both visible side window grids remain recognisable at distance.
    for side in [-1,1]:
        for x in [-.25,.25]:m.box((x,1.15,side*.405),(.025,1.76,.025),0)
        for z in [-.25,.25]:m.box((side*.405,1.15,z),(.025,1.76,.025),0)
    for j in range(1,9 if level!='district' else 5):
        y=.26+j*(1.75/(9 if level!='district' else 5))
        for side in [-1,1]:
            m.box((0,y,side*.405),(.72,.025,.025),0)
            m.box((side*.405,y,0),(.025,.025,.72),0)
    for side in [-1,1]:
        m.box((0,2.27,side*.447),(.71,.14,.012),3)
        m.box((side*.447,2.27,0),(.012,.14,.71),3)
    if level!='district':m.box((.31,1.08,.445),(.025,.18,.04),1)
    return m


def build_lod(name, settings, asset_dir):
    return kiosk(settings['level'],name).finish([])


def build_boundary(frame, finish, stone, plain, black, red, glass, white):
    width=math.hypot(33.12-30.4,.36)
    opening=rectangle(.96,.10,1.97,2.18)
    finish(wall('Envelope boundary wall',width,2.63,[opening]),mats=[stone],transform=frame)
    finish(wall('Ashlar boundary courses',width,2.63,[opening],True),mats=plain,transform=frame)
    m=Mesh('Trim boundary door surround')
    for x in [.88,2.05]:m.box((x,1.16,.08),(.16,2.18,.20))
    for y,w,h,dep in [(2.25,1.35,.14,.25),(2.37,1.52,.10,.30),(2.65,width,.12,.30)]:
        m.box((width/2 if y==2.65 else 1.465,y,dep/2),(w,h,dep))
    # Solid semicircular pediment and concentric mouldings.
    m.outline([(1.465-.70,2.71),(1.465+.70,2.71)]+[(1.465+.70*math.cos(i*math.pi/32),2.71+.70*math.sin(i*math.pi/32)) for i in range(33)],-.20,.02)
    arc(m,1.465,2.71,.64,.72,out=.13,depth=.13)
    arc(m,1.465,2.71,.54,.58,out=.08,depth=.08)
    finish(m,mats=[plain[1]],transform=frame)
    door=Mesh('Door boundary black gate');door.box((1.465,1.14,-.15),(1.01,2.08,.08))
    finish(door,mats=[black],transform=frame)
    ornament=Mesh('Fine boundary circular frieze')
    for x in [.12,.34,.56,.78,2.15,2.36,2.57]:
        arc(ornament,x,2.48,.035,.055,0,math.tau,out=.04,depth=.02,steps=16)
    finish(ornament,mats=[plain[0]],transform=frame)
