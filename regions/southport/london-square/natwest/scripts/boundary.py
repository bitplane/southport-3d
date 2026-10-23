"""Photograph-led boundary and red kiosk beside the bank; dimensions estimated."""
import math
from southport3d.geometry import Mesh
from components import wall, rectangle, arc


from kiosk import kiosk


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
