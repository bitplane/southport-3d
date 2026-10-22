"""Metric landscape proxies: explicit canopy LODs and capped retaining edges.

Tree material slots are bark, dark foliage, mid foliage, light foliage.
No species or individual tree survey is implied by the generic crown.
"""
import math
from .geometry import Mesh


def tree(level='detail', name='Tree'):
    m=Mesh(name)
    segments,rings={'detail':(12,8),'walk':(8,5),'district':(6,3)}[level]
    m.lathe((0,0),[(0,.24),(1.8,.21),(3.8,.12),(5,.035)],segments,0)
    if level!='district':
        for i in range(5):
            a=i*math.tau/5
            m.tube([(0,0,2.7),(math.cos(a)*1.1,math.sin(a)*1.1,4.4)],.065,0,max(4,segments//2))
    # Same outer envelope at every level; fewer lobes and radial samples at distance.
    m.ellipsoid((0,0,5.9),(3.3,3,3.3),2,segments,rings)
    if level!='district':
        for i in range(5):
            a=i*math.tau/5
            m.ellipsoid((math.cos(a)*1.7,math.sin(a)*1.7,5.5+(i%2)*.6),(1.8,1.6,2),1+i%3,segments,rings)
    return m


def capped_wall(points, height=.42, width=.32, name='Wall'):
    """Open polyline; caller supplies datum Z and explicit entrance gaps."""
    m=Mesh(name)
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length<1e-6:continue
        for low,high,w in [(0,height-.07,width),(height-.07,height,width+.08)]:
            nx,ny=-dy/length*w/2,dx/length*w/2
            v=[(p[0]+s*nx,p[1]+s*ny,p[2]+z) for z in [low,high] for p,s in [(a,-1),(b,-1),(b,1),(a,1)]]
            m.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    return m
