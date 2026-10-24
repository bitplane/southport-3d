"""Fixed-budget District receiver; dimensions follow the authored source geometry."""
import json, math
from blender_envelope import Surfaces

def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    xf,xr,yn,ys=(d[k] for k in ('front_x','rear_x','north_y','south_y'))
    w=yn-ys;mr=xf-d['main_depth'];px,py=d['registration_pivot'];angle=d['registration_radians']
    def world(p):
        x,y,z=p
        return px+math.cos(angle)*(x-px)-math.sin(angle)*(y-py),py+math.sin(angle)*(x-px)+math.cos(angle)*(y-py),z+d['base_z']
    s=Surfaces(['architecture','roof','shopfront','rear'],world)
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    def panel(name,u,v,lo,hi,dep=0):wall(name,(xf-dep,ys+u),(xf-dep,ys+v),lo,hi)
    # Seven chords match the authored cylindrical glazing; no tessellation dependency.
    radius=1.45;half=math.radians(65);gc=w/2;edge=gc-radius*math.sin(half)
    panel('south pier',0,.9,3.81,12.25);panel('north pier',w-.9,w,3.81,12.25)
    wall('south swept return',(xf,ys+.9),(xf-.28,ys+edge),3.81,12.25)
    wall('north swept return',(xf-.28,ys+w-edge),(xf,yn-.9),3.81,12.25)
    arc=[(xf-.28+radius*(math.cos(-half+i*2*half/7)-math.cos(half)),ys+gc+radius*math.sin(-half+i*2*half/7)) for i in range(8)]
    for i,(a,b) in enumerate(zip(arc,arc[1:])):wall('round glazing '+str(i),a,b,3.81,13.1)
    # Larger crown cap is silhouette geometry, with the detailed ribs baked away.
    r=1.68;cap=[(xf-.42,ys+gc-r*math.sin(half)),(xf-.42,ys+gc+r*math.sin(half))]
    cap += [(xf-.28+r*(math.cos(half-i*2*half/12)-math.cos(half)),ys+gc+r*math.sin(half-i*2*half/12)) for i in range(13)]
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    verts=[Vector((*p,13.29)) for p in cap]
    for i,t in enumerate(tessellate_polygon([verts])):
        s.triangle('crown top '+str(i),[verts[k] if isinstance(k,int) else k for k in reversed(t)])
    for i,(a,b) in enumerate(zip(cap,cap[1:]+cap[:1])):wall('crown edge '+str(i),a,b,13.11,13.29)
    wall('north party',(xf,yn),(xr,yn),0,11.94)
    wall('south party',(xr,ys),(xf,ys),0,11.94)
    s.part='rear';wall('rear wall',(xr,yn),(xr,ys),0,11.94)
    s.part='roof'
    s.quad('flat deck',[(xr+.26,ys+.26,11.86),(xf,ys+.26,11.86),(xf,yn-.26,11.86),(xr+.26,yn-.26,11.86)])
    for name,a,b in [('south',(xr,ys),(xf,ys)),('north',(xf,yn),(xr,yn)),('rear',(xr,yn),(xr,ys))]:wall('parapet '+name,a,b,11.94,12.29)
    for y,Y in [(ys,ys+.26),(yn-.26,yn)]:
        s.quad('side cap '+str(y),[(xr+.26,y,12.29),(xf,y,12.29),(xf,Y,12.29),(xr+.26,Y,12.29)])
        wall('side inside '+str(y),(xr+.26,Y if y==ys else y),(xf,Y if y==ys else y),11.91,12.29)
    s.quad('rear cap',[(xr,ys,12.29),(xr+.26,ys,12.29),(xr+.26,yn,12.29),(xr,yn,12.29)])
    wall('rear inside',(xr+.26,ys+.26),(xr+.26,yn-.26),11.91,12.29)
    # Rooflights project into the deck texture at this distance.
    s.part='shopfront';left=.24;right=1.82
    panel('south shop pier',0,left,0,3.81);panel('display',right,w,0,3.81)
    panel('entry head',left,right,2.97,3.81);panel('entry leaf',left,right,0,2.97,.36)
    for u in (left,right):s.quad('entry return '+str(u),[(xf-.08,ys+u,0),(xf-.47,ys+u,0),(xf-.47,ys+u,2.97),(xf-.08,ys+u,2.97)])
    return s.result
