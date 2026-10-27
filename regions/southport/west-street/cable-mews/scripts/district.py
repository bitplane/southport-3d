import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());p=d['footprint'];s=Surfaces(['building'],lambda q:(q[0],q[1],q[2]+2.448));s.part='building'
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
  lo=d['brick_base'] if i in (0,1,6,7,8) else 0
  if i==2:
   dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
   A=(a[0]-nx,a[1]-ny);B=(b[0]-nx,b[1]-ny)
   s.quad('wall lower 2',[(b[0],b[1],lo),(a[0],a[1],lo),(a[0],a[1],9),(b[0],b[1],9)])
   s.quad('wall upper 2',[(B[0],B[1],9),(A[0],A[1],9),(A[0],A[1],d['wall_top']),(B[0],B[1],d['wall_top'])])
  else:s.quad('wall '+str(i),[(b[0],b[1],lo),(a[0],a[1],lo),(a[0],a[1],d['wall_top']),(b[0],b[1],d['wall_top'])])
 # The separate large roofs retain the concave footprint without filling the court.
 from mathutils import Vector
 from mathutils.geometry import tessellate_polygon
 a,b=p[2],p[3];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);normal=(-dy/length,dx/length)
 A=(a[0]-normal[0],a[1]-normal[1]);B=(b[0]-normal[0],b[1]-normal[1])
 roof_p=p[:];roof_p[2]=A;roof_p[3]=B
 vv=[Vector((x,y,0)) for x,y in roof_p]
 for i,tri in enumerate(tessellate_polygon([vv])):
  q=[vv[k] if isinstance(k,int) else k for k in tri];q=q if (q[1]-q[0]).cross(q[2]-q[0]).z>0 else list(reversed(q));s.triangle('roof '+str(i),[(v.x,v.y,d['wall_top']) for v in q])
 for j,(x,y) in enumerate([(-63.,120.2),(-64.,115.2)]):s.box('parking column '+str(j),(x-.12,y-.12,0),(x+.12,y+.12,2.8))
 # Fixed coarse gate preserves its silhouette independently of bar count.
 gx=-59.;gy=[104.65,107.,109.85,112.7,114.75];gz=2.14157-2.448
 for j,y in enumerate(gy):s.box('gate post '+str(j),(gx-.05,y-.05,gz-.12),(gx+.05,y+.05,gz+1.92))
 for j,(lo,hi) in enumerate(zip(gy,gy[1:])):
  lo+=.05;hi-=.05
  for k,z in enumerate((.07,1.8)):s.box('gate rail '+str(j)+' '+str(k),(gx-.018,lo,gz+z-.018),(gx+.018,hi,gz+z+.018))
  for k,t in enumerate((1/3,2/3)):
   y=lo+(hi-lo)*t;s.box('gate bar '+str(j)+' '+str(k),(gx-.018,y-.016,gz+.088),(gx+.018,y+.016,gz+1.782))
 x,y,r=d['tower'];n=12
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  s.quad('tower '+str(i),[(x+r*math.cos(a),y+r*math.sin(a),0),(x+r*math.cos(b),y+r*math.sin(b),0),(x+r*math.cos(b),y+r*math.sin(b),d['wall_top']+.3),(x+r*math.cos(a),y+r*math.sin(a),d['wall_top']+.3)])
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  s.triangle('tower cap '+str(i),[(x,y,d['wall_top']+.3),(x+r*math.cos(a),y+r*math.sin(a),d['wall_top']+.3),(x+r*math.cos(b),y+r*math.sin(b),d['wall_top']+.3)])
 return s.result
