"""Observed entrance fittings, projecting sign and window lettering.

No menus or hidden interiors are invented. All vectors are authored; references
supply appearance, not pixels. Small fittings disappear at District.
"""
import bpy,math
from mathutils import Matrix,Vector
from southport3d.geometry import Mesh,face_matrix,text_object
from components import rectangle_frame


def add_frontage(finish,front,side,corner,flen,slen,L,mats,brass,lantern,root):
    stone,trim,glass,dark,white=mats
    font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
    italic=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf')
    red=bpy.data.materials.new('Red window script interpretation');red.use_nodes=True
    red.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.035,.075,1)

    def sign(name,text,w,h,bg,fg,matrix,script=False):
        m=Mesh('Sign '+name);m.box((0,0,-.015),(w,h,.03),0)
        ob=text_object('temporary',text,(0,0,.015),(0,0,1),h*.64,w*.91,italic if script else font,fg,extrude=.004)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],1);bpy.data.objects.remove(ob,do_unlink=True)
        finish(m,'shopfront',[bg,fg],matrix)
    for u,text in [(2.05,'Pasta'),(9.55,'Pizza'),(17.05,'Vino')]:
        sign('window script '+text,text,1.05,.35,glass,red,front@Matrix.Translation((u,3.75,-.055)),True)
    # Slim projecting sign with two faces, centred off the street wall.
    u=8.0;origin=front@Vector((u,3.9,.63))
    for direction in [-1,1]:
        matrix=face_matrix((origin.x+direction*.035,origin.y,origin.z),(direction,0,0))
        sign('projecting '+str(direction),'PREZZO',.80,.53,dark,white,matrix)
    m=Mesh('Hardware projecting bracket');m.box((u,4.24,.46),(.05,.05,.92));m.box((u,3.64,.46),(.04,.04,.92));finish(m,'shopfront',[dark],front)
    # Two small wall lanterns flank the arched corner door.
    for u in [.48,L-.48]:
        m=Mesh('Hardware corner lantern')
        m.box((u,2.24,.12),(.12,.35,.12),0)
        m.box((u,2.30,.27),(.20,.29,.14),1)
        for x in [u-.11,u+.11]:m.box((x,2.30,.35),(.025,.32,.025),0)
        for y in [2.14,2.46]:m.box((u,y,.29),(.26,.035,.20),0)
        m.add([(u-.15,2.49,.17),(u+.15,2.49,.17),(u+.15,2.49,.40),(u-.15,2.49,.40),(u,2.60,.28)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],0)
        finish(m,'shopfront',[brass,lantern],corner)
    # London Street's framed wall display: retain the frame but no unreadable copy.
    m=Mesh('Hardware London menu frame');rectangle_frame(m,6.45,2.18,.50,1.44,.025,-.024,.035,0)
    for y in [1.53,2.83]:
        for x in [6.23,6.67]:m.box((x,y,.002),(.015,.015,.009),0)
    finish(m,'shopfront',[dark],side)
    # Small end doorway seen on the Lord Street oblique photograph.
    u=flen-.50;m=Mesh('Entrance end door')
    m.box((u,1.4,-.10),(.80,2.8,.06),3)
    rectangle_frame(m,u,1.40,.80,2.8,.07,-.035,.10,3)
    for y in [.45,1.05,1.67,2.30]:
        rectangle_frame(m,u,y,.56,.41,.025,.025,.03,3)
        m.box((u,y,-.015),(.51,.36,.025),3)
    m.box((u,3.95,-.09),(.80,.70,.025),2)
    rectangle_frame(m,u,3.95,.80,.70,.06,.01,.12,1)
    m.tube([(u-.31,3.67,.06),(u+.31,4.23,.06)],.016,1,6)
    m.tube([(u+.31,3.67,.06),(u-.31,4.23,.06)],.016,1,6)
    finish(m,'shopfront',mats,front)
    m=Mesh('Hardware end door')
    m.box((u-.28,1.25,.08),(.08,.23,.035));m.box((u,1.75,.05),(.26,.045,.025))
    m.box((u-.57,1.65,.11),(.12,.26,.05));finish(m,'shopfront',[brass],front)
