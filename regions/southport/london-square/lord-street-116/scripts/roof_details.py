"""Observed roof forms, calibrated within the existing estimated building frame.

The satellite view resolves outlines, not access function or surveyed heights.
Keep closed edge housings, a walled recess and plant separate; do not invent doors.
"""
import math
from southport3d.geometry import Mesh


def build_roof(D, R, finish, mats):
    deck=D['base_z']+D['roof_level'];base=D['base_z']
    felt,brick,cap,metal,pale,dark,rust=mats
    x0,x1,y0,y1=D['x_far'],D['x_near'],D['rear_y'],D['front_y']-.45
    well=R['walled_recess'];cx,cy=well['centre'];ww,dd=well['size'];wx0,wx1=cx-ww/2,cx+ww/2;wy0,wy1=cy-dd/2,cy+dd/2
    # Four disjoint roof slabs leave a genuine shallow external recess.
    m=Mesh('Roof membrane fields')
    for a,b,c,d in [(x0+.3,wx0,y0+.3,y1),(wx1,x1-.3,y0+.3,y1),(wx0,wx1,y0+.3,wy0),(wx0,wx1,wy1,y1)]:
        m.box(((a+b)/2,(c+d)/2,deck),(b-a,d-c,.20))
    finish(m,'roof',[felt])
    m=Mesh('Roof walled recess')
    floor=deck+well['floor_relative'];m.box((cx,cy,floor-.06),(ww,dd,.12),0)
    # High two-sided screen and low return curbs reproduce the visible outline.
    for a,b,c,d,top in [(wx0,wx1,wy0,wy0+.22,deck+.95),(wx1-.22,wx1,wy0+.22,wy1,deck+.95),(wx0,wx0+.18,wy0+.22,wy1,deck+.12),(wx0+.18,wx1-.22,wy1-.18,wy1,deck+.12)]:
        m.box(((a+b)/2,(c+d)/2,(floor+top)/2),(b-a,d-c,top-floor),1)
        m.box(((a+b)/2,(c+d)/2,top+.035),(b-a+.035,d-c+.035,.07),2)
    finish(m,'roof',[felt,felt,cap])
    # Different parapet heights and a broad church-side capped strip are observed.
    m=Mesh('Roof stepped parapets')
    for wall in R['parapets']:
        xa,ya=wall['a'];xb,yb=wall['b'];th=wall['thickness'];top=base+wall['top'];wi=0 if wall['material']=='brick' else 2
        if xa==xb:
            m.box((xa,(ya+yb)/2,(deck+top)/2),(th,abs(yb-ya),top-deck),wi)
            m.box((xa,(ya+yb)/2,top+.045),(th+.10,abs(yb-ya),.09),1)
        else:
            m.box(((xa+xb)/2,ya,(deck+top)/2),(abs(xb-xa),th,top-deck),wi)
            m.box(((xa+xb)/2,ya,top+.045),(abs(xb-xa),th+.10,.09),1)
    finish(m,'roof',[brick,cap,felt])
    # Three roof-edge housings have capped tops. Their use is unresolved from above.
    for i,housing in enumerate(R['edge_housings']):
        if i<2:continue  # Integrated into the court wall by service_side.py.
        x,y=housing['centre'];w,d=housing['size'];h=housing['height']
        m=Mesh(f'Roof edge housing {i+1}')
        m.box((x,y,deck+h/2),(w,d,h),0)
        m.box((x,y,deck+h+.06),(w+.16,d+.16,.12),1)
        m.box((x,y,deck+h+.145),(w-.24,d-.24,.05),2)
        # Weathering upstand around the flat cap, deliberately no inferred door.
        for xx in [x-w/2+.07,x+w/2-.07]:m.box((xx,y,deck+h+.18),(.08,d-.14,.08),1)
        for yy in [y-d/2+.07,y+d/2-.07]:m.box((x,yy,deck+h+.18),(w-.22,.08,.08),1)
        finish(m,'roof',[cap,cap,felt])
    x,y=R['low_rooflight']['centre'];w,d=R['low_rooflight']['size']
    m=Mesh('Roof elongated rooflight or vent')
    m.box((x,y,deck+.17),(w,d,.34),0)
    # Shallow double pitch with weathered pale perimeter and rust-coloured bars.
    verts=[(x-w/2,y-d/2,deck+.34),(x,y-d/2,deck+.54),(x+w/2,y-d/2,deck+.34),(x-w/2,y+d/2,deck+.34),(x,y+d/2,deck+.54),(x+w/2,y+d/2,deck+.34)]
    # Outward winding on both pitches and end caps; double-sided display
    # must not conceal an inside-out rooflight shell. The underside meets its base.
    m.add(verts,[(1,4,3,0),(2,5,4,1),(2,1,0),(4,5,3)],1)
    for yy in [y-d/2,y+d/2]:
        m.tube([(x-w/2,yy,deck+.355),(x,yy,deck+.555),(x+w/2,yy,deck+.355)],.045,0,6)
    for xx,zz in [(x-w/2,deck+.355),(x,deck+.555),(x+w/2,deck+.355)]:m.tube([(xx,y-d/2,zz),(xx,y+d/2,zz)],.035,0,6)
    for yy in [y-d*.25,y,y+d*.25]:m.tube([(x-w/2,yy,deck+.355),(x,yy,deck+.555),(x+w/2,yy,deck+.355)],.045,2,6)
    finish(m,'roof',[pale,dark,rust])
    # Main plant volumes remain in every LOD; detailed fans/rails are separate.
    plant=R['plant'];px,py=plant['centre'];pw,pd=plant['size'];pz=deck+.22
    m=Mesh('Roof plant platform and cabinets')
    m.box((px,py,deck+.12),(pw,pd,.24),0)
    m.box((px+1.85,py,pz+.69),(1.65,4.85,1.38),1)
    m.box((px+1.85,py,pz+1.42),(1.78,4.99,.08),1)
    # Four circular-top condensers are distinguishable in the satellite capture.
    for yy in [py-2.25,py-.75,py+.75,py+2.25]:m.box((px-.15,yy,pz+.43),(1.05,1.20,.86),1)
    # One small pale curved terminal beside the main cabinet at the platform head.
    m.box((px+1.7,py+3.35,pz+.24),(.78,.72,.48),1)
    m.lathe((px+1.7,py+3.35),[(pz+.48,.29),(pz+.59,.32),(pz+.72,.20),(pz+.75,.04)],12,1)
    finish(m,'roof',[metal,pale])
    m=Mesh('Fine roof plant rails and fan rims')
    for yy in [py-2.25,py-.75,py+.75,py+2.25]:
        m.lathe((px-.15,yy),[(pz+.862,.39),(pz+.878,.39)],24,1)
        m.closed_ring((px-.15,yy,pz+.895),.40,.022,0,32,6)
    # Sparse perimeter steelwork and top rails; no invented opaque plant shed.
    for xx in [px-pw/2+.07,px+pw/2-.07]:
        for yy in [py-pd/2+.07,py,py+pd/2-.07]:m.box((xx,yy,pz+.6),(.045,.045,1.2),0)
        for zz in [pz+.18,pz+1.2]:m.box((xx,py,zz),(.045,pd-.10,.045),0)
    for yy in [py-pd/2+.07,py+pd/2-.07]:
        for zz in [pz+.18,pz+1.2]:m.box((px,yy,zz),(pw-.14,.045,.045),0)
    finish(m,'roof',[metal,dark])
    m=Mesh('Micro roof fan guards and cabinet seams')
    for yy in [py-2.25,py-.75,py+.75,py+2.25]:
        for r in [.12,.23,.32]:m.closed_ring((px-.15,yy,pz+.90),r,.007,0,24,4)
        for i in range(4):
            a=math.tau*i/4;m.tube([(px-.15,yy,pz+.905),(px-.15+.37*math.cos(a),yy+.37*math.sin(a),pz+.905)],.009,0,4)
    for yy in [py-1.6,py,py+1.6]:m.box((px+1.85,yy,pz+1.465),(1.70,.018,.008),0)
    finish(m,'roof',[metal])
    m=Mesh('Fine roof vent caps and flashings')
    for x,y in R['vent_caps']:
        m.lathe((x,y),[(deck+.10,.12),(deck+.30,.12),(deck+.32,.23),(deck+.36,.23)],12,0)
    for x,y in R['pipe_cluster']:
        m.lathe((x,y),[(deck+.10,.09),(deck+.58,.09),(deck+.65,.14),(deck+.70,.14)],12,1)
    # Flashing sits above the roof plane and at the foot of the external walls.
    for x in [x0+.38,x1-.38]:m.box((x,(y0+y1)/2,deck+.105),(.16,y1-y0,.010),0)
    finish(m,'roof',[metal,pale])
