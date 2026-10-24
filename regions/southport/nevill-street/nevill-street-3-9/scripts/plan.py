"""Shared measured envelope controls, without decorative topology."""

def world(d,p):
 u,v,z=p; x,y,b=d['origin']
 return (x+.0135*u-v,y+u-.02087*v,z+b)

def footprint(d):
 W=d['width'];L=d['depth'];a,b,c,e,h,r=d['rear_wing'];q,Q,v,V,hh,rr=d['low_rear']
 return [(0,0),(W,0),(W,e),(a,e),(a,L),(Q,L),(Q,V),(0,V)]

def roof_faces(d):
 W=d['width'];L=d['depth'];e=d['roof_eave'];r=d['roof_top'];i=d['roof_inset']
 # Truncated hip roof visible in the overhead and four oblique captures.
 A=(.08,.08,e);B=(W-.08,.08,e);C=(W-.08,L-.08,e);D=(.08,L-.08,e)
 a=(i,i,r);b=(W-i,i,r);c=(W-i,L-i,r);dd=(i,L-i,r)
 return [('front slope',[A,B,b,a]),('right hip',[B,C,c,b]),('back slope',[C,D,dd,c]),('left hip',[D,A,a,dd]),('upper deck',[a,b,c,dd])]

def wing_roof(spec):
 a,b,c,e,h,r=spec;mid=(a+b)/2;h+=.08;r+=.08
 return [[(a,c,h),(mid,c,r),(mid,e,r),(a,e,h)],[(mid,c,r),(b,c,h),(b,e,h),(mid,e,r)]]
