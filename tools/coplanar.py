"""Coplanar triangle overlap audit for explicitly selected exterior surfaces.

Same-facing triangles within tolerance are clipped in their dominant projection.
Touching edges have zero area. Opposing internal seams are excluded. This detects
geometric causes of z-fighting, not every camera/driver depth-buffer artefact.
"""
import numpy as np


def overlap_area(a,b):
    def cross(u,v):return u[0]*v[1]-u[1]*v[0]
    out=[p for p in a]
    if cross(b[1]-b[0],b[2]-b[0])<0:b=b[::-1]
    for p,q in zip(b,np.roll(b,-1,axis=0)):
        old=out;out=[]
        if not old:break
        for s,t in zip(old,old[1:]+old[:1]):
            ds=cross(q-p,s-p);dt=cross(q-p,t-p)
            if ds>=-1e-10:out.append(s)
            if (ds>0 and dt<0) or (ds<0 and dt>0):out.append(s+(t-s)*ds/(ds-dt))
    if len(out)<3:return 0.
    return abs(sum(cross(p,q) for p,q in zip(out,out[1:]+out[:1])))/2


def overlaps(triangles,labels,tolerance=2e-5,min_area=1e-6):
    tri=np.asarray(triangles,dtype=float)
    if not len(tri):return []
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
    normals/=np.maximum(length[:,None],1e-30)
    low=tri.min(axis=1);high=tri.max(axis=1);found=[]
    # Normal buckets avoid quadratic comparisons across differently oriented walls.
    buckets={}
    for i,n in enumerate(normals):
        if length[i]>min_area*2:buckets.setdefault(tuple(np.round(n,4)),[]).append(i)
    for group in buckets.values():
        ids=np.asarray(group)
        for k,i in enumerate(ids):
            js=ids[k+1:]
            mask=np.all(high[js]>=low[i]-tolerance,axis=1)&np.all(low[js]<=high[i]+tolerance,axis=1)
            js=js[mask]
            for j in js:
                if np.max(np.abs((tri[j]-tri[i,0])@normals[i]))>tolerance:continue
                axis=int(np.argmax(abs(normals[i])));axes=[v for v in range(3) if v!=axis]
                area=overlap_area(tri[i][:,axes],tri[j][:,axes])/abs(normals[i,axis])
                if area>min_area:found.append((labels[i],labels[j],float(area)))
    return found


def check_blender(objects):
    triangles=[];labels=[]
    for ob in objects:
        ob.data.calc_loop_triangles()
        for t in ob.data.loop_triangles:
            triangles.append([tuple(ob.matrix_world@ob.data.vertices[i].co) for i in t.vertices])
            labels.append(ob.name)
    errors=overlaps(triangles,labels)
    if errors:raise AssertionError('Coplanar exterior overlap: '+repr(errors[:12]))
