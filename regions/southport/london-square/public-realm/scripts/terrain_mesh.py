"""Split authored ground/kerb faces at measured terrain breaks, retaining offsets.

Only ground recipes call this. Pools remain horizontal and furniture generators
place rigid components at explicit anchors; neither passes through this helper.
"""


def lift_relative_triangle(triangle,field):
    points=[tuple(p)for p in triangle]
    offsets=[p[2]-field.height(*p[:2])for p in points]
    a,b,c=points
    det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if abs(det)>1e-10:
        for tri in field.lift_triangle([p[:2]for p in points]):
            out=[]
            for x,y,z in tri:
                u=((x-a[0])*(c[1]-a[1])-(y-a[1])*(c[0]-a[0]))/det
                v=((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))/det
                out.append((x,y,z+offsets[0]*(1-u-v)+offsets[1]*u+offsets[2]*v))
            signed=(out[1][0]-out[0][0])*(out[2][1]-out[0][1])-(out[1][1]-out[0][1])*(out[2][0]-out[0][0])
            if signed*det<0:out.reverse()
            yield out
        return
    # Vertical kerb faces have zero XY area. Split along their horizontal extent
    # while interpolating relative height, retaining the original face winding.
    axis=max(range(2),key=lambda k:max(p[k]for p in points)-min(p[k]for p in points))
    low=min(points,key=lambda p:p[axis]);high=max(points,key=lambda p:p[axis])
    if high[axis]-low[axis]<1e-10:return
    pieces=[[(p[0],p[1],offset)for p,offset in zip(points,offsets)]]
    for cut in list(field.edge_points(low,high))[1:-1]:
        divided=[]
        for poly in pieces:
            values=[p[axis]-cut[axis]for p in poly]
            if min(values)>=-1e-10 or max(values)<=1e-10:
                divided.append(poly);continue
            for side in [-1,1]:
                result=[]
                for p,q in zip(poly,poly[1:]+poly[:1]):
                    dp,dq=side*(p[axis]-cut[axis]),side*(q[axis]-cut[axis])
                    if dp>=0:result.append(p)
                    if dp*dq<0:
                        t=dp/(dp-dq);result.append(tuple(p[k]+t*(q[k]-p[k])for k in range(3)))
                if len(result)>=3:divided.append(result)
        pieces=divided
    for poly in pieces:
        for i in range(1,len(poly)-1):
            yield [(x,y,field.height(x,y)+z)for x,y,z in [poly[0],poly[i],poly[i+1]]]
