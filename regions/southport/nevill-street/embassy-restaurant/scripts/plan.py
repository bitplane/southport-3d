"""Metric Embassy frame: u up Nevill, v east along Stanley. Estimated dimensions."""
def world(d,p):
 u,v,z=p
 return (d['x']+.00646*u+v,d['y']+u-.00625*v,d['base_z']+z)
def outline(d):
 return [(d['chamfer_u'],0),(d['width'],0),(d['width'],d['depth']),(0,d['depth']),(0,d['chamfer_v'])]
def roof(d):
 w,l,e,r=d['width'],d['depth'],d['eave'],d['ridge'];a=d['chamfer_u'];b=d['chamfer_v'];hip=4.8
 A=(a,0,e);B=(w,0,e);C=(w,l,e);D=(0,l,e);E=(0,b,e);P=(w/2,hip,r);Q=(w/2,l,r)
 return [('front',[A,B,P]),('party',[B,C,Q,P]),('stanley',[E,P,Q,D]),('corner',[A,P,E])]
