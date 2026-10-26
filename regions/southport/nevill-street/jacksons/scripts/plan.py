"""Plan in Nevill site coordinates, metres; independent coarse envelope uses these controls."""
def world(d,p):
 u,v,z=p;x,y,b=d['origin'];return(x-v-.056*u,y+u,b+z)
def outline(d):
 return [(1,0),(d['width'],0),(d['width'],d['depth']),(0,d['depth']),(0,1)]
def roofs(d):
 w=d['width'];v=d['main_depth'];e=d['eave'];h=d['ridge'];a=(3.5,3.7,h);b=(6.9,3.7,h)
 return [('front',[(1,0,e),(w,0,e),b,a]),('party',[(w,0,e),(w,v,e),b]),('rear',[(w,v,e),(0,v,e),a,b]),('cable',[(0,v,e),(0,1,e),a]),('corner',[(0,1,e),(1,0,e),a]),('extension',[(0,v,4.1),(w,v,4.1),(w,d['depth'],3.8),(0,d['depth'],3.8)])]
