"""Measured building plan; fixed ring roof and envelope independent of decoration."""
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(p,holes):
 out=[p]
 for h in holes:out=[q for a in out for q in subtract(a,h)]
 return out

def transform(d,p):
 x,y,z=p;u=x/d['front_width'];v=y/d['depth'];a,b,c,e=d['footprint']
 return ((1-v)*((1-u)*a[0]+u*b[0])+v*((1-u)*e[0]+u*c[0]),(1-v)*((1-u)*a[1]+u*b[1])+v*((1-u)*e[1]+u*c[1]),z+d['floor_z'])

def roofs(d):
 w=d['front_width'];dep=d['depth'];a,b,c,e=d['court'];z=d['eaves'];h=d['ridge'];rz=d['rear_eaves'];rh=d['rear_ridge']
 # A continuous ring roof with authored ridges and hips; courtyard remains open.
 # Main range occupies front 15m; north/south longitudinal wings border court.
 ring=[(0,0,z),(w,0,z),(w,dep,rz),(0,dep,rz)]
 inner=[(a,b,z),(c,b,z),(c,e,rz),(a,e,rz)]
 ridge=[(4.5,6.8,h),(w-4.5,6.8,h),(w-4.5,dep-5.5,rh),(4.5,dep-5.5,rh)]
 out=[]
 for i in range(4):
  j=(i+1)%4
  out.append((f'outer slope {i}',[ring[i],ring[j],ridge[j],ridge[i]]))
  out.append((f'inner slope {i}',[ridge[i],ridge[j],inner[j],inner[i]]))
 return out

def elevations(d):
 w=d['front_width'];dep=d['depth'];a,b,c,e=d['court'];lo=d['foundation_z']-d['floor_z'];z=d['eaves'];rz=d['rear_eaves']
 return [('north',(0,dep),(0,0),rz,z),('rear',(w,dep),(0,dep),rz,rz),('arcade',(w,0),(w,dep),z,rz),('court-front',(c,b),(a,b),z,z),('court-north',(a,b),(a,e),z,rz),('court-rear',(a,e),(c,e),rz,rz),('court-south',(c,e),(c,b),rz,z)]
