"""Bounded, mutually exclusive street surfaces for the Lord Street block plan."""
import bpy,bmesh,json,math,os,sys
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(ROOT/'scripts')]
from southport3d.geometry import Mesh
from southport3d.planar import subtract,halfplane,area
import southport3d.conform as conforming
# GEOS has already snapped/noded boundaries before float32 export. Do not pull nearby
# distinct edges into the same edge: that creates skinny overlapping fans.
conforming.TOLERANCE=1e-7
conforming.GRID=1e-6
conform=conforming.conform
from datum import grade,SURFACE
D=json.loads((ROOT/'research/layout.json').read_text())
BLOCKS=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/D['block_plan']).read_text())
D['building_cutouts'] += [{'id':b['id'],'polygon':b['footprint']} for b in BLOCKS['blocks']]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
colours={'paving':(.48,.46,.41),'asphalt':(.085,.092,.093),'lawn':(.16,.25,.10),'kerb':(.40,.40,.37),'pattern':(.32,.37,.34)}
mats={}
for name,c in colours.items():
 m=bpy.data.materials.new('Provisional '+name);m.use_nodes=True;m.diffuse_color=(*c,1)
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;mats[name]=m

def rect(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def clean(p):
 q=[]
 for v in p:
  v=tuple(v)
  if not q or math.dist(v,q[-1])>1e-7:q.append(v)
 if len(q)>1 and math.dist(q[0],q[-1])<1e-7:q.pop()
 return q

def triangles(p):
 p=clean(p)
 if len(p)<3 or area(p)<1e-6:return []
 if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))<0:p.reverse()
 if all((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])>=-1e-8 for a,b,c in zip(p,p[1:]+p[:1],p[2:]+p[:2])):return [p]
 out=[]
 for t in tessellate_polygon([[Vector((x,y,0)) for x,y in p]]):
  q=[p[i] if isinstance(i,int) else (i.x,i.y) for i in t]
  if area(q)>1e-6:out.append(q)
 return out

def bbox(p):return (min(x for x,y in p),max(x for x,y in p),min(y for x,y in p),max(y for x,y in p))
def overlap(a,b):return a[0]<b[1] and a[1]>b[0] and a[2]<b[3] and a[3]>b[2]
def clipbox(p,bb):
 for a,b in zip(rect(*bb),rect(*bb)[1:]+rect(*bb)[:1]):p=halfplane(p,a,b)
 return clean(p)
rows=[]
def surface(p,mat,priority):
 for q in triangles(p):rows.append((q,mat,priority,bbox(q)))
def ribbon(points,width,mat,priority,road=False):
 points=[tuple(v) for v in points]
 if road:
  # Insert exact existing tile seams before offsetting the running road.
  refined=[]
  for a,b in zip(points,points[1:]):
   refined.append(a)
   if abs(b[0]-a[0])>.01:
    for x in sorted([x for x in [-160,-136,218,245] if min(a[0],b[0])<x<max(a[0],b[0])],reverse=b[0]<a[0]):
     t=(x-a[0])/(b[0]-a[0]);refined.append((x,a[1]+t*(b[1]-a[1])))
  refined.append(points[-1]);points=[]
  for x,y in refined:
   if 20<y<32:
    weight=max(0,min(1,(x+160)/24,(245-x)/27))
    y=y*(1-weight)+26*weight
   points.append((x,y))
 for a,b in zip(points,points[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
  if l<1e-5:continue
  nx,ny=-dy/l*width/2,dx/l*width/2
  surface([(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],mat,priority)
 # Fill bends and connected mouths. These are width estimates, not surveyed kerbs.
 for x,y in points:
  if -815<x<605 and -50<y<80:
   surface([(x+width/2*math.cos(i*math.tau/12),y+width/2*math.sin(i*math.tau/12)) for i in range(12)],mat,priority)

for g in D['landscaped_areas']:surface(g['polygon'],'lawn',10)
for p in D['paths']:ribbon(p['points'],p['width_m'],'paving',20)
for r in D['roads']:ribbon(r['points'],r['width_m'],'asphalt',100,road=r['tags'].get('highway')=='trunk' and r['tags'].get('name')=='Lord Street' and not r['tags'].get('oneway')=='yes')
# Existing owners and all foundations are hard exclusions at every material level.
cutters=[]
for r in D['excluded_rectangles']:cutters.extend(triangles(rect(*r)))
for b in D['building_cutouts']:cutters.extend(triangles(b['polygon']))
for b in D.get('excluded_polygons',[]):cutters.extend(triangles(b['polygon']))
cutters=[(p,bbox(p)) for p in cutters]
from plan_geometry import Plan
plan=Plan()
xmin,xmax,ymin,ymax=D['bounds'];outer=plan.polygons([rect(xmin,xmax,ymin,ymax)])
excluded=plan.polygons([p for p,_ in cutters]);available=plan.difference(outer,excluded)
# Union each material before subtracting it. Internal construction edges must
# not survive as thousands of tiny slivers in the published street mesh.
road=plan.intersection(available,plan.polygons([p for p,mat,pr,_ in rows if mat=='asphalt']))
green=plan.intersection(available,plan.polygons([p for p,mat,pr,_ in rows if mat=='lawn']))
# Town Hall Gardens is a paved civic plaza, not the broad OSM landscape lawn.
# This bounded correction is provisional; garden furnishings and patterned
# surfaces are reconstructed separately after their positions are checked.
green=plan.difference(green,plan.polygons([rect(-245,-136,-25,25)]))
paths=plan.polygons([p for p,mat,pr,_ in rows if mat=='paving'])
green=plan.difference(plan.difference(green,road),paths)
paved=plan.difference(plan.difference(available,road),green)
# Historic checkerwork on the longitudinal axis, conservatively simplified.
# The circular fountain zone is reserved for its independently modelled tiers.
checker=[]
for i in range(32):
 for j in range(4):
  if (i+j)%2==0:checker.append(rect(-220+2*i,-218+2*i,-3+j,-2+j))
ring=[(-186.7+10*math.cos(i*math.tau/48),-1+10*math.sin(i*math.tau/48)) for i in range(48)]
pattern=plan.intersection(paved,plan.difference(plan.polygons(checker),plan.polygons([ring])))
paved=plan.difference(paved,pattern)
compiled={};collections={};cuts=D['tile_cuts']
for ti,(lo,hi) in enumerate(zip(cuts,cuts[1:])):
 name=f'section-{ti:02d}';c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
 # A grade break is a shared geometric edge, not two independently tilted faces.
 for ya,yb in zip([ymin,36,41,ymax],[36,41,ymax]):
  cell=plan.polygons([rect(lo,hi,ya,yb)])
  for mat,g in [('asphalt',road),('lawn',green),('paving',paved),('pattern',pattern)]:
   m=compiled.setdefault((name,mat),Mesh('Ground '+name+' '+mat))
   for p in plan.triangles(plan.intersection(g,cell)):
    for lifted in SURFACE.lift_triangle(p):m.add([(x,y,0) for x,y,z in lifted],[(0,1,2)])
 print(name,'triangles before conformance',sum(len(m.faces) for (n,_),m in compiled.items() if n==name),flush=True)
plan.close()
# Conform at a common plane first: road and footway boundaries must share XY
# vertices even though their finished surfaces have a 120 mm height difference.
import numpy as np
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=conform(compiled,preserve_triangles=True,weld_distance=5e-5)
edge_mats=defaultdict(list)
for (name,mat),m in compiled.items():
 for face in m.faces:
  for ia,ib in zip(face,face[1:]+face[:1]):
   a,b=m.vertices[ia],m.vertices[ib];key=tuple(sorted((tuple(round(float(v),4) for v in a[:2]),tuple(round(float(v),4) for v in b[:2]))))
   edge_mats[key].append((name,mat,a,b))
curbs={}
for hits in edge_mats.values():
 if not any(h[1]=='asphalt' for h in hits) or not any(h[1]!='asphalt' for h in hits):continue
 name,_,a,b=next(h for h in hits if h[1]=='asphalt')
 m=curbs.setdefault((name,'kerb'),Mesh('Ground '+name+' kerb'))
 za,zb=grade(*a[:2]),grade(*b[:2])
 m.add([(a[0],a[1],za-.12),(b[0],b[1],zb-.12),(b[0],b[1],zb),(a[0],a[1],za)],[(0,1,2,3)])
for (name,mat),m in compiled.items():
 m.vertices=[(x,y,grade(x,y)-(.12 if mat=='asphalt' else 0)) for x,y,z in m.vertices]
compiled.update(curbs)
count=0
for (name,mat),m in compiled.items():
 if not m.faces:continue
 ob=m.finish([mats[mat]],collections[name]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 # Long clipped polygons can become near-degenerate after float32 conversion.
 bm=bmesh.new();bm.from_mesh(ob.data);bad=[f for f in bm.faces if f.calc_area()<1e-9]
 bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric ground UV')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 count+=len(ob.data.polygons)
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
print('Ground triangles',count,report,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
