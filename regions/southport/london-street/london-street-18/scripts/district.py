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
    panel('upper front',0,w,4.34,10.65)
    wall('north party',(xf,yn),(mr,yn),0,10.4)
    wall('south party',(mr,ys),(xf,ys),0,10.4)
    s.part='rear';wn=ys+5.8;wf=mr
    wall('main rear',(mr,yn),(mr,ys),4.15,10.4)
    wall('main rear yard',(mr,yn),(mr,wn),0,4.15)
    wall('wing north',(wf,wn),(xr,wn),0,3.3)
    wall('wing south',(xr,ys),(wf,ys),0,3.3)
    wall('wing end',(xr,wn),(xr,ys),0,3.3)
    ry=(ys+wn)/2
    s.triangle('main rear above south pitch',[(mr,ys,3.3),(mr,ys,4.15),(mr,ry,4.15)])
    s.triangle('main rear above north pitch',[(mr,ry,4.15),(mr,wn,4.15),(mr,wn,3.3)])
    s.triangle('rear wing gable',[(xr,wn,3.3),(xr,ry,4.15),(xr,ys,3.3)])
    s.part='roof';xe=xf-.2;xb=mr+.15;ridge=(xe+xb)/2
    v=[(xe,ys,10.4),(xe,yn-.12,10.4),(xb,yn-.12,10.4),(xb,ys,10.4),(ridge,ys,12.1),(ridge,yn-2.15,12.1)]
    for i,ids in enumerate([(0,1,5,4),(1,2,5),(2,3,4,5)]):
        p=[v[k] for k in ids];(s.quad if len(p)==4 else s.triangle)('main hip '+str(i),p)
    s.quad('wing south pitch',[(xr,ys,3.3),(wf,ys,3.3),(wf,ry,4.15),(xr,ry,4.15)])
    s.quad('wing north pitch',[(xr,ry,4.15),(wf,ry,4.15),(wf,wn,3.3),(xr,wn,3.3)])
    s.part='shopfront';door=w-1.35;left=door-.55;right=w-.4
    panel('shop south',0,left,0,4.34);panel('shop north',right,w,0,4.34)
    panel('entry head',left,right,2.79,4.34);panel('entry leaf',left,right,0,2.79,.35)
    for u in (left,right):s.quad('entry return '+str(u),[(xf-.08,ys+u,0),(xf-.43,ys+u,0),(xf-.43,ys+u,2.79),(xf-.08,ys+u,2.79)])
    return s.result
