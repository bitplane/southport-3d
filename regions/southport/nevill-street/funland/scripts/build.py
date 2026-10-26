"""Funland measured envelope and evidenced cream amusement frontage; no interior."""
import bpy,math,sys,os
from pathlib import Path
from mathutils import Vector,Matrix
from plan import D,W,L,world,top,XS,YS,at,canopy_ring
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ['architecture','carousel']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);C[name]=c
def mat(name,col,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
M=[mat('Cream cladding',(.73,.70,.56)),mat('Pale arch moulding',(.81,.75,.53)),mat('Red shopfront',(.39,.018,.027),.45),mat('Terracotta brick piers',(.40,.15,.075)),mat('Opaque dark shop glazing',(.045,.065,.065),.3),mat('White roof',(.78,.79,.76)),mat('Blue lettering',(.025,.15,.46)),mat('Dark base',(.055,.05,.04)),mat('Ivory lamps',(.95,.87,.58)),mat('Carousel provisional enclosure',(.32,.27,.20))]
G={}
def face(g,p,mi=0,part='architecture'):
 vs=[Vector(q)for q in p]
 if len(p)<3 or (vs[1]-vs[0]).cross(vs[2]-vs[0]).length<1e-10:return
 key=(part,g);d=G.setdefault(key,[[],[],[]]);n=len(d[0]);d[0].extend(world(q)for q in p);d[1].append(tuple(range(n,n+len(p))));d[2].append(mi)
def rect(g,f,a,b,z0,z1,o=0,mi=0):
 if b-a>1e-6 and z1-z0>1e-6:face(g,[f(a,z0,o),f(b,z0,o),f(b,z1,o),f(a,z1,o)],mi)
def box(g,a,b,mi=0,omit=('bottom','back')):
 x,y,z=a;X,Y,Z=b;p=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
 for name,ids in [('front',(0,1,5,4)),('right',(1,2,6,5)),('back',(2,3,7,6)),('left',(3,0,4,7)),('top',(4,5,6,7)),('bottom',(3,2,1,0))]:
  if name not in omit:face(g,[p[k]for k in ids],mi)
def framed(f,a,b,z0,z1,mi=2):
 t=.075;back=-.12
 for aa,bb,zz,tt in [(a,a+t,z0,z1),(b-t,b,z0,z1),(a+t,b-t,z0,z0+t),(a+t,b-t,z1-t,z1)]:rect('Architecture frames',f,aa,bb,zz,tt,.025,mi)
 for q in [[f(a,z0),f(a,z1),f(a,z1,back),f(a,z0,back)],[f(b,z1),f(b,z0),f(b,z0,back),f(b,z1,back)],[f(a,z1),f(b,z1),f(b,z1,back),f(a,z1,back)],[f(b,z0),f(a,z0),f(a,z0,back),f(b,z0,back)]]:face('Architecture reveals',q,0)
 # Inner frame depth closes oblique sightlines behind the front rim.
 for q in [[f(a+t,z0+t,.025),f(a+t,z1-t,.025),f(a+t,z1-t,back),f(a+t,z0+t,back)],[f(b-t,z1-t,.025),f(b-t,z0+t,.025),f(b-t,z0+t,back),f(b-t,z1-t,back)],[f(a+t,z1-t,.025),f(b-t,z1-t,.025),f(b-t,z1-t,back),f(a+t,z1-t,back)],[f(b-t,z0+t,.025),f(a+t,z0+t,.025),f(a+t,z0+t,back),f(b-t,z0+t,back)]]:face('Architecture inner frame depth',q,mi)
 rect('Architecture glazing',f,a+t,b-t,z0+t,z1-t,back,4)
 for x in [a+(b-a)*i/max(1,round((b-a)/1.1))for i in range(1,max(1,round((b-a)/1.1)))]:rect('Architecture mullions',f,x-.027,x+.027,z0+t,z1-t,.028,mi)
def elevation(side,length,cuts,heights,holes):
 f=at(side);xs=sorted(set([0,length]+cuts+[v for h in holes for v in h[:2]]));zs=sorted(set([D['footing'],0,2.55,3.05]+[v for h in holes for v in h[2:]]))
 for a,b in zip(xs,xs[1:]):
  roof=heights((a+b)/2);levels=sorted(set([z for z in zs if z<roof]+[roof]))
  for z,t in zip(levels,levels[1:]):
   if any(h[0]<(a+b)/2<h[1] and h[2]<(z+t)/2<h[3] for h in holes):continue
   mi=7 if t<=0 else(3 if side=='front' and t<=2.55 else(5 if side=='north' and t<=2.55 else 0))
   rect('Shell walls',f,a,b,z,t,0,mi)
 for a,b,z,t in holes:framed(f,a,b,z,t)
front_holes=[(i*W/4+.28,(i+1)*W/4-.28,0,2.55)for i in range(4)]
elevation('front',W,XS,lambda x:top(x,.01),front_holes)
elevation('north',L,YS,lambda y:top(W-.01,y),[(1,5.2,0,2.55),(26,30.7,0,2.55),(53.5,57.9,0,2.55)])
elevation('rear',W,[W-x for x in XS],lambda x:top(W-x,L-.01),[])
pierholes=[(L-17,L-6,0,2.55),(L-26.3,L-22,0,2.55)]+[(L-y-.65,L-y+.65,4.25,5.7)for y in [20,21.9,23.8,25.7,27.6]]
elevation('pier',L,[L-y for y in YS],lambda y:top(.01,L-y),pierholes)
# Roof grid owns upper surfaces; vertical returns only at genuine height breaks.
for x,X in zip(XS,XS[1:]):
 for y,Y in zip(YS,YS[1:]):
  z=top((x+X)/2,(y+Y)/2);face('Shell roofs',[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z)],5)
for x in XS[1:-1]:
 for y,Y in zip(YS,YS[1:]):
  a,b=top(x-.001,(y+Y)/2),top(x+.001,(y+Y)/2)
  if a!=b:
   p=[(x,y,min(a,b)),(x,Y,min(a,b)),(x,Y,max(a,b)),(x,y,max(a,b))];face('Shell roof returns',p if a>b else list(reversed(p)))
for y in YS[1:-1]:
 for x,X in zip(XS,XS[1:]):
  a,b=top((x+X)/2,y-.001),top((x+X)/2,y+.001)
  if a!=b:
   p=[(X,y,min(a,b)),(x,y,min(a,b)),(x,y,max(a,b)),(X,y,max(a,b))];face('Shell roof returns',p if a>b else list(reversed(p)))
# Scalloped parapet is independently silhouette-bearing, even at massing/District.
f=at('front')
for k in range(8):
 a=k*W/8;b=(k+1)*W/8
 for j in range(8):
  t0=j/8;t1=(j+1)/8;x0=a+(b-a)*t0;x1=a+(b-a)*t1
  z0=8.65-.45*math.sin(math.pi*t0);z1=8.65-.45*math.sin(math.pi*t1)
  face('Architecture scalloped parapet',[(x0,0,8.05),(x1,0,8.05),(x1,0,z1),(x0,0,z0)],0)
  face('Architecture scalloped parapet',[(x1,.20,8.05),(x0,.20,8.05),(x0,.20,z0),(x1,.20,z1)],0)
  face('Architecture scalloped parapet',[(x0,0,z0),(x1,0,z1),(x1,.2,z1),(x0,.2,z0)],1)
# Simplified explicitly provisional carousel enclosure + 16-sided tent canopy.
r=D['carousel']['radius'];cx,cy=D['carousel']['centre'];bottom=canopy_ring(r*.79,-.25,48);mid=canopy_ring(r*.79,3.55,48);edge=canopy_ring(r,3.8,48);shoulder=canopy_ring(r*.42,5.7,48);tip=(cx,cy,10)
for i in range(48):
 j=(i+1)%48;face('Placeholder carousel enclosure',[bottom[i],bottom[j],mid[j],mid[i]],9,'carousel');face('Placeholder carousel canopy',[edge[i],edge[j],shoulder[j],shoulder[i]],5,'carousel');face('Placeholder carousel canopy',[shoulder[i],shoulder[j],tip],5,'carousel')
if D['detail']:
 # Front scalloped arch mouldings stand proud of continuous cream wall.
 for k in range(8):
  a=k*W/8;b=(k+1)*W/8;cx=(a+b)/2;rx=(b-a)/2
  for tier,(off,depth) in enumerate([(0,.13),(.12,.19),(.24,.25)]):
   for j in range(24):
    t0=math.pi*j/24;t1=math.pi*(j+1)/24
    def q(t,r,z):return f(cx+(rx-r)*math.cos(t),3.08+(1.35-r)*math.sin(t),z)
    face('Architecture arch mouldings',[q(t0,off,depth),q(t1,off,depth),q(t1,off+.075,depth),q(t0,off+.075,depth)],1)
  # Fanlight ribs use shallow curved bands, wholly above the fascia.
  for t in [math.pi*.3,math.pi*.5,math.pi*.7]:
   x=cx+(rx-.33)*math.cos(t);z=3.08+1.02*math.sin(t)
   base=cx+.35*math.cos(t)
   face('Architecture fanlight ribs',[f(base-.022,3.08,.09),f(base+.022,3.08,.09),f(x+.022,z,.09),f(x-.022,z,.09)],1)
 # Horizontal fascia and front cornice avoid duplicate mitred corner surfaces.
 box('Architecture fascia',(0,-.24,2.55),(W,-.02,3.05),1,omit=('back',))
 box('Architecture cornice',(0,-.16,7.92),(W,-.02,8.05),1,omit=('back',))
 # Fine vertical cladding grooves are slightly recessed-colour strips on wall.
 for i in range(1,int(W/.15)):
  x=i*.15;rect('Fine front panel seams',f,x,x+.009,4.55,7.92,.007,1)
 # North and pier panel ribs, shallow horizontal lower white cladding.
 for side,ranges in [('north',[(7,25),(31.2,53),(58,59)]),('pier',[(30,40)])]:
  ff=at(side)
  for a,b in ranges:
   for i in range(int((b-a)/2.15)+1):
    x=a+i*2.15;rect('Architecture side ribs',ff,x,x+.15,3.0,7.5,.10,0)
 for z in [i*.18 for i in range(1,14)]:
  for a,b in [(5.3,25.9),(30.8,53.4),(58,59)]:rect('Fine north lower cladding',at('north'),a,b,z,z+.012,.009,0)
 # Only evidenced small ventilation patches; not invented window rows.
 for y,z in [(31.8,6.4),(34,4.45),(38.7,4.45),(43,4.45),(56,4.5)]:
  rect('Architecture vents',at('north'),y,y+.48,z,z+.4,.035,7)
  for j in range(4):rect('Fine vent slats',at('north'),y,y+.48,z+j*.1,z+j*.1+.025,.047,5)
 # Side door fascia and retained low pier linking range fascia.
 for side,spans in [('north',[(26,30.7),(53.5,57.9)]),('pier',[(L-17,L-6)])]:
  for a,b in spans:rect('Architecture side fascia',at(side),a,b,2.55,3.02,.18,1)
 # Lettering is independently authored geometry, consolidated after creation.
 def text(body,f,x,z,size,mi=2,offset=.20,font='LiberationSerif-Bold.ttf',maxwidth=None):
  curve=bpy.data.curves.new('Glyph','FONT');curve.body=body;curve.size=size;curve.align_x='CENTER';curve.extrude=.012;curve.resolution_u=4
  path=Path('/usr/share/fonts/truetype/liberation')/font
  if not path.exists():path=Path('/usr/share/fonts/truetype/liberation2')/font
  if path.exists():curve.font=bpy.data.fonts.load(str(path))
  ob=bpy.data.objects.new('Architecture lettering',curve);C['architecture'].objects.link(ob);ob.location=world(f(x,z,offset))
  a=Vector(world(f(x+1,z,offset)))-Vector(ob.location);up=Vector((0,0,1));out=a.cross(up);ob.rotation_euler=Matrix((a,up,out)).transposed().to_euler();curve.materials.append(M[mi]);bpy.context.view_layer.update()
  if maxwidth:
   bb=[v[0]for v in ob.bound_box];ob.scale.x=maxwidth/(max(bb)-min(bb))
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 text('Silcocks',f,5.7,5.8,2.7,2,.21,'LiberationSerif-BoldItalic.ttf',9.0)
 text('FUNLAND',f,19.8,5.55,3.4,2,.21,maxwidth=15.6)
 text('SOUTHPORT PIER',f,20.4,4.72,1.05,6,.22,maxwidth=12)
 for body,x,mw in [('FAMILY FUN FROM 2p TO £1',6.8,11.8),('WELCOME TO FUNLAND',17.1,7.8),('SNACK BAR INSIDE',W*.84,6.5)]:text(body,f,x,2.69,.37,2,.26,maxwidth=mw)
 text('Silcocks FUNLAND',at('north'),43,5.7,1.8,2,.14,'LiberationSerif-Bold.ttf',24)
 text('SOUTHPORT PIER',at('north'),43.8,4.85,.70,6,.14,maxwidth=17)
 text('Silcocks FUNLAND',at('rear'),W/2,5.9,1.45,2,.14,maxwidth=25)
 text('FUNLAND & PIER',at('pier'),15,6.2,1.45,2,-.94,maxwidth=27)
 for y in range(1,30,2):rect('Architecture rear hall ribs',at('pier'),y,y+.16,3.85,8.12,-1.0,0)
 for a,b in [(26,30.7),(53.5,57.9)]:text('FUNLAND OPEN EVERYDAY',at('north'),(a+b)/2,2.69,.28,2,.20,maxwidth=b-a-.1)
 # Parapet ball finials, small lamp beads and poles define actual silhouette.
 for i in range(9):
  x=i*W/8;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.13,location=world((x,.1,8.76)));ob=bpy.context.object;ob.name='Architecture finial';
  for c in list(ob.users_collection):c.objects.unlink(ob)
  C['architecture'].objects.link(ob);ob.data.materials.append(M[1])
 for i in [0,2,4,6,8]:box('Architecture flag pole',(i*W/8-.025,.075,8.8),(i*W/8+.025,.125,10.05),5,omit=())
 for k in range(8):
  cx=(k+.5)*W/8
  for j in range(19 if k else 20):
   t=math.pi*j/19;x=cx+W/16*math.cos(t);z=3.08+1.35*math.sin(t)
   face('Fine arch lamps',[f(x-.023,z-.016,.28),f(x+.023,z-.016,.28),f(x,z+.023,.28)],8)
# Finish bounded groups and consolidate glyphs for bake performance.
for (part,name),(verts,faces,mids) in G.items():
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);C[part].objects.link(ob)
 for m in M:me.materials.append(m)
 for p,mi in zip(me.polygons,mids):p.material_index=mi
for c in C.values():
 for ob in c.objects:
  if ob.type=='MESH':
   me=ob.data;uv=me.uv_layers.new(name='Authored metric UV')
   for p in me.polygons:
    axes=sorted(range(3),key=lambda i:abs(p.normal[i]))[:2]
    for li in p.loop_indices:
     v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
for prefix in ['Architecture lettering','Architecture finial']:
 obs=[o for o in C['architecture'].objects if o.name.startswith(prefix)]
 if obs:
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name=prefix
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.67,.73,.82,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.5;sun.rotation_euler=(.4,-.7,-.5);s.collection.objects.link(sun)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';s.camera=cam;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
(ROOT/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/funland.blend'))
