"""Marine Drive forecourt kiosk: hipped roof, cream panels and side access."""
import math

def add_kiosk(f,config,coarse,p,Z):
    if not config.get('road_bridge'):return
    a,b=478.6,492.;near,far=3.9755,8.95;mid=(near+far)/2
    def box(name,aa,bb,mat='ivory',part='fittings',**kw):f.box(name,p(*aa),p(*bb),mat,part,**kw)
    def beam(name,aa,bb,w,d,mat='ivory',part='fittings',**kw):f.beam(name,p(*aa),p(*bb),w,d,mat,part,**kw)
    def face(name,verts,mat='ivory',part='fittings',**kw):f.face(name,[p(*v)for v in verts],mat,part,**kw)
    face('kiosk platform',[(a,near,Z),(b,near,Z),(b,far,Z),(a,far,Z)],'plank-long','deck',cage=.1)
    # Visible broad wall and closed seaward end, based on 2011/2022 Street View.
    for y in [near,far]:face(f'kiosk wall {y}',[(a,y,Z),(b,y,Z),(b,y,Z+2.48),(a,y,Z+2.48)],'ivory','structure',cage=.1)
    for x in [a,b]:face(f'kiosk end {x}',[(x,near,Z),(x,far,Z),(x,far,Z+2.48),(x,near,Z+2.48)],'ivory','structure',cage=.1)
    for x in [a,b]:
        for y in [near,far]:box(f'kiosk corner {x} {y}',(x-.045,y-.045,Z+.02),(x+.045,y+.045,Z+2.5),'trim',cage=.07)
    v=[(a-.2,near-.2,Z+2.53),(b+.2,near-.2,Z+2.53),(b+.2,far+.2,Z+2.53),(a-.2,far+.2,Z+2.53),(a+2.4,mid,Z+3.8),(b-2.4,mid,Z+3.8)]
    for k,ix in enumerate([(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]):face(f'kiosk hip {k}',[v[i]for i in ix],'roof','structure',cage=.15)
    if not coarse:
        for x in [a+.9,a+4.2,b-1.7]:
            # Applied boards have real thickness, so they own a separate outer face.
            box(f'kiosk sign board {x}',(x,near-.075,Z+1.1),(x+1.1,near-.035,Z+2.0),'kiosk-sign',cage=.07)
        for x in [a+1.6,a+4.8,a+8.0,a+11.2]:
            # Observed picnic tables opposite the kiosk, with crossed timber legs.
            t=-2.55
            for X in [x-.55,x+.55]:
                for sign in [-1,1]:beam(f'picnic leg {x} {X} {sign}',(X+sign*.05,t-sign*.64,Z),(X+sign*.05,t+sign*.2,Z+.72),.075,.075,'timber',cage=.1)
            box(f'picnic table {x}',(x-.85,t-.36,Z+.72),(x+.85,t+.36,Z+.79),'timber',cage=.1)
            for side in [-1,1]:box(f'picnic seat {x} {side}',(x-.85,t+side*.67-.14,Z+.40),(x+.85,t+side*.67+.14,Z+.46),'timber',cage=.1)
    # Seaward stair landing is separately walkable below the pier. Exact riser
    # count is an estimate from imagery and a 4.2 m local level difference.
    x0,x1=494.,496.;y0=3.9755;bottom=-1.0;steps=24;tread=.27;rise=(Z-bottom)/steps
    for i in range(steps):
        y=y0+i*tread;z=Z-i*rise
        face(f'kiosk stair tread {i}',[(x0,y,z),(x1,y,z),(x1,y+tread,z),(x0,y+tread,z)],'stone','deck',cage=.07)
        face(f'kiosk stair riser {i}',[(x0,y+tread,z-rise),(x1,y+tread,z-rise),(x1,y+tread,z),(x0,y+tread,z)],'stone','structure',cage=.07)
    for x in [x0,x1]:
        beam(f'kiosk stair handrail {x}',(x,y0,Z+.95),(x,y0+steps*tread,bottom+.95),.05,.05,'blue',cage=.07)
        for i in range(0,25,4):beam(f'kiosk stair post {x} {i}',(x,y0+i*tread,Z-i*rise),(x,y0+i*tread,Z-i*rise+.95),.045,.045,'blue',cage=.07,cap=False)
