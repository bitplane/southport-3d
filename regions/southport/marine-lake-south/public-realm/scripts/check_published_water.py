"""Complete published Marine Lake water coverage at all three levels."""
import json,sys,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5];sys.path[:0]=[str(R/'tools'),str(R/'regions/southport/lord-street/corridor-public-realm/scripts')]
from audit_published_coplanar import primitives
from plan_geometry import Plan
from southport3d.elevation import Elevations
D=json.load(open(R/'regions/southport/marine-lake-south/public-realm/research/layout.json'));cat=json.load(open(R/'dist/catalog.json'));P=Plan()
def area(g):return sum(abs(sum(x*y2-x2*y for (x,y),(x2,y2)in zip(t,t[1:]+t[:1])))/2 for t in P.triangles(g))
expected=area(P.difference(P.polygons([D['lake_outline']]),P.polygons(D['lake_islands'])))
def inside(p,poly):
 x,y=p;v=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if(a[1]>y)!=(b[1]>y)and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:v=not v
 return v
c,s=math.cos(math.radians(43.5293)),math.sin(math.radians(43.5293));results={}
for level in ['detail','walk','district']:
 rows=[]
 for a in cat['assets']:
  if a['id']not in ['southport.marine-lake-south.public-realm','southport.marine-drive.public-realm']:continue
  for part in a['parts']:
   if part['id']=='lake-water':
    assert not part.get('ground')
    for t,meta in primitives(R/'dist'/part['levels'][level]['uri'],a):rows.append(t)
 t=np.concatenate(rows);xy=np.stack([t[:,:,0]*c-t[:,:,2]*s,-t[:,:,0]*s-t[:,:,2]*c],axis=2);u=xy[:,1]-xy[:,0];v=xy[:,2]-xy[:,0];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];actual=float(abs(det).sum()/2);assert abs(actual-expected)<.5,(expected,actual)
 water=Elevations(R/'regions/southport/elevation/marine-lake-south.json').surface('south-water').height(-300,400)
 assert float(abs(t[:,:,1]-water).max())<1e-5
 count=0
 for x in np.arange(-515,1390,10):
  for y in np.arange(325,930,10):
   p=[x+.371,y+.183]
   if not inside(p,D['lake_outline'])or any(inside(p,i)for i in D['lake_islands']):continue
   q=np.array(p)-xy[:,0];U=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;V=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
   assert ((U>=-1e-7)&(V>=-1e-7)&(U+V<=1+1e-7)).any(),(level,p,'water hole');count+=1
 results[level]={'source_water_area_m2':expected,'exported_water_area_m2':actual,'difference_m2':actual-expected,'covered_grid_points':count,'water_is_nonwalkable':True}
out=R.parent/'output/lake-south/water-coverage.json';out.write_text(json.dumps(results,indent=2)+'\n');print(results);P.close()
