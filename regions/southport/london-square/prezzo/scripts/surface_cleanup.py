"""Remove coincident same-facing faces inside an authored component.

Keep earlier surface ownership, split later convex triangles, retain material
indices. This does not decimate, move surfaces or union separate objects, so
prototype coordinates and the LOD component boundaries remain intact.
"""
import math
from collections import defaultdict
from mathutils import Vector
import bmesh


def area(poly):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2


def halfplane(poly,a,b,inside):
    def d(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp,dq=d(p),d(q);pin=dp>=0 if inside else dp<=0;qin=dq>=0 if inside else dq<=0
        if pin:out.append(p)
        if pin!=qin:
            t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out


def subtract(poly,cutter):
    if max(p[0] for p in poly)<=min(p[0] for p in cutter)+1e-8 or min(p[0] for p in poly)>=max(p[0] for p in cutter)-1e-8 or max(p[1] for p in poly)<=min(p[1] for p in cutter)+1e-8 or min(p[1] for p in poly)>=max(p[1] for p in cutter)-1e-8:return [poly]
    remaining=poly;out=[]
    for a,b in zip(cutter,cutter[1:]+cutter[:1]):
        piece=halfplane(remaining,a,b,False)
        if len(piece)>=3 and area(piece)>1e-10:out.append(piece)
        remaining=halfplane(remaining,a,b,True)
        if len(remaining)<3:break
    return out


def clean(data):
    bm=bmesh.new();bm.from_mesh(data)
    order=bm.faces.layers.int.new('source_order')
    for i,face in enumerate(bm.faces):face[order]=i
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    # Triangulation appends triangles and can interleave different owners.
    # Restore original face priority before assigning coincident surface patches.
    bm.faces.sort(key=lambda f:f[order]);bm.faces.index_update()
    bm.faces.layers.int.remove(order);bm.to_mesh(data);bm.free();data.update()
    rows=[];groups=defaultdict(list)
    for face in data.polygons:
        n=face.normal.copy();pts=[data.vertices[i].co.copy() for i in face.vertices]
        if face.area<1e-10:continue
        dist=n.dot(pts[0]);axes=sorted(range(3),key=lambda a:abs(n[a]))[:2]
        xy=[(p[axes[0]],p[axes[1]]) for p in pts]
        signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]));flip=signed<0
        if flip:xy.reverse()
        key=(*[round(v,6) for v in n],round(dist,6));groups[key].append(len(rows));rows.append((pts,n,dist,axes,xy,flip,face.material_index))
    replacements={}
    for ids in groups.values():
        if len(ids)<2:continue
        grid=defaultdict(list)
        for i in ids:
            xy=rows[i][4];xs=[p[0] for p in xy];ys=[p[1] for p in xy]
            cells=[(x,y) for x in range(math.floor(min(xs)*2),math.floor(max(xs)*2)+1) for y in range(math.floor(min(ys)*2),math.floor(max(ys)*2)+1)]
            candidates=sorted({j for c in cells for j in grid[c]});fragments=[xy]
            for j in candidates:
                fragments=[p for f in fragments for p in subtract(f,rows[j][4])]
                if not fragments:break
            if abs(sum(area(f) for f in fragments)-area(xy))>1e-9:replacements[i]=fragments
            for c in cells:grid[c].append(i)
    if not replacements:return 0
    vertices=[];faces=[];materials=[]
    for i,(pts,n,dist,axes,xy,flip,mat) in enumerate(rows):
        for fragment in replacements.get(i,[xy]):
            if flip:fragment=list(reversed(fragment))
            other=next(a for a in range(3) if a not in axes);points=[]
            for x,y in fragment:
                p=Vector((0,0,0));p[axes[0]]=x;p[axes[1]]=y;p[other]=(dist-sum(n[a]*p[a] for a in axes))/n[other];points.append(tuple(p))
            off=len(vertices);vertices.extend(points)
            for j in range(1,len(points)-1):faces.append((off,off+j,off+j+1));materials.append(mat)
    data.clear_geometry();data.from_pydata(vertices,[],faces)
    for f,mat in zip(data.polygons,materials):f.material_index=mat
    data.update();return len(replacements)
