"""Burlington Buildings: four unequal front divisions and cross-gabled rear wings."""
from pathlib import Path
import bpy,bmesh,json,math,os,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from shapes import rect,cuts,transform,roofs,exterior,canopy_profile,main_roof_z
D=json.loads((ROOT/'research/layout.json').read_text());W=D['front_width'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for p in ['front','rear','roof','canopy']:
 C[p]=bpy.data.collections.new(p);s.collection.children.link(C[p])
T=Matrix(((1,D['side_shear'],0,D['front_origin'][0]),(D['front_shear'],1,0,D['front_origin'][1]),(0,0,1,D['floor_z']),(0,0,0,1)))
F=face_matrix((0,0,0),(0,-1,0))
def mat(name,rgb,rough=.8,tex=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;nt=m.node_tree;p=nt.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if tex:
  uv=nt.nodes.new('ShaderNodeTexCoord');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'textures'/('slate.png' if tex=='slate' else 'brick.png')));im.extension='REPEAT';nt.links.new(uv.outputs['UV'],im.inputs['Vector']);nt.links.new(im.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Burlington red brick',(.33,.13,.075),tex=True);cream=mat('Pale painted dressings',(.79,.77,.67));infill=mat('Modern pale infill',(.66,.67,.63));glass=mat('Muted window glass',(.17,.23,.26),.26);white=mat('White joinery',(.84,.85,.81),.45);slate=mat('Grey slate',(.16,.18,.20),tex='slate');lead=mat('Dark membrane and flashing',(.14,.15,.16));iron=mat('Dark iron',(.035,.055,.046),.48);roofglass=mat('Opaque canopy glass',(.34,.40,.39),.3);black=mat('Dark shop joinery',(.035,.045,.047));green=mat('The Works green',(.09,.30,.12));brown=mat('Cafe dark joinery',(.075,.07,.06));stone=mat('Foundation stone',(.33,.31,.28));pot=mat('Chimney terracotta',(.38,.17,.09));gold=mat('Muted lettering',(.63,.54,.29))
def finish(m,part,material,M=None):
 if not m.faces:return
 if m.name.startswith('Shell'):m=conform({'m':m})[0]['m']
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.0,v[axes[1]]/1.2)
 ob.data.transform(T@(M if M is not None else Matrix.Identity(4)));return ob

def box(name,c,sz,material=cream,part='front',M=F):
 if M is F and name.startswith('Trim'):
  a=max(0,c[0]-sz[0]/2);b=min(W,c[0]+sz[0]/2);c=((a+b)/2,c[1],c[2]);sz=(b-a,sz[1],sz[2])
 m=Mesh(name);m.box(c,sz)
 if name.startswith('Trim') and M is not None:
  # Attached dressings own the outward skin; their buried back is the wall's surface.
  m.faces.pop(0);m.indices.pop(0)
 if (M is F and name.startswith('Trim')) or (name=='Canopy longitudinal beam' and abs(c[1])<1e-8):
  # Shared party-line end skin belongs to the structural wall, not attached trim.
  m.faces=[f for f in m.faces if not any(all(abs(m.vertices[i][0]-edge)<1e-8 for i in f) for edge in (0,W))];m.indices=[0]*len(m.faces)
 return finish(m,part,material,M)
def plane(name,p,material,part='front',M=F):
 m=Mesh(name);m.add(p,[tuple(range(len(p)))]);return finish(m,part,material,M)
def tube(name,pts,r,material=iron,part='canopy',M=None,n=8):
 m=Mesh(name);m.tube(pts,r,sides=n);return finish(m,part,material,M)
def wall(name,p,holes,material=brick,part='front',M=F):
 m=Mesh('Shell '+name)
 for poly in cuts(p,holes):
  m.add([(*v,0) for v in poly],[tuple(range(len(poly)))])
  if 'parapet' in name:m.add([(*v,-.22) for v in poly],[tuple(reversed(range(len(poly))))])
 if 'parapet' in name:
  for a,b in zip(p,p[1:]+p[:1]):m.add([(*b,0),(*a,0),(*a,-.22),(*b,-.22)],[(0,1,2,3)])
 for poly in holes:
  for a,b in zip(poly,poly[1:]+poly[:1]):m.add([(*a,0),(*b,0),(*b,-.22),(*a,-.22)],[(0,1,2,3)])
 return finish(m,part,material,M)
def window(name,x,z,w,h,M=F,part='front',out=0,material=white,divide=2):
 # Glass lies behind a non-overlapping joined frame. Jambs end at the rails.
 plane('Glass '+name,[(x-w/2,z,-.205+out),(x+w/2,z,-.205+out),(x+w/2,z+h,-.205+out),(x-w/2,z+h,-.205+out)],glass,part,M)
 t=.065
 for zz in (z+t/2,z+h-t/2):box('Joinery '+name+' rail',(x,zz,-.115+out),(w,t,.15),material,part,M)
 for xx in (x-w/2+t/2,x+w/2-t/2):box('Joinery '+name+' jamb',(xx,z+h/2,-.115+out),(t,h-2*t,.15),material,part,M)
 for i in range(1,divide):box('Joinery '+name+' mullion',(x-w/2+w*i/divide,z+h/2,-.115+out),(.06,h-2*t,.15),material,part,M)
 for i in range(divide):
  xx=x-w/2+w*(i+.5)/divide
  box('Joinery '+name+' transom',(xx,z+h*(.73 if name=='cafe first' else .67 if 'first' in name else .50),-.112+out),(w/divide-.07,.055,.15),material,part,M)
 if DETAIL and not name.startswith(('shop','door')):
  box('Trim '+name+' sill',(x,z-.065,.21+out),(w+.16,.13,.42),cream,part,M)
  if 'second' not in name or name=='name second':box('Trim '+name+' lintel',(x,z+h+.12,.12+out),(w+.16,.24,.24),cream,part,M)

# Window groups measured against the photographed four facade divisions.
win=[('south first',2.52,4.95,2.9,2.55),('middle first west',7.8,4.95,2.9,2.55),('middle first east',11.45,4.95,2.9,2.55),('name first',16.65,4.95,3.05,2.55),('cafe first',22.65,4.95,3.6,2.55),('south second',2.52,9.15,2.9,2.65),('name second',16.65,9.15,3.05,2.65)]
for bay,xc,lights in [('middle',9.55,[(-3,.65),(-1.8,.8),(0,1.45),(1.8,.8),(3,.65)]),('cafe',22.65,[(-1.3,.75),(0,1.45),(1.3,.75)])]:
 for i,(dx,ww) in enumerate(lights):win.append((bay+' second '+str(i),xc+dx,9.15,ww,2.65))
holes=[rect(x-w/2,z,x+w/2,z+h) for _,x,z,w,h in win]
wall('front main',rect(0,4.44,W,12.55),holes)
for name,x,z,w,h in win:window(name,x,z,w,h,out=.35 if name=='cafe first' else 0,divide=3 if name=='cafe first' else (2 if w>2 else 1))
# Ground shopfronts; apartment entrance and commercial openings remain recessed.
shops=[('apartments',.16,1.22,black),('works',1.4,9.13,green),('menswear',9.33,19.22,black),('cafe',19.6,W-.16,brown)]
doors=[]
for name,a,b,material in shops:
 cx=(a+b)/2 if name in ('apartments','works','cafe') else a+.625
 dw=(b-a) if name=='apartments' else 1.25
 da,db=cx-dw/2,cx+dw/2;doors.append((name,da,db))
 box('Shop '+name+' fascia',((a+b)/2,3.79,.01),(b-a,.54,.24),material)
 for j,(lo,hi) in enumerate([(a,da),(db,b)]):
  if hi-lo<.03:continue
  box('Shop '+name+' base',((lo+hi)/2,.19,-.01),(hi-lo,.38,.22),material)
  window('shop '+name+str(j),(lo+hi)/2,.38,hi-lo,3.14,out=-.10,material=material,divide=max(1,round((hi-lo)/1.4)))
  box('Foundation shop '+name,((lo+hi)/2,.10,-.18),(hi-lo,.2,.36),stone,'front',None)
 window('door '+name,cx,0,dw,3.52,out=-.395,material=material,divide=1 if name=='apartments' else 2)
 for xx,rev in [(da,False),(db,True)]:
  pp=[(xx,0,0),(xx,3.52,0),(xx,3.52,-.435),(xx,0,-.435)]
  plane('Door return '+name,pp[::-1] if rev else pp,material)
pier_base=D['foundation_z']-D['floor_z']
for i,(a,b) in enumerate([(0,.16),(1.22,1.4),(9.13,9.33),(19.22,19.6),(W-.16,W)]):box('Shop pier '+str(i),((a+b)/2,(4.44+pier_base)/2,0),(b-a,4.44-pier_base,.35),brick)
from southport3d.elevation import Elevations
approach=Elevations(REPO/'regions/southport/elevation/lord-burlington.json').surface('burlington-front-approach')
for name,left,right in doors:
 pts=[]
 for x,y in [(left,0),(right,0),(right,.6),(left,.6)]:
  world=transform(D,(x,y,0));h=approach.height(world[0],world[1]) if y==0 else D['floor_z']
  pts.append((x,y,h-D['floor_z']))
 plane('Entrance threshold '+name,pts,stone,'front',None)
# Structural roof and rear surfaces, including unequal wings and valley cuts.
for name,p in exterior(D):
 if name=='cafe rear gable':
  # Marketing first-floor plan shows a rear kitchen door/window; upper rear has one light.
  a,b=D['wings'][-1]['x0'],D['wings'][-1]['x1'];end=D['wings'][-1]['end'];mid=(a+b)/2
  M=face_matrix((b,end,0),(0,1,0));poly=[(b-x,z) for x,y,z in p]
  apertures=[rect(1.1,4.2,2.0,6.35),rect(3.9,4.95,4.85,6.25),rect(2.7,8.2,3.65,9.5)]
  wall(name,poly,apertures,brick,'rear',M)
  window('rear kitchen door',1.55,4.2,.9,2.15,M,'rear',material=black,divide=1)
  window('rear kitchen light',4.375,4.95,.95,1.3,M,'rear',divide=1)
  window('rear upper light',3.175,8.2,.95,1.3,M,'rear',divide=1)
 else:plane('Shell '+name,p,brick,'rear',None)
rm=Mesh('Roof continuous slopes')
for name,p in roofs(D):
 if 'membrane' in name:plane('Roof '+name,p,lead,'roof',None)
 else:rm.add(p,[tuple(range(len(p)))])
rm=conform({'roof':rm})[0]['roof'];finish(rm,'roof',slate)
# Continuous front parapet has separately owned openings; supports stay in their bays.
wall('parapet base',rect(0,12.55,W,12.85),[],brick)
for a,b in zip(D['bay_edges'],D['bay_edges'][1:]):
 if abs(a-13.9)<.01:
  wall('name parapet',rect(a,12.85,b,13.65),[],brick)
 else:
  n=max(2,round((b-a)/.46));gap=(b-a-.4)/n
  hs=[rect(a+.20+i*gap+.10,12.91,a+.20+(i+1)*gap-.10,13.22) for i in range(n)]
  wall('pierced parapet',rect(a,12.85,b,13.35),hs,brick)
# Canopy profile: paired skins separate top and underside, open air below.
profile=canopy_profile(D,12)
for j,((p,z),(q,zz)) in enumerate(zip(profile,profile[1:])):
 plane('Canopy glass top '+str(j),[(0,-q,zz),(W,-q,zz),(W,-p,z),(0,-p,z)],roofglass,'canopy',None)
 plane('Canopy glass underside '+str(j),[(0,-p,z-.035),(W,-p,z-.035),(W,-q,zz-.035),(0,-q,zz-.035)],roofglass,'canopy',None)
support=Elevations(REPO/'regions/southport/elevation/lord-burlington.json').surface('burlington-canopy-support')
def post_base(x):
 p=transform(D,(x,-D['canopy']['projection'],0));return support.height(p[0],p[1])-D['floor_z']
for i,x in enumerate(D['canopy']['post_x']):
 tube('Canopy post '+str(i),[(x,-D['canopy']['projection'],post_base(x)+(.56 if DETAIL else 0)),(x,-D['canopy']['projection'],D['canopy']['spring_z']-.07)],.065,n=12)
# Detail pass adds shallow mouldings, roof fittings, signage and canopy joinery.
if DETAIL:
 for z,h,depth in [(4.53,.14,.18),(8.16,.13,.15),(8.53,.10,.12),(12.57,.13,.23)]:box('Trim continuous band',(W/2,z,depth/2),(W,h,depth))
 for i,x in enumerate(D['bay_edges']):
  width=.26 if i in (0,4) else .30;xx=max(width/2,min(W-width/2,x))
  box('Trim brick pilaster',(xx,8.56,.06),(width,7.78,.12),brick)
  for z in (4.59,8.16,12.58):box('Trim pilaster stone band',(xx,z,.145),(width+.14,.19,.29),cream)
  top=13.92 if i in (2,3) else 13.63
  box('Trim parapet pier',(xx,(12.65+top)/2,.01),(width+.12,top-12.65,.40),brick)
  box('Trim pier cap',(xx,top+.06,.03),(width+.27,.12,.50),cream)
  m=Mesh('Trim finial '+str(i));m.lathe((xx,0),[(top+.12,.10),(top+.18,.14),(top+.28,.08),(top+.36,.16),(top+.48,.10),(top+.55,0)],12);finish(m,'front',cream)
 for a,b in zip(D['bay_edges'],D['bay_edges'][1:]):
  top=13.65 if abs(a-13.9)<.01 else 13.35
  box('Trim parapet coping',((a+b)/2,top+.045,.025),(b-a-.42,.09,.38))
 # First-floor cafe bay projects from the plane, with physical returns and skirt.
 for side in (-1,1):
  x=22.65+side*1.8
  plane('Trim cafe bay return',[(x,4.95,0),(x,4.95,.35),(x,7.50,.35),(x,7.50,0)][::side],infill,'front',F)
 box('Trim cafe bay skirt',(22.65,4.78,.175),(3.76,.34,.35),infill)
 box('Trim cafe bay roof',(22.65,7.68,.20),(3.95,.15,.50),lead)
 # Shallow stepped heads preserve the five-light centre rhythm and cafe triplet.
 for name,x,z,w,h in win:
  if 'second' not in name or name=='name second':continue
  q=z+h
  box('Trim upper head centre',(x,q+.18,.13),(w+.10,.20,.20),cream)
  box('Trim upper head shoulder',(x,q+.04,.12),(w+.18,.08,.22),cream)
   # Fine shallow curved shoulders and stops seen on the painted heads.
  for side in (-1,1):
   xx=x+side*(w/2+.03)
   pts=[(xx+side*.03*math.sin(t*math.pi/2),q+.16-.25*t,.22) for t in [i/8 for i in range(9)]]
   tube('Trim moulded head shoulder',pts,.02,cream,'front',F,n=6)
 # Brick dentil band below the parapet keeps its alternating shadow.
 for i in range(round(W/.32)):
  xx=(i+.5)*W/round(W/.32)
  if any(abs(xx-edge)<.30 for edge in D['bay_edges']):continue
  box('Fine brick dentil',(xx,12.43,.075),(.12,.12,.15),brick)
 # Circular medallion and semicircular central hood on the southwest double light.
 pts=[(2.52+.29*math.cos(math.pi*i/16),12.03+.20*math.sin(math.pi*i/16),.22) for i in range(17)]
 tube('Trim southwest hood',pts,.055,cream,'front',F,n=6)
 m=Mesh('Trim southwest roundel');m.outline([(2.52+.16*math.cos(i*math.tau/24),12.88+.16*math.sin(i*math.tau/24)) for i in range(24)],.045,.095);finish(m,'front',cream,F)
 # Modern pale replacements surround their apertures, never cover glazing.
 for x,w in [(2.52,3.3),(7.8,3.3),(11.45,3.3),(16.65,3.45)]:
  z0,z1=(4.66,8.0) if x!=16.65 else(4.66,12.23)
  hs=[rect(xx-ww/2,zz,xx+ww/2,zz+hh) for _,xx,zz,ww,hh in win if abs(xx-x)<.01]
  m=Mesh('Trim pale infill')
  for pp in cuts(rect(x-w/2,z0,x+w/2,z1),hs):m.add([(u,z,.018) for u,z in pp],[tuple(range(len(pp)))])
  finish(m,'front',infill,F)
 box('Trim name panel',(16.65,13.28,.055),(5.0,.54,.11),cream)
 # Actual observed inscription, independent of current tenant signs.
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
 def label(name,body,x,z,size,width,material=black,out=.12,fit=False):
  ob=text_object(name,body,(x,z,out),(0,0,1),size,width,font,material,collection=C['front'],fit_bounds=fit);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.data.transform(T@F@ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.select_set(False)
 label('Architecture Burlington inscription','BURLINGTON BUILDINGS',16.65,13.28,.31,4.4,fit=True)
 label('Shop lettering Works','The Works',5.23,3.64,.34,5.0,white,out=.15)
 label('Shop lettering Menswear','MAN TO MAN',14.27,3.65,.22,6.2,white,out=.15)
 label('Shop lettering Cafe','CAFFE DOLCE',22.65,3.65,.24,5.4,cream,out=.15)
 for name,xx,ww in [('menswear left',12.1,3.1),('menswear right',16.4,3.5),('cafe left',20.9,1.8),('cafe right',24.2,1.8)]:
  plane('Shop shutter '+name,[(xx-ww/2,.42,-.245),(xx+ww/2,.42,-.245),(xx+ww/2,3.42,-.245),(xx-ww/2,3.42,-.245)],infill)
  for j in range(42):box('Fine shutter slat',(xx,.46+j*.07,-.238),(ww,.009,.008),white)
 for i,ch in enumerate(D['chimneys']):
  x,y,w,depth,top=ch['x'],ch['y'],ch['w'],ch['d'],ch['top'];base=main_roof_z(D,y)-.5 if y<D['main_depth'] else D['rear_eaves']-.2
  box('Roof stack '+str(i),(x,y,(base+top)/2),(w,depth,top-base),brick,'roof',None)
  box('Roof stack cap '+str(i),(x,y,top+.07),(w+.15,depth+.15,.14),brick,'roof',None)
  for j in range(ch['pots']):
   xx=x+(-.25 if j%2==0 else .25);yy=y+(-.35 if j//2==0 else .35);m=Mesh('Roof chimney pot');m.lathe((xx,yy),[(top+.14,.12),(top+.45,.11),(top+.50,.15),(top+.57,.15)],10);finish(m,'roof',pot)
 # Ridge rolls, valley flashings and gutters are attached to the measured roof planes.
 tube('Roof ridge roll',[(.12,D['ridge_y'],D['front_ridge']+.04),(W-.12,D['ridge_y'],D['front_ridge']+.04)],.10,pot,'roof',None,n=8)
 for wing in D['wings']:
  a,c=wing['x0'],wing['x1'];mid=(a+c)/2;h=wing['ridge'];join=D['ridge_y']+(D['front_ridge']-h)*(D['main_depth']-D['ridge_y'])/(D['front_ridge']-D['rear_eaves'])
  tube('Roof wing ridge',[(mid,join,h+.04),(mid,wing['end']-.10,h+.04)],.09,lead,'roof',None,n=8)
  for edge in (a,c):tube('Roof valley flashing',[(edge,D['main_depth'],D['rear_eaves']+.015),(mid,join,h+.015)],.055,lead,'roof',None,n=6)
  for xx in (a,c):
   tube('Drain rear gutter',[(xx,D['main_depth'],D['rear_eaves']-.03),(xx,wing['end'],D['rear_eaves']-.03)],.065,iron,'rear',None,n=8)
  xx=c-.12;tube('Drain rear downpipe',[(xx,wing['end']+.08,4.0),(xx,wing['end']+.08,D['rear_eaves']-.08)],.045,iron,'rear',None,n=8)
 # Individually evidenced rooflights, not a regular invented grid.
 for x,y in [(3.5,8.3),(4.7,8.3),(10.5,11.0),(16.1,10.5),(23.2,11.3)]:
  z=main_roof_z(D,y);slope=(D['rear_eaves']-D['front_ridge'])/(D['main_depth']-D['ridge_y'])
  p=[(x-.35,y-.55,z-.55*slope+.06),(x+.35,y-.55,z-.55*slope+.06),(x+.35,y+.55,z+.55*slope+.06),(x-.35,y+.55,z+.55*slope+.06)]
  plane('Roof rooflight',p,glass,'roof',None)
  for a,b in zip(p,p[1:]+p[:1]):tube('Roof rooflight frame',[a,b],.035,lead,'roof',None,n=6)
 for x in [0.0,5.05,13.9,19.4,W]:
  tube('Drain front downpipe',[(min(W-.08,x+.08),-.21,4.4),(min(W-.08,x+.08),-.21,12.4)],.045,iron,'front',None,n=8)
 for i in range(round(W/.53)+1):
  x=W*i/round(W/.53);tube('Canopy glazing bar '+str(i),[(x,-p,z+.035) for p,z in profile],.025,cream,'canopy',None,n=6)
 for y,z in [(0,4.34),(-D['canopy']['projection'],D['canopy']['spring_z'])]:box('Canopy longitudinal beam',(W/2,y,z-.08),(W,.10,.16),iron,'canopy',None)
 for x in D['canopy']['post_x']:
  box('Canopy post pedestal',(x,-D['canopy']['projection'],post_base(x)+.28),(.20,.20,.56),iron,'canopy',None)
  for sign in (-1,1):
   pts=[(x+sign*.95*(1-t),-D['canopy']['projection'],D['canopy']['spring_z']-.12-.65*t*t) for t in [i/10 for i in range(11)]]
   if min(p[0] for p in pts)>=0 and max(p[0] for p in pts)<=W:tube('Canopy scrolling bracket',pts,.034,cream,'canopy',None,n=6)
 # Cast-iron small valance drops remain a controlled detail feature.
 for i in range(round(W/.18)):
  x=(i+.5)*W/round(W/.18);tube('Fine canopy valance',[(x,-3.18,3.54),(x,-3.18,3.43)],.012,cream,'canopy',None,n=5)
# Upright camera and neutral daylight.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.6;l.rotation_euler=(.6,-.4,-.6);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));c.data.type='ORTHO';s.collection.objects.link(c);s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/burlington-buildings.blend'))
