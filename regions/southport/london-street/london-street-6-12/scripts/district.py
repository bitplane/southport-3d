"""Fixed block envelope with the registered rear court and neighbour stair cutouts."""
import json
from mathutils import Vector
from blender_envelope import Surfaces
from southport3d.planar import subtract, area
from roof import roof_planes, roof_height


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());base=d['base_z']
    s=Surfaces(['architecture','roof','shopfront','rear'],lambda p:(p[0],p[1],p[2]+base))
    xf,xr=d['front_x'],d['rear_x'];ys,yn=d['south_y'],d['north_y'];ur=d['upper_rear_x'];rn=d['rear_wall_north_y'];e=d['eaves_height']
    h=lambda x,y:roof_height(d,x,y)-base-.14
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('front upper',(xf,ys),(xf,yn),3.45,e)
    wall('Glebe low service band',(xr,ys),(ur,ys),3.45,4.65)
    cuts=[ur,xf];planes=roof_planes(d)[2]
    for p in planes:
        for q in planes:
            if abs(p[0]-q[0])>1e-10:
                x=-((p[1]-q[1])*ys+p[2]-q[2])/(p[0]-q[0])
                if ur<x<xf:cuts.append(x)
    cuts=sorted({round(x,8) for x in cuts})
    for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
        s.quad('Glebe hip wall '+str(j),[(a,ys,3.45),(b,ys,3.45),(b,ys,h(b,ys)),(a,ys,h(a,ys))])
    path=d['north_boundary']
    for i,(a,b) in enumerate(zip(path,path[1:])):s.quad('stepped party '+str(i),[(*a,0),(*b,0),(*b,h(*b)),(*a,h(*a))])
    s.part='roof'
    # Use only the shared analytic planes, not build_roof or a detailed mesh.
    # Clip these bounded polygons against the established courtyard cutouts.
    points,faces,planes=roof_planes(d)
    for i,(face,plane) in enumerate(zip(faces,planes)):
        pieces=[[points[k][:2] for k in face]]
        for x0,x1,y0,y1 in d['roof_cutouts']:
            cut=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            pieces=[q for p in pieces for q in subtract(p,cut)]
        for j,p in enumerate(pieces):
            # Clipping can leave collinear repeated vertices: remove them before
            # triangulating so float32 export never emits degenerate faces.
            changed=True
            while changed and len(p)>3:
                changed=False
                for k in range(len(p)):
                    if area([p[k-1],p[k],p[(k+1)%len(p)]])<1e-8:p.pop(k);changed=True;break
            for k in range(1,len(p)-1):
                q=[p[0],p[k],p[k+1]]
                if (q[1][0]-q[0][0])*(q[2][1]-q[0][1])-(q[1][1]-q[0][1])*(q[2][0]-q[0][0])<0:q.reverse()
                s.triangle(f'hip {i} {j} {k}',[(x,y,plane[0]*x+plane[1]*y+plane[2]-base) for x,y in q])
    s.part='shopfront'
    wall('Glebe ground',(xr,ys),(xf,ys),0,3.45)
    # Preserve the central Halifax door recess, not a filled glass facade.
    a,b=ys+6.95,ys+9.8
    wall('shop left',(xf,ys),(xf,a),0,3.45)
    wall('shop right',(xf,b),(xf,yn),0,3.45)
    wall('entrance fascia',(xf,a),(xf,b),3.09,3.45)
    wall('entrance leaf',(xf-.65,a),(xf-.65,b),0,3.09)
    for y in (a,b):wall('entrance return '+str(y),(xf-.65,y),(xf,y),0,3.09)
    s.quad('entrance soffit',[(xf-.65,a,3.09),(xf-.65,b,3.09),(xf,b,3.09),(xf,a,3.09)])
    s.part='rear'
    # Rear upper return crosses a hip seam: split where analytic planes meet.
    breaks=[ys+.36,-55.7,rn]
    planes=roof_planes(d)[2]
    for p in planes:
        for q in planes:
            if abs(p[1]-q[1])>1e-10:
                y=-((p[0]-q[0])*ur+p[2]-q[2])/(p[1]-q[1])
                if ys+.36<y<rn:breaks.append(y)
    breaks=sorted({round(y,8) for y in breaks})
    for i,(a,b) in enumerate(zip(breaks,breaks[1:])):
        lo=4.65 if (a+b)/2<-55.7 else 0
        s.quad('upper rear '+str(i),[(ur,b,lo),(ur,a,lo),(ur,a,h(ur,a)),(ur,b,h(ur,b))])
    for name,ya,yb,height,x in [('rooflight',-55.7,rn,3.85,xr),('south',ys,-59.2,4.65,xr),('yard bay',-59.2,-55.7,4.65,xr+1.6)]:
        omit={'rooflight':('bottom','right','rear'), 'south':('bottom','right','front','rear'), 'yard bay':('bottom','right','front','rear')}[name]
        s.box('service '+name,(x,ya,0),(ur,yb,height),omit=omit)
    wall('rooflight exposed end',(xr,-55.7),(xr+1.6,-55.7),0,3.85)
    wall('south yard return',(xr+1.6,-59.2),(xr,-59.2),0,4.65)
    wall('yard bay upper join',(ur,-55.7),(xr+1.6,-55.7),3.85,4.65)
    s.box('yard wall',(xr,-59.2,0),(xr+.32,-55.7,2.38),omit=('bottom',))
    s.quad('yard floor',[(xr+.32,-59.2,0),(xr+1.6,-59.2,0),(xr+1.6,-55.7,0),(xr+.32,-55.7,0)])
    y=d['rear_chimney_y']
    s.box('chimney',(-25.625,y-.4,4.15),(-24.675,y+.4,11.78),omit=('bottom',))
    s.box('flue',(-25.26,y-.11,11.78),(-25.04,y+.11,12.2),omit=('bottom',),cage=.08)
    # Four coarse rooflight planes; roof rails and ladder remain open by omission.
    x,y,z=-27.2,-49.5,3.95
    p=[(x-1.35,y-1.35,z),(x+1.35,y-1.35,z),(x+1.35,y+1.35,z),(x-1.35,y+1.35,z)]
    for j in range(4):s.triangle('rooflight '+str(j),[p[j],p[(j+1)%4],(x,y,z+.75)])
    return s.result
