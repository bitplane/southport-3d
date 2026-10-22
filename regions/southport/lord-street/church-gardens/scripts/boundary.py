"""Continuous garden retaining wall: shared rings avoid overlapping curve caps."""
import math
from southport3d.geometry import Mesh


def continuous_wall(points, height, width, name):
    mesh=Mesh(name)
    normals=[]
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        normals.append((-dy/length,dx/length))
    offsets=[normals[0]]
    for a,b in zip(normals,normals[1:]):
        denom=1+a[0]*b[0]+a[1]*b[1]
        offsets.append(((a[0]+b[0])/denom,(a[1]+b[1])/denom))
    offsets.append(normals[-1])
    # One cross-section contains body, projecting coping underside and top.
    profile=[(-width/2,0),(width/2,0),(width/2,height-.07),
             (width/2+.04,height-.07),(width/2+.04,height),
             (-width/2-.04,height),(-width/2-.04,height-.07),(-width/2,height-.07)]
    vertices=[(x+nx*w,y+ny*w,z+h) for (x,y,z),(nx,ny) in zip(points,offsets) for w,h in profile]
    k=len(profile)
    faces=[tuple(reversed(range(k))),tuple(range((len(points)-1)*k,len(points)*k))]
    for i in range(len(points)-1):
        for j in range(k):
            q=(j+1)%k
            faces.append((i*k+j,i*k+q,(i+1)*k+q,(i+1)*k+j))
    mesh.add(vertices,faces)
    return mesh
