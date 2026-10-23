import math
from mathutils import Matrix
from southport3d.geometry import Mesh, face_matrix
from southport3d.planar import subtract


def panel(name,width,height,holes):
    parts=[[(0,0),(width,0),(width,height),(0,height)]]
    for a,b,c,d in holes:
        cut=[(a,b),(c,b),(c,d),(a,d)]
        parts=[piece for poly in parts for piece in subtract(poly,cut)]
    m=Mesh(name)
    for poly in parts:m.outline(poly,-.30,0)
    return m


def window(name,u,z,w,h,colour,glass,finish,frame,bars=False):
    m=Mesh('Fixture '+name)
    m.box((u,z,-.16),(w,h,.04),1)
    for x in [u-w/2+.035,u+w/2-.035]:m.box((x,z,-.06),(.07,h,.12))
    for y in [z-h/2+.035,z+h/2-.035,z+h*.24]:m.box((u,y,-.06),(w-.14,.07,.12))
    m.box((u,z,-.06),(.045,h-.14,.12))
    if bars:
        for j in range(1,6):m.box((u-w/2+j*w/6,z,.055),(.025,h,.025),2)
        for y in [z-h*.25,z+h*.25]:m.box((u,y,.055),(w,.025,.025),2)
    finish(m,mats=[colour,glass,colour],transform=frame)


def stairs(name,u,landing,width,height,run,frame,finish,metal):
    m=Mesh('Fixture '+name+' treads')
    count=math.ceil(height/.19)
    for i in range(count):
        # Stair runs parallel to facade, rising towards +u.
        m.box((u-run+(i+.5)*run/count,(i+1)*height/count,landing),
              (run/count,.065,width))
    m.box((u+.35,height,landing),(.70,.10,width))
    finish(m,mats=[metal],transform=frame)
    m=Mesh('Fine '+name+' rails')
    for depth in [landing-width/2,landing+width/2]:
        m.tube([(u-run,1,depth),(u,height+1,depth),(u+.70,height+1,depth)],.025,sides=6)
        m.tube([(u-run,.08,depth),(u,height,depth)],.075,sides=6)
        for t in [0,.33,.66,1]:
            x=u-run+t*run;y=t*height
            m.tube([(x,y,depth),(x,y+1,depth)],.025,sides=6)
        m.tube([(u+.70,height,depth),(u+.70,height+1,depth)],.025,sides=6)
    finish(m,mats=[metal],transform=frame)


def build(D,R,finish,brick,cap,dark,glass,metal,cream):
    f=face_matrix((D['x_near'],D['rear_y'],D['base_z']),(1,0,0))
    width=D['front_y']-D['rear_y']-.45
    # Court-facing side wall: upper windows, two collection doors and roller bay.
    windows=[(8,8.9,1.9,1.55),(13,8.9,1.8,1.55),(18,8.9,1.9,1.55),
             (22,8.9,1.8,1.55),(27.5,8.4,1.9,1.55),(21.6,4.0,1.0,1.45)]
    doors=[(14.0,.7,2.2,2.7),(16.8,.7,1.65,2.7),(2.0,.1,3.2,4.6)]
    holes=[(x-w/2,z-h/2,x+w/2,z+h/2) for x,z,w,h in windows]
    holes += [(x-w/2,z,x+w/2,z+h) for x,z,w,h in doors]
    finish(panel('Envelope brick court side',width,D['roof_level'],holes),mats=[brick],transform=f)
    for i,(x,z,w,h) in enumerate(windows):
        window('BHF court window '+str(i),x,z,w,h,cream if i<2 else dark,glass,finish,f,bars=i>=2)
        m=Mesh('Trim court lintel');m.box((x,z+h/2+.13,.02),(w+.28,.26,.18));finish(m,mats=[cap],transform=f)
    for i,(x,z,w,h) in enumerate(doors):
        m=Mesh('Fixture collection door '+str(i));m.box((x,z+h/2,-.22),(w,h,.08));finish(m,mats=[dark if i<2 else metal],transform=f)
        m=Mesh('Trim collection doorway');m.box((x,z+h+.13,.02),(w+.3,.26,.18));finish(m,mats=[cap],transform=f)
    # Raised paired landings and three shallow steps, railings clear of door swing.
    m=Mesh('Fixture collection landings')
    for x,z,w,h in doors[:2]:
        m.box((x,.59,.68),(w+.18,.22,1.65))
        for j in range(3):m.box((x,.17+j*.17,2.1-j*.30),(w+.18,.17,.30))
    finish(m,mats=[cap],transform=f)
    m=Mesh('Fine collection handrails')
    for x in [12.8,15.2,15.85,17.75]:
        m.tube([(x,1.7,.1),(x,1.7,1.5),(x,1.05,2.45)],.035,sides=8)
        for depth,z in [(1.4,.7),(2.35,.1)]:m.tube([(x,z,depth),(x,z+1,depth)],.035,sides=8)
    # Rolling shutter ribs and long black rainwater pipes remain detail features.
    for j in range(48):m.box((2,.15+j*.093,-.165),(3.16,.018,.025))
    for x in [5,11,15.55,23,29,34]:m.tube([(x,.1,.14),(x,D['roof_level']-.1,.14)],.055,sides=8)
    finish(m,mats=[dark],transform=f)
    # The two reported roof forms continue down the wall as brick shafts.
    # Their top-down centres are retained; bodies now meet the court elevation.
    for i,housing in enumerate(R['edge_housings'][:2]):
        x,y=housing['centre'];w,d=housing['size'];top=D['roof_level']+housing['height']
        u=y-D['rear_y'];depth=D['x_near']-(x-w/2)
        m=Mesh('Envelope integrated court shaft '+str(i))
        m.box((u,top/2,.08-depth/2),(d,top,depth))
        finish(m,mats=[brick],transform=f)
        m=Mesh('Roof integrated shaft coping '+str(i))
        m.box((u,top+.06,.08-depth/2),(d+.16,.12,depth+.16))
        finish(m,'roof',[cap],f)
    # Low utility enclosure and pale double doors along the rear part of court.
    m=Mesh('Envelope court utility enclosure');m.box((8.2,1.4,.75),(8.4,2.8,1.5));finish(m,mats=[brick],transform=f)
    m=Mesh('Fixture court utility doors')
    for u in [6.0,10.5]:
        m.box((u,1.15,1.515),(1.7,2.3,.03))
    finish(m,mats=[cap],transform=f)
