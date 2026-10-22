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
    # Shaped dark metal lanterns, from the two private user closeups.
    pewter=bpy.data.materials.new('Lantern weathered dark metal');pewter.use_nodes=True
    shader=pewter.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.12,.15,.14,1)
    shader.inputs['Metallic'].default_value=.55;shader.inputs['Roughness'].default_value=.42
    pane=bpy.data.materials.new('Lantern muted glazing');pane.use_nodes=True
    pane.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.15,.19,.12,1)
    bulb=bpy.data.materials.new('Lantern ivory bulb');bulb.use_nodes=True
    bulb.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.79,.67,.40,1)
    for u in [.48,L-.48]:
        m=Mesh('Hardware corner lantern')
        m.box((u,2.30,.10),(.12,.42,.08),0)
        m.box((u,2.16,.19),(.055,.045,.18),0)
        # Front panes are recessed so the slender frame remains visible.
        m.box((u,2.31,.25),(.185,.30,.13),1)
        for x in (u-.106,u+.106):
            for out in (.175,.335):m.box((x,2.31,out),(.022,.32,.022),0)
        for height in (2.15,2.47):m.box((u,height,.255),(.245,.025,.20),0)
        # Faceted hipped cap, raised vent and curled lower bowl.
        def shell(rings):
            verts=[]
            for height,half,dep in rings:
                verts.extend([(u-half,height,.255-dep),(u+half,height,.255-dep),
                              (u+half,height,.255+dep),(u-half,height,.255+dep)])
            faces=[(3,2,1,0)]
            for k in range(len(rings)-1):
                faces.extend((4*k+j,4*k+(j+1)%4,4*k+4+(j+1)%4,4*k+4+j) for j in range(4))
            n=len(verts);faces.append(tuple(range(n-4,n)));m.add(verts,faces,0)
        shell([(2.47,.145,.12),(2.50,.15,.125),(2.57,.065,.055),(2.61,.043,.04)])
        shell([(2.15,.12,.09),(2.10,.085,.065),(2.065,.04,.035)])
        m.ellipsoid((u,2.635,.255),(.024,.035,.024),0,segments=12,rings=8)
        m.ellipsoid((u,2.045,.255),(.024,.03,.024),0,segments=12,rings=8)
        # Bulb in front of opaque interior backing; no transparent sorting shell.
        m.box((u,2.23,.327),(.04,.08,.025),0)
        m.ellipsoid((u,2.31,.33),(.029,.064,.021),2,segments=16,rings=10)
        finish(m,'shopfront',[pewter,pane,bulb],corner)
    # London Street's framed wall display: retain the frame but no unreadable copy.
    m=Mesh('Hardware London menu frame');rectangle_frame(m,6.45,2.18,.50,1.44,.025,-.024,.035,0)
    for y in [1.53,2.83]:
        for x in [6.23,6.67]:m.box((x,y,.002),(.015,.015,.009),0)
    finish(m,'shopfront',[dark],side)
