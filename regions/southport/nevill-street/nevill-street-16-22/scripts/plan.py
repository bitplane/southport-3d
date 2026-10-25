"""Authored measured plan. Local u follows Nevill towards Lord Street, v rearward."""
def world(d,p):
 u,v,z=p
 return(d['x']+v-.0003*u,d['y']-u+.0125*v,d['base_z']+z)

def outline(d):
 w,l,c=d['width'],d['depth'],d['chamfer']
 return[(c,0),(w,0),(w,l),(0,l),(0,c)]

def roof(d):
 w,l,c=d['width'],d['depth'],d['chamfer'];e=d['front_eave'];r=d['ridge'];b=d['rear_eave'];v=d['ridge_v'];h=d['hip_run']
 # Unequal pitches: shallow lead front, steep slate rear, hipped Stanley end.
 return [('front',[(c,0,e),(w,0,e),(w,v,r),(h,v,r)]),
 ('rear',[(w,l,b),(0,l,b),(h,v,r),(w,v,r)]),
 ('hip',[(0,c,e),(c,0,e),(h,v,r),(0,l,b)])]
