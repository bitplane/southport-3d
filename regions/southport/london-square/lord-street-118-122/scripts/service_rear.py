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
    for depth in [landing-width/2,landing+width/2]:
        m.tube([(u-run,.08,depth),(u,height,depth)],.075,sides=6)
        m.box((u+.65,height/2,depth),(.07,height,.07))
    finish(m,mats=[metal],transform=frame)
    m=Mesh('Fine '+name+' rails')
    for depth in [landing-width/2,landing+width/2]:
        m.tube([(u-run,1,depth),(u,height+1,depth),(u+.70,height+1,depth)],.025,sides=6)
        for t in [0,.33,.66,1]:
            x=u-run+t*run;y=t*height
            m.tube([(x,y,depth),(x,y+1,depth)],.025,sides=6)
        m.tube([(u+.70,height,depth),(u+.70,height+1,depth)],.025,sides=6)
    finish(m,mats=[metal],transform=frame)


def build(D,finish,brick,dark,glass,metal,cream,roofmat):
    x0,x1=D['x_far'],D['x_near'];width=x1-x0;z0=D['base_z']
    upper=face_matrix((x0,D['rear_y'],z0),(0,-1,0))
    f=face_matrix((x0,-49.0,z0),(0,-1,0))
    # Broad service annex with flat roof below the original upper rear storey.
    openings=[]
    windows=[(2.5,5.25,1.25,1.5),(5.1,5.25,1.35,1.5),(7.6,5.25,1.35,1.5),
             (12.9,5.25,1.45,1.5),(15.5,5.25,1.55,1.5),(17.5,5.25,1.25,1.5),
             (2.3,2.4,1.4,.85),(7.5,2.3,1.45,.85),(14.8,2.4,1.6,.85),(17.2,2.4,1.45,.85)]
    doors=[(.65,3.6,1.1,2.5),(9.7,3.6,1.05,2.5),(4.4,0,1.05,2.65),(6.4,0,1.05,2.65),(12.9,0,1.05,2.65)]
    for x,z,w,h in windows:openings.append((x-w/2,z-h/2,x+w/2,z+h/2))
    for x,z,w,h in doors:openings.append((x-w/2,z,x+w/2,z+h))
    finish(panel('Envelope service annex rear',width,7.0,openings),mats=[brick],transform=f)
    for i,(x,z,w,h) in enumerate(windows):window('service annex window '+str(i),x,z,w,h,cream if x<11 else dark,glass,finish,f,bars=i==0)
    for i,(x,z,w,h) in enumerate(doors):
        m=Mesh('Fixture service rear door '+str(i));m.box((x,z+h/2,-.16),(w,h,.08));finish(m,mats=[dark if i in [0,2] else metal],transform=f)
        m=Mesh('Trim service door lintel');m.box((x,z+h+.06,.03),(w+.20,.12,.14));finish(m,mats=[cream],transform=f)
    # Annex sides close against the original rear wall, not overlapping it.
    m=Mesh('Envelope service annex returns')
    for x in [x0+.15,x1-.15]:m.box((x,-45.25,z0+3.5),(.30,7.5,7.0))
    finish(m,mats=[brick])
    m=Mesh('Roof service annex');m.box(((x0+x1)/2,-45.1,z0+7.0),(width,7.8,.18));finish(m,'roof',[roofmat])
    # Exposed upper rear lights, doors and downpipes from the Glebe Place view.
    upper_windows=[(2.1,8.3,1.1,1.0),(4.7,8.3,1.2,.65),(7.2,8.3,1.1,.65),(9.2,8.3,1.1,.65),(14.0,8.3,1.15,.65),(16.4,8.3,1.15,.65)]
    holes=[(x-w/2,z-h/2,x+w/2,z+h/2) for x,z,w,h in upper_windows]+[(11,7.1,12,9.1)]
    finish(panel('Envelope service upper rear',width,D['parapet_top'],holes),mats=[brick],transform=upper)
    for i,(x,z,w,h) in enumerate(upper_windows):window('upper rear window '+str(i),x,z,w,h,cream if x<10 else dark,glass,finish,upper)
    m=Mesh('Fixture upper rear door');m.box((11.5,8.1,-.16),(1,2,.08));finish(m,mats=[dark],transform=upper)
    stairs('service west stair',0,0,.85,3.6,3.6,f@Matrix.Translation((.65,0,.75))@Matrix.Rotation(math.pi/2,4,'Y'),finish,dark)
    stairs('service central stair',9.4,.9,.95,3.6,4.2,f,finish,metal)
    # Condensers, visible round fan faces, and sparse external pipework.
    m=Mesh('Fixture service condensers')
    for x,z in [(2.0,6.45),(3.9,3.2),(6.2,4.1),(10.7,2.7)]:m.box((x,z,.35),(1.05,.75,.60))
    finish(m,mats=[cream],transform=f)
    m=Mesh('Fine service fan faces')
    for x,z in [(2.0,6.45),(3.9,3.2),(6.2,4.1),(10.7,2.7)]:
        m.outline([(x+.28*math.cos(j*math.tau/24),z+.28*math.sin(j*math.tau/24)) for j in range(24)],.655,.67)
    for x in [3.2,5.8,11.2]:m.tube([(x,.1,.12),(x,6.9,.12)],.045,sides=8)
    m.tube([(0,6.1,.65),(.45,6.1,.65),(.75,6.5,.65),(.75,7.5,.65)],.20,sides=12)
    finish(m,mats=[dark],transform=f)
