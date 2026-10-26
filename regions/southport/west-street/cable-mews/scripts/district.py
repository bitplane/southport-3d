import json,math
from blender_envelope import Surfaces

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());p=d['footprint'];s=Surfaces(['building'],lambda q:(q[0],q[1],q[2]+2.448));s.part='building'
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
  lo=d['brick_base'] if i in (0,1,7,8) else 0
  s.quad('wall '+str(i),[(b[0],b[1],lo),(a[0],a[1],lo),(a[0],a[1],d['wall_top']),(b[0],b[1],d['wall_top'])])
 # The separate large roofs retain the concave footprint without filling the court.
 from mathutils import Vector
 from mathutils.geometry import tessellate_polygon
 vv=[Vector((x,y,0)) for x,y in p]
 for i,tri in enumerate(tessellate_polygon([vv])):
  q=[vv[k] if isinstance(k,int) else k for k in tri];q=q if (q[1]-q[0]).cross(q[2]-q[0]).z>0 else list(reversed(q));s.triangle('roof '+str(i),[(v.x,v.y,d['wall_top']) for v in q])
 for j,(x,y) in enumerate([(-63.,120.2),(-64.,115.2)]):s.box('parking column '+str(j),(x-.12,y-.12,0),(x+.12,y+.12,2.8))
 x,y,r=d['tower'];n=12
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  s.quad('tower '+str(i),[(x+r*math.cos(a),y+r*math.sin(a),0),(x+r*math.cos(b),y+r*math.sin(b),0),(x+r*math.cos(b),y+r*math.sin(b),d['wall_top']+.3),(x+r*math.cos(a),y+r*math.sin(a),d['wall_top']+.3)])
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  s.triangle('tower cap '+str(i),[(x,y,d['wall_top']+.3),(x+r*math.cos(a),y+r*math.sin(a),d['wall_top']+.3),(x+r*math.cos(b),y+r*math.sin(b),d['wall_top']+.3)])
 return s.result
