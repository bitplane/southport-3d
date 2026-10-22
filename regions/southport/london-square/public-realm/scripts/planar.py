"""Convex planar clipping for mutually exclusive pavement/paint surfaces."""
def area(poly):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2

def halfplane(poly,a,b,inside=True):
    def d(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp,dq=d(p),d(q);pin=dp>=0 if inside else dp<=0;qin=dq>=0 if inside else dq<=0
        if pin:result.append(p)
        if pin!=qin:
            t=dp/(dp-dq);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return result

def subtract(poly,cutter):
    """Return disjoint convex fragments of poly minus a CCW convex cutter."""
    if not poly:return []
    if max(p[0] for p in poly)<=min(p[0] for p in cutter) or min(p[0] for p in poly)>=max(p[0] for p in cutter) or max(p[1] for p in poly)<=min(p[1] for p in cutter) or min(p[1] for p in poly)>=max(p[1] for p in cutter):return [poly]
    remaining=poly;out=[]
    for a,b in zip(cutter,cutter[1:]+cutter[:1]):
        piece=halfplane(remaining,a,b,False)
        if len(piece)>=3 and area(piece)>1e-9:out.append(piece)
        remaining=halfplane(remaining,a,b)
        if len(remaining)<3:break
    return out
