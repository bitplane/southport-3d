"""Independent structural recipe, in pier station/transverse coordinates."""
import json,math
from pathlib import Path
from geometry import Faces
from features import add_features,shelter_gap,SHELTERS
BAY=15.25
Z=3.208
WIDTH=7.951
# Positive transverse is southwest. Four trusses, with the extra cantilever north.
TRUSSES=[WIDTH/2,WIDTH/2-2.386,WIDTH/2-2.386-2.265,WIDTH/2-2.386-2.265-2.288]

def centre(s):
    knots=[(0,1.0),(75,1.0),(500,.6),(710,2.5),(1044,2.5)]
    for (a,v),(b,w) in zip(knots,knots[1:]):
        if s<=b:return v+(w-v)*(s-a)/(b-a)
    return knots[-1][1]

def edge(s,side):
    if s>=75:return side*WIDTH/2
    if side<0:return -3.526 if s<=57 else -3.526+(-WIDTH/2+3.526)*(s-57)/18
    south=14.788-(6.776*s/7.174) if s<7.174 else 7.012 if s<=57 else 7.012+(WIDTH/2-7.012)*(s-57)/18
    return south

def create(config,coarse=False):
    f=Faces();lo,hi=config['stations'];start=lo
    # Geometry stays local to each section, while station rhythms stay global.
    def p(s,t,z):return (s-start,t+centre(s),z)
    def box(name,a,b,mat='blue',part='structure',**kw):
        f.box(name,p(*a),p(*b),mat,part,**kw)
    def tube(name,a,b,r,mat='blue',part='fittings',**kw):f.tube(name,p(*a),p(*b),r,mat,part,**kw)
    def beam(name,a,b,w,d,**kw):f.beam(name,p(*a),p(*b),w,d,**kw)
    # One owner for each walking strip. Rail heads and paint replace deck strips.
    # Two 914 mm gauge rails; narrow flangeway strips are dark solid recess tops.
    strips=[(-WIDTH/2,-1.34,'plank-long'),(-1.34,-1.28,'yellow'),(-1.28,-.499,'plank-cross'),(-.499,-.477,'dark'),(-.477,-.437,'rail'),(-.437,.437,'plank-cross'),(.437,.477,'rail'),(.477,.499,'dark'),(.499,1.28,'plank-cross'),(1.28,1.34,'yellow'),(1.34,WIDTH/2,'plank-long')]
    for a,b,mat in strips:
        # Keep crossfall zero. Draw four station breaks for precise shared seams.
        cuts=sorted({lo,hi,*[v for v in [7.174,57,75,500,710] if lo<v<hi]})
        for i,(s,S) in enumerate(zip(cuts,cuts[1:])):
            A=edge(s,-1) if a==-WIDTH/2 else a;AA=edge(S,-1) if a==-WIDTH/2 else a
            B=edge(s,1) if b==WIDTH/2 else b;BB=edge(S,1) if b==WIDTH/2 else b
            f.face(f'deck {mat} {a} {i}',[p(s,A,Z),p(S,AA,Z),p(S,BB,Z),p(s,B,Z)],mat,'deck',.06,1)
    # Deck slab sides are separate from top, no duplicate section end caps.
    for i,(s,S) in enumerate(zip(cuts,cuts[1:])):
        for side in [-1,1]:
            t,T=edge(s,side),edge(S,side)
            f.face(f'deck fascia {side} {i}',[p(s,t,Z-.14),p(S,T,Z-.14),p(S,T,Z),p(s,t,Z)],'timber','structure',.08)
        f.face(f'deck soffit {i}',[p(s,edge(s,-1),Z-.14),p(s,edge(s,1),Z-.14),p(S,edge(S,1),Z-.14),p(S,edge(S,-1),Z-.14)],'timber','structure',.08)
    # Structural bay centres and four transverse trusses from the published plan.
    bridge=config.get('road_bridge')
    intervals=[(lo,hi)] if not bridge else [(lo,bridge[0]),(bridge[1],hi)]
    stations=[n*BAY for n in range(math.ceil(lo/BAY),math.ceil(hi/BAY)) if not bridge or not bridge[0]-1<n*BAY<bridge[1]+1]
    for st in stations:
        # Foundations are a simple cutoff, not terrain-following pier deck controls.
        base=config.get('column_base_z',-3.4)
        for j,t in enumerate(TRUSSES):
            foot=t+(.25 if j==0 else -.25 if j==3 else 0)
            tube(f'column {st} {j}',(st,foot,base),(st,t,Z-1.05),.089,'blue','structure',segments=4 if coarse else 12,cap=True,cage=.12)
            if not coarse:
                for z in [Z-1.3,base+.55]:tube(f'fine collar {st} {j} {z}',(st,t,z-.045),(st,t,z+.045),.12,'blue','structure',segments=12,cap=False,cage=.08)
        for j,(a,b) in enumerate(zip(TRUSSES,TRUSSES[1:])):
            for z in [base+.5,Z-1.10]:beam(f'cross tie {st} {j} {z}',(st,a,z),(st,b,z),.07,.08,cap=False,cage=.1)
            if not coarse:
                for swap in [False,True]:tube(f'fine column brace {st} {j} {swap}',(st-.025 if swap else st+.025,a,base+.5 if swap else Z-1.14),(st-.025 if swap else st+.025,b,Z-1.14 if swap else base+.5),.0125,'blue','structure',segments=6,cap=False,cage=.05)
        # Transverse deck bearing, ends stop at outer joists.
        beam(f'bearing {st}',(st,-WIDTH/2,Z-.24),(st,WIDTH/2,Z-.24),.15,.17,cap=True,cage=.12)
    # Longitudinal outer trusses remain visually open at every LoD.
    ts=[TRUSSES[0],TRUSSES[-1]] if coarse else TRUSSES
    for j,t in enumerate(ts):
        for k,(begin,end) in enumerate(intervals):
            for z in [Z-.29,Z-1.08]:beam(f'chord {j} {z} {k}',(begin,t,z),(end,t,z),.09,.09,cap=False,cage=.12)
        panel=BAY/(8 if coarse else 16)
        for n in range(math.floor(lo/panel),math.ceil(hi/panel)):
            s,S=max(lo,n*panel),min(hi,(n+1)*panel)
            if bridge and s<bridge[1] and S>bridge[0]:
                if s<bridge[0]:S=bridge[0]
                elif S>bridge[1]:s=bridge[1]
                else:continue
            if S-s<.001:continue
            beam(f'lattice {j} {n}',(s,t,Z-1.035),(S,t,Z-.335),.065,.035,cap=False,cage=.1)
            if not coarse:beam(f'lattice return {j} {n}',(s,t+.045,Z-.335),(S,t+.045,Z-1.035),.045,.025,cap=False,cage=.08)
    # Railing posts: published spacing ~1.8 m. Coarse posts every second station.
    spacing=3.6 if coarse else 1.8
    for side in [-1,1]:
        t=side*(WIDTH/2-.10)
        for n in range(math.ceil(lo/spacing),math.ceil(hi/spacing)):
            s=n*spacing
            if shelter_gap(s,side):continue
            t=edge(s,side)-side*.10
            box(f'rail post {side} {n}',(s-.045,t-.05,Z+.08),(s+.045,t+.05,Z+1.11),cage=.07,part='fittings')
            if not coarse:
                box(f'fine foot {side} {n}',(s-.13,t-.12,Z+.015),(s+.13,t+.12,Z+.07),part='fittings',cage=.05)
                if side<0:
                    for z,h in [(Z+.35,.10),(Z+.66,.13),(Z+.92,.17)]:
                        pts=[(s,t-.058,z+h),(s+.027,t-.058,z),(s,t-.058,z-h),(s-.027,t-.058,z),(s,t-.058,z+h)]
                        for k,(a,b) in enumerate(zip(pts,pts[1:])):tube(f'fine diamond {n} {z} {k}',a,b,.009,'ivory',segments=4,cap=False,cage=.025)
        # North has three blue bars; south over the lake matches, further out pickets.
        horizontal=side<0 or hi<=180
        levels=[.15,.59,1.12] if coarse else ([.20,.44,.70,1.12] if horizontal else [.15,.77,1.12])
        railcuts=sorted(set(cuts+[s for a,b,sign in SHELTERS if sign==side for s in [a-.2,b+.2] if lo<s<hi]))
        for z in levels:
            for i,(a,b) in enumerate(zip(railcuts,railcuts[1:])):
                if shelter_gap((a+b)/2,side):continue
                tube(f'handrail {side} {z} {i}',(a,edge(a,side)-side*.10,Z+z),(b,edge(b,side)-side*.10,Z+z),.038 if z<1 else .052,'ivory' if z>1 else 'blue',segments=4 if coarse else 8,cap=False,cage=.07)
        if not horizontal and not coarse:
            for n in range(math.ceil(lo/.14),math.ceil(hi/.14)):
                s=n*.14
                if shelter_gap(s,side):continue
                if min(s%1.8,1.8-s%1.8)<.07:continue
                tube(f'fine picket {n}',(s,t,Z+.19),(s,t,Z+.73),.011,'blue',segments=4,cap=False,cage=.03)
    # Distinctive paired arches cross in plan, with lantern and crown at the apex.
    for st in [60+n*30.5 for n in range(33) if lo<=60+n*30.5<hi and (not bridge or not bridge[0]<60+n*30.5<bridge[1])]:
        for sign in [-1,1]:
            seg=12 if coarse else 32
            pts=[]
            for i in range(seg+1):
                theta=math.pi*i/seg
                pts.append((st+sign*2.2*math.cos(theta),-3.85*math.cos(theta),Z+5.3*math.sin(theta)))
            for j,(a,b) in enumerate(zip(pts,pts[1:])):tube(f'arch {st} {sign} {j}',a,b,.043,'ivory',segments=4 if coarse else 8,cap=False,cage=.07)
        tube(f'lantern hanger {st}',(st,0,Z+5.32),(st,0,Z+4.84),.02,'blue',segments=6,cap=False,cage=.05)
        tube(f'lantern {st}',(st,0,Z+4.75),(st,0,Z+4.90),.17,'ivory',segments=6 if coarse else 12,cap=True,cage=.12,r2=.23)
        tube(f'lantern cap {st}',(st,0,Z+4.90),(st,0,Z+4.99),.26,'blue',segments=6 if coarse else 12,cap=True,cage=.12,r2=.12)
        if not coarse:
            for sign in [-1,1]:
                pts=[(st,sign*.36*math.sin(i*math.pi/12),Z+5.3+.58*math.sin(i*math.pi/24))for i in range(25)]
                f.path_tube(f'fine crown {st} {sign}',[p(*v) for v in pts],.012,'ivory',segments=6,cage=.03)
    if bridge:
        a,b=bridge
        # Road crossing has through trusses above the boardwalk, keeping the
        # carriageway clear underneath; both pedestrian side strips stay open.
        for side in [-1,1]:
            t=side*1.57
            for h in [.13,1.40]:beam(f'bridge chord {side} {h}',(a,t,Z+h),(b,t,Z+h),.16,.16,cap=True,cage=.14)
            for k in range(16):
                x=a+(b-a)*k/16;X=a+(b-a)*(k+1)/16
                beam(f'bridge diagonal {side} {k}',(x,t,Z+.22),(X,t,Z+1.31),.09,.06,cap=False,cage=.1)
                if not coarse:beam(f'bridge return {side} {k}',(x,t+.07,Z+1.31),(X,t+.07,Z+.22),.07,.05,cap=False,cage=.1)
        for st in [a-.3,b+.3]:
            beam(f'bridge transverse {st}',(st,-WIDTH/2,Z-.25),(st,WIDTH/2,Z-.25),.25,.20,cap=True,cage=.14)
            for side in [-1,1]:
                box(f'bridge bearing {st} {side}',(st-.35,side*3.1-.4,-1.8),(st+.35,side*3.1+.4,Z-.36),'stone','structure',cage=.15)
    add_features(f,config,coarse,p,edge,Z)
    return f
