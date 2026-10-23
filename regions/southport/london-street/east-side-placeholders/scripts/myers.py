"""19–21: brick shop front, rendered Anchor Street side and dormered hip roof."""
import math
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh
from facades import rect


def build(f):
    w=f.w;depth=19.6
    brick=f.mat('Myers orange brown brick',(.38,.19,.095))
    render=f.mat('Myers warm cream render',(.72,.69,.59))
    white=f.mat('Shop white lettering',(.87,.88,.84))
    black=f.mat('Myers black fascia',(.025,.035,.032))
    tile=f.mat('Myers brown roof tiles',(.22,.16,.125))
    holes=[rect(.22,.12,w-.22,2.9)]+[rect(c-.48,4.68,c+.48,6.43) for c in [w*.15,w*.38,w*.62,w*.85]]
    f.wall('Envelope Myers brick frontage',rect(0,0,w,7.75),holes,brick)
    for c in [w*.15,w*.38,w*.62,w*.85]:
        f.window('Myers front sash',c,5.55,.96,1.75,white,transom=0)
        for z in [4.62,6.51]:f.box('Trim Myers stone sill lintel',(c,z,.035),(1.12,.10,.15),render)
        f.box('Detail Myers vent',(c,7.2,.045),(.24,.24,.05),black)
    f.box('Trim Myers parapet cap',(w/2,7.80,.015),(w+.10,.09,.32),black)
    for a,b in [(.22,w*.48),(w*.70,w-.22)]:f.window('Myers display',(a+b)/2,1.52,b-a,2.8,black,transom=1.12)
    f.window('Myers entrance',w*.59,1.52,w*.22,2.8,black,frame=f.frame@Matrix.Translation((0,0,-.18)),mullions=2,transom=1.12)
    f.sign('Myers','DAVID H MYERS\nOPTICIANS',w*.335,3.52,w*.67,.95,black,white)
    m=Mesh('Sign Myers spectacles')
    m.box((w*.835,3.52,.04),(w*.33,.95,.10),0)
    cx,cy=w*.835,3.55
    # Authored outline of the prominent spectacles symbol, not image pixels.
    for side in [-1,1]:
        pts=[]
        for j in range(33):
            a=2*math.pi*j/32;x=side*.43+.36*math.cos(a);y=.25*math.sin(a)
            pts.append((cx+x*math.cos(.22)-y*math.sin(.22),cy+x*math.sin(.22)+y*math.cos(.22),.105))
        m.tube(pts,.035,material=1,sides=6)
    m.tube([(cx-.1,cy+.025,.105),(cx,cy+.10,.105),(cx+.1,cy+.07,.105)],.035,material=1,sides=6)
    f.finish(m,[black,white])
    handle=f.mat('Shop stainless handles',(.56,.59,.60))
    for x in [w*.59-.11,w*.59+.11]:f.box('Trim Myers door pull',(x,1.28,-.16),(.025,.42,.06),handle)
    # Side faces Anchor Street, with real window holes and recessed garage.
    side=f.frame@Matrix.Translation((w,0,0))@Matrix.Rotation(math.pi/2,4,'Y')
    centres=[3.0,6.2,10.6,13.0,15.4,17.8]
    holes=[rect(d-.53,4.5,d+.53,6.0) for d in centres]+[rect(13,.05,19,2.6),rect(.25,.10,5.8,2.8)]
    f.wall('Envelope Myers Anchor wall',rect(0,0,depth,7.6),holes,render,frame=side)
    for d in centres:f.window('Myers side sash',d,5.25,1.06,1.5,white,frame=side)
    f.window('Myers side display',3.025,1.45,5.55,2.7,black,frame=side,mullions=3,transom=1.1)
    f.sign('Myers Anchor fascia','DAVID H MYERS\nOPTICIANS',3.025,3.45,5.8,1.0,black,white,frame=side)
    f.box('Door Myers garage shutter',(16,1.33,-.16),(6,2.55,.06),black,side)
    for j in range(25):f.box('Detail Myers shutter slat',(16,.1+j*.10,-.12),(5.95,.018,.02),render,side)
    for d in [7.4,12.1]:f.box('Trim Myers rainwater pipe',(d,3.8,.1),(.08,7.6,.08),black,side)
    f.box('Envelope Myers north party wall',(0,3.8,-depth/2),(.22,7.6,depth),brick)
    f.box('Envelope Myers rear',(w/2,3.8,-depth),(w,7.6,.25),brick)
    roof=f.roof('Myers hip',0,w,0,depth,7.6,10.9,tile,hip=(3.5,0))
    back=f.frame@Matrix.Translation((w,0,-depth-.015))@Matrix.Rotation(math.pi,4,'Y')
    f.wall('Envelope Myers rear gable',[(0,7.6),(w,7.6),(w/2,10.9)],[],brick,frame=back,back=-.20,front=0)
    # A broad dark dormer/roof interruption on the party side is visible in the
    # north orbit. Its exact cladding and concealed openings are unresolved.
    nf=f.frame@Matrix.Translation((.75,0,-11.5))@Matrix.Rotation(-math.pi/2,4,'Y')
    dark=f.mat('Myers north roof cladding',(.115,.12,.12))
    m=Mesh('Temporary north roof opening');m.box((0,8.55,-.9),(7.0,1.95,2.2))
    cutter=f.finish(m,[tile],nf);bpy.context.view_layer.objects.active=roof
    mod=roof.modifiers.new('North dormer aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    f.box('Envelope Myers north dormer face',(0,8.55,0),(7.0,1.95,.13),dark,nf)
    for x in [-3.5,3.5]:f.box('Envelope Myers north dormer return',(x,8.55,-.9),(.13,1.95,1.8),dark,nf)
    f.box('Roof Myers north dormer',(0,9.59,-.9),(7.2,.13,2.1),tile,nf)
    # One flat-headed front dormer and two shallow pitched side dormers are
    # visible from London/Anchor Street and in the 3D orbit. Cut the roof skin
    # behind the glazing so it cannot obscure the lower panes.
    for name,frame,width,z in [
        ('front',f.frame@Matrix.Translation((w/2,0,-1.05)),2.2,8.95),
        ('Anchor near',f.frame@Matrix.Translation((w-.8,0,-4.5))@Matrix.Rotation(math.pi/2,4,'Y'),2.0,8.85),
        ('Anchor far',f.frame@Matrix.Translation((w-.8,0,-16.0))@Matrix.Rotation(math.pi/2,4,'Y'),2.0,8.85),
    ]:
        m=Mesh('Temporary roof opening');m.box((0,z,-1.0),(width,.98,2.5))
        cutter=f.finish(m,[tile],frame)
        bpy.context.view_layer.objects.active=roof
        mod=roof.modifiers.new('Dormer clear glazing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
        f.window('Myers dormer '+name,0,z,width,.9,white,frame=frame,mullions=3,transom=.38)
        for x in [-width/2-.05,width/2+.05]:
            f.box('Envelope Myers dormer cheek',(x,z,-1.1),(.10,1.1,2.3),tile,frame)
        f.box('Trim Myers dormer sill',(0,z-.50,0),(width+.22,.12,.3),white,frame)
        if name=='front':
            f.box('Roof Myers dormer cap',(0,z+.56,-1.0),(width+.32,.14,2.5),black,frame)
        else:
            f.wall('Envelope Myers dormer gable',[(-width/2-.1,z+.5),(width/2+.1,z+.5),(0,z+1.0)],[],white,frame=frame,back=-.15,front=.02)
            cap=f.roof('Myers side dormer pitch',-width/2-.15,width/2+.15,-.2,2.3,z+.53,z+1.03,tile)
            cap.matrix_world=frame
