"""Continuous bas-relief sculpting in a source photograph's coordinate frame.

This generates numeric surface geometry, not a colourized/retouched photograph.
Silhouettes, overlapping forms and their depths are authored explicitly. A
bounded, high-frequency shape-from-shading residual may recover the visible
small carving. It is a single-view interpretation, NEVER measured 3D depth.
"""
from pathlib import Path
import math
import numpy as np


def curve(points, samples=7, closed=False):
    p=np.asarray(points,dtype=float)
    if closed:p=np.concatenate((p[-1:],p,p[:2]))
    else:p=np.concatenate((p[:1],p,p[-1:]))
    out=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for t in np.linspace(0,1,samples,endpoint=False):
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    if not closed:out.append(p[-2])
    return np.asarray(out)


class Surface:
    def __init__(self, bounds, width_m, height_m, columns=500, origin_y=0):
        self.bounds=np.array(bounds,float)
        x0,y0,x1,y1=bounds
        self.width,self.height=width_m,height_m
        self.origin_y=origin_y
        self.nx=columns
        self.ny=round(columns*height_m/width_m)
        self.x,self.y=np.meshgrid(np.linspace(x0,x1,self.nx),np.linspace(y0,y1,self.ny))
        self.z=np.full(self.x.shape,.001,dtype=float)
        self.feature=np.zeros(self.x.shape,dtype=float)
        self.layers=[]

    def _field(self, points, closed=False, smooth=True):
        p=curve(points,closed=closed) if smooth else np.array(points,dtype=float)
        # Only evaluate the bounding rectangle of the stroke or region.
        margin=48
        ix=np.where((self.x[0]>=p[:,0].min()-margin)&(self.x[0]<=p[:,0].max()+margin))[0]
        iy=np.where((self.y[:,0]>=p[:,1].min()-margin)&(self.y[:,0]<=p[:,1].max()+margin))[0]
        if not len(ix) or not len(iy):raise ValueError('Trace lies outside canvas')
        sl=np.s_[iy[0]:iy[-1]+1,ix[0]:ix[-1]+1]
        x,y=self.x[sl],self.y[sl]
        d=np.full(x.shape,1e12);inside=np.zeros(x.shape,bool)
        end=np.roll(p,-1,axis=0) if closed else p[1:]
        for a,b in zip(p,end):
            dx,dy=b-a;l2=dx*dx+dy*dy
            if l2<1e-12:continue
            t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/l2,0,1)
            d=np.minimum(d,(x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2)
            if closed:inside^=((a[1]>y)!=(b[1]>y))&(x<dx*(y-a[1])/(dy if abs(dy)>1e-10 else 1e-10)+a[0])
        return sl,np.sqrt(d),inside

    def region(self,name,points,depth,edge=8,base=.001,smooth=True,bulge=None):
        sl,d,inside=self._field(points,True,smooth)
        shape=np.clip(d/edge,0,1)
        shape=np.sin(shape*np.pi/2)**.65
        target=base+(depth-base)*shape
        if bulge:
            cx,cy,rx,ry,amount=bulge
            target+=amount*np.exp(-((self.x[sl]-cx)/rx)**2-((self.y[sl]-cy)/ry)**2)*shape
        self.z[sl]=np.where(inside,np.maximum(self.z[sl],target),self.z[sl])
        self.feature[sl]=np.maximum(self.feature[sl],inside*np.clip(d/6,0,1))
        self.layers.append({'name':name,'depth_m':float(depth),
                            'outline_pixels':np.asarray(points,dtype=float).tolist()})

    def stroke(self,points,width,amount,mode='add',smooth=True):
        sl,d,_=self._field(points,False,smooth)
        w=np.exp(-.5*(d/width)**2)
        if mode=='add':self.z[sl]+=amount*w
        elif mode=='max':self.z[sl]=np.maximum(self.z[sl],amount*w)
        else:raise ValueError(mode)

    def cut_region(self,name,points,depth=.001,edge=2,smooth=True):
        """A traced opening or incised region; preserve a short rounded edge."""
        sl,d,inside=self._field(points,True,smooth)
        weight=np.sin(np.clip(d/edge,0,1)*np.pi/2)**.65
        target=self.z[sl]*(1-weight)+depth*weight
        self.z[sl]=np.where(inside,np.minimum(self.z[sl],target),self.z[sl])
        self.feature[sl]=np.where(inside,self.feature[sl]*(1-weight),self.feature[sl])
        self.layers.append({'name':name,'cut_to_depth_m':float(depth),
                            'outline_pixels':np.asarray(points,dtype=float).tolist()})

    def ellipse(self,cx,cy,rx,ry,depth,base=.001,angle=0):
        a=math.radians(angle);dx=self.x-cx;dy=self.y-cy
        u=dx*math.cos(a)+dy*math.sin(a);v=-dx*math.sin(a)+dy*math.cos(a)
        rr=(u/rx)**2+(v/ry)**2
        target=base+(depth-base)*np.sqrt(np.maximum(0,1-rr))
        self.z=np.where(rr<1,np.maximum(self.z,target),self.z)
        self.feature=np.maximum(self.feature,np.clip((1-rr)*8,0,1))

    def ring(self,cx,cy,rx,ry,width,depth,start=0,end=math.tau):
        points=[(cx+rx*math.cos(a),cy+ry*math.sin(a)) for a in np.linspace(start,end,85)]
        self.stroke(points,width,depth,'max',smooth=False)

    def annulus(self,cx,cy,rx,ry,half_width,depth):
        """Rounded ring with a finite edge, avoiding a Gaussian stone halo."""
        rho=np.sqrt(((self.x-cx)/rx)**2+((self.y-cy)/ry)**2)
        d=(rho-1)*(rx+ry)*.5
        profile=np.sqrt(np.maximum(0,1-(d/half_width)**2))
        target=.001+(depth-.001)*profile
        self.z=np.maximum(self.z,target)
        self.feature=np.maximum(self.feature,np.clip((half_width-abs(d))/4,0,1))

    def leaf(self,base,tip,width,depth=.065,ground=.025):
        a,b=np.array(base),np.array(tip);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
        p=[a,a+v*.28+n*width,a+v*.67+n*width*.8,b,a+v*.67-n*width*.8,a+v*.28-n*width]
        self.region('Carved foliate leaf',[tuple(x) for x in p],depth,edge=max(width*.7,2),base=ground)
        self.stroke([a+v*.1,a+v*.9],1.0,-.0025,smooth=False)

    def flower(self,x,y,radius=16,depth=.075):
        self.ellipse(x,y,radius,radius,depth-.012)
        for a in np.linspace(0,math.tau,6,endpoint=False):
            xx=x+math.cos(a)*radius*.48;yy=y+math.sin(a)*radius*.48
            self.ellipse(xx,yy,radius*.41,radius*.41,depth,base=depth-.025)
        self.ellipse(x,y,radius*.24,radius*.24,depth+.008,base=depth-.01)

    def detail_from_shading(self,image_path,light=(-.7,-.7),amount=.7,limit=.007):
        """Regularized integration of only small-scale shading gradients.

        Large shapes remain hand-authored. Low frequency illumination, colour,
        stains and shadows are not treated as true object depth. The residual
        is limited in amplitude and restricted to the traced sculpted regions.
        """
        from PIL import Image
        im=np.asarray(Image.open(image_path).convert('RGB'),dtype=float)/255
        x=np.clip(np.round(self.x).astype(int),0,im.shape[1]-1)
        y=np.clip(np.round(self.y).astype(int),0,im.shape[0]-1)
        # Green channel reduces brown archival print tint without embedding it.
        signal=im[y,x,1]
        signal=np.pad(signal,64,mode='reflect')
        fy=np.fft.fftfreq(signal.shape[0])[:,None]*math.tau
        fx=np.fft.fftfreq(signal.shape[1])[None,:]*math.tau
        k2=fx*fx+fy*fy
        # Smooth sensor/print noise, retain wavelengths about 5–100 pixels.
        band=np.exp(-k2*1.25**2/2)-np.exp(-k2*24**2/2)
        q=-(light[0]*fx+light[1]*fy)
        transfer=(-1j*q)/(q*q+.20*k2+.0001)
        h=np.fft.ifft2(np.fft.fft2(signal)*band*transfer).real[64:-64,64:-64]
        metres_per_sample=(self.width/(self.nx-1)+self.height/(self.ny-1))/2
        h=np.clip(h*metres_per_sample*amount,-limit,limit)
        # Do not pull dark gaps, the source background, or cast shadows forward.
        valid=(self.x>=0)&(self.x<im.shape[1])&(self.y>=0)&(self.y<im.shape[0])
        gate=self.feature*np.clip((self.z-.012)/.025,0,1)*valid
        self.z+=h*gate
        return {'method':'bounded single-view shading-gradient residual on hand-authored depth regions',
                'source_image':str(image_path),'maximum_abs_m':float(abs(h*gate).max()),
                'rms_m':float(np.sqrt(np.mean((h*gate)**2))),
                'warning':'Interpretation of carving, not photogrammetric or measured depth; source colour not included'}

    def save(self,path):
        self.z=np.maximum(self.z,.001)
        np.savez_compressed(path,z=self.z.astype('float32'),width=self.width,height=self.height,
                            origin_y=self.origin_y)


def mesh_from_surface(path,name):
    from geometry import Mesh
    data=np.load(path)
    z=data['z'];ny,nx=z.shape
    xx,yy=np.meshgrid(np.linspace(-float(data['width'])/2,float(data['width'])/2,nx),
                      np.linspace(float(data['height']),0,ny)+float(data.get('origin_y',0)))
    vertices=np.stack((xx,yy,z),axis=-1).reshape(-1,3)
    j,i=np.indices((ny-1,nx-1));a=(j*nx+i).ravel()
    # Pixel Y runs down, panel Y up: reverse front-facing winding.
    faces=np.stack((a+nx,a+nx+1,a+1,a),axis=1)
    m=Mesh(name);m.add(vertices,faces)
    return m


def trim_empty_relief_background(obj,threshold=.00115,radial_limit=None):
    """Remove the empty rectangular margin of a separately mounted mask."""
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    empty=[f for f in bm.faces if max(v.co.z for v in f.verts)<threshold or
           (radial_limit is not None and any(v.co.x*v.co.x+v.co.y*v.co.y>radial_limit**2 for v in f.verts))]
    count=len(empty)
    bmesh.ops.delete(bm,geom=empty,context='FACES')
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    return count


def simplify_relief(obj,source_path,ratio=.28):
    """Reduce the regular grid while retaining the traced shape, then measure it.

    The reference NPZ is the editable high-resolution surface. This is a mesh
    approximation check only; it says nothing about accuracy against real stone.
    """
    import bpy
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector
    data=np.load(source_path);z=data['z'];ny,nx=z.shape
    before=len(obj.data.polygons)*2
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Adaptive simplification of traced surface','DECIMATE')
    mod.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)
    # A reduced flat background can contain very large triangles. Averaging its
    # normals with an adjacent steep carved edge creates false fans of shading
    # across otherwise flat stone. Split the genuinely flat backing faces.
    flat_faces=0
    for p in obj.data.polygons:
        heights=[obj.data.vertices[i].co.z for i in p.vertices]
        if max(heights)<.00115:
            p.use_smooth=False;flat_faces+=1
    tree=BVHTree.FromPolygons([v.co for v in obj.data.vertices],
                            [tuple(p.vertices) for p in obj.data.polygons])
    errors=[];spatial_errors=[];misses=0
    for j in range(1,ny-1,5):
        y=float(data['height'])*(1-j/(ny-1))+float(data.get('origin_y',0))
        for i in range(1,nx-1,4):
            x=float(data['width'])*(i/(nx-1)-.5)
            hit,normal,index,distance=tree.ray_cast(Vector((x,y,1)),Vector((0,0,-1)))
            if hit is None:misses+=1
            else:
                errors.append(abs(hit.z-float(z[j,i])))
                nearest,normal,index,distance=tree.find_nearest(Vector((x,y,float(z[j,i]))))
                spatial_errors.append(distance)
    result={'figure':obj.name,'original_triangles':before,'retained_faces':len(obj.data.polygons),
            'ratio':ratio,'flat_backing_faces':flat_faces,'samples':len(errors),'ray_misses':misses,
            'rms_error_m':float(np.sqrt(np.mean(np.array(errors)**2))),
            'p99_error_m':float(np.percentile(errors,99)),
            'max_error_m':float(max(errors)),
            'closest_surface_rms_m':float(np.sqrt(np.mean(np.array(spatial_errors)**2))),
            'closest_surface_p99_m':float(np.percentile(spatial_errors,99)),
            'closest_surface_max_m':float(max(spatial_errors)),
            'error_interpretation':'Vertical differences can be large at steep edges after tiny lateral changes; closest-surface distance measures positional approximation.'}
    obj['simplification_check']=str(result)
    print('RELIEF_SIMPLIFICATION',obj.name,result,flush=True)
    if misses or result['closest_surface_p99_m']>.0008 or result['closest_surface_max_m']>.004:
        raise RuntimeError('Relief mesh approximation exceeded its tolerance: '+str(result))
    return result
