"""Fixed Betfred envelope with the Glebe setback and three roof heights."""
import json,math
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());xf,xr,yn,ys=(d[k] for k in ('front_x','rear_x','north_y','south_y'));w=yn-ys;dep=xf-xr;setback=d['upper_side_setback'];angle=.02418
    def world(p):
        x,y,z=p;return xf+math.cos(angle)*(x-xf)-math.sin(angle)*(y-yn),yn+math.sin(angle)*(x-xf)+math.cos(angle)*(y-yn),z+d['base_z']
    s=Surfaces(['architecture','roof','shopfront','rear'],world)
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('upper front',(xf,ys),(xf,yn),4.09,10.3)
    wall('Glebe tall return',(xf,yn),(xf-5.35,yn),0,10.3)
    wall('setback upper',(xf-5.35,yn-setback),(xf-9.25,yn-setback),3.35,6.5)
    wall('south party',(xr,ys),(xf,ys),0,6.5)
    s.triangle('party roof wedge',[(xf-5.35,ys,6.5),(xf-.35,ys,6.5),(xf-.35,ys,9.95)])
    s.part='rear'
    wall('low street wall',(xf-5.35,yn),(xr,yn),0,3.35)
    wall('rear wall',(xr,yn),(xr,ys),0,3.35)
    wall('upper step',(xr+5.72,yn-setback-.36),(xr+5.72,ys+.36),3.35,6.5)
    wall('setback cheek',(xf-5.35,yn-.18),(xf-5.35,yn-setback),3.35,6.5)
    s.part='roof'
    s.quad('front slope',[(xf-.36,ys+.16,9.95),(xf-.36,yn-.16,9.95),(xf-5.35,yn-.16,6.52),(xf-5.35,ys+.16,6.52)])
    s.quad('middle deck',[(xr+5.9,ys+.175,6.49),(xf-5.35,ys+.175,6.49),(xf-5.35,yn-setback-.175,6.49),(xr+5.9,yn-setback-.175,6.49)])
    s.quad('side strip',[(xr+5.72,yn-setback-.02,3.34),(xf-5.35,yn-setback-.02,3.34),(xf-5.35,yn-.18,3.34),(xr+5.72,yn-.18,3.34)])
    s.quad('rear deck',[(xr+.18,ys+.175,3.34),(xr+5.72,ys+.175,3.34),(xr+5.72,yn-.175,3.34),(xr+.18,yn-.175,3.34)])
    # The high frontage/return extend above the roof as real parapets.
    wall('front inner',(xf-.36,yn-.16),(xf-.36,ys+.16),9.95,10.3)
    s.quad('front coping',[(xf-.36,ys,10.355),(xf+.075,ys,10.355),(xf+.075,yn,10.355),(xf-.36,yn,10.355)])
    s.quad('tall return inner',[(xf-.36,yn-.36,9.95),(xf-5.35,yn-.36,6.52),(xf-5.35,yn-.36,10.3),(xf-.36,yn-.36,10.3)])
    s.quad('Glebe coping',[(xf-5.35,yn-.36,10.355),(xf-.36,yn-.36,10.355),(xf-.36,yn+.075,10.355),(xf-5.35,yn+.075,10.355)])
    s.part='shopfront';entry=w*.31;a,b=entry-.75,entry+.75
    wall('left shop',(xf,ys),(xf,ys+a),0,4.09)
    wall('right shop',(xf,ys+b),(xf,yn),0,4.09)
    wall('entrance fascia',(xf,ys+a),(xf,ys+b),3.09,4.09)
    wall('inset entrance',(xf-.52,ys+a),(xf-.52,ys+b),0,3.09)
    for u in (a,b):s.quad('entry return '+str(u),[(xf-.15,ys+u,0),(xf-.72,ys+u,0),(xf-.72,ys+u,3.03),(xf-.15,ys+u,3.03)])
    s.quad('entry soffit',[(xf-.72,ys+a,3.03),(xf-.72,ys+b,3.03),(xf+.05,ys+b,3.03),(xf+.05,ys+a,3.03)])
    return s.result
