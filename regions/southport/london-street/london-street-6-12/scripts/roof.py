"""Planar hip roof with the rear court and neighbouring stair wells cut out."""
import bpy
import bmesh
from mathutils import Vector
from southport3d.geometry import Mesh


def roof_planes(d):
    b=d['base_z'];xf=d['front_x']+.12;xr=d['rear_x'];ys=d['south_y']-.12
    rx=d['ridge_x'];ry=d['ridge_end_y'];yn=d['north_y']
    ze=b+d['eaves_height'];zb=b+d['rear_eaves_height'];zr=b+d['ridge_height']
    points=[(xf,ys,ze),(xf,yn,ze),(xr,yn,zb),(xr,ys,zb),(rx,yn,zr),(rx,ry,zr)]
    faces=[(0,1,4,5),(0,5,3),(3,5,4,2)]
    planes=[]
    for face in faces:
        a,c,e=[Vector(points[i]) for i in face[:3]]
        n=(c-a).cross(e-a)
        planes.append((-n.x/n.z,-n.y/n.z,n.dot(a)/n.z))
    return points,faces,planes


def roof_height(d,x,y):
    return min(a*x+b*y+c for a,b,c in roof_planes(d)[2])


def build_roof(d,finish):
    points,faces,planes=roof_planes(d)
    thickness=.14
    mesh=Mesh('Roof hipped slate envelope')
    mesh.add(points+[(x,y,z-thickness) for x,y,z in points],
             faces+[tuple(i+6 for i in reversed(f)) for f in faces]+
             [(a,b,b+6,a+6) for a,b in [(0,1),(1,4),(4,2),(2,3),(3,0)]])
    roof=finish(mesh)
    bm=bmesh.new();bm.from_mesh(roof.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(roof.data);bm.free()
    for x0,x1,y0,y1 in d['roof_cutouts']:
        cutter=Mesh('Temporary roof setback cutter')
        cutter.box(((x0+x1)/2,(y0+y1)/2,10),(x1-x0,y1-y0,40))
        ob=cutter.finish([])
        bpy.context.view_layer.objects.active=roof
        mod=roof.modifiers.new('Court and neighbour clearance','BOOLEAN')
        mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(ob,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(roof.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),'Roof shell has open edges'
    bm.to_mesh(roof.data);bm.free();roof.data.update()
    uv=roof.data.uv_layers.active
    for face in roof.data.polygons:
        normal=face.normal;u=Vector((-normal.y,normal.x,0))
        if u.length<1e-6:u=Vector((1,0,0))
        u.normalize();v=normal.cross(u)
        for li in face.loop_indices:
            p=roof.data.vertices[roof.data.loops[li].vertex_index].co
            uv.data[li].uv=(p.dot(u)/2.4,p.dot(v)/2.2)
    return roof


def party_return(d):
    """A stepped, mitred wall ending under the roof, outside both stair wells."""
    path=d['north_boundary']
    outer=[Vector(p) for p in path];inner=[]
    for i,p in enumerate(outer):
        directions=[]
        if i:directions.append((p-outer[i-1]).normalized())
        if i+1<len(outer):directions.append((outer[i+1]-p).normalized())
        normals=[Vector((-v.y,v.x)) for v in directions]
        offset=sum(normals,Vector((0,0)))
        if len(normals)==2:offset/=1+normals[0].dot(normals[1])
        inner.append(p+offset*.28)
    mesh=Mesh('Envelope stepped northern party wall')
    vertices=[]
    for p,q in zip(outer,inner):
        vertices.extend([(p.x,p.y,d['base_z']),(q.x,q.y,d['base_z']),
                         (p.x,p.y,roof_height(d,p.x,p.y)-.14),
                         (q.x,q.y,roof_height(d,q.x,q.y)-.14)])
    faces=[]
    for i in range(len(path)-1):
        a=i*4;b=a+4
        faces.extend([(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),
                      (a+2,b+2,b+3,a+3),(a,a+1,b+1,b)])
    faces.extend([(0,2,3,1),(len(vertices)-4,len(vertices)-3,len(vertices)-1,len(vertices)-2)])
    mesh.add(vertices,faces)
    return mesh


def eave_return(d,name,a,b,inward,bottom):
    """Close a wall to the actual roof underside rather than a flat guess."""
    polygon=[a,b,(b[0]+inward[0],b[1]+inward[1]),(a[0]+inward[0],a[1]+inward[1])]
    if sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(polygon,polygon[1:]+polygon[:1]))<0:
        polygon.reverse()
    vertices=[(x,y,d['base_z']+bottom) for x,y in polygon]
    vertices += [(x,y,roof_height(d,x,y)-.14) for x,y in polygon]
    mesh=Mesh(name)
    mesh.add(vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    return mesh
