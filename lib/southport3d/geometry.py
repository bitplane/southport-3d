"""Mesh construction utilities for the independently authored memorial model."""
import math
import bpy
import numpy as np
from mathutils import Vector, Matrix

TAU = math.tau

class Mesh:
    def __init__(self, name):
        self.name, self.vertices, self.faces, self.indices = name, [], [], []

    def add(self, verts, faces, material=0):
        start = len(self.vertices)
        self.vertices.extend(tuple(v) for v in verts)
        self.faces.extend(tuple(start+i for i in f) for f in faces)
        self.indices.extend([material]*len(faces))

    def box(self, centre, size, material=0):
        x,y,z=centre; a,b,c=(s/2 for s in size)
        self.add([(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
                  (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)],
                 [(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],material)

    def cut_box_from_ashlar(self, centre, size):
        """Subtract an axis-aligned recess from a mesh made only of ashlar boxes.

        Splitting each stone avoids Boolean ambiguity where separate masonry
        blocks overlap at a chamber corner. Materials and course gaps survive.
        This deliberately rejects arbitrary meshes; use only before beveling.
        """
        assert len(self.vertices)%8==0 and len(self.faces)==len(self.vertices)//8*6
        lo=[centre[i]-size[i]/2 for i in range(3)]
        hi=[centre[i]+size[i]/2 for i in range(3)]
        result=Mesh(self.name)
        def piece(a,b,mat):
            if all(b[i]-a[i]>1e-7 for i in range(3)):
                result.box([(a[i]+b[i])/2 for i in range(3)],
                           [b[i]-a[i] for i in range(3)],mat)
        for k in range(len(self.vertices)//8):
            v=self.vertices[k*8:k*8+8]
            assert all(k*8<=i<k*8+8 for face in self.faces[k*6:k*6+6] for i in face)
            mat=self.indices[k*6]
            a=[min(p[i] for p in v) for i in range(3)]
            b=[max(p[i] for p in v) for i in range(3)]
            il=[max(a[i],lo[i]) for i in range(3)]
            ih=[min(b[i],hi[i]) for i in range(3)]
            if any(ih[i]<=il[i] for i in range(3)):
                piece(a,b,mat);continue
            # Six non-overlapping pieces surround the removed intersection.
            piece(a,[il[0],b[1],b[2]],mat)
            piece([ih[0],a[1],a[2]],b,mat)
            piece([il[0],a[1],a[2]],[ih[0],il[1],b[2]],mat)
            piece([il[0],ih[1],a[2]],[ih[0],b[1],b[2]],mat)
            piece([il[0],il[1],a[2]],[ih[0],ih[1],il[2]],mat)
            piece([il[0],il[1],ih[2]],[ih[0],ih[1],b[2]],mat)
        self.vertices,self.faces,self.indices=result.vertices,result.faces,result.indices

    def rect_profile(self, centre, rings, material=0):
        """rings: height, full x width, full y width."""
        verts=[]; faces=[]
        for z,w,d in rings:
            verts.extend([(centre[0]-w/2,centre[1]-d/2,z),(centre[0]+w/2,centre[1]-d/2,z),
                          (centre[0]+w/2,centre[1]+d/2,z),(centre[0]-w/2,centre[1]+d/2,z)])
        faces.append((3,2,1,0))
        for j in range(len(rings)-1):
            for i in range(4):
                a=j*4+i;b=j*4+(i+1)%4;faces.append((a,b,b+4,a+4))
        q=4*(len(rings)-1);faces.append((q,q+1,q+2,q+3))
        self.add(verts,faces,material)

    def lathe(self, centre, profile, segments=48, material=0, flutes=0, flute_depth=0):
        verts=[];faces=[]
        z0=profile[0][0];z1=profile[-1][0]
        for z,r in profile:
            fade=min(1,max(0,(z-z0)/.07),max(0,(z1-z)/.07))
            for j in range(segments):
                a=TAU*j/segments
                rr=r-flute_depth*(.5+.5*math.cos(flutes*a))*fade if flutes else r
                verts.append((centre[0]+rr*math.cos(a),centre[1]+rr*math.sin(a),z))
        faces.append(tuple(reversed(range(segments))))
        for k in range(len(profile)-1):
            for j in range(segments):
                a=k*segments+j;b=k*segments+(j+1)%segments
                faces.append((a,b,b+segments,a+segments))
        faces.append(tuple((len(profile)-1)*segments+j for j in range(segments)))
        self.add(verts,faces,material)

    def ellipsoid(self, centre, radii, material=0, segments=20, rings=10):
        verts=[];faces=[]
        for i in range(rings+1):
            v=math.pi*i/rings
            for j in range(segments):
                u=TAU*j/segments
                verts.append((centre[0]+radii[0]*math.sin(v)*math.cos(u),
                              centre[1]+radii[1]*math.sin(v)*math.sin(u),
                              centre[2]+radii[2]*math.cos(v)))
        for i in range(rings):
            for j in range(segments):
                a=i*segments+j;b=i*segments+(j+1)%segments
                faces.append((a,b,b+segments,a+segments))
        self.add(verts,faces,material)

    def outline(self, points, back, front, material=0):
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
        if area<0:points=list(reversed(points))
        n=len(points);verts=[(x,y,back) for x,y in points]+[(x,y,front) for x,y in points]
        faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
        faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        self.add(verts,faces,material)

    def cushion(self, points, back, front, material=0, softness=.035, spacing=.004):
        """Softly rounded relief surface constrained to a traced silhouette.

        A signed interior-distance profile gives a carved volume rather than a
        flat extruded paper shape. This is authored geometry, not image shading
        interpreted as measured depth.
        """
        pts=np.asarray(smooth_path(points+[points[0]],4)[:-1],dtype=float)
        xmin,ymin=pts.min(axis=0);xmax,ymax=pts.max(axis=0)
        nx=max(6,int((xmax-xmin)/spacing)+1);ny=max(6,int((ymax-ymin)/spacing)+1)
        xx,yy=np.meshgrid(np.linspace(xmin,xmax,nx),np.linspace(ymin,ymax,ny))
        inside=np.zeros(xx.shape,dtype=bool);distance=np.full(xx.shape,np.inf)
        for a,b in zip(pts,np.roll(pts,-1,axis=0)):
            dx,dy=b-a;length2=dx*dx+dy*dy
            if length2<1e-15:continue
            t=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/length2,0,1)
            distance=np.minimum(distance,np.sqrt((xx-a[0]-t*dx)**2+(yy-a[1]-t*dy)**2))
            crossing=((a[1]>yy)!=(b[1]>yy)) & (xx < (dx*(yy-a[1])/(dy if abs(dy)>1e-14 else 1e-14)+a[0]))
            inside ^= crossing
        zz=back+(front-back)*(1-np.exp(-distance/softness))**.55
        mask=inside[:-1,:-1]&inside[1:,:-1]&inside[1:,1:]&inside[:-1,1:]
        jj,ii=np.where(mask)
        # Keep complete sampled quads only; the sub-4 mm perimeter lies in the backing stone.
        faces=[(int(j*nx+i),int(j*nx+i+1),int((j+1)*nx+i+1),int((j+1)*nx+i)) for j,i in zip(jj,ii)]
        self.add(np.stack((xx,yy,zz),axis=-1).reshape(-1,3),faces,material)

    def tube(self, pts, radius, material=0, sides=8, depth_scale=1):
        pts=[Vector(p) for p in pts];verts=[];faces=[]
        for i,p in enumerate(pts):
            tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
            side=tangent.cross(Vector((0,0,1)))
            if side.length<.01:side=tangent.cross(Vector((0,1,0)))
            side.normalize();other=tangent.cross(side).normalized()
            for j in range(sides):
                a=TAU*j/sides
                v=side*(math.cos(a)*radius)+other*(math.sin(a)*radius*depth_scale)
                verts.append(p+v)
        faces.append(tuple(reversed(range(sides))))
        for i in range(len(pts)-1):
            for j in range(sides):
                a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
        faces.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
        self.add(verts,faces,material)

    def ring(self, centre, radius, tube_radius, material=0, segments=80, depth_scale=1):
        self.tube([(centre[0]+radius*math.cos(TAU*i/segments),centre[1]+radius*math.sin(TAU*i/segments),centre[2]) for i in range(segments+1)],tube_radius,material,8,depth_scale)

    def closed_ring(self,centre,radius,tube_radius,material=0,segments=256,sections=12,depth_scale=1):
        """Periodic torus without coincident end caps; suitable for stone cuts."""
        verts=[];faces=[]
        for i in range(segments):
            a=TAU*i/segments
            for j in range(sections):
                b=TAU*j/sections;r=radius+tube_radius*math.cos(b)
                verts.append((centre[0]+r*math.cos(a),centre[1]+r*math.sin(a),
                              centre[2]+tube_radius*depth_scale*math.sin(b)))
        for i in range(segments):
            for j in range(sections):
                faces.append((i*sections+j,((i+1)%segments)*sections+j,
                              ((i+1)%segments)*sections+(j+1)%sections,i*sections+(j+1)%sections))
        self.add(verts,faces,material)

    def transform(self, mat):
        self.vertices=[tuple(mat @ Vector(p)) for p in self.vertices]
        return self

    def finish(self, materials, collection=None, bevel=0, smooth=False):
        data=bpy.data.meshes.new(self.name);data.from_pydata(self.vertices,[],self.faces);data.update()
        ob=bpy.data.objects.new(self.name,data)
        (collection or bpy.context.scene.collection).objects.link(ob)
        for mat in materials:data.materials.append(mat)
        for p,idx in zip(data.polygons,self.indices):p.material_index=idx;p.use_smooth=smooth
        if bevel:
            mod=ob.modifiers.new('Small worn stone arrises','BEVEL');mod.width=bevel;mod.segments=2
        return ob

def face_matrix(origin, normal):
    n=Vector(normal).normalized();up=Vector((0,0,1)) if abs(n.z)<.99 else Vector((0,1,0));right=up.cross(n)
    return Matrix(((right.x,up.x,n.x,origin[0]),(right.y,up.y,n.y,origin[1]),
                   (right.z,up.z,n.z,origin[2]),(0,0,0,1)))

def smooth_path(points, steps=6):
    """Catmull-Rom; preserves supplied contour control points."""
    p=[Vector(points[0])]+[Vector(v) for v in points]+[Vector(points[-1])];out=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for j in range(steps):
            t=j/steps
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
    out.append(tuple(p[-2]));return out

def text_object(name, body, origin, normal, height, max_width, font, material,
                extrude=.001, collection=None, fit_bounds=False):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.font=font
    data.align_x='CENTER';data.align_y='CENTER';data.size=1
    data.space_character=1.12;data.resolution_u=4;data.extrude=extrude
    ob=bpy.data.objects.new(name,data);(collection or bpy.context.scene.collection).objects.link(ob)
    data.materials.append(material)
    bpy.context.view_layer.update()
    scale=height/max(ob.dimensions.y,1e-6)
    sx=max_width/max(ob.dimensions.x,1e-6) if fit_bounds else min(scale,max_width/max(ob.dimensions.x,1e-6))
    ob.matrix_world=face_matrix(origin,normal) @ Matrix.Diagonal((sx,scale,1,1))
    if fit_bounds:
        xs=[v[0] for v in ob.bound_box];ys=[v[1] for v in ob.bound_box]
        ob.matrix_world=ob.matrix_world @ Matrix.Translation((-(min(xs)+max(xs))/2,-(min(ys)+max(ys))/2,0))
    elif body.strip()=='—':
        # Font alignment centres an em box, not this very short glyph. Without
        # this correction scaling a lone underline displaces it vertically.
        ys=[v[1] for v in ob.bound_box]
        ob.matrix_world=ob.matrix_world @ Matrix.Translation((0,-(min(ys)+max(ys))/2,0))
    return ob
