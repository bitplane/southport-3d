"""Facade opening primitives for St George's Mansions."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract


def rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def roundtop(width,bottom,top,radius,steps=12):
    """Flat topped opening with quarter-circle upper shoulders, CCW."""
    w=width/2;r=min(radius,w)
    pts=[(-w,bottom),(w,bottom),(w,top-r)]
    for i in range(1,steps+1):
        a=i*math.pi/2/steps;pts.append((w-r+r*math.cos(a),top-r+r*math.sin(a)))
    for i in range(steps+1):
        a=math.pi/2+i*math.pi/2/steps;pts.append((-w+r+r*math.cos(a),top-r+r*math.sin(a)))
    return pts


def sash_panel_aperture(width,bottom,height):
    """Wall opening occupied by the complete authored/baked sash panel."""
    return rect(-width/2-.2,bottom-.35,width/2+.2,bottom+height+.5)


def sash_aperture(width,bottom,height):
    """Masonry ends at the outside of the 70 mm timber frame."""
    return roundtop(width+.14,bottom-.07,bottom+height+.07,.22)


def wall(name,poly,holes,thickness=.48):
    """Conforming facade shell with reveals only on true boundary edges."""
    from southport3d.conform import conform
    def clean(points):
        out=[]
        for p in points:
            if not out or sum((p[k]-out[-1][k])**2 for k in range(2))>1e-16:out.append(p)
        if len(out)>1 and sum((out[0][k]-out[-1][k])**2 for k in range(2))<1e-16:out.pop()
        return out
    poly=clean(poly);holes=[clean(h) for h in holes]
    shapes=[poly]
    for hole in holes:shapes=[p for q in shapes for p in subtract(q,hole)]
    edges=[(a,b) for ring in [poly]+holes for a,b in zip(ring,ring[1:]+ring[:1])]
    def on_boundary(a,b):
        midpoint=((a[0]+b[0])/2,(a[1]+b[1])/2)
        for c,d in edges:
            v=(d[0]-c[0],d[1]-c[1]);length2=v[0]**2+v[1]**2
            if length2<1e-14:continue
            t=((midpoint[0]-c[0])*v[0]+(midpoint[1]-c[1])*v[1])/length2
            error=sum((midpoint[k]-c[k]-t*v[k])**2 for k in range(2))
            if -.00001<=t<=1.00001 and error<1e-12:return True
        return False
    m=Mesh(name);limits=(min(p[0] for p in poly),max(p[0] for p in poly))
    for shape in shapes:
        shape=clean(shape)
        if len(shape)<3:continue
        n=len(shape);verts=[(x,y,z) for z in (-thickness,0) for x,y in shape]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        for i,(a,b) in enumerate(zip(shape,shape[1:]+shape[:1])):
            shared_corner=any(abs(a[0]-x)<1e-7 and abs(b[0]-x)<1e-7 for x in limits)
            if on_boundary(a,b) and not shared_corner:faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
        m.add(verts,faces)
    return conform({'wall':m})[0]['wall']


def ring(name,width,bottom,top,radius,border=.10,depth=.15,steps=12):
    inner=roundtop(width,bottom,top,radius,steps)
    outer=roundtop(width+2*border,bottom-border,top+border,radius+border,steps)
    # Continuous annular shell: no overlapping caps between adjacent arc sectors.
    n=len(inner);m=Mesh(name)
    vertices=[(x,y,z) for z in (-.08,depth) for loop in (inner,outer) for x,y in loop]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                      (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    m.add(vertices,faces);return m


def ring_lod(name,settings,asset_directory):
    return ring(name,settings['width'],0,.85,settings['width']/2,.035,.035,settings['steps']).finish([])



def leaded(name,width,height=.85,detail=True):
    m=Mesh(name);r=width/2
    outline=roundtop(width,0,height,r,10 if detail else 5)
    m.outline(outline,-.035,0,0)
    if detail:
        strips=[]
        for i in range(1,6):
            x=-r+i*width/6;top=height-r+math.sqrt(max(0,r*r-x*x))
            strips.append((x-.006,0,x+.006,top))
        for i in range(1,7):
            y=i*height/7
            half=r if y<=height-r else math.sqrt(max(0,r*r-(y-(height-r))**2))
            strips.append((-half,y-.006,half,y+.006))
        # One closed union retains the lead widths without duplicate crossing faces.
        came=rectangle_union_shell('Leaded transom came',strips,.004,.022)
        m.add(came.vertices,came.faces,1)
    return m


def leaded_lod(name,settings,asset_directory):return leaded(name,settings['width'],detail=False).finish([])


def sash_receiver(name,settings,asset_directory):
    w=settings['width'];h=settings['height'];m=Mesh(name)
    m.box((0,h/2+.075,-.06),(w+.4,h+.85,.15));return m.finish([])


def street_wall_lod(name,settings,asset_directory):
    import json
    d=json.loads((asset_directory/'research/layout.json').read_text());w=d['width'];holes=[]
    for x in d['bay_centres']:holes.append(rect(w-x-1.7,.35,w-x+1.7,11.0))
    for x in d['flat_centres']:
        holes.append([(u+w-x,z) for u,z in roundtop(2.7,.12,3.08,.65,12)])
        for dx in (-.96,.96):
            for z in (4.02,7.60):holes.append([(u+w-x-dx,zz) for u,zz in sash_panel_aperture(1.12,z,2.52)])
        for dx in (-1.12,0,1.12):holes.append(rect(w-x-dx-.43,11.73,w-x-dx+.43,12.94))
    # Build a shared rectangular grid around aperture bounds; add only the
    # curved shoulders locally. This avoids repeated whole-wall clipping.
    bounds=[(min(x for x,y in h),min(y for x,y in h),max(x for x,y in h),max(y for x,y in h)) for h in holes]
    xs=sorted({0,w,*(x for a,b,c,e in bounds for x in (a,c))});ys=sorted({0,d['eaves'],*(y for a,b,c,e in bounds for y in (b,e))})
    filled=set()
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
            if not any(a<x<c and b<y<e for a,b,c,e in bounds):filled.add((i,j))
    m=Mesh(name)
    for i,j in filled:
        a,b,c,e=xs[i],ys[j],xs[i+1],ys[j+1]
        v=[(a,b,z) for z in (-.48,0)]+[(c,b,z) for z in (-.48,0)]+[(c,e,z) for z in (-.48,0)]+[(a,e,z) for z in (-.48,0)]
        f=[(0,6,4,2),(1,3,5,7)]
        if (i,j-1) not in filled:f.append((0,2,3,1))
        if (i+1,j) not in filled and c<w-.00001:f.append((2,4,5,3))
        if (i,j+1) not in filled:f.append((4,6,7,5))
        if (i-1,j) not in filled and a>.00001:f.append((6,0,1,7))
        m.add(v,f)
    for h,(a,b,c,e) in zip(holes,bounds):
        for corner in subtract(rect(a,b,c,e),h):
            clean=[]
            for point in corner:
                if not clean or math.dist(point,clean[-1])>1e-7:clean.append(point)
            if len(clean)>2:m.outline(clean,-.48,0)
    ob=m.finish([])
    import bmesh
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    # Wall has only a repeating brick material, so retain that authored map rather
    # than baking thousands of tiny reveal islands. Box UV layout is known.
    import bpy
    mat=bpy.data.materials.new('District metric brick');mat.use_nodes=True
    nodes=mat.node_tree.nodes;shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.8
    tex=nodes.new('ShaderNodeTexImage');tex.image=next(im for im in bpy.data.images if im.name.startswith('brick.png'))
    coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value=(3*w/(.9*2.95),2*d['eaves']/(.9*1.92),1)
    mat.node_tree.links.new(coord.outputs['UV'],mapping.inputs['Vector']);mat.node_tree.links.new(mapping.outputs['Vector'],tex.inputs['Vector']);mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    ob.data.materials.append(mat);return ob


def fascia_receiver(name,settings,asset_directory):
    m=Mesh(name);w=settings['width'];m.add([(0,3.215,.128),(w,3.215,.128),(w,3.645,.128),(0,3.645,.128)],[(0,1,2,3)])
    return m.finish([])


def oriel_frame(name):
    """Union the original triple-sash strips, preserving their exact outline."""
    strips=[]
    for k in range(3):
        centre=(k-1)*.67
        for dx in (-.32,.32):
            x=centre+dx
            strips.append((x-.0275,12.47-.83,x+.0275,12.47+.83))
        for z in (11.65,12.45,13.28):
            strips.append((centre-.34,z-.0275,centre+.34,z+.0275))
    return rectangle_union_shell(name,strips,-.09,0)


def rectangle_union_shell(name,strips,back,front):
    """Closed extrusion of a union of axis-aligned metric rectangles."""
    xs=sorted({v for a,b,c,d in strips for v in (a,c)})
    ys=sorted({v for a,b,c,d in strips for v in (b,d)})
    filled={(i,j) for i in range(len(xs)-1) for j in range(len(ys)-1)
            if any(a<(xs[i]+xs[i+1])/2<c and b<(ys[j]+ys[j+1])/2<d for a,b,c,d in strips)}
    vertices=[];faces=[];indices={}
    def face(points):
        ids=[]
        for p in points:
            if p not in indices:indices[p]=len(vertices);vertices.append(p)
            ids.append(indices[p])
        faces.append(tuple(ids))
    for i,j in sorted(filled):
        a,b,c,d=xs[i],ys[j],xs[i+1],ys[j+1]
        face([(a,b,front),(c,b,front),(c,d,front),(a,d,front)])
        face([(a,d,back),(c,d,back),(c,b,back),(a,b,back)])
        for neighbour,p,q in [((i,j-1),(a,b),(c,b)),((i+1,j),(c,b),(c,d)),
                               ((i,j+1),(c,d),(a,d)),((i-1,j),(a,d),(a,b))]:
            if neighbour not in filled:
                face([(*p,front),(*p,back),(*q,back),(*q,front)])
    m=Mesh(name);m.add(vertices,faces);return m
