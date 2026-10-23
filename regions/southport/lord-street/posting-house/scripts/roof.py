"""Intersecting observed gable ranges, with closed union and course-aligned UVs."""
import bpy
import bmesh
from mathutils import Matrix, Vector
from southport3d.geometry import Mesh


def make_roof(a,b,depth,eave,ridge,finish,front,slate):
    def volume(name,x0,x1,y0,y1,along_x=True,top=ridge):
        z=eave-.16
        v=[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),
           (x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave)]
        if along_x:v += [(x0,(y0+y1)/2,top),(x1,(y0+y1)/2,top)]
        else:v += [((x0+x1)/2,y0,top),((x0+x1)/2,y1,top)]
        faces=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        faces+=([(4,5,9,8),(5,6,9),(6,7,8,9),(7,4,8)] if along_x else
                [(4,5,8),(5,6,9,8),(6,7,9),(7,4,8,9)])
        m=Mesh(name);m.add(v,faces);o=finish(m,'roof',[slate])
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        return o
    main=volume('Roof historic joined gables',a,b,.06,depth-.06)
    # Three rear gables terminate at the documented rear brick elevation.
    for c,w,top in [(a+3.1,5.7,ridge-.65),((a+b)/2,6.2,ridge-.15),(b-3.0,5.7,ridge-.65)]:
        operand=volume('temporary cross gable',c-w/2,c+w/2,depth/2,depth,False,top)
        bpy.context.view_layer.objects.active=main
        mod=main.modifiers.new('Resolve valley','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(operand,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(main.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges)
    bm.to_mesh(main.data);bm.free();main.data.update()
    for f in main.data.polygons:
        u=Vector((-f.normal.y,f.normal.x,0))
        if u.length<1e-6:u=Vector((1,0,0))
        u.normalize();v=f.normal.cross(u)
        for li in f.loop_indices:
            p=main.data.vertices[main.data.loops[li].vertex_index].co
            main.data.uv_layers.active.data[li].uv=(p.dot(u)/3.2,p.dot(v)/1.28)
    main.matrix_world=front@Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
    return main
