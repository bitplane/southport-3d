"""Authored independent shell dimensions, shared by master and District."""
def world(d,p):
 u,v,z=p
 return (d['x']+.00646*u+v,d['y']+u-.00625*v,d['base_z']+z)
def roofs(d):
 h,w,l=d['hall_width'],d['width'],d['depth'];e=d['hall_eave'];r=d['hall_ridge'];be=d['bath_eave'];br=d['bath_ridge'];mid=(h+w)/2
 return [('hall front',[(0,0,e),(h,0,e),(h,4.5,r),(0,4.5,r)]),('hall back',[(0,4.5,r),(h,4.5,r),(h,9,e),(0,9,e)]),('hall dark felt',[(0,9,7.1),(h,9,7.1),(h,16,7.1),(0,16,7.1)]),('hall pale felt',[(0,16,7.1),(h,16,7.1),(h,23.2,7.1),(0,23.2,7.1)]),('Bath front pitch',[(mid,0,br),(w,0,be),(w,l,be),(mid,l,br)]),('Bath court pitch',[(h,0,be),(mid,0,br),(mid,l,br),(h,l,be)])]
