"""Reference-led exterior. Building X runs along the frontage; Y towards bridge."""
import json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Matrix, Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
D=json.loads((R/'research/layout.json').read_text())
ox,oy=D['origin_site_xy']; ux,uy=D['x_axis_site']; vx,vy=D['y_axis_site']; ground=D['ground_datum_m']
def P(x,y,z): return (ox+ux*x+vx*y, oy+uy*x+vy*y, ground+z)
def wing_raw(x): return 3.8-1.12*(abs(x)/11.25)**2.6
wing_breaks=sorted({a+(b-a)*i/20 for a,b in [(-10.84,-2.8),(2.87,11.5)] for i in range(21)})
def wing(x):
 for a,b in zip(wing_breaks[:-1],wing_breaks[1:]):
  if a<=x<=b:return wing_raw(a)+(wing_raw(b)-wing_raw(a))*(x-a)/(b-a)
 return wing_raw(x)
def barrel(x): return 4.12+.53*(1-(x/2.8)**2)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;c=bpy.data.collections.new('building');s.collection.children.link(c)
def material(name,col,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
mats={
 'cream':material('Warm off-white cladding',(.79,.78,.71)),
 'base':material('Dark charcoal plinth',(.055,.058,.054)),
 'green':material('Deep green fascia and joinery',(.035,.23,.105)),
 'roof':material('Pale weathered wing roof',(.58,.62,.60)),
 'barrel':material('Pale translucent-looking canopy',(.72,.81,.80),.35),
 'glass':material('Recessed dark glazing',(.10,.19,.18),.3),
 'joint':material('Panel joint shadow',(.36,.38,.34)),
 'letter':material('Ivory sign lettering',(.86,.83,.68)),
 'drum':material('Blue grey drum cap',(.48,.65,.68)),
 'grille':material('Vent and shutter shadow',(.10,.18,.12))}
meshes={}
def mesh(key):
 if key not in meshes:meshes[key]=Mesh(key)
 return meshes[key]
def face(key,pts):
 # The local horizontal frame is reflected. Correct principal wall windings
 # before applying that reflection; roof and radial faces already wind outward.
 if len(pts)>=3:
  a,b,c0=map(Vector,pts[:3]); n=(b-a).cross(c0-a)
  if abs(n.y)>1e-9 and max(p[1] for p in pts)-min(p[1] for p in pts)<1e-7 and abs(pts[0][1])>5:
   if n.y*pts[0][1]<0:pts=list(reversed(pts))
  elif abs(n.x)>1e-9 and max(p[0] for p in pts)-min(p[0] for p in pts)<1e-7 and abs(pts[0][0])>2.7:
   if n.x*pts[0][0]<0:pts=list(reversed(pts))
 mesh(key).add([P(*p) for p in pts],[tuple(reversed(range(len(pts))))])
def quad(key,p0,p1,p2,p3): face(key,[p0,p1,p2,p3])
def panel_wall_y(key,y,a,b,z0,z1,door=None):
 # Photograph-derived wide panel grid. Subdivide only at shared roof samples.
 steps=max(1,round((b-a)/2.45)); panels=sorted(set([a+(b-a)*i/steps for i in range(steps+1)]+(list(door) if door else [])))
 for outer0,outer1 in zip(panels[:-1],panels[1:]):
  x0,x1=outer0+.009,outer1-.009
  opening=door and door[0]+.001 < (x0+x1)/2 < door[1]-.001
  if not opening:
   for low,high in [(z0,1.13),(1.15,2.12)]:face(key,[(x0,y,low),(x1,y,low),(x1,y,high),(x0,y,high)])
  edges=[x0]+[x for x in wing_breaks if x0<x<x1]+[x1]
  for p,q in zip(edges[:-1],edges[1:]):
   h0=wing(p)-.26;h1=wing(q)-.26
   for low,high in [(2.14,3.05),(3.07,z1)]:
    h0a=min(h0,high);h1a=min(h1,high)
    if min(h0a,h1a)<=low+.01:continue
    face(key,[(p,y,low),(q,y,low),(q,y,h1a),(p,y,h0a)])
  # Recessed substrate owns the dark gaps, but leaves the door genuinely cut.
  back=y-.02 if y>0 else y+.02
  edges=[outer0]+[x for x in wing_breaks if outer0<x<outer1]+[outer1]
  for p,q in zip(edges[:-1],edges[1:]):
   low=2.12 if opening else z0
   if min(wing(p)-.26,wing(q)-.26)>low:face('Shell joint backing',[(p,back,low),(q,back,low),(q,back,wing(q)-.26),(p,back,wing(p)-.26)])
def panel_wall_x(x,a,b,door=None):
 # Side wall panels and cut-out for the observed narrow service door.
 edges=sorted(set([a,b]+[a+(b-a)*i/5 for i in range(1,5)]+(list(door) if door else [])))
 for y0,y1 in zip(edges[:-1],edges[1:]):
  y0+=.009;y1-=.009
  for low,high in [(.25,1.13),(1.15,2.12),(2.14,wing(x)-.26)]:
   if high<=low+.01:continue
   if door and door[0]+.001 < (y0+y1)/2 < door[1]-.001 and low<2.12:continue
   pts=[(x,y0,low),(x,y1,low),(x,y1,high),(x,y0,high)]
   if x>0:pts.reverse()
   face('Shell cream side',pts)
# Main plinth: front stops at entrance; rear stops at drum chord.
for a,b in [(-10.84,-2.8),(2.87,10.10),(11.00,11.5)]:
 quad('Shell dark plinth',(a,6.5,0),(b,6.5,0),(b,6.5,.25),(a,6.5,.25))
for a,b in [(-10.84,-2.8),(2.87,11.5)]:
 panel_wall_y('Shell cream front',6.5,a,b,.25,4.1,door=(10.1,11.0) if a>0 else None)
quad('Joinery green door',(10.1,6.45,0),(11.0,6.45,0),(11.0,6.45,2.12),(10.1,6.45,2.12))
for a,b in [(-10.84,-2.04),(2.04,11.5)]:
 quad('Shell dark plinth',(b,-6,0),(a,-6,0),(a,-6,.25),(b,-6,.25));panel_wall_y('Shell cream rear',-6,a,b,.25,4.1)
for x in [-10.84,11.5]:
 pts=[(x,-6,0),(x,6.5,0),(x,6.5,.25),(x,-6,.25)]
 if x>0:pts.reverse()
 face('Shell dark plinth',pts);panel_wall_x(x,-6,6.5,door=(3.4,4.3) if x>0 else None)
# Narrow recessed side door, with a shallow reveal and frame.
x=11.5; y0,y1=3.4,4.3
quad('Joinery green door',(x-.035,y1,.03),(x-.035,y0,.03),(x-.035,y0,2.10),(x-.035,y1,2.10))
for y in [y0,y1]:quad('Joinery green reveals',(x,y,.03),(x-.035,y,.03),(x-.035,y,2.10),(x,y,2.10))
quad('Joinery green reveals',(x,y0,2.10),(x,y1,2.10),(x-.035,y1,2.10),(x-.035,y0,2.10))
# Curved roof planes project 0.20 m beyond the end walls. A 0.31 m
# vertical green fascia and continuous undersoffit own the exposed eaves.
for a,b in [(-10.84,-2.8),(2.87,11.5)]:
 xs=[a+(b-a)*i/20 for i in range(21)]
 for p,q in zip(xs[:-1],xs[1:]):
  quad('Roof wing',(p,-6.20,wing(p)),(q,-6.20,wing(q)),(q,6.70,wing(q)),(p,6.70,wing(p)))
  for y,wall in [(-6.20,-6.0),(6.70,6.5)]:
   face('Roof green fascia',[(p,y,wing(p)-.26),(q,y,wing(q)-.26),(q,y,wing(q)+.045),(p,y,wing(p)+.045)])
   face('Roof eaves soffit',[(p,wall,wing(p)-.26),(p,y,wing(p)-.26),(q,y,wing(q)-.26),(q,wall,wing(q)-.26)])
 for x in [a,b]:
  if abs(x)<3:continue
  outer=x+(.17 if x>0 else -.17)
  quad('Roof green edge',(outer,-6.20,wing(x)-.26),(outer,6.70,wing(x)-.26),(outer,6.70,wing(x)+.045),(outer,-6.20,wing(x)+.045))
  quad('Roof side overhang',(x,-6.20,wing(x)),(outer,-6.20,wing(x)),(outer,6.70,wing(x)),(x,6.70,wing(x)))
# Full height drum, clipped where it meets the rear wall. No unsupported openings.
r=4.05;cy=-9.5;alpha=math.asin(3.5/r);angs=[math.pi-alpha+(math.pi+2*alpha)*i/36 for i in range(37)]
for a,b in zip(angs[:-1],angs[1:]):
 x0,y0=r*math.cos(a),cy+r*math.sin(a);x1,y1=r*math.cos(b),cy+r*math.sin(b)
 quad('Shell drum wall',(x0,y0,.24),(x1,y1,.24),(x1,y1,4.12),(x0,y0,4.12));quad('Shell dark drum plinth',(x0,y0,0),(x1,y1,0),(x1,y1,.24),(x0,y0,.24))
 quad('Roof green drum rim',(x0,y0,4.12),(x1,y1,4.12),(x1,y1,4.24),(x0,y0,4.24))
face('Roof drum cap',[(r*math.cos(a),cy+r*math.sin(a),4.24) for a in angs])
# Front entrance: true shallow recess and separate glazing left/right of kiosk.
for x0,x1 in [(-2.8,-1.1),(1.1,2.87)]:
 quad('Glazing doors',(x0,6.40,.03),(x1,6.40,.03),(x1,6.40,2.30),(x0,6.40,2.30))
 for x in [x0,x1]:quad('Joinery door frame',(x-.035,6.43,.03),(x+.035,6.43,.03),(x+.035,6.43,2.30),(x-.035,6.43,2.30))
 quad('Joinery door head',(x0,6.43,2.24),(x1,6.43,2.24),(x1,6.43,2.31),(x0,6.43,2.31))
 mid=(x0+x1)/2;quad('Joinery door mullions',(mid-.027,6.44,.03),(mid+.027,6.44,.03),(mid+.027,6.44,2.25),(mid-.027,6.44,2.25))
 quad('Fine door handle',(mid+.075,6.445,.95),(mid+.115,6.445,.95),(mid+.115,6.445,1.15),(mid+.075,6.445,1.15))
quad('Glazing central infill',(-1.1,6.40,.03),(1.1,6.40,.03),(1.1,6.40,2.30),(-1.1,6.40,2.30))
# Clerestory above entry; framed individual panes, green panel below.
for x0,x1 in [(-2.8,-.95),(-.95,.95),(.95,2.87)]:
 quad('Glazing transom',(x0+.035,6.42,2.46),(x1-.035,6.42,2.46),(x1-.035,6.42,3.51),(x0+.035,6.42,3.51))
quad('Joinery entry fascia',(-2.8,6.45,2.30),(2.87,6.45,2.30),(2.87,6.45,2.46),(-2.8,6.45,2.46))
for x in [-2.8,-.95,.95,2.87]:quad('Joinery transom mullions',(x-.035,6.45,2.46),(x+.035,6.45,2.46),(x+.035,6.45,3.51),(x-.035,6.45,3.51))
quad('Joinery transom head',(-2.8,6.45,3.50),(2.87,6.45,3.50),(2.87,6.45,3.57),(-2.8,6.45,3.57))
# Sign panel is below the projecting curved canopy, with observed readable text.
xs=[-2.8+5.6*i/24 for i in range(25)]
for a,b in zip(xs[:-1],xs[1:]):quad('Sign green panel',(a,6.47,3.57),(b,6.47,3.57),(b,6.47,barrel(b)-.10),(a,6.47,barrel(a)-.10))
# Canopy roof: alternating surface panels and structural ribs, each owns its strip.
y0,y1=-6,8.85; count=10; ys=[y0+(y1-y0)*i/count for i in range(count+1)]
for j,(a,b) in enumerate(zip(ys[:-1],ys[1:])):
 for x0,x1 in zip(xs[:-1],xs[1:]):quad('Roof canopy panel',(x0,a+.025,barrel(x0)),(x1,a+.025,barrel(x1)),(x1,b-.025,barrel(x1)),(x0,b-.025,barrel(x0)))
for y in ys:
 for x0,x1 in zip(xs[:-1],xs[1:]):quad('Roof canopy ribs',(x0,y-.025,barrel(x0)),(x1,y-.025,barrel(x1)),(x1,y+.025,barrel(x1)),(x0,y+.025,barrel(x0)))
for x in [-2.8,2.8]:quad('Roof canopy side rail',(x,-6,3.86),(x,8.85,3.86),(x,8.85,barrel(x)),(x,-6,barrel(x)))
# The projecting canopy is seen from below at street height. The undersurface
# has distinct pale bays and dark framing, below the top roof rather than a decal.
for j in range(2):
 a=6.5+j*(8.85-6.5)/2;b=6.5+(j+1)*(8.85-6.5)/2
 for x0,x1 in zip(xs[:-1],xs[1:]):
  face('Roof canopy underside',[(x0,a+.035,barrel(x0)-.065),(x0,b-.035,barrel(x0)-.065),(x1,b-.035,barrel(x1)-.065),(x1,a+.035,barrel(x1)-.065)])
for y in [6.5,7.675,8.85]:
 for x0,x1 in zip(xs[:-1],xs[1:]):
  face('Roof canopy underside ribs',[(x0,y-.035,barrel(x0)-.065),(x0,y+.035,barrel(x0)-.065),(x1,y+.035,barrel(x1)-.065),(x1,y-.035,barrel(x1)-.065)])
for x0,x1 in zip(xs[:-1],xs[1:]):quad('Roof green canopy lip',(x0,8.85,barrel(x0)-.065),(x1,8.85,barrel(x1)-.065),(x1,8.85,barrel(x1)+.015),(x0,8.85,barrel(x0)+.015))
# Small kiosk: visible half-round cream corrugation, dark cap and small green shutter.
r=1.1;cy=7.5;angs=[math.pi*i/96 for i in range(97)]
for a,b in zip(angs[:-1],angs[1:]):
 ra=r+.035*math.cos(24*a);rb=r+.035*math.cos(24*b)
 x0,y0=ra*math.cos(a),cy+ra*math.sin(a);x1,y1=rb*math.cos(b),cy+rb*math.sin(b)
 if .26 < (a+b)/2 < .92:
  quad('Kiosk cream',(x0,y0,.12),(x1,y1,.12),(x1,y1,.85),(x0,y0,.85))
  quad('Kiosk cream',(x0,y0,1.75),(x1,y1,1.75),(x1,y1,2.04),(x0,y0,2.04))
 else:quad('Kiosk cream', (x0,y0,.12),(x1,y1,.12),(x1,y1,2.04),(x0,y0,2.04))
 quad('Kiosk dark base',(x0,y0,0),(x1,y1,0),(x1,y1,.12),(x0,y0,.12))
 quad('Kiosk dark coping',(x0,y0,2.04),(x1,y1,2.04),(x1,y1,2.13),(x0,y0,2.13))
face('Kiosk dark roof',[(r*math.cos(a),cy+r*math.sin(a),2.13) for a in angs])
# Green rectangular shutter occupies an actual opening at one shoulder of the
# kiosk in the photographs; represented just off the curved wall as a distinct fitting.
quad('Kiosk shutter',(.62,8.31,.85),(1.06,7.79,.85),(1.06,7.79,1.75),(.62,8.31,1.75))
# Two small square louvres in the bridge-front wings.
for x in [-5.0,5.2]:
 quad('Joinery vents',(x-.13,6.52,2.25),(x+.13,6.52,2.25),(x+.13,6.52,2.52),(x-.13,6.52,2.52))
 for z in [2.29,2.34,2.39,2.44,2.49]:quad('Fine vent slots',(x-.09,6.525,z),(x+.09,6.525,z),(x+.09,6.525,z+.012),(x-.09,6.525,z+.012))
# Fitting and geometric panel seams are grouped by semantic material.
for name,m in meshes.items():
 key=('joint' if 'joint backing' in name else 'cream' if ('cream' in name or 'drum wall' in name) else 'base' if ('dark' in name or 'coping' in name) else 'green' if ('green' in name or 'mullion' in name or 'fascia' in name or 'shutter' in name or 'ribs' in name or 'rail' in name or 'frame' in name or 'head' in name) else 'roof' if name=='Roof wing' else 'barrel' if ('canopy panel' in name or 'canopy underside' in name) else 'drum' if 'drum cap' in name else 'glass' if 'Glazing' in name else 'joint' if 'vents' in name else 'grille')
 ob=m.finish([mats[key]],c);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='metric')
 for f in ob.data.polygons:
  ax=sorted(sorted(range(3),key=lambda k:abs(f.normal[k]))[:2])
  for i in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[i].vertex_index].co;uv.data[i].uv=(v[ax[0]],v[ax[1]])
# Readable permanent fascia: the large observed line follows the arch.
base=Matrix(((ux,0,vx,0),(uy,0,vy,0),(0,1,0,0),(0,0,0,1)))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf')
def lettering(body,x,z,size,angle=0):
 cu=bpy.data.curves.new('Sign '+body,'FONT');cu.body=body;cu.font=font;cu.align_x='CENTER';cu.size=size;cu.extrude=.001
 ob=bpy.data.objects.new('Sign lettering '+body,cu);c.objects.link(ob)
 ob.matrix_world=base@Matrix.Rotation(angle,4,'Z');ob.location=P(x,6.485,z);ob.data.materials.append(mats['letter']);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='lettering')
title='THE HERITAGE CENTRE'
for i,ch in enumerate(title):
 x=(i-(len(title)-1)/2)*.22
 if ch!=' ':lettering(ch,x,3.98+.18*(1-(x/2.1)**2),.34,math.atan(-.36*x/(2.1**2)))
lettering('SOUTHPORT',0,3.77,.18)
lettering('GIFT SHOP      CAFE      GALLERY',0,3.60,.15)
# Neutral daylight and render cameras are not exported.
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.75,.80,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';s.camera=cam;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/heritage-centre.blend'))
