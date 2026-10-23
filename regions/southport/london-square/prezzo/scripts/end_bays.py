"""Narrow recessed terminal bays, calibrated from exterior views and user review."""
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh,face_matrix,text_object
from components import window,rectangle_frame


def add_end_bays(finish,instance,z0,mats):
    stone,trim,glass,dark,white=mats
    specifications=[('Lord flats',(-30.4,-23.75),(0,1,0),1.8,15.0,15.25),
                    ('London inset',(-9.92,-41.2),(1,0,0),2.2,15.0,4.3)]
    for label,origin,normal,w,h,depth in specifications:
        frame=face_matrix((*origin,z0),normal);cx=w/2
        wall=Mesh('Envelope end bay '+label)
        wall.box((cx,h/2,-.21),(w,h,.42))
        # Real apertures and reveals: main cornice stops before this plain bay.
        for cy,wh in [(1.55,3.10),((4.4 if label=='Lord flats' else 4.05),(1.0 if label=='Lord flats' else .90)),(6.95,1.95),(10.35,1.85),(13.50,1.75)]:
            ww=1.05 if cy<5 else .78
            wall.cut_box_from_ashlar((cx,cy,-.21),(ww,wh,.60))
        # Side return and plain provisional backing close the narrow wing.
        if label=='Lord flats':wall.box((.10,h/2,-depth/2),(.20,h,depth))
        # The photographed rear west wing owns the outer wall beyond y=-37.1.
        # End the flats return at that junction rather than overlaying it.
        return_depth=13.35 if label=='Lord flats' else depth
        wall.box((w-.10,h/2,-return_depth/2),(.20,h,return_depth))
        if label=='Lord flats':wall.box((cx,h/2,-depth+.10),(w-.40,h,.20))
        finish(wall,'architecture',[stone],frame)
        for cy,wh in [(6.95,1.95),(10.35,1.85),(13.50,1.75)]:
            instance('terminal-'+str(wh),window(.78,wh,'detail','Window terminal '+label),'architecture',frame@Matrix.Translation((cx,cy,0)),mats)
            surround=Mesh('Dressings terminal '+label)
            rectangle_frame(surround,cx,cy,1.05,wh+.22,.075,.025,.10,0)
            finish(surround,'architecture',[stone],frame)
        if label=='Lord flats':add_flats_entrance(finish,frame,cx,mats)
        else:
            door=Mesh('Entrance recessed '+label)
            door.box((cx,1.55,-.30),(1.05,3.10,.06),3)
            rectangle_frame(door,cx,1.55,1.05,3.10,.07,-.25,.08,3)
            for cy in [.55,1.28,2.10,2.70]:
                rectangle_frame(door,cx,cy,.78,.48,.035,-.205,.04,3)
            # Glazed rectangular fanlight above entrance; no invented lettering.
            door.box((cx,4.05,-.24),(1.05,.90,.025),2)
            rectangle_frame(door,cx,4.05,1.05,.90,.07,-.16,.08,1)
            door.box((cx,4.05,-.13),(.035,.76,.035),1)
            finish(door,'shopfront',mats,frame)
            surrounds=Mesh('Dressings entrance '+label)
            rectangle_frame(surrounds,cx,1.55,1.27,3.25,.11,.025,.14,0)
            surrounds.box((cx,3.45,.055),(1.40,.16,.20),0)
            surrounds.box((cx,.04,-.12),(1.17,.08,.50),0)
            finish(surrounds,'architecture',[stone],frame)
            hardware=Mesh('Hardware terminal '+label)
            hardware.box((cx+.34,1.36,-.17),(.055,.21,.035),0)
            hardware.box((cx-.65,1.48,.08),(.12,.25,.045),0)
            finish(hardware,'shopfront',[dark],frame)
        roof=Mesh('Roof terminal '+label)
        roof.box((cx,h+.04,-depth/2),(w+.10,.12,depth+.08))
        if label=='Lord flats':finish(roof,'roof',[stone],frame)


def add_flats_entrance(finish,frame,cx,mats):
    """124 Lord Street flats door, from the supplied close Street View capture."""
    stone,trim,glass,dark,white=mats
    brass=bpy.data.materials.new('Flats door aged brass');brass.diffuse_color=(.40,.29,.12,1)
    brass.use_nodes=True;p=brass.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.40,.29,.12,1);p.inputs['Roughness'].default_value=.36
    door=Mesh('Entrance recessed Lord flats')
    door.box((cx,1.70,-.30),(1.05,2.80,.06),3)
    rectangle_frame(door,cx,1.70,1.05,2.80,.075,-.25,.08,3)
    # Three fielded panels: short top and bottom, much taller centre.
    for cy,h in [(2.73,.38),(1.75,1.30),(.69,.38)]:
        rectangle_frame(door,cx,cy,.77,h,.045,-.205,.05,3)
        rectangle_frame(door,cx,cy,.67,h-.10,.025,-.222,.028,3)
    door.box((cx,1.70,-.19),(.26,.075,.012),4)
    # Crossed glazing bars have an inner square and outer narrow border lights.
    door.box((cx,4.40,-.24),(1.05,1.0,.025),2)
    rectangle_frame(door,cx,4.40,1.05,1.0,.07,-.16,.08,1)
    rectangle_frame(door,cx,4.40,.72,.64,.025,-.13,.035,1)
    for a,b in [((cx-.35,4.09,-.105),(cx+.35,4.71,-.105)),((cx-.35,4.71,-.105),(cx+.35,4.09,-.105))]:door.tube([a,b],.013,1,6)
    finish(door,'shopfront',mats,frame)
    stonework=Mesh('Dressings flats rusticated doorway')
    for u in [cx-.70,cx+.70]:
        for i in range(8):stonework.box((u,.52+i*.36,.015),(.35,.33,.09))
    # Splayed flat arch with central projecting keystone.
    for left,right in [(-.64,-.30),(-.30,-.13),(.13,.30),(.30,.64)]:
        top_left=left*1.17;top_right=right*1.17
        stonework.outline([(cx+left+.008,3.12),(cx+right-.008,3.12),(cx+top_right-.008,3.63),(cx+top_left+.008,3.63)],-.015,.09)
    stonework.outline([(cx-.12,3.12),(cx+.12,3.12),(cx+.17,3.75),(cx-.17,3.75)],.0,.14)
    # Two shallow treads fit entirely within the recessed threshold.
    stonework.box((cx,.075,-.03),(1.12,.15,.42))
    stonework.box((cx,.225,-.18),(1.09,.15,.20))
    finish(stonework,'architecture',[stone],frame)
    metal=Mesh('Hardware flats kickplate and handle')
    metal.box((cx,.405,-.19),(.98,.19,.025))
    metal.box((cx-.36,1.72,-.18),(.055,.28,.035))
    metal.tube([(cx-.36,1.72,-.13),(cx-.21,1.72,-.13)],.018,0,8)
    finish(metal,'shopfront',[brass],frame)
    rails=Mesh('Hardware flats white handrails')
    for side in [-1,1]:
        x=cx+side*.46
        rails.tube([(x,1.04,-.05),(x,1.04,.08),(x,1.09,.12),(x,1.49,.12),(x,1.54,.08),(x,1.54,-.05)],.025,0,10)
    finish(rails,'shopfront',[trim],frame)
    intercom=Mesh('Hardware flats intercom')
    intercom.box((cx-.72,1.68,.10),(.19,.53,.09),0)
    intercom.box((cx-.72,1.68,.15),(.14,.46,.02),1)
    for i in range(10):intercom.box((cx-.69,1.50+i*.031,.166),(.045,.018,.008),2)
    for i in range(4):intercom.box((cx-.72,1.84+i*.018,.166),(.10,.006,.008),0)
    intercom.box((cx-.72,1.13,.09),(.105,.15,.06),1)
    finish(intercom,'shopfront',[dark,stone,trim],frame)
    # Only the clearly readable address/instruction is transcribed.
    sign=Mesh('Sign flats address');sign.box((0,0,-.018),(.43,.56,.036),0)
    font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
    text=text_object('temporary address','No 124\nLORD STREET\n—\nENTRANCE\nTO FLATS',(0,0,.006),(0,0,1),.43,.37,font,dark,extrude=.001)
    bpy.ops.object.select_all(action='DESELECT');text.select_set(True);bpy.context.view_layer.objects.active=text;bpy.ops.object.convert(target='MESH')
    sign.add([tuple(text.matrix_world@v.co) for v in text.data.vertices],[tuple(p.vertices) for p in text.data.polygons],1);bpy.data.objects.remove(text,do_unlink=True)
    finish(sign,'shopfront',[stone,dark],frame@Matrix.Translation((cx+.70,1.63,.10)))
