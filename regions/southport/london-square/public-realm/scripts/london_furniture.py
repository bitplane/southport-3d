"""London Street photo-derived furniture; shared palette indices from street.py."""
import math
from southport3d.geometry import Mesh


def stainless_bin(level='detail',name=None):
    m=Mesh(name or 'stainless-bin');n={'detail':48,'walk':24,'district':12}[level]
    # Slender cylindrical shell and flat overhanging lid. The front aperture is
    # absent from the shell, with a black recessed interior instead of a decal.
    r=.215
    m.lathe((0,0),[(.035,.17),(.075,.17)],n,8)
    m.lathe((0,0),[(.075,r),(.76,r)],n,1)
    m.lathe((0,0),[(.91,r),(.94,r),(.94,.23),(.965,.23)],n,1)
    for i in range(n):
        a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
        # Opening faces local -Y, spanning a broad curved mouth.
        if math.sin((a+b)/2)<-.45:continue
        m.add([(r*math.cos(a),r*math.sin(a),.76),(r*math.cos(b),r*math.sin(b),.76),(r*math.cos(b),r*math.sin(b),.91),(r*math.cos(a),r*math.sin(a),.91)],[(0,1,2,3)],1)
    m.lathe((0,0),[(.75,.19),(.91,.19)],n,8)
    if level!='district':
        for h in [.20,.67]:m.box((-.207,-.03,h),(.025,.035,.06),1)
        m.tube([(-.211,-.03,.12),(-.211,-.03,.87)],.005,8,4)
    # Tiny perforations use dark recess marks in Detail; lower levels keep the
    # metal envelope and actual mouth instead of retaining hundreds of dots.
    if level=='detail':
        for j in range(30):
            z=.14+j*.018
            for k in range(17):
                a=-math.pi*.82+k*math.pi*.64/16+(j%2)*.012
                x,y=(r+.001)*math.cos(a),(r+.001)*math.sin(a)
                tangent=(-math.sin(a),math.cos(a));rr=.0035
                m.add([(x+tangent[0]*rr*math.cos(t*math.pi/3),y+tangent[1]*rr*math.cos(t*math.pi/3),z+rr*math.sin(t*math.pi/3)) for t in range(6)],[tuple(range(6))],8)
    return m


def led_lamp(level='detail',name=None):
    m=Mesh(name or 'london-led');n={'detail':20,'walk':12,'district':8}[level]
    # Straight tapered pole, short outreach and narrow rectangular LED head.
    m.lathe((0,0),[(0,.075),(.95,.075),(1.08,.065),(6.7,.042)],n,1)
    m.tube([(0,0,6.62),(0,-.20,6.85),(0,-.48,6.87)],.035,1,max(4,n//2))
    m.box((0,-.45,6.88),(.20,.64,.085),1)
    m.box((0,-.45,6.832),(.15,.52,.012),2)
    if level!='district':
        m.box((0,-.072,.68),(.08,.02,.32),0)
        m.box((0,.09,2.30),(.22,.12,.50),1)
    return m
