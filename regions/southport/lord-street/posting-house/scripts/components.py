"""Posting House facade profiles; face-local horizontal X, height Y, outward Z."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract


def rect(x0,y0,x1,y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def opening(x,bottom,spring,rx,ry,steps=32):
    return [(x-rx,bottom),(x+rx,bottom)]+[(x+rx*math.cos(math.pi*i/steps),spring+ry*math.sin(math.pi*i/steps)) for i in range(steps+1)]


def wall(name,outline,holes,back=-.40,front=0):
    parts=[outline]
    for hole in holes:parts=[p for a in parts for p in subtract(a,hole)]
    m=Mesh(name)
    for p in parts:m.outline(p,back,front)
    return m


def ellipse_band(m,cx,cy,rx,ry,width,depth=.22,start=0,end=math.pi,steps=40,mat=0):
    for j in range(steps):
        a=start+(end-start)*j/steps;b=start+(end-start)*(j+1)/steps
        m.outline([(cx+rx*math.cos(a),cy+ry*math.sin(a)),(cx+(rx+width)*math.cos(a),cy+(ry+width)*math.sin(a)),(cx+(rx+width)*math.cos(b),cy+(ry+width)*math.sin(b)),(cx+rx*math.cos(b),cy+ry*math.sin(b))],.01,depth,mat)


def sash(name,width,height,arched=False):
    """Shallow glazing + timber, separate from the stone surrounds for baking."""
    m=Mesh(name);w=width/2;h=height/2
    if arched:m.outline(opening(0,-h,h-w,w,w),-.24,-.21,0)
    else:m.box((0,0,-.23),(width,height,.04),0)
    for sign in (-1,1):m.box((sign*(w-.045),-w/2 if arched else 0,-.10),(.09,height-w if arched else height,.13),1)
    for y in [-h,0] + ([] if arched else [h]):m.box((0,y,-.10),(width-.18,.09,.13),1)
    for x in [-w/3,w/3]:m.box((x,-w/2 if arched else 0,-.13),(.032,height-w if arched else height,.08),1)
    for y in [-h/2,h/2]:
        for a,b in [(-w+.09,-w/3-.016),(-w/3+.016,w/3-.016),(w/3+.016,w-.09)]:
            m.box(((a+b)/2,y,-.13),(b-a,.03,.08),1)
    if arched:ellipse_band(m,0,h-w,w-.09,w-.09,.09,-.035,steps=28,mat=1)
    return m


def surround(name,width,height,transom=True):
    m=Mesh(name);w=width/2;h=height/2
    for side in (-1,1):
        m.box((side*(w+.13),0,.04),(.26,height+.3,.26))
        m.box((side*(w+.29),0,.10),(.075,height+.48,.28))
    for y in (-h,h):m.box((0,y,.10),(width+.62,.19,.35))
    m.box((0,-h-.14,.18),(width+.84,.15,.52))
    if transom:m.box((0,h-.76,.08),(width,.16,.30))
    return m


def cross_window(name,width,height):
    """Painted frame, one timber sash transom; stone cross is separate geometry."""
    m=Mesh(name);w=width/2;h=height/2
    m.box((0,0,-.23),(width+.04,height+.04,.04),0)
    for x in [-w+.035,w-.035]:m.box((x,0,-.12),(.09,height,.12),1)
    for y in [-h,h,-.35]:m.box((0,y,-.12),(width-.16,.07,.12),1)
    return m
