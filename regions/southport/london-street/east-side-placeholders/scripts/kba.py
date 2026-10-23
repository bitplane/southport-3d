"""15–17: paired canted upper bays and decorative gables, observed August 2024."""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh
from facades import rect


def build(f):
    w=f.w
    cream=f.mat('KBA pale grey render',(.66,.68,.65))
    trim=f.mat('KBA grey timber',(.36,.40,.39))
    brown=f.mat('KBA reddish window timber',(.13,.065,.045))
    white=f.mat('Shop white lettering',(.87,.88,.84))
    green=f.mat('Yorkshire dark green',(.03,.28,.12))
    dark=f.mat('KBA tile plinth',(.14,.135,.12))
    slate=f.mat('KBA dark slate',(.17,.18,.175))
    holes=[rect(.3,.3,w-.3,3.12)]+[rect(c-1.5,4.15,c+1.5,6.35) for c in [w*.25,w*.75]]
    f.wall('Envelope KBA front',rect(0,0,w,6.6),holes,cream)
    f.enclosed('KBA main',0,w,0,8.5,6.6,cream)
    for c in [w*.25,w*.75]:
        # Canted bays: a broad front light and angled narrow side lights.
        f.window('KBA upper bay front',c,5.25,2.05,2.2,brown,frame=f.frame@Matrix.Translation((0,0,.40)),transom=.28)
        for side in [-1,1]:
            a=(c+side*1.5,0);b=(c+side*1.025,.40)
            dx,dz=b[0]-a[0],b[1]-a[1]
            # Mirror the construction so both face normals point outside.
            if side==1:dx,dz=-dx,-dz
            angle=math.atan2(-dz,dx)
            frame=f.frame@Matrix.Translation(((a[0]+b[0])/2,0,(a[1]+b[1])/2))@Matrix.Rotation(angle,4,'Y')
            f.window('KBA upper bay return',0,5.25,math.hypot(dx,dz),2.2,brown,frame=frame,transom=.28)
        f.box('Trim KBA bay head',(c,6.53,.25),(w/2-.12,.22,.85),trim)
        # The front gable projects beyond the bay and rests on small brackets.
        u0,u1=c-w/4+.10,c+w/4-.10
        f.wall('Envelope KBA gable',[(u0,6.6),(u1,6.6),(c,7.95)],[],cream,front=.65,back=.42)
        m=Mesh('Trim KBA gable timber')
        for a,b in [((u0,6.64,.70),(c,7.95,.70)),((c,7.95,.70),(u1,6.64,.70)),
                    ((c,6.64,.70),(c,7.93,.70)),((c,6.67,.70),(u0+.65,7.15,.70)),
                    ((c,6.67,.70),(u1-.65,7.15,.70))]:m.tube([a,b],.055,sides=4)
        f.finish(m,[trim])
        for x in [u0+.12,u1-.12]:f.box('Trim KBA gable bracket',(x,6.25,.24),(.09,.55,.35),trim)
        f.roof('KBA paired pitch',u0-.10,u1+.10,-.65,8.5,6.6,7.95,slate)
    f.box('Envelope KBA rear extension',(w/2,2.1,-14.5),(w,4.2,12),cream)
    f.box('Roof KBA rear flat',(w/2,4.27,-14.5),(w,.14,12),slate)
    # Shallow shop-window bays flank the inset central entrance.
    for a,b in [(.30,w/2-.8),(w/2+.8,w-.30)]:
        f.window('KBA display',(a+b)/2,1.72,b-a,2.72,trim,transom=.98)
        f.box('Trim KBA shop plinth',((a+b)/2,.2,.1),(b-a,.4,.35),dark)
    f.window('KBA door',w/2,1.58,1.55,2.9,trim,frame=f.frame@Matrix.Translation((0,0,-.30)),mullions=2,transom=1.0)
    f.sign('Yorkshire','YORKSHIRE\nBUILDING SOCIETY',w*.25,3.6,w*.47,.8,white,green)
    f.sign('KBA','KBA FINANCIAL',w*.75,3.6,w*.47,.8,white,dark)
    f.sign('KBA date plaque','1989',w/2,5.9,.5,.24,cream,trim)
