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
# GEOS nodes boundaries in double precision; a 10-micrometre edge tolerance
# also captures junctions displaced by float32 rounding at the garden circle.
# Larger tolerances can pull genuinely distinct nearby edges into skinny fans.
conforming.TOLERANCE=1e-5
conforming.GRID=1e-6
conform=conforming.conform
from datum import grade,SURFACE
import garden_plan as garden
D=json.loads((ROOT/'research/layout.json').read_text())
BLOCKS=json.loads((Path(os.environ['SOUTHPORT_REPO_ROOT'])/D['block_plan']).read_text())
# The garden pavilions replace two seed volumes. Their authoritative adjusted
# footprints also own their ground cutouts, so no old hole or buried paving is
# left when the architecture is registered to the measured garden axis.
pavilion_path=Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/lord-street/town-hall-gardens-pavilions/research/layout.json'
pavilion_cuts={b['source_way']:b['footprint'] for b in json.loads(pavilion_path.read_text())['pavilions']}
D['building_cutouts'] += [{'id':b['id'],'polygon':pavilion_cuts.get(b['id'],b['footprint'])} for b in BLOCKS['blocks']]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
colours={'paving':(.48,.46,.41),'asphalt':(.085,.092,.093),'lawn':(.16,.25,.10),'kerb':(.40,.40,.37),'pattern':(.18,.22,.22),'pattern-light':(.74,.73,.66),'garden-paving':(.53,.49,.42),'fountain-stone':(.57,.54,.47),'water':(.19,.32,.32)}
mats={}
for name,c in colours.items():
 m=bpy.data.materials.new('Provisional '+name);m.use_nodes=True;m.diffuse_color=(*c,1)
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;mats[name]=m

# Sandstone flag repeat is authored, not projected photographic imagery.
tex=mats['garden-paving'].node_tree.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(ROOT/'textures/garden-paving.png'));tex.extension='REPEAT'
mats['garden-paving'].node_tree.links.new(tex.outputs['Color'],mats['garden-paving'].node_tree.nodes['Principled BSDF'].inputs['Base Color'])

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
# Bounded planted beds behind the Lord Street bench row, visually estimated
# from the 2017 panorama; keep the central side entrance clear.
beds=plan.difference(plan.polygons([rect(-218,-199,12.5,15.8),rect(-174,-158,12.5,15.8)]),
                     plan.polygons(garden.path_rectangles()))
green=plan.intersection(available,plan.polygons([*plan.triangles(green),*plan.triangles(plan.difference(beds,road))]))
paved=plan.difference(plan.difference(available,road),green)
# The observed axial strip, both end cross paths and the fountain approaches are
# cut into the pavement. The central ring is divided into outlined panels.
cx,cy=garden.CENTRE
circle=garden.circle
inner=plan.polygons([circle(garden.RING_INNER)])
dark,light=garden.surfaces(plan)
# A wide raised tongue and shallow treads replace the former invented ramp.
# Their exact heights and the final joining tread need a ground survey.
tongue=plan.polygons([rect(cx-2.4,cx+2.4,cy-9.4,cy)])
approach=plan.polygons([rect(cx-2.4,cx+2.4,cy-12.4,cy-9.4)])
fountain_cut=plan.polygons([*plan.triangles(inner),*plan.triangles(tongue),*plan.triangles(approach)])
pattern=plan.difference(plan.intersection(paved,dark),fountain_cut)
pattern_light=plan.difference(plan.intersection(paved,light),fountain_cut)
paved=plan.difference(plan.difference(plan.difference(paved,pattern),pattern_light),fountain_cut)
garden_paved=plan.intersection(paved,plan.polygons([rect(-245,-136,-19,18)]))
paved=plan.difference(paved,garden_paved)
# Disk is removed from the ordinary ground.  Three horizontal tiers and a
# horizontal pool own the centre; an outer collar meets the bounded grade.
def disc(r):return plan.polygons([circle(r)])
def annulus(ri,ro):return plan.difference(disc(ro),disc(ri))
fountain_shapes={
 'collar':plan.triangles(plan.difference(annulus(6.3,6.4),tongue)),
 'lower':plan.triangles(plan.difference(annulus(6.2,6.3),tongue)),
 'middle':plan.triangles(plan.difference(annulus(5.4,6.2),tongue)),
 'upper':plan.triangles(plan.difference(annulus(4.6,5.4),tongue)),
 'platform':plan.triangles(plan.difference(annulus(garden.POOL_RADIUS,4.6),tongue)),
 'tongue':plan.triangles(plan.difference(tongue,disc(garden.POOL_RADIUS))),
 'pool':plan.triangles(disc(garden.POOL_RADIUS)),
}
for i in range(3):
 fountain_shapes['approach-'+str(i)]=plan.triangles(plan.polygons([rect(cx-2.4,cx+2.4,cy-12.4+i,cy-11.4+i)]))
compiled={};collections={};cuts=D['tile_cuts']
for ti,(lo,hi) in enumerate(zip(cuts,cuts[1:])):
 name=f'section-{ti:02d}';c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c
 # A grade break is a shared geometric edge, not two independently tilted faces.
 for ya,yb in zip([ymin,36,41,ymax],[36,41,ymax]):
  cell=plan.polygons([rect(lo,hi,ya,yb)])
  for mat,g in [('asphalt',road),('lawn',green),('paving',paved),('garden-paving',garden_paved),('pattern',pattern),('pattern-light',pattern_light)]:
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
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4) if mat=='garden-paving' else (v.x,v.y)
 count+=len(ob.data.polygons)
# Furniture is separately streamed and is never classified as walking ground.
from garden_components import make as garden_component, clean as clean_furniture
furniture_collection=bpy.data.collections.new('garden-furniture');s.collection.children.link(furniture_collection)
furniture_mats=[]
for name,colour in [('iron',(.10,.10,.09)),('metal',(.27,.27,.25)),('edge',(.65,.64,.57)),('yellow',(.5,.4,.1)),('red',(.4,.1,.1)),('amber',(.5,.3,.1)),('green',(.1,.3,.1)),('timber',(.26,.16,.10)),('glass',(.25,.3,.3))]:
 m=bpy.data.materials.new('Garden furniture '+name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*colour,1);furniture_mats.append(m)
stone=mats['fountain-stone'];dark=furniture_mats[0];opal=mats['pattern-light']
tree_mats=[]
for name,colour in [('bark',(.20,.16,.12)),('deep foliage',(.13,.24,.10)),('foliage',(.18,.31,.12)),('light foliage',(.24,.36,.15))]:
 m=bpy.data.materials.new('Garden '+name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*colour,1);tree_mats.append(m)
def fixture(kind,x,y,angle=0):
 ob=garden_component(kind,'detail','Garden '+kind+' '+str(x)+' '+str(y)).finish(furniture_mats if kind=='bench' else tree_mats if kind=='tree' else [stone,dark,opal],furniture_collection)
 clean_furniture(ob);ob.location=(x,y,grade(x,y));ob.rotation_euler.z=angle
 uv=ob.data.uv_layers.new(name='Furniture metric UV')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.z)
# Remove only provisional furniture which obstructs the observed terminal
# routes; leave the other previously estimated placements alone.
def crosses_terminal(a,b):
 return any(a<x+garden.HALF_WIDTH and b>x-garden.HALF_WIDTH for x in garden.END_STATIONS)
gates=[x+d for x in garden.END_STATIONS for d in (-3.5,3.5)]
def crosses_gate(a,b):return any(a<x+1.04 and b>x-1.04 for x in gates)
for x in [-215,-204,-173,-162]:
 if not crosses_terminal(x-1,x+1):fixture('tree',x,14.1)
# Bench backs face the beds or service edge, so seats face the plaza.
for x in [-216,-213.8,-211.6,-209.4,-207.2,-205,-202.8,-200.6,-172,-169.8,-167.6,-165.4,-163.2,-161]:
 if not crosses_terminal(x-.95,x+.95):fixture('bench',x,11.4)
for x in [-217,-214.8,-212.6,-210.4,-208.2,-206,-203.8,-201.6,-178,-175.8,-173.6,-171.4,-169.2,-167,-164.8,-162.6]:
 if not crosses_terminal(x-.95,x+.95):fixture('bench',x,-13.8,math.pi)
# Short open runs and gaps represent the observed entrance rhythm. Exact pier
# stations are visual estimates rather than a measured inventory.
for x in [-218,-214,-210,-206,-202,-174,-170,-166,-162]:
 if not crosses_terminal(x,x+4) and not crosses_gate(x,x+4):fixture('balustrade',x,16.4)
for x in [-219,-215,-211,-207,-203,-199,-175,-171,-167,-163]:
 if not crosses_terminal(x,x+4):fixture('balustrade',x,-16.4)
for x,y in [(-220,16.4),(-198,16.4),(-176,16.4),(-158,16.4),(-221,-16.4),(-197,-16.4),(-177,-16.4),(-159,-16.4)]:
 if not crosses_terminal(x-.3,x+.3) and (y<0 or not crosses_gate(x-.3,x+.3)):fixture('globe',x,y)
# Both photographed Lord Street gateways have a pair of triple-column groups.
for x in gates:fixture('column',x,16.4)
# The fountain's pool and platform stay level. The collar meets the terrain;
# the photographed broad break is represented as a raised tongue, with three
# shallow treads connecting it to the provisional surrounding grade.
base=max(grade(*p) for p in circle(garden.RING_INNER))
levels={'lower':base,'middle':base+.14,'upper':base+.28,'platform':base+.42,'tongue':base+.42,'pool':base+.42,
        **{'approach-'+str(i):base+i*.14 for i in range(3)}}
fountain={name:Mesh('Fountain '+name) for name in fountain_shapes}
for name,polys in fountain_shapes.items():
 for tri in polys:
  # Grade profile split points preserve the road-surface edge at the collar.
  for lifted in SURFACE.lift_triangle(tri):
   points=[]
   for x,y,_ in lifted:
    if name=='collar':
     r=math.hypot(x-cx,y-cy);t=max(0,min(1,(6.4-r)/.1));z=grade(x,y)*(1-t)+base*t
    else:z=levels[name]
    points.append((x,y,z))
   fountain[name].add(points,[(0,1,2)])
for r,lo,hi in [(6.2,base,base+.14),(5.4,base+.14,base+.28),(4.6,base+.28,base+.42)]:
 ring=circle(r)
 for a,b in zip(ring,ring[1:]+ring[:1]):
  ts=[0.,1.]
  if abs(b[0]-a[0])>1e-10:
   for x in (cx-2.4,cx+2.4):
    t=(x-a[0])/(b[0]-a[0])
    if 0<t<1:ts.append(t)
  ts.sort()
  for t0,t1 in zip(ts,ts[1:]):
   aa=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0);bb=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
   mid=((aa[0]+bb[0])/2,(aa[1]+bb[1])/2)
   if mid[1]<cy and cx-2.4<mid[0]<cx+2.4:continue
   fountain['upper'].add([(aa[0],aa[1],lo),(bb[0],bb[1],lo),(bb[0],bb[1],hi),(aa[0],aa[1],hi)],[(0,1,2,3)])
# Close the vertical interfaces at the sides of the tongue and the three treads.
for x in (cx-2.4,cx+2.4):
 cuts=[cy-9.4,cy]
 for radius in (6.4,6.3,6.2,5.4,4.6,garden.POOL_RADIUS):
  poly=circle(radius)
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if (a[0]-x)*(b[0]-x)<0:
    t=(x-a[0])/(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
    if y < cy and cy-9.4<y<cy:cuts.append(y)
 cuts=sorted(cuts)
 for y0,y1 in zip(cuts,cuts[1:]):
  r=math.hypot(x-cx,(y0+y1)/2-cy)
  if r>=6.4:target=lambda y:grade(x,y)
  elif r>=6.3:target=lambda y:grade(x,y)*(1-max(0,min(1,(6.4-math.hypot(x-cx,y-cy))/.1)))+base*max(0,min(1,(6.4-math.hypot(x-cx,y-cy))/.1))
  elif r>=6.2:target=lambda y:base
  elif r>=5.4:target=lambda y:base+.14
  elif r>=4.6:target=lambda y:base+.28
  else:target=lambda y:base+.42
  ys=sorted(set([y0,y1]+[v[1] for v in SURFACE.edge_points((x,y0),(x,y1))]))
  for a,b in zip(ys,ys[1:]):
   d0=base+.42-target(a);d1=base+.42-target(b);segments=[a,b]
   if d0*d1<0:segments.insert(1,a+(b-a)*(-d0)/(d1-d0))
   for u,v in zip(segments,segments[1:]):
    fountain['tongue'].add([(x,u,target(u)),(x,v,target(v)),(x,v,base+.42),(x,u,base+.42)],[(0,1,2,3)])
 for i in range(3):
  a,b=cy-12.4+i,cy-11.4+i;z=base+i*.14
  ys=[v[1] for v in SURFACE.edge_points((x,a),(x,b))]
  for u,v in zip(ys,ys[1:]):
   fountain['approach-'+str(i)].add([(x,u,grade(x,u)),(x,v,grade(x,v)),(x,v,z),(x,u,z)],[(0,1,2,3)])
# Straight risers follow the observed wide break, not a narrow accessibility ramp.
for i in range(3):
 y=cy-11.4+i;lo=base+i*.14;hi=base+(i+1)*.14
 fountain['approach-'+str(i)].add([(cx-2.4,y,lo),(cx+2.4,y,lo),(cx+2.4,y,hi),(cx-2.4,y,hi)],[(0,1,2,3)])
y=cy-12.4
edge=list(SURFACE.edge_points((cx-2.4,y),(cx+2.4,y)))
for a,b in zip(edge,edge[1:]):
 fountain['approach-0'].add([(a[0],y,grade(a[0],y)),(b[0],y,grade(b[0],y)),(b[0],y,base),(a[0],y,base)],[(0,1,2,3)])
for name,m in fountain.items():
 ob=m.finish([mats['water' if name=='pool' else 'fountain-stone']],collections['section-06'])
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Fountain metric UV')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
print('Ground triangles',count,report,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
