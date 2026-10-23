"""Photographed red-brick transverse rear wing; dimensions remain calibrated."""
import math
import bpy
from southport3d.geometry import Mesh, face_matrix
from components import rect, wall, ring, roof


def build_rear(ctx):
    finish,box=ctx['finish'],ctx['box'];base=ctx['z0']
    brick,cream,glass,wood,slate,metal=[ctx[k] for k in ('brick','cream','glass','wood','slate','metal')]
    x0,x1,y0,y1=-113.8,-89.55,-61.2,-52.1
    depth=y1-y0;centre=depth/2;eave=6.7;ridge=10.2
    # West-facing gable: tall glazed door, two narrow slots and a circular light.
    frame=face_matrix((x0,y1,base),(-1,0,0))
    circle=[(centre+.69*math.cos(i*math.tau/48),7.75+.69*math.sin(i*math.tau/48)) for i in range(48)]
    holes=[rect(centre-.72,.12,centre+.72,5.15),circle]
    for u in (centre-2.0,centre+2.0):holes.append(rect(u-.10,3.45,u+.10,4.75))
    finish(wall('Envelope rear cross gable',[(0,0),(depth,0),(depth,eave),(centre,ridge),(0,eave)],holes,.32),'modern-hall',[brick],frame)
    m=Mesh('Window modern rear roundel');m.outline(circle,-.22,-.18,0)
    ring(m,centre,7.75,.69,.085,.10,48,1)
    ring(m,centre,7.75,.21,.06,-.08,32,1)
    for sign in (-1,1):
        m.box((centre+sign*.46,7.75,-.08),(.38,.055,.08),1)
        m.box((centre,7.75+sign*.46,-.08),(.055,.38,.08),1)
    finish(m,'modern-hall',[glass,cream],frame)
    m=Mesh('Door rear gable glazed entrance')
    m.box((centre,2.64,-.19),(1.43,5.0,.06),0)
    for u in (centre-.76,centre+.76):m.box((u,2.64,.08),(.13,5.2,.22),1)
    for z in (.08,5.25):m.box((centre,z,.08),(1.7,.15,.22),1)
    for u in (centre-.35,centre,centre+.35):m.box((u,2.64,-.12),(.055,4.98,.08),2)
    for z in (1.7,3.4,4.7):m.box((centre,z,-.12),(1.43,.055,.08),2)
    finish(m,'modern-hall',[glass,cream,wood],frame)
    for u in (centre-2.0,centre+2.0):
        box('Window modern rear slit',(u,4.10,-.17),(.20,1.3,.05),'modern-hall',glass,frame)
        for xx in (u-.14,u+.14):box('Trim rear slit surround',(xx,4.10,.035),(.07,1.42,.14),'modern-hall',cream,frame)
    # Projecting corner piers, pale caps and inset diamond panels.
    for u in (.12,depth-.12):
        box('Pier rear gable brick',(u,3.25,.17),(.54,6.5,.48),'modern-hall',brick,frame)
        for z,w,h in [(0.22,.77,.34),(2.1,.74,.22),(2.43,.62,.17),(5.55,.64,.20),(6.70,.77,.20)]:
            box('Trim rear gable pier cap',(u,z,.22),(w,h,.60),'modern-hall',cream,frame)
        m=Mesh('Trim rear gable diamond')
        m.tube([(u,5.75,.49),(u+.23,6.12,.49),(u,6.5,.49),(u-.23,6.12,.49),(u,5.75,.49)],.035,sides=4)
        finish(m,'modern-hall',[cream],frame)
    # Coping follows the true gable, rather than an invented hipped return.
    m=Mesh('Trim rear gable coping');m.tube([(0,eave+.05,.08),(centre,ridge+.06,.08),(depth,eave+.05,.08)],.10,sides=4)
    m.tube([(centre,ridge+.05,.08),(centre,ridge+.27,.08)],.075,sides=8)
    finish(m,'modern-hall',[cream],frame)
    # One continuous annex-facing wall ends at the underside of the roof.
    # A separate full-height box plus a coplanar triangular cap caused roof-edge
    # fighting and an offset return. Derive this silhouette from the roof shell.
    east=face_matrix((x1,y0,base),(1,0,0))
    shell=.16;overhang=.12
    end_height=ridge-(ridge-eave)*centre/(centre+overhang)-shell
    outline=[(0,0),(-29.72-y0,0),(-29.72-y0,eave-shell),
             (depth+overhang,eave-shell),(centre,ridge-shell),(0,end_height)]
    finish(wall('Envelope cafe west return',outline,[],.30),'modern-hall',[brick],east)
    # Rear long elevation: six recessed windows, brick piers and two string courses.
    frame=face_matrix((x0,y0,base),(0,-1,0));width=x1-x0
    centres=[1.9+i*(width-3.8)/5 for i in range(6)]
    holes=[rect(u-.72,2.05,u+.72,5.55) for u in centres]
    # The gable and cafe return own the corner thickness. Stop the long wall
    # at their inner faces so their exposed end caps are not drawn twice.
    finish(wall('Envelope rear long wall',rect(.32,0,width-.30,eave),holes,.32),'modern-hall',[brick],frame)
    for u in centres:
        m=Mesh('Window modern rear side');m.box((u,3.8,-.19),(1.44,3.5,.06),0)
        for dx in (-.76,.76):m.box((u+dx,3.8,.02),(.10,3.65,.14),1)
        for z in (1.98,5.62):m.box((u,z,.04),(1.75,.15,.25),1)
        for dx in (-.24,.24):m.box((u+dx,3.8,-.11),(.045,3.5,.08),2)
        for z in (3.25,4.55):m.box((u,z,-.11),(1.44,.045,.08),2)
        finish(m,'modern-hall',[glass,cream,wood],frame)
    for u in [0]+[(a+b)/2 for a,b in zip(centres,centres[1:])]+[width]:
        box('Pier rear long wall',(u,3.3,.13),(.35,6.6,.30),'modern-hall',brick,frame)
    for z in (1.74,1.9):box('Trim rear long band',(width/2,z,.035),(width,.055,.09),'modern-hall',cream,frame)
    # Closed roof union: the longitudinal ridge meets a transverse ridge, with
    # actual valleys and no duplicate sheets at the T junction.
    main=finish(roof('Roof main cross gabled hall',-112.15,-89.55,(y0+y1)/2,-29.6,base+eave,base+ridge,0),'roofs',[slate])
    cross=roof('Temporary transverse roof',y0-.12,y1+.12,x0-.16,x1,base+eave,base+ridge,0)
    cross.vertices=[(y,x,z) for x,y,z in cross.vertices]
    cross.faces=[tuple(reversed(f)) for f in cross.faces]
    cutter=finish(cross,'roofs',[slate])
    bpy.context.view_layer.objects.active=main
    mod=main.modifiers.new('Joined transverse rear roof','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    # Hollow the joined volume into a closed thin shell. Solid wedge endcaps
    # would otherwise cover the brick gable and its round window with slate.
    inner=main.copy();inner.data=main.data.copy();bpy.context.collection.objects.link(inner)
    inner.location.z-=.16
    mod=main.modifiers.new('Roof shell thickness','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=inner
    bpy.context.view_layer.objects.active=main
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(inner,do_unlink=True)
    # Flush flashing and simple gutters survive every viewing level.
    m=Mesh('Roof rear ridge and gutters')
    m.tube([(x0-.12,(y0+y1)/2,base+ridge+.025),(x1,(y0+y1)/2,base+ridge+.025)],.055,sides=6)
    m.tube([(x0,y0-.12,base+eave),(x1,y0-.12,base+eave)],.07,sides=6)
    finish(m,'roofs',[metal])
