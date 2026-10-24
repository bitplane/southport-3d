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
    panel('upper front',0,w,3.88,7.25)
    wall('north party',(xf,yn),(mr,yn),0,7.25)
    wall('south party',(mr,ys),(xf,ys),0,7.25)
    xe=xf+.12;xb=mr-.10;ridge=(xe+xb)/2
    for y in (ys,yn):s.triangle('roof end '+str(y),[(xf-.15,y,7.25),(mr+.15,y,7.25),(ridge,y,9.08)])

    s.part='rear'
    wall('main rear',(mr,yn),(mr,ys),3.42,7.25)
    wall('wing north',(mr,yn),(xr,yn),0,3.42)
    wall('wing south',(xr,ys),(mr,ys),0,3.42)
    wall('wing end',(xr,yn),(xr,ys),0,3.42)
    s.part='roof'
    s.quad('street pitch',[(xe,ys,7.25),(xe,yn,7.25),(ridge,yn,9.2),(ridge,ys,9.2)])
    s.quad('rear pitch',[(ridge,ys,9.2),(ridge,yn,9.2),(xb,yn,7.25),(xb,ys,7.25)])
    s.quad('rear deck',[(xr,ys,3.42),(mr,ys,3.42),(mr,yn,3.42),(xr,yn,3.42)])
    s.part='shopfront';left=w-1.42;right=w-.30
    panel('shop south',0,left,0,3.88);panel('shop north',w-.24,w,0,3.88)
    panel('entry head',left,right,3.145,3.88);panel('entry leaf',left,right,0,2.965,.32)
    # The source has thin doorway frames, not deep solid jamb walls.
    return s.result
