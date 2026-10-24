"""Fixed classical bank envelope, shared hip end and low rear service wing."""
import json,math
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());xf,xr,yn,ys=(d[k] for k in ('front_x','rear_x','north_y','south_y'));w=yn-ys;mr=xf-d['main_depth']
    px,py=d['registration_pivot'];angle=d['registration_radians']
    def world(p):
        x,y,z=p;return px+math.cos(angle)*(x-px)-math.sin(angle)*(y-py),py+math.sin(angle)*(x-px)+math.cos(angle)*(y-py),z+d['base_z']
    s=Surfaces(['architecture','roof','shopfront','rear'],world)
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('upper front',(xf,ys),(xf,yn),4.34,10.68)
    wall('north party',(xf,yn),(mr,yn),0,10.4)
    wall('south party',(mr,ys),(xf,ys),0,10.4)
    s.part='rear'
    wall('main rear',(mr,yn),(mr,ys),3.4,10.4)
    wn=yn-.9;wf=mr
    wall('rear north',(wf,wn),(xr,wn),0,3.7)
    wall('rear south',(xr,ys),(wf,ys),0,3.7)
    wall('rear end',(xr,wn),(xr,ys),0,3.4)
    wall('exposed main rear',(mr,yn),(mr,wn),0,3.4)
    # Inner faces and top strips preserve the low service parapets.
    for y,Y in ((ys,ys+.2),(wn-.2,wn)):
        s.quad('parapet cap '+str(y),[(xr,y,3.7),(wf,y,3.7),(wf,Y,3.7),(xr,Y,3.7)])
        wall('parapet inner '+str(y),(xr,Y if y==ys else y),(wf,Y if y==ys else y),3.32,3.7)
    s.part='roof';xe,xb=xf-.20,mr+.15;ridge=(xe+xb)/2;ze=10.4;zr=d['ridge_height']
    v=[(xe,ys+.12,ze),(xe,yn,ze),(xb,yn,ze),(xb,ys+.12,ze),(ridge,ys+2.15,zr),(ridge,yn,zr)]
    for i,ids in enumerate([(0,1,5,4),(2,3,4,5),(3,0,4)]):
        p=[v[k] for k in ids];(s.quad if len(p)==4 else s.triangle)('hip '+str(i),p)
    s.quad('rear deck',[(xr+.02,ys+.2,3.36),(wf-.02,ys+.2,3.36),(wf-.02,wn-.2,3.36),(xr+.02,wn-.2,3.36)])
    s.box('rooflight',(xr+3.5,(ys+wn)/2-.6,3.4),(xr+4.9,(ys+wn)/2+.6,3.6375))
    s.part='shopfront'
    def panel(name,a,b,lo,hi,dep=0):wall(name,(xf-dep,ys+a),(xf-dep,ys+b),lo,hi)
    last=0
    for name,c,width,depth in [('bank',w-1.35-.58,1,.27),('flats',w-.72,.88,.26)]:
        a,b=c-width/2,c+width/2
        panel(name+' left',last,a,0,4.34);panel(name+' head',a,b,2.9,4.34);panel(name+' leaf',a,b,0,2.9,depth)
        jamb_front,jamb_back,jamb_top=(.155,.245,2.5) if name=='bank' else (.105,.215,2.38)
        for u in (a,b):s.quad(name+' jamb '+str(u),[(xf-jamb_front,ys+u,0),(xf-jamb_back,ys+u,0),(xf-jamb_back,ys+u,jamb_top),(xf-jamb_front,ys+u,jamb_top)])
        last=b
    panel('end pier',last,w,0,4.34)
    return s.result
