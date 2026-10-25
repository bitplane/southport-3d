"""Make clipped ground faces share boundary vertices before float32 export.

Independent polygon clipping creates T-junctions. A long edge and two short
edges cease to coincide after float32 rounding, exposing bright subpixel gaps
in WebGL. Snap once, insert every boundary junction and fan each convex face;
ordinary n-gon triangulators may discard the collinear junction vertices.
"""
import math
from collections import defaultdict
import numpy as np

GRID=.0001  # 0.1 mm, far below the uncertainty of the street reconstruction
TOLERANCE=.0002

def conform(meshes, preserve_triangles=False, weld_distance=0.):
    vertices=[]
    lookup={}
    polygons=[]
    weld_cells=defaultdict(list)
    def index(point):
        if weld_distance:
            cell=tuple(math.floor(float(v)/weld_distance) for v in point)
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        for i in weld_cells[(cell[0]+dx,cell[1]+dy,cell[2]+dz)]:
                            if sum((float(point[j])-vertices[i][j])**2 for j in range(3)) <= weld_distance**2:
                                return i
        key=tuple(round(float(v)/GRID) for v in point)
        if key not in lookup:
            lookup[key]=len(vertices)
            vertices.append(tuple(float(v) for v in np.asarray([v*GRID for v in key],dtype=np.float32)))
            if weld_distance:
                weld_cells[tuple(math.floor(v/weld_distance) for v in vertices[-1])].append(lookup[key])
        return lookup[key]
    for key,mesh in meshes.items():
        for face in mesh.faces:
            ids=[index(mesh.vertices[i]) for i in face]
            ids=[v for i,v in enumerate(ids) if v!=ids[i-1]]
            if len(set(ids))>=3:
                polygons.append((key,ids))
    cells=defaultdict(set)
    for i,p in enumerate(vertices):
        cells[math.floor(p[0]),math.floor(p[1])].add(i)
    edge_cache={}
    inserted=0
    for _,ids in polygons:
        for ia,ib in zip(ids,ids[1:]+ids[:1]):
            key=tuple(sorted((ia,ib)))
            if key in edge_cache:
                continue
            a=vertices[key[0]]
            b=vertices[key[1]]
            d=tuple(b[i]-a[i] for i in range(3))
            length2=sum(v*v for v in d)
            hits=[(0,key[0]),(1,key[1])]
            candidates=set()
            for x in range(math.floor(min(a[0],b[0])-TOLERANCE),math.floor(max(a[0],b[0])+TOLERANCE)+1):
                for y in range(math.floor(min(a[1],b[1])-TOLERANCE),math.floor(max(a[1],b[1])+TOLERANCE)+1):
                    candidates.update(cells[x,y])
            for i in candidates:
                if i in key:
                    continue
                p=vertices[i]
                t=sum((p[j]-a[j])*d[j] for j in range(3))/length2
                if not 1e-7<t<1-1e-7:
                    continue
                error=sum((p[j]-a[j]-t*d[j])**2 for j in range(3))
                if error<TOLERANCE*TOLERANCE:
                    hits.append((t,i))
            hits.sort()
            edge_cache[key]=[i for _,i in hits]
            inserted+=len(hits)-2
    result={key:type(mesh)(mesh.name) for key,mesh in meshes.items()}
    removed=0
    for key,ids in polygons:
        boundary=[]
        for a,b in zip(ids,ids[1:]+ids[:1]):
            edge=edge_cache[tuple(sorted((a,b)))]
            edge=edge if edge[0]==a else list(reversed(edge))
            boundary.extend(edge[:-1])
        if preserve_triangles and len(boundary)==3:
            # A triangle with no inserted edge junction needs no centroid fan.
            # Keep the default for legacy recipes with fixed topology checks.
            tri=[vertices[i] for i in boundary]
            u=[tri[1][j]-tri[0][j] for j in range(3)]
            v=[tri[2][j]-tri[0][j] for j in range(3)]
            cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            if sum(x*x for x in cross)>=1e-18:
                result[key].add(tri,[(0,1,2)])
            else:removed+=1
            continue
        centre=tuple(float(v) for v in np.asarray([sum(vertices[i][j] for i in ids)/len(ids) for j in range(3)],dtype=np.float32))
        for a,b in zip(boundary,boundary[1:]+boundary[:1]):
            if a==b:
                continue
            p,q=vertices[a],vertices[b]
            u=[p[i]-centre[i] for i in range(3)]
            v=[q[i]-centre[i] for i in range(3)]
            cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            if sum(x*x for x in cross)<1e-18:
                removed+=1
                continue
            result[key].add([centre,p,q],[(0,1,2)])
    return result,{'grid_m':GRID,'unique_boundary_vertices':len(vertices),'inserted_edge_junctions':inserted,'discarded_zero_area_triangles':removed}
