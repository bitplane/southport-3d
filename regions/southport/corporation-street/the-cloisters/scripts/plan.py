def world(d,p):
 u,v,z=p
 return (d['x']+v,d['y']-u,d['base_z']+z)
def roofs(d):
 w,l,e,r=d['width'],d['depth'],d['eave'],d['ridge']
 return [('front pitch',[(0,0,e),(w,0,e),(w,3.8,r),(0,3.8,r)]),('front back pitch',[(0,3.8,r),(w,3.8,r),(w,7.6,e),(0,7.6,e)]),('middle pitch',[(0,7.6,e),(w,7.6,e),(w,11.2,13.9),(0,11.2,13.9)]),('middle back pitch',[(0,11.2,13.9),(w,11.2,13.9),(w,14.8,e),(0,14.8,e)]),('rear lower terrace',[(3.8,14.8,9.9),(w,14.8,9.9),(w,l,9.9),(3.8,l,9.9)]),('rear corner pitch',[(0,14.8,e),(3.8,14.8,e),(3.8,16.55,12.8),(0,16.55,12.8)]),('rear corner back',[(0,16.55,12.8),(3.8,16.55,12.8),(3.8,l,e),(0,l,e)])]
