"""Measured main dimensions; separate fixed District topology consumes these only."""
def world(d,p):
 u,v,z=p;x,y,b=d['origin'];return(x-v,y+u,b+z)
def outline(d):
 w=d['width'];l=d['depth'];a=d['wing_width'];b=d['wing_depth']
 return [(0,0),(w,0),(w,l),(a,l),(a,b),(0,b)]
def roofs(d):
 w=d['width'];l=d['main_depth'];r=d['ridge_v'];e=d['eave'];t=d['ridge'];a=d['wing_width'];b=d['wing_depth'];back=d['depth']
 return [('front slate',[(-.10,-.16,e-.06),(w+.10,-.16,e-.06),(w+.10,r,t),(-.10,r,t)]),('rear slate',[(-.10,r,t),(w+.10,r,t),(w+.10,l,e),(-.10,l,e)]),('rear lower lean-to',[(a,l,4.85),(w,l,4.85),(w,back,4.1),(a,back,4.1)]),('rear wing slate',[(0,l,4.85),(a,l,4.85),(a,b,4.25),(0,b,4.25)])]
def bay_line(c,w,depth):return [(c-w/2,0),(c-w/2+.25,-depth),(c+w/2-.25,-depth),(c+w/2,0)]
