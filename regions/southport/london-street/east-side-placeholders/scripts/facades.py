"""Metric construction helpers for the three adjoining London Street shops.

Coordinates are frontage distance, height above pavement, outward distance.
The shop-specific recipes retain their own evidence and proportions.
"""
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix
from southport3d.geometry import Mesh, text_object
from southport3d.planar import subtract


def rect(x0,y0,x1,y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


class Facade:
    def __init__(self,block,base,collection):
        self.w=block['y'][1]-block['y'][0]
        self.depth=block['x'][1]-block['x'][0]
        self.frame=Matrix(((0,0,-1,block['x'][0]),(-1,0,0,block['y'][1]),
                           (0,1,0,base),(0,0,0,1)))
        self.collection=collection
        self.materials={}

    def mat(self,name,color):
        m=bpy.data.materials.get(name)
        if m:return m
        m=bpy.data.materials.new(name);m.use_nodes=True
        p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
        p.inputs['Roughness'].default_value=.8
        texture={'Myers orange brown brick':'brick','KBA dark slate':'slate','Myers brown roof tiles':'tile'}.get(name)
        if texture:
            image=bpy.data.images.load(str(Path(__file__).resolve().parents[1]/'textures'/f'{texture}.png'));image.pack()
            node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
            m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
        return m

    def finish(self,m,materials,frame=None):
        ob=m.finish(materials,self.collection)
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
        uv=ob.data.uv_layers.new(name='Metric')
        for p in ob.data.polygons:
            axis=max(range(3),key=lambda i:abs(p.normal[i]))
            axes=[2,1] if axis==0 else [0,2] if axis==1 else [0,1]
            if m.name.startswith('Roof ') and abs(p.normal.y)>.1:
                axes=[2,0] if abs(p.normal.x)>abs(p.normal.z) else [0,2]
            for li in p.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
        ob.matrix_world=frame if frame is not None else self.frame
        return ob

    def box(self,name,centre,size,mat,frame=None):
        m=Mesh(name);m.box(centre,size);return self.finish(m,[mat],frame)

    def wall(self,name,outline,holes,mat,frame=None,back=-.25,front=0):
        parts=[outline]
        for h in holes:parts=[p for a in parts for p in subtract(a,h)]
        m=Mesh(name)
        for p in parts:m.outline(p,back,front)
        return self.finish(m,[mat],frame)

    def window(self,name,x,z,w,h,paint,frame=None,mullions=1,transom=.0):
        m=Mesh('Window '+name)
        m.box((x,z,-.12),(w,h,.035),0)
        for xx in [x-w/2+.025,x+w/2-.025]:m.box((xx,z,-.065),(.05,h,.075),1)
        for yy in [z-h/2+.025,z+h/2-.025,z+transom]:m.box((x,yy,-.065),(w,.05,.075),1)
        for i in range(1,mullions):m.box((x-w/2+w*i/mullions,z,-.065),(.035,h,.07),1)
        return self.finish(m,[self.mat('Shop dark glazing',(.07,.105,.12)),paint],frame)

    def sign(self,name,text,x,z,w,h,background,ink,frame=None):
        m=Mesh('Sign '+name);m.box((x,z,.04),(w,h,.10),0)
        font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
        ob=text_object('Temporary lettering',text,(x,z,.10),(0,0,1),h*.55,w*.94,font,ink,extrude=.002)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],1)
        bpy.data.objects.remove(ob,do_unlink=True)
        return self.finish(m,[background,ink],frame)

    def roof(self,name,u0,u1,d0,d1,eave,ridge,mat,hip=0):
        """Closed thin roof shell; ridge runs perpendicular to the frontage."""
        c=(u0+u1)/2
        top=[(u0,eave,-d0),(u1,eave,-d0),(u1,eave,-d1),(u0,eave,-d1),
             (c,ridge,-d0-hip),(c,ridge,-d1+hip)]
        faces=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)] if hip else [(0,4,5,3),(4,1,2,5)]
        # Gabled roofs have open space beneath, closed skins along each edge.
        edges=[(0,1),(1,2),(2,3),(3,0)] if hip else [(0,4),(4,1),(1,2),(2,5),(5,3),(3,0)]
        m=Mesh('Roof '+name);n=len(top)
        m.add(top+[(x,y-.12,z) for x,y,z in top],faces+[tuple(i+n for i in reversed(f)) for f in faces]+[(a,b,b+n,a+n) for a,b in edges])
        return self.finish(m,[mat])

    def enclosed(self,name,u0,u1,d0,d1,height,mat):
        # Side/rear walls only: the separately authored front contains openings.
        for u in [u0,u1]:self.box('Envelope '+name+' side',(u,height/2,-(d0+d1)/2),(.22,height,d1-d0),mat)
        self.box('Envelope '+name+' rear',((u0+u1)/2,height/2,-d1),(u1-u0,height,.22),mat)
