"""Maritime Court: measured L-plan, exposed undercroft and authored facade openings."""
import bpy,sys,os,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from plan import D,world,outline,facade,strips,TALL,SMALL
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
c=bpy.data.collections.new('architecture');s.collection.children.link(c)
def mat(n,col,rough=.75):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
M=[mat('Buff masonry',(.36,.27,.17)),mat('Warm pale concrete',(.59,.55,.44)),mat('White uPVC',(.79,.79,.72),.45),mat('Blue grey opaque window glass',(.12,.19,.22),.28),mat('Grey upper cladding',(.28,.29,.26)),mat('Pale flat membrane',(.45,.47,.45)),mat('Shadow and basement',(.075,.065,.05)),mat('Warm curtain',(.53,.50,.41)),mat('Dark bronze fittings',(.12,.10,.065))]
p=M[0].node_tree.nodes['Principled BSDF'];tex=M[0].node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/buff-brick.png'));M[0].node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
# Consolidated material-bearing surface groups keep baking independent of object count.
G={}
def face(group,pts,mi=0,uv=None):
 if len(pts)<3:return
 g=G.setdefault(group,[[],[],[],[]]);base=len(g[0]);g[0].extend(world(p) for p in pts);g[1].append(tuple(range(base,base+len(pts))));g[2].append(mi)
 if uv is None:
  v=[Vector(p) for p in pts];n=(v[1]-v[0]).cross(v[2]-v[0]);axes=sorted(range(3),key=lambda j:abs(n[j]))[:2];uv=[(p[axes[0]]/1.8,p[axes[1]]/1.2)for p in pts]
 g[3].append(uv)
def rect(g,at,a,b,z0,z1,o=0,mi=0):
 if b-a<1e-7 or z1-z0<1e-7:return
 face(g,[at(a,z0,o),at(b,z0,o),at(b,z1,o),at(a,z1,o)],mi,[(a/1.8,z0/1.2),(b/1.8,z0/1.2),(b/1.8,z1/1.2),(a/1.8,z1/1.2)])
def box(g,x0,x1,y0,y1,z0,z1,mi=0):
 p=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 for f in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(3,2,1,0)]:face(g,[p[k]for k in f],mi)
def window(at,a,b,z0,z1,idx,tall=False):
 # Aperture has four reveals, a non-overlapping frame ring and recessed pane.
 outer=.035;back=-.13;t=.065
 face('Architecture reveals',[at(a,z0,0),at(a,z1,0),at(a,z1,back),at(a,z0,back)],1)
 face('Architecture reveals',[at(b,z1,0),at(b,z0,0),at(b,z0,back),at(b,z1,back)],1)
 face('Architecture reveals',[at(a,z1,0),at(b,z1,0),at(b,z1,back),at(a,z1,back)],1)
 face('Architecture reveals',[at(b,z0,0),at(a,z0,0),at(a,z0,back),at(b,z0,back)],1)
 for aa,bb,zz,tt in [(a,a+t,z0,z1),(b-t,b,z0,z1),(a+t,b-t,z0,z0+t),(a+t,b-t,z1-t,z1)]:rect('Architecture frames',at,aa,bb,zz,tt,outer,2)
 # Pane is separated behind frame. Warm curtain variations are deliberately generic.
 rect('Architecture glazing',at,a+t,b-t,z0+t,z1-t,back,7 if idx%9 in (1,4) else 3)
 mid=(a+b)/2
 rect('Architecture mullions',at,mid-.025,mid+.025,z0+t,z1-t,outer+.004,2)
 if tall:
  z=z0+(z1-z0)*.46;rect('Architecture mullions',at,a+t,b-t,z-.024,z+.024,outer+.012,2)
  # Projecting pale sill: front and upper face only, no duplicate buried back.
  rect('Architecture sills',at,a-.045,b+.045,z0-.11,z0,.14,1)
  face('Architecture sills',[at(a-.045,z0,.14),at(b+.045,z0,.14),at(b+.045,z0,0),at(a-.045,z0,0)],1)
  if idx%7==2:
   rect('Fine Juliet rail',at,a+.12,b-.12,z0+.78,z0+.81,.20,2)
   for j in range(12):
    x=a+.14+(b-a-.28)*j/11;rect('Fine Juliet rail',at,x-.012,x+.012,z0+.12,z0+.78,.20,2)
 else:
  z=z1-.25;rect('Fine opening lights',at,a+t,b-t,z-.014,z+.014,outer+.012,2)
idx=0
for i in range(6):
 l,at=facade(i);opening=[]
 for floor in range(8):
  z=D['podium']+floor*D['floor']
  for x in TALL[i]:opening.append((x-1.25,x+1.25,z+.18,z+2.53,True))
  for x,w in SMALL[i]:
   if i==0 and floor==0 and x==9:continue
   lo=z+1.0;hi=z+2.05
   if i in (1,4) and w<1:lo=z+.65;hi=z+1.75
   opening.append((x-w/2,x+w/2,lo,hi,False))
 # Entrance is an actual aperture at Promenade left of first glazed stack.
 if i==0:opening.append((7.6,10.5,.55,2.85,False))
 # Raised ground floors retain separate slit vents below residential windows.
 if i in (0,5):
  for x in TALL[i]:opening.append((x-1.15,x+1.15,.75,1.4,False))
 low=D['podium'] if i in (2,3) else -.15
 bands=strips(i)
 for a,b,o,top in bands:
  holes=[h for h in opening if h[0]>=a-1e-6 and h[1]<=b+1e-6]
  xs=sorted(set([a,b]+[v for h in holes for v in h[:2]]));zs=sorted(set([low,top,D['podium']+2*D['floor'],D['podium']+2*D['floor']+.18,D['podium']+5*D['floor'],D['podium']+5*D['floor']+.18,D['podium']+7*D['floor']]+[v for h in holes for v in h[2:4] if low<v<top]))
  for aa,bb in zip(xs,xs[1:]):
   for zz,tt in zip(zs,zs[1:]):
    x=(aa+bb)/2;z=(zz+tt)/2
    if any(h[0]<x<h[1] and h[2]<z<h[3] for h in holes):continue
    mi=0
    if not o and z>D['podium']+7*D['floor'] and i not in (1,4) and not (i==0 and x<7):mi=4
    if any(q<z<q+.18 for q in [D['podium']+2*D['floor'],D['podium']+5*D['floor']]):mi=1
    rect('Shell elevations',at,aa,bb,zz,tt,o,mi)
  # Thin top coping has one surface owner, including projecting pier heads.
  if o:face('Shell pier caps',[at(a,top,o),at(b,top,o),at(b,top,0),at(a,top,0)],1)
  for h in holes:
   aa,bb,z0,z1,tall=h
   if z0<low:continue
   idx+=1;window(at,aa,bb,z0,z1,idx,tall)
 # Vertical returns at every real projection change.
 for left,right in zip(bands,bands[1:]):
  x=left[1];o0,o1=left[2],right[2];h0,h1=left[3],right[3]
  if o0!=o1:face('Shell pier returns',[at(x,low,o0),at(x,low,o1),at(x,max(h0,h1),o1),at(x,max(h0,h1),o0)],0)
 # Rear open undercroft: piers, inset backing and ceiling, independently budgeted.
 if i in (2,3):
  rect('Architecture undercroft backing',at,0,l,-.1,D['podium'],-2.4,6)
  face('Architecture undercroft soffit',[at(0,D['podium'],0),at(l,D['podium'],0),at(l,D['podium'],-2.4),at(0,D['podium'],-2.4)],1)
  for x in [0.3]+TALL[i]+[l-.3]:
   aa,bb=max(0,x-.22),min(l,x+.22)
   rect('Architecture undercroft piers',at,aa,bb,-.1,D['podium'],0,0)
   face('Architecture undercroft piers',[at(aa,-.1,0),at(aa,D['podium'],0),at(aa,D['podium'],-2.4),at(aa,-.1,-2.4)],0)
   face('Architecture undercroft piers',[at(bb,D['podium'],0),at(bb,-.1,0),at(bb,-.1,-2.4),at(bb,D['podium'],-2.4)],0)
# Flat roof triangulated from authored L; hidden front strips beneath cap excluded by inset.
p=outline();vv=[Vector((x,y,D['roof']))for x,y in p]
for t in tessellate_polygon([vv]):face('Shell flat roof',[tuple(vv[v])if isinstance(v,int)else tuple(v)for v in t],5)
# Central lift/stair overrun with metal coping, documented in all roof orbits.
box('Architecture lift',9.5,15.0,10.3,15.6,D['roof'],D['lift_top'],0)
box('Architecture lift coping',9.35,15.15,10.15,15.75,D['lift_top'],D['lift_top']+.12,1)
# Modest entrance canopy and actual connected approach: landing, broad short flight.
box('Architecture entrance signboard',7.2,11.0,-.15,-.02,3.10,3.65,1)
box('Architecture entrance canopy',7.2,11.0,-1.45,-.1,2.85,3.10,1)
box('Architecture entrance landing',7.6,10.5,-1.7,-.02,.0,.55,1)
for k in range(3):box('Architecture entrance steps',7.6,10.5,-2.75+k*.35,-2.4+k*.35,-.1,.18*(k+1),1)
# Lettering only where readable in July2026 imagery.
for body,sz,z in [('MARITIME COURT',.26,3.36),('PRIVATE APARTMENTS',.12,3.18)]:
 curve=bpy.data.curves.new('Entrance sign','FONT');curve.body=body;curve.size=sz;curve.align_x='CENTER';curve.extrude=0
 ob=bpy.data.objects.new('Fine entrance lettering',curve);c.objects.link(ob)
 ob.location=world((9.1,-.17,z));u=Vector((*D['u_axis'],0));normal=Vector((-D['v_axis'][0],-D['v_axis'][1],0));from mathutils import Matrix
 ob.rotation_euler=Matrix((u,Vector((0,0,1)),normal)).transposed().to_euler();ob.data.materials.append(M[8]);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
for name,(verts,faces,mids,uvs) in G.items():
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o)
 for m in M:me.materials.append(m)
 uv=me.uv_layers.new(name='Metric surface UV')
 for poly,mi,coords in zip(me.polygons,mids,uvs):
  poly.material_index=mi
  for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
# All meshes including glyphs carry UVs for export.
for ob in c.objects:
 if ob.type=='MESH' and not ob.data.uv_layers:ob.data.uv_layers.new(name='Glyph UV')
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.66,.73,.81,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.5;sun.rotation_euler=(.4,-.7,-.5);s.collection.objects.link(sun)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';s.camera=cam;s.render.resolution_x=1500;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
(ROOT/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/maritime-court.blend'))
