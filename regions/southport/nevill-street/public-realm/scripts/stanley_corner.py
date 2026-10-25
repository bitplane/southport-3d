"""Bounded Stanley/Cable junction replacement, retaining old outer ownership.

Every visible boundary, kerb and stripe comes from one measured kerb trace.
The rectangular work window is a cut only: it never receives a painted edge.
"""
import json,sys
from southport3d.planar import subtract
from southport3d.road import parallel,clip_segment

def replace(root,repo,rows,verticals,surface,grade):
 sys.path.insert(0,str(repo/'regions/southport/lord-street/corridor-public-realm/scripts'))
 from plan_geometry import Plan
 d=json.loads((root/'research/stanley-corner.json').read_text());bounds=d['bounds'];x0,y0,x1,y1=bounds;cut=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 p=Plan();old=list(rows);domain=p.intersection(p.polygons([row[1] for row in old]),p.polygons([cut]));rows.clear()
 for name,poly,mat,priority,z in old:
  for piece in subtract(poly,cut):rows.append((name,piece,mat,priority,z))
 # Retain only the old kerb segments outside this bounded work window.
 keep=[]
 for a,b in verticals:
  clipped=clip_segment(a,b,bounds)
  if clipped is None:keep.append((a,b));continue
  aa,bb=clipped
  if sum((a[i]-aa[i])**2 for i in (0,1))>1e-12:keep.append((a,aa))
  if sum((b[i]-bb[i])**2 for i in (0,1))>1e-12:keep.append((bb,b))
 verticals[:]=keep
 def add(name,poly,mat,priority=0,road=False):
  for tri in p.triangles(p.intersection(p.polygons([poly]),domain)):
   surface(name,tri,mat,priority,lambda x,y:grade(y)-(.12 if road else 0))
 for tri in p.triangles(domain):surface('Stanley corner paving',tri,'paving',20)
 curves=d['curves'];south,north,ws,wn=[curves[k] for k in ['stanley_south','stanley_north','cable_south','cable_north']]
 main=[ws[-1],south[0],north[-1],wn[0]]
 add('Stanley junction main road',main,'asphalt',125,True)
 add('Stanley flared mouth',south+list(north)+[(-2,116),(-2,91)],'asphalt',126,True)
 add('Cable flared mouth',wn+list(ws)+[(4,91),(4,116)],'asphalt',127,True)
 for key,curve in curves.items():
  # Directed curves have road to their left, pavement to their right.
  cap=parallel(curve,-.18);unit=parallel(curve,-1);red=[];red_inner=[]
  for i,(a,n) in enumerate(zip(curve,unit)):
   at_main=(i==0 and key in ('stanley_south','cable_north')) or (i==len(curve)-1 and key in ('stanley_north','cable_south'))
   at_side=i in (0,len(curve)-1) and not at_main
   inner=.32 if at_main else .18;outer=.77 if at_main else (.18 if at_side else (1.0 if key=='cable_north' else 2.25))
   red_inner.append(tuple(a[j]+inner*(n[j]-a[j]) for j in (0,1)))
   red.append(tuple(a[j]+outer*(n[j]-a[j]) for j in (0,1)))
  for i,(a,b) in enumerate(zip(curve,curve[1:])):
   add('Stanley kerb cap',[a,b,cap[i+1],cap[i]],'kerb',180)
   add('Stanley red apron',[red_inner[i],red_inner[i+1],red[i+1],red[i]],'brick',142)
   verticals.append((a,b))
  for inside in (.185,.365):
   aa=parallel(curve,inside-.035);bb=parallel(curve,inside+.035)
   for i in range(len(curve)-1):add('Stanley continuous double yellow',[aa[i],aa[i+1],bb[i+1],bb[i]],'yellow',300,True)
 # Buff tactile pads are observed at the two Stanley mouth corners. The
 # positions/lengths remain visual estimates, not a current accessibility survey.
 for q in d['tactile']:add('Stanley tactile',q,'tactile',210)
 # Give-way teeth and transverse dashes visible on the Nevill approaches.
 for y in (98.2,103.7):
  for x in (-.5,1.1,2.7):add('Stanley worn give way',[(x,y),(x+.70,y),(x+.70,y+.12),(x,y+.12)],'white',310,True)
 p.close()
