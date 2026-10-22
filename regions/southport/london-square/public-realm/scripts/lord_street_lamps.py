"""Unequal-height twin swan-neck lamps: Sefton appraisal (2017), page 74.

Estimated metric proportions, not a surveyed equipment specification.
"""
import math
from southport3d.geometry import Mesh


def lamp(level='detail',name=None):
    m=Mesh(name or 'lord-street-lamp')
    n={'detail':32,'walk':16,'district':8}[level]
    steps={'detail':24,'walk':12,'district':6}[level]
    m.lathe((0,0),[(0,.17),(.10,.17),(.13,.13),(1.32,.13),(1.40,.095)],n,0)
    m.lathe((0,0),[(1.40,.095),(1.48,.08),(5.45,.06)],n,2)
    for z in [1.40,3.15,4.72,5.39]:
        m.lathe((0,0),[(z,.10),(z+.055,.10)],n,0)
    # Taller arm over the road (-Y); lower arm over the footway (+Y).
    for side,height,span in [(-1,6.65,1.35),(1,6.08,1.22)]:
        y0=0 if side==-1 else .12
        path=[(0,y0,4.77)]
        # Elliptical arch with vertical tangent at each pendant end.
        for i in range(steps+1):
            t=math.pi*i/steps
            path.append((0,y0+side*span*(1-math.cos(t))/2,height-.48+.48*math.sin(t)))
        m.tube(path,.045,2,max(6,n//2))
        y=y0+side*span;z=height-.48
        m.lathe((0,y),[(z-.16,.075),(z,.075)],n,0)
        m.lathe((0,y),[(z-.30,.31),(z-.26,.33),(z-.23,.32),(z-.18,.15),(z-.16,.075)],n,0)
        m.lathe((0,y),[(z-.43,.06),(z-.40,.16),(z-.34,.255),(z-.30,.27)],n,2)
        if level!='district':
            m.lathe((0,y),[(z-.31,.28),(z-.29,.28)],n,0)
    if level=='detail':
        m.box((0,-.132,.76),(.14,.012,.54),1)
        for h in [.52,1.0]:m.box((0,-.142,h),(.025,.009,.025),0)
    return m
