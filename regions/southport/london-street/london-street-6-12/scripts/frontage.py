"""Observed Halifax machines and number-six entrances, no invented interiors."""
import math
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh,text_object


def cash_machine(finish,front,u,white,metal,black,blue,glass,font):
    def done(m,mats):return finish(m,'shopfront',mats,front@Matrix.Translation((u,0,0)))
    m=Mesh('Shop ATM backboard');m.box((0,1.32,-.04),(.94,1.24,.12));done(m,[white])
    # Border is an actual frame around the inset front, rather than a solid box.
    m=Mesh('Shop ATM frame')
    for x in [-.335,.335]:m.box((x,1.31,.07),(.065,.91,.13))
    for h in [.855,1.765]:m.box((0,h,.07),(.735,.065,.13))
    done(m,[metal])
    m=Mesh('Shop ATM upper display');m.box((0,1.65,.025),(.59,.20,.025),0)
    m.box((0,1.65,.041),(.52,.145,.01),1);done(m,[black,blue])
    # Recessed well behind the sloping screen and projecting lower shelf.
    m=Mesh('Shop ATM control well');m.box((0,1.25,.005),(.60,.57,.025),0)
    m.box((.245,1.24,.10),(.12,.57,.18),1)
    m.box((-.04,1.50,.16),(.51,.055,.23),0)
    # Screen leans back at its upper edge; shelf projects towards the pavement.
    m.add([(-.225,1.10,.20),(.165,1.10,.20),(.165,1.40,.045),(-.225,1.40,.045)],[(0,1,2,3)],2)
    for x in [-.25,.19]:m.tube([(x,1.08,.21),(x,1.41,.05)],.022,sides=6,material=1)
    for h,z in [(1.08,.21),(1.41,.05)]:m.box((-.03,h,z),(.48,.035,.03),1)
    m.add([(-.30,.89,.30),(.30,.89,.30),(.30,1.00,.09),(-.30,1.00,.09),(-.30,.85,.30),(.30,.85,.30)],[(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2),(2,5,4,3)],1)
    for x in [-.17,.16]:m.box((x,1.025,.065),(.25,.055,.035),0)
    done(m,[black,metal,glass])
    m=Mesh('Fine ATM controls')
    for side in [-1,1]:
        for j in range(4):
            h=1.12+j*.065;z=.20-(h-1.10)*.155/.30
            m.ellipsoid((-.03+side*.192,h,z+.025),(.018,.012,.009),segments=8,rings=4,material=0)
    for row in range(4):
        for col in range(3):
            h=.91+row*.018;z=.30-(h-.89)*.21/.11
            m.box((-.05+col*.025,h,z+.012),(.018,.012,.010),0)
    # Raised green circular card guide and narrow slot on the right-hand cheek.
    m.ellipsoid((.245,1.26,.205),(.043,.043,.025),segments=16,rings=8,material=1)
    m.box((.245,1.26,.231),(.055,.010,.008),2)
    done(m,[metal,_green(),black])
    # One local sign mesh, with fully authored logo and two readable lines.
    m=Mesh('Sign ATM identity');m.box((0,0,-.025),(.79,.49,.05),0)
    for points in [[(-.14,.185),(-.04,.185),(.14,.025),(.04,.025)],[(.14,.185),(.04,.185),(-.14,.025),(-.04,.025)]]:
        m.outline(points,.003,.014,1)
    m.box((0,.105,.020),(.31,.072,.008),0)
    for text,h,size,w in [('HALIFAX',.105,.052,.28),('cash machine',-.10,.105,.65)]:
        ob=text_object('Temporary ATM text',text,(0,h,.027),(0,0,1),size,w,font,white,extrude=.003,fit_bounds=True)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons],1);bpy.data.objects.remove(ob,do_unlink=True)
    finish(m,'shopfront',[blue,white],front@Matrix.Translation((u,2.23,.035)))


def _green():
    name='ATM card guide green'
    if name in bpy.data.materials:return bpy.data.materials[name]
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.035,.28,.09,1);return m


def number_six(box,finish,front,hw,width,stone,metal,black,glass,white):
    # Shared pier owns the Halifax boundary. The access door has its own granite
    # jambs and glazed overlight, followed by a separate glazed shop entrance.
    door_c=width-.78;door_w=1.08;left=door_c-door_w/2
    shop_door=left-.52
    for u,w in [(left-.07,.14),(width-.19,.32)]:
        box('Shop six stone jamb',u,1.59,w,3.18,.38,-.07,stone,'shopfront')
    box('Shop six head return',(hw+width)/2,3.10,width-hw,.16,.40,-.22,stone,'shopfront')
    box('Shop six access overlight',door_c,2.90,door_w,.40,.04,-.23,glass,'shopfront')
    box('Shop six overlight rail',door_c,2.68,door_w,.07,.15,-.18,metal,'shopfront')
    box('Shop six access leaf',door_c,1.33,door_w,2.62,.08,-.245,black,'shopfront')
    for u in [door_c-door_w/2+.035,door_c+door_w/2-.035]:
        box('Shop six access frame',u,1.34,.07,2.68,.18,-.18,black,'shopfront')
    box('Shop six threshold',door_c,.03,door_w,.06,.38,-.14,metal,'shopfront')
    # Four subtly raised timber panels and two letterboxes visible in the photo.
    for h,hh in [(.40,.57),(1.10,.43),(1.72,.43),(2.30,.38)]:
        box('Shop six timber panel',door_c,h,.84,hh,.025,-.187,black,'shopfront')
        for dh in [-hh/2,hh/2]:box('Shop six panel moulding',door_c,h+dh,.87,.025,.025,-.168,stone,'shopfront')
    for h in [1.10,1.74]:
        box('Fine six letterbox rim',door_c,h,.32,.13,.024,-.151,metal,'shopfront')
        box('Fine six letterbox slot',door_c,h,.25,.065,.012,-.133,black,'shopfront')
    m=Mesh('Fine six door knob');m.ellipsoid((door_c-.39,1.11,-.115),(.052,.052,.055),segments=12,rings=6);finish(m,'shopfront',[metal],front)
    # Glazed retail door is distinct from the black offices entrance.
    shop_left=hw+.24;shop_right=left-.14
    box('Shop six display glazing',(shop_left+shop_right)/2,1.56,shop_right-shop_left,3.06,.035,-.20,glass,'shopfront')
    for u in [shop_left,shop_door-.44,shop_right]:box('Shop six window jamb',u,1.56,.055,3.08,.10,-.12,metal,'shopfront')
    for h in [.06,.86,2.57]:box('Shop six glazed door rail',shop_door,h,.86,.055,.10,-.12,metal,'shopfront')
    box('Fine six shop letter slot',shop_door,1.0,.26,.045,.035,-.13,black,'shopfront')
