"""Construction primitives for the Post Office Avenue terrace, in face XY."""
import math
from southport3d.geometry import Mesh
from southport3d.planar import subtract
import southport3d.conform as conform_module


def conform(meshes):
    # Independently rotated wall frames must meet at shared mitres; the ground
    # helper's 0.1 mm rounding otherwise moves their cap corners apart.
    grid,tolerance=conform_module.GRID,conform_module.TOLERANCE
    try:
        conform_module.GRID=1e-6
        conform_module.TOLERANCE=2e-6
        return conform_module.conform(meshes)
    finally:
        conform_module.GRID,conform_module.TOLERANCE=grid,tolerance


def rect(x0,y0,x1,y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def segment_arch(cx,width,bottom,spring,rise,steps=16):
    # A shallow circular segment, rather than a semicircle on a shop window.
    radius=(width*width/4+rise*rise)/(2*rise)
    yc=spring+rise-radius
    theta=math.asin(width/(2*radius))
    return [(cx-width/2,bottom),(cx+width/2,bottom)]+[
        (cx+radius*math.sin(theta-2*theta*i/steps),yc+radius*math.cos(theta-2*theta*i/steps))
        for i in range(steps+1)]


def wall(name,outer,holes,thickness=.30,mitres=None):
    """A conforming pierced shell; no duplicate internal fragment walls."""
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    # Three gables make the upper outline concave; clipping/fan triangulation
    # must start from convex pieces rather than bridging across its valleys.
    verts=[Vector((x,y,0)) for x,y in outer]
    pieces=[[(outer[v][0],outer[v][1]) if isinstance(v,int) else (v.x,v.y)
             for v in triangle] for triangle in tessellate_polygon([verts])]
    for hole in holes:pieces=[p for q in pieces for p in subtract(q,hole)]
    xmin=min(x for x,y in outer);xmax=max(x for x,y in outer)
    strip=max(.45,*(abs(v)*1.5 for v in mitres)) if mitres else 0
    if mitres:
        # Split at both taper breakpoints BEFORE moving vertices: a long edge
        # crossing an affine-region boundary must gain the same breakpoint as
        # its subdivided neighbours, otherwise their rear edges diverge.
        for cut in (xmin+strip,xmax-strip):
            pieces=[part for p in pieces for part in
                    (clip_values(p,lambda v:v[0]-cut),
                     clip_values(p,lambda v:cut-v[0])) if len(part)>=3]
    boundary=[(a,b) for loop in [outer]+holes for a,b in zip(loop,loop[1:]+loop[:1])]
    def edge(a,b):
        m=((a[0]+b[0])/2,(a[1]+b[1])/2)
        for c,d in boundary:
            v=(d[0]-c[0],d[1]-c[1]);l=v[0]*v[0]+v[1]*v[1]
            if l<1e-16:continue
            t=((m[0]-c[0])*v[0]+(m[1]-c[1])*v[1])/l
            if -1e-8<=t<=1+1e-8 and sum((m[k]-c[k]-t*v[k])**2 for k in range(2))<1e-14:return True
        return False
    mesh=Mesh(name)
    for p in pieces:
        p=[v for j,v in enumerate(p) if math.dist(v,p[j-1])>1e-9]
        if len(p)<3:continue
        n=len(p);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        for j,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
            if edge(a,b):faces.append((j,(j+1)%n,(j+1)%n+n,j+n))
        xmin=min(x for x,y in outer);xmax=max(x for x,y in outer)
        def back_x(x):
            if mitres is None:return x
            # Move a continuous corner strip, not just exact endpoint vertices.
            # Clipping openings introduces vertices arbitrarily close to the
            # endpoint; endpoint-only movement folds those rear triangles back
            # across each other. A monotone taper keeps their order and leaves
            # the photographed openings (all beyond this strip) unchanged.
            strip=max(.45,abs(mitres[0])*1.5,abs(mitres[1])*1.5)
            return (x+mitres[0]*max(0.,1-(x-xmin)/strip)
                     +mitres[1]*max(0.,1-(xmax-x)/strip))
        mesh.add([(back_x(x),y,-thickness) for x,y in p]+[(x,y,0) for x,y in p],faces)
    return conform({'wall':mesh})[0]['wall']


def ring(name,inner,outer,back=-.12,front=-.025):
    assert len(inner)==len(outer)
    m=Mesh(name);n=len(inner)
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                      (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    m.add([(x,y,z) for z in (back,front) for loop in (inner,outer) for x,y in loop],faces)
    return m


def wedge(name,u0,u1,v0,v1,eaves,ridge,hip):
    m=Mesh(name);vc=(v0+v1)/2
    m.add([(u0,v0,eaves),(u1,v0,eaves),(u1,v1,eaves),(u0,v1,eaves),
           (u0+hip,vc,ridge),(u1-hip,vc,ridge)],
          [(3,2,1,0),(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)])
    return m


def clip_values(poly,fn):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        fa,fb=fn(a),fn(b)
        if fa>=-1e-9:out.append(a)
        if (fa>1e-9 and fb<-1e-9) or (fa<-1e-9 and fb>1e-9):
            t=fa/(fa-fb);out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(2)))
    return out


def roof_shapes(width,depth,eaves,ridge):
    """Height fields whose maximum forms three cross-gables and a hipped main roof."""
    rise=ridge-eaves;k=rise/((depth+.4)/2);end=rise/2.0
    # Anchor's mapped rear corner projects ~0.26 m beyond its front corner.
    # Carry the eave beyond that skewed wall instead of clipping the roof at
    # the front width and leaving an uncovered rear corner.
    end_u=width+.55
    shapes=[(rect(-.2,-.2,end_u,depth+.2),
             [(0,k,eaves+k*.2),(0,-k,eaves+k*(depth+.2)),
              (end,0,eaves+end*.2),(-end,0,eaves+end*end_u)])]
    for centre in (width*.1,width*.5,width*.9):
        half=2.30;g=rise/half
        shapes.append((rect(centre-half,-.38,centre+half,depth/2),
                       [(g,0,ridge-g*centre),(-g,0,ridge+g*centre)]))
    return shapes


def height(shapes,x,y):
    values=[]
    for poly,planes in shapes:
        if min(p[0] for p in poly)-1e-8<=x<=max(p[0] for p in poly)+1e-8 and min(p[1] for p in poly)-1e-8<=y<=max(p[1] for p in poly)+1e-8:
            values.append(min(a*x+b*y+c for a,b,c in planes))
    assert values,(x,y)
    return max(values)


def profile(shapes,start,end):
    """Exact breakpoints of the piecewise planar roof along a wall line."""
    dx,dy=end[0]-start[0],end[1]-start[1];ts={0.,1.}
    lines=[(a*dx+b*dy,a*start[0]+b*start[1]+c) for poly,planes in shapes for a,b,c in planes]
    for m,c in lines:
        for n,d in lines:
            if abs(m-n)>1e-10:
                t=(d-c)/(m-n)
                if 0<t<1:ts.add(t)
    for poly,_ in shapes:
        for p in poly:
            for axis,delta in enumerate((dx,dy)):
                if abs(delta)>1e-9:
                    t=(p[axis]-start[axis])/delta
                    if 0<t<1:ts.add(t)
    points=[(t,height(shapes,start[0]+t*dx,start[1]+t*dy)-.12) for t in sorted(ts)]
    result=[]
    for point in points:
        if result and abs(point[0]-result[-1][0])<1e-7:continue
        result.append(point)
        while len(result)>2:
            a,b,c=result[-3:]
            error=abs((b[1]-a[1])*(c[0]-a[0])-(c[1]-a[1])*(b[0]-a[0]))
            if error>1e-8:break
            result.pop(-2)
    return result


def roof_shell(shapes):
    """Direct planar upper envelope; no costly mesh Boolean intersections."""
    mesh=Mesh('Roof joined hipped ridge and three cross gables')
    for index,(domain,planes) in enumerate(shapes):
        for plane in planes:
            a,b,c=plane
            region=domain
            for d,e,f in planes:
                region=clip_values(region,lambda p:d*p[0]+e*p[1]+f-(a*p[0]+b*p[1]+c)) if region else []
            if len(region)<3:continue
            regions=[region]
            for other,(od,op) in enumerate(shapes):
                if other==index:continue
                cover=od
                for d,e,f in op:
                    cover=clip_values(cover,lambda p:d*p[0]+e*p[1]+f-(a*p[0]+b*p[1]+c)-1e-10) if cover else []
                if len(cover)>2:regions=[p for r in regions for p in subtract(r,cover)]
            for p in regions:
                if len(p)<3:continue
                mesh.add([(x,y,a*x+b*y+c) for x,y in p],[tuple(range(len(p)))])
    # Conformance stitches valleys and intersections before making an underside.
    mesh=conform({'roof':mesh})[0]['roof']
    import bmesh
    from mathutils import Vector
    bm=bmesh.new();vertices=[bm.verts.new(v) for v in mesh.vertices]
    for face in mesh.faces:
        try:bm.faces.new([vertices[i] for i in face])
        except ValueError:pass
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for face in bm.faces:
        if face.normal.z<0:face.normal_flip()
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    top=[tuple(v.co) for v in bm.verts];faces=[tuple(v.index for v in f.verts) for f in bm.faces]
    boundary=[]
    for edge in bm.edges:
        if len(edge.link_faces)==1:
            loop=next(l for l in edge.link_faces[0].loops if l.edge==edge)
            boundary.append((loop.vert.index,loop.link_loop_next.vert.index))
    n=len(top);mesh=Mesh(mesh.name)
    mesh.add(top+[(x,y,z-.12) for x,y,z in top],
             faces+[tuple(i+n for i in reversed(f)) for f in faces]+[(a,a+n,b+n,b) for a,b in boundary])
    bm.free();return mesh
