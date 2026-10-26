"""Pier-head platform and shedkm pavilion, observed exterior, estimated heights."""
import math

def add_head(f,config,coarse,p,Z):
    lo,hi=config['stations']
    def face(name,points,mat='ivory',part='structure',**kw):f.face(name,[p(*v) for v in points],mat,part,**kw)
    def box(name,a,b,mat='ivory',part='structure',**kw):f.box(name,p(*a),p(*b),mat,part,**kw)
    def tube(name,a,b,r,mat='blue',part='fittings',**kw):f.tube(name,p(*a),p(*b),r,mat,part,**kw)
    def beam(name,a,b,w,d,mat='ivory',part='structure',**kw):f.beam(name,p(*a),p(*b),w,d,mat,part,**kw)
    def rectangle(name,a,b,y,Y):
        face(name,[(a,y,Z),(b,y,Z),(b,Y,Z),(a,Y,Z)],'plank-long','deck',cage=.1)
    def rail(name,a,b):
        distance=math.dist(a,b);n=max(1,math.ceil(distance/(3.6 if coarse else 1.8)))
        for i in range(n):
            x=a[0]+(b[0]-a[0])*i/n;y=a[1]+(b[1]-a[1])*i/n
            box(name+f' post {i}',(x-.045,y-.045,Z+.04),(x+.045,y+.045,Z+1.1),'blue','fittings',cage=.07)
        for h in [.22,.66,1.12]:tube(name+f' rail {h}',(*a,Z+h),(*b,Z+h),.04,'ivory' if h>1 else 'blue',segments=4 if coarse else 8,cap=False,cage=.07)
    if lo<=960<hi:
        # White utility cabin on a side platform; this is not a third cream shelter.
        a,b=951.5,974.5;y,Y=3.9755,6.45
        rectangle('utility platform',a,b,y,Y)
        box('utility cabin',(954.0,4.3,Z),(958.0,6.2,Z+2.35),'ivory',omit=('bottom',),cage=.12)
        box('utility roof',(953.9,4.2,Z+2.37),(958.1,6.3,Z+2.5),'roof',cage=.1)
        for x in [954.3,955.5,956.7]:box(f'utility hatch {x}',(x,4.24,Z+.9),(x+.85,4.28,Z+1.95),'pale-panel',cage=.05)
        for a0,b0 in [((a,y),(a,Y)),((a,Y),(b,Y))]:rail('utility perimeter '+str(a0),a0,b0)
    if lo<974 or lo>975:return
    # Rectangular side platform carries the 45 m long pavilion. Its floor remains
    # level and independent of the sand/water below.
    a,b=974.5,1020.5;near,far=3.9755,25.85
    rectangle('pavilion platform',a,b,near,far)
    face('pavilion soffit',[(a,near,Z-.2),(a,far,Z-.2),(b,far,Z-.2),(b,near,Z-.2)],'blue',cage=.12)
    for x in [a,b]:face(f'pavilion end fascia {x}',[(x,near,Z-.2),(x,far,Z-.2),(x,far,Z),(x,near,Z)],'blue',cage=.12)
    face('pavilion sea fascia',[(a,far,Z-.2),(b,far,Z-.2),(b,far,Z),(a,far,Z)],'blue',cage=.12)
    for x in [a+1+i*7.5 for i in range(7)]:
        for y in [7.0,16.0,24.5]:
            tube(f'pavilion pile {x} {y}',(x,y,-3.4),(x,y,Z-.32),.11,'blue','structure',segments=4 if coarse else 12,cap=True,cage=.14)
        for y,Y in [(7.,16.),(16.,24.5)]:
            beam(f'pavilion crosshead {x} {y}',(x,y,Z-.35),(x,Y,Z-.35),.18,.20,'blue',cap=False,cage=.14)
            if not coarse:
                for sign in [-1,1]:tube(f'fine pavilion brace {x} {y} {sign}',(x+sign*.03,y,-2.8 if sign<0 else Z-.6),(x+sign*.03,Y,Z-.6 if sign<0 else -2.8),.018,'blue','structure',segments=6,cap=False,cage=.05)
    # Roof is shallow concave across its width, with rounded exposed edges.
    def roof(y):return Z+3.65+.0058*(y-15.0)**2
    y0,y1=6.5,26.0;xs=[a-.4,b+.4];ys=[y0+(y1-y0)*i/(6 if coarse else 16)for i in range((6 if coarse else 16)+1)]
    for j,(y,Y) in enumerate(zip(ys,ys[1:])):
        face(f'pavilion roof {j}',[(xs[0],y,roof(y)),(xs[1],y,roof(y)),(xs[1],Y,roof(Y)),(xs[0],Y,roof(Y))],'silver',cage=.15)
        face(f'pavilion roof soffit {j}',[(xs[0],Y,roof(Y)-.19),(xs[1],Y,roof(Y)-.19),(xs[1],y,roof(y)-.19),(xs[0],y,roof(y)-.19)],'silver',cage=.15)
        for x in xs:face(f'pavilion roof edge {x} {j}',[(x,y,roof(y)-.19),(x,Y,roof(Y)-.19),(x,Y,roof(Y)),(x,y,roof(y))],'ivory',cage=.12)
    for y in [y0,y1]:tube(f'pavilion rolled edge {y}',(xs[0]-.02,y,roof(y)-.08),(xs[1]+.02,y,roof(y)-.08),.15,'silver','structure',segments=6 if coarse else 16,cap=True,cage=.14)
    # Inclined front and southwest glass elevation. Window panels own the gaps
    # between real frame bars instead of sitting coplanar on a complete wall.
    front0,front1=11.5,9.65;rear0,rear1=24.5,25.6;bottom=Z+.08
    bays=30  # Fixed facade rhythm; extra detailed fittings do not grow this envelope.
    for side,(y,Y) in enumerate([(front0,front1),(rear0,rear1)]):
        top=roof(Y)-.23
        for i in range(bays):
            x=a+.8+(b-a-1.6)*i/bays;X=a+.8+(b-a-1.6)*(i+1)/bays
            material='glass' if side==1 or 989<x<1006 else 'pavilion-blue'
            # Full cladding panels are explicit facade surfaces, with seams/frames
            # proud of them. End closures below join exactly to these planes.
            panel_top_y=y if side==0 and material=='glass' else Y
            face(f'pavilion facade {side} {i}',[(x,y,bottom),(X,y,bottom),(X,panel_top_y,top),(x,panel_top_y,top)],material,cage=.12)
            if not coarse or material=='glass':
                beam(f'pavilion mullion {side} {i}',(x,y-.035 if side==0 else y+.035,bottom),(x,panel_top_y-.035 if side==0 else panel_top_y+.035,top),.045,.045,'dark' if material=='glass' else 'trim',cap=False,cage=.06)
        if side==1:
            for h in [1.1,2.85]:
                t=h/(top-bottom);yy=y+(Y-y)*t+.045
                beam(f'pavilion transom {h}',(a+.8,yy,bottom+h),(b-.8,yy,bottom+h),.05,.05,'dark',cap=False,cage=.06)
    # Recessed upright entrance glazing within the inclined blue outer shell.
    for x in [990.1,1006.38]:
        face(f'pavilion glass reveal {x}',[(x,front0,bottom),(x,front1,roof(front1)-.23),(x,front0,roof(front1)-.23)],'dark',cage=.12)
    for x in [995.7,997.2,998.7]:
        box(f'pavilion door jamb {x}',(x-.035,front0-.075,Z+.09),(x+.035,front0-.015,Z+2.42),'dark','fittings',cage=.06,omit=('top',))
    box('pavilion door lintel',(995.665,front0-.075,Z+2.42),(998.735,front0-.015,Z+2.49),'dark','fittings',cage=.06,omit=('bottom',))
    if not coarse:
        for x in [996.98,997.42]:tube(f'pavilion door handle {x}',(x,front0-.13,Z+.95),(x,front0-.13,Z+1.38),.018,'silver',segments=8,cap=True,cage=.04)
    face('pavilion entrance sign',[(995.5,front0-.09,Z+2.60),(999.,front0-.09,Z+2.60),(999.,front0-.09,Z+3.10),(995.5,front0-.09,Z+3.10)],'pavilion-sign','fittings',cage=.1)
    for x in [a+.8,b-.8]:
        topfront=roof(front1)-.23;toprear=roof(rear1)-.23
        face(f'pavilion end wall {x}',[(x,front0,bottom),(x,rear0,bottom),(x,rear1,toprear),(x,front1,topfront)],'pale-panel',cage=.12)
    # White V columns exposed on the canopy frontage; main architectural identity.
    for x in [a+4+i*7.5 for i in range(6)]:
        box(f'pavilion V pedestal {x}',(x-.36,8.36,Z),(x+.36,8.84,Z+.34),'ivory','structure',omit=('bottom',),cage=.12)
        for sign in [-1,1]:beam(f'pavilion V column {x} {sign}',(x+sign*.16,8.6,Z+.28),(x+sign*3.2,7.5,roof(7.5)-.22),.15,.20,'ivory',cap=True,cage=.16)
    for x in [a+4,b-4]:
        box(f'pavilion end pedestal {x}',(x-.24,16.64,Z),(x+.24,17.36,Z+.34),'ivory','structure',omit=('bottom',),cage=.12)
        for sign in [-1,1]:beam(f'pavilion end V {x} {sign}',(x,17.+sign*.16,Z+.28),(x,17.+sign*7.0,roof(17.+sign*7)-.22),.14,.20,'ivory',cap=True,cage=.16)
    # Four squat rectangular extract cowls seen in architect and aerial views.
    for x in [a+3.0,a+5.5,b-5.5,b-3.0]:
        z=roof(9.1);box(f'pavilion vent {x}',(x,8.6,z+.03),(x+1.0,9.7,z+.66),'dark',omit=('bottom',),cage=.12)
    # Pier-head T and rounded seaward nose, partitioned around the existing deck.
    for y,Y in [(-16.3,-3.9755),(3.9755,15.8)]:rectangle('head arm '+str(y),1028,1038,y,Y)
    n=4 if coarse else 24;arc=[(1038+5.8*math.cos(-math.pi/2+i*math.pi/n),5.8*math.sin(-math.pi/2+i*math.pi/n))for i in range(n+1)]
    for i,(v,w) in enumerate(zip(arc,arc[1:])):
        face(f'head nose {i}',[(1038,0,Z),(*v,Z),(*w,Z)],'plank-cross','deck',cage=.1)
        face(f'head nose fascia {i}',[(*v,Z-.2),(*w,Z-.2),(*w,Z),(*v,Z)],'blue',cage=.1)
        rail(f'head nose {i}',v,w)
    paths=[((1028,-3.9755),(1028,-16.3)),((1028,-16.3),(1038,-16.3)),((1038,-16.3),(1038,-5.8)),((1038,5.8),(1038,15.8)),((1038,15.8),(1028,15.8)),((1028,15.8),(1028,3.9755))]
    for i,(v,w) in enumerate(paths):rail(f'head perimeter {i}',v,w)
    for x in [1029,1036]:
        for y in [-15.,-8.,8.,14.]:tube(f'head pile {x} {y}',(x,y,-3.4),(x,y,Z-.22),.11,'blue','structure',segments=4 if coarse else 12,cap=True,cage=.14)
    tube('head flagpole',(1039,0,Z),(1039,0,Z+7.0),.065,'ivory',segments=6 if coarse else 12,cap=True,cage=.1,r2=.035)
    if not coarse:
        for x,y in [(1033,-12),(1033,11)]:
            tube(f'view telescope pedestal {y}',(x,y,Z),(x,y,Z+1.2),.06,'blue',segments=12,cap=True,cage=.1)
            tube(f'view telescope {y}',(x-.26,y,Z+1.32),(x+.26,y,Z+1.5),.12,'trim',segments=12,cap=True,cage=.1)
