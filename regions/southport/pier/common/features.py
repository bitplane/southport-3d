"""Observed pier furnishings and cream glazed wind shelters."""
import math
SHELTERS=[(281.2,297.9,-1),(692.0,709.5,-1),(951.5,966.5,1)]

def shelter_gap(s,side):return any(a-.2<=s<=b+.2 and sign==side for a,b,sign in SHELTERS)

def add_features(f,config,coarse,p,edge,Z):
    lo,hi=config['stations']
    def box(name,a,b,mat='blue',part='fittings',**kw):f.box(name,p(*a),p(*b),mat,part,**kw)
    def tube(name,a,b,r,mat='blue',part='fittings',**kw):f.tube(name,p(*a),p(*b),r,mat,part,**kw)
    def beam(name,a,b,w,d,mat='ivory',part='fittings',**kw):f.beam(name,p(*a),p(*b),w,d,mat,part,**kw)
    def bench(st,t,side,length=1.9):
        for s in [st-length*.36,st+length*.36]:
            box(f'bench foot {s} {t}',(s-.055,t-.22,Z),(s+.055,t+.22,Z+.37),'blue',omit=('bottom',),cage=.08)
            beam(f'bench back support {s} {t}',(s,t+side*.19,Z+.32),(s,t+side*.28,Z+.97),.045,.055,cage=.07)
        if coarse:
            box(f'bench seat {st} {t}',(st-length/2,t-.23,Z+.39),(st+length/2,t+.23,Z+.45),'timber',cage=.1)
            box(f'bench back {st} {t}',(st-length/2,t+side*.21-.035,Z+.59),(st+length/2,t+side*.21+.035,Z+.91),'timber',cage=.1)
        else:
            for j in range(5):
                y=t-.23+j*.095;box(f'bench slat {st} {t} {j}',(st-length/2,y,Z+.39),(st+length/2,y+.077,Z+.45),'timber',cage=.07)
            for j in range(3):
                z=Z+.58+j*.12;box(f'bench back slat {st} {t} {j}',(st-length/2,t+side*.21-.035,z),(st+length/2,t+side*.21+.035,z+.09),'timber',cage=.07)
    for st in [32+n*30.5 for n in range(32) if lo<=32+n*30.5<hi]:
        side=1 if int(st//30.5)%2 else -1
        if shelter_gap(st,side):continue
        t=edge(st,side)-side*.52
        bench(st,t,side)
        if not coarse:
            tube(f'bin body {st}',(st+2.6,t,Z+.05),(st+2.6,t,Z+.83),.29,'dark',segments=12,cap=True,cage=.1)
            for h in [.12,.72]:tube(f'fine bin band {st} {h}',(st+2.6,t,Z+h),(st+2.6,t,Z+h+.025),.296,'gold',segments=12,cap=False,cage=.04)
            tube(f'bin lid {st}',(st+2.6,t,Z+.86),(st+2.6,t,Z+.97),.31,'dark',segments=12,cap=True,r2=.23,cage=.1)
    for a,b,side in SHELTERS:
        if not lo<=(a+b)/2<hi:continue
        near=edge((a+b)/2,side);far=near+side*4.85;Y0,Y1=sorted([near,far]);mid=(near+far)/2
        # Adjacent extension owns its own walking top, never overlaying the main deck.
        f.face(f'shelter deck {a}',[p(a,Y0,Z),p(b,Y0,Z),p(b,Y1,Z),p(a,Y1,Z)],'plank-long','deck',.1)
        for y in [Y0,Y1]:
            if abs(y-near)<1e-4:continue
            f.face(f'shelter fascia {a} {y}',[p(a,y,Z-.2),p(b,y,Z-.2),p(b,y,Z),p(a,y,Z)],'blue','structure',.12)
        for st in [a,b]:
            tube(f'shelter column {st}',(st,far,-3.4),(st,far,Z-.2),.12,'blue','structure',segments=4 if coarse else 12,cap=True,cage=.14)
            for y in [Y0+.15,Y1-.15]:box(f'shelter post {st} {y}',(st+.10,y-.05,Z),(st+.20,y+.05,Z+2.25),'ivory',cage=.1)
        # Back-to-back seating along a glazed spine; four broad bays preserve openness.
        ends=[a+.25+(b-a-.5)*i/4 for i in range(5)]
        for k,(s,S) in enumerate(zip(ends,ends[1:])):
            if not coarse:
                for sign in [-1,1]:bench((s+S)/2,mid+sign*.33,sign,(S-s)-.18)
            else:
                for sign in [-1,1]:box(f'shelter bench {a} {k} {sign}',(s,mid+sign*.36-.23,Z+.40),(S,mid+sign*.36+.23,Z+.46),'timber',cage=.1)
            box(f'shelter lower spine {a} {k}',(s,mid-.045,Z+.5),(S,mid+.045,Z+1.05),'ivory',cage=.1)
            f.face(f'shelter glazing {a} {k}',[p(s+.055,mid,Z+1.05),p(S-.055,mid,Z+1.05),p(S-.055,mid,Z+2.15),p(s+.055,mid,Z+2.15)],'glass','fittings',.06)
        for s in ends:
            box(f'shelter spine post {s}',(s-.055,mid-.065,Z),(s+.055,mid+.065,Z+2.3),'ivory',cage=.1)
        # Hipped shallow metal roof with open-front valance, confirmed in Street View.
        x0,x1=a-.2,b+.2;y0,y1=Y0-.2,Y1+.2;z=Z+2.35;ridge=Z+3.0;hip=2.2
        v=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),(x0+hip,mid,ridge),(x1-hip,mid,ridge)]
        for k,ids in enumerate([(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]):f.face(f'shelter roof {a} {k}',[p(*v[i])for i in ids],'roof','structure',.12)
        for y in [y0,y1]:
            box(f'shelter valance {a} {y}',(x0,y-.04,z-.21),(x1,y+.04,z-.03),'ivory',cage=.1)
            if not coarse:
                for n in range(int((x1-x0)/.22)):
                    x=x0+n*.22+.03
                    f.face(f'fine shelter tooth {a} {y} {n}',[p(x,y-.045,z-.21),p(x+.17,y-.045,z-.21),p(x+.11,y-.045,z-.32),p(x+.06,y-.045,z-.32)],'ivory','fittings',.04)
        # Three exposed platform edges, with the front intentionally open to pier.
        for s in [a,b]:
            for h in [.24,.63,1.12]:tube(f'shelter end rail {a} {s} {h}',(s,near,Z+h),(s,far,Z+h),.04,'ivory' if h>1 else 'blue',segments=4 if coarse else 8,cap=False,cage=.07)
        for h in [.24,.63,1.12]:tube(f'shelter rear rail {a} {h}',(a,far,Z+h),(b,far,Z+h),.04,'ivory' if h>1 else 'blue',segments=4 if coarse else 8,cap=False,cage=.07)
