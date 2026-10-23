"""15–17: paired canted upper bays and decorative gables, observed August 2024."""
import math
import bpy
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
    holes=[rect(.3,.3,w-.3,3.12)]+[rect(c-1.25,4.15,c+1.25,5.75) for c in [w*.25,w*.75]]
    f.wall('Envelope KBA front',rect(0,0,w,5.95),holes,cream)
    f.enclosed('KBA main',0,w,0,8.5,5.95,cream)
    # Orbit evidence shows a common transverse roof behind the two projecting
    # front gables, not two independent full-depth parallel roofs.
    main=f.roof('KBA main hip',0,8.5,0,w,5.95,7.5,slate,hip=1.0)
    main.matrix_world=f.frame@Matrix.Translation((0,0,-8.5))@Matrix.Rotation(-math.pi/2,4,'Y')
    for c in [w*.25,w*.75]:
        # Canted bays: a broad front light and angled narrow side lights.
        f.window('KBA upper bay front',c,4.95,1.7,1.6,brown,frame=f.frame@Matrix.Translation((0,0,.40)),transom=.28)
        for side in [-1,1]:
            a=(c+side*1.25,0);b=(c+side*.85,.40)
            dx,dz=b[0]-a[0],b[1]-a[1]
            # Mirror the construction so both face normals point outside.
            if side==1:dx,dz=-dx,-dz
            angle=math.atan2(-dz,dx)
            frame=f.frame@Matrix.Translation(((a[0]+b[0])/2,0,(a[1]+b[1])/2))@Matrix.Rotation(angle,4,'Y')
            f.window('KBA upper bay return',0,4.95,math.hypot(dx,dz),1.6,brown,frame=frame,transom=.28)
        f.box('Trim KBA bay sill',(c,4.13,.17),(2.58,.12,.76),trim)
        f.box('Trim KBA bay head',(c,5.88,.25),(w*.4+.15,.22,.85),trim)
        # The front gable projects beyond the bay and rests on small brackets.
        u0,u1=c-w*.20,c+w*.20
        f.wall('Envelope KBA gable',[(u0,5.95),(u1,5.95),(c,7.15)],[],cream,front=.65,back=.42)
        m=Mesh('Trim KBA gable timber')
        for a,b in [((u0,5.99,.70),(c,7.15,.70)),((c,7.15,.70),(u1,5.99,.70)),
                    ((c,5.99,.70),(c,7.13,.70)),((c,6.02,.70),(u0+.65,6.40,.70)),
                    ((c,6.02,.70),(u1-.65,6.40,.70))]:m.tube([a,b],.055,sides=4)

        for side in [-1,1]:
            m.tube([(c+side*.65,5.99,.70),(c+side*1.20,6.27,.70)],.035,sides=4)
        f.finish(m,[trim])
        for x in [u0+.12,u1-.12]:f.box('Trim KBA gable bracket',(x,5.6,.24),(.09,.55,.35),trim)
        cross=f.roof('KBA projecting gable pitch',u0-.10,u1+.10,-.65,4.25,5.97,7.17,slate)
        bpy.context.view_layer.objects.active=main
        mod=main.modifiers.new('Join projecting gable roof','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=cross
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cross,do_unlink=True)
    f.box('Envelope KBA rear extension',(w/2,2.1,-14.5),(w,4.2,12),cream)
    f.box('Roof KBA rear flat',(w/2,4.27,-14.5),(w,.14,12),slate)
    # Canted display bays turn back into the recessed central doorway.
    for a,b in [(.30,w/2-.8),(w/2+.8,w-.30)]:
        left,right=a+.28,b-.28
        f.window('KBA display',(left+right)/2,1.72,right-left,2.72,trim,
                 frame=f.frame@Matrix.Translation((0,0,.24)),transom=.98)
        for x0,x1,z0,z1 in [(a,left,0,.24),(right,b,.24,0)]:
            angle=math.atan2(-(z1-z0),x1-x0)
            frame=f.frame@Matrix.Translation(((x0+x1)/2,0,(z0+z1)/2))@Matrix.Rotation(angle,4,'Y')
            f.window('KBA display return',0,1.72,math.hypot(x1-x0,z1-z0),2.72,trim,frame=frame@Matrix.Translation((0,0,.12)),transom=.98)
        f.box('Trim KBA shop plinth',((a+b)/2,.2,.07),(b-a,.4,.42),dark)
    for x in [.13,w-.13]:
        f.box('Trim KBA shop pilaster',(x,1.7,.02),(.23,3.4,.22),trim)
        f.box('Trim KBA fascia end',(x,3.62,.12),(.38,1.05,.3),cream)
        f.wall('Trim KBA fascia pediment',[(x-.24,4.14),(x+.24,4.14),(x,4.43)],[],cream,front=.3,back=.15)
    for x in [.14,w-.14]:f.box('Trim KBA downpipe',(x,4.8,.11),(.08,2.1,.1),trim)
    f.window('KBA door',w/2,1.58,1.55,2.9,trim,frame=f.frame@Matrix.Translation((0,0,-.30)),mullions=2,transom=1.0)
    f.sign('Yorkshire','YORKSHIRE\nBUILDING SOCIETY',w*.25,3.6,w*.47,.8,white,green)
    f.sign('KBA','KBA FINANCIAL\nPersonal & Corporate Financial Planning',w*.75,3.6,w*.47,.8,white,dark)
    f.sign('KBA date plaque','1989',w/2,5.3,.5,.24,cream,trim)
