"""Stanley corner: authored stone openings, chamfer and unequal roof pitches."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from southport3d.terrain import GroundControls
from components import rect,cut,arch,ring,profile
from plan import world,outline,roof
D=json.loads((ROOT/'research/layout.json').read_text());W=D['width'];L=D['depth'];H=D['parapet'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
T=Matrix(((-.0003,1,0,D['x']),(-1,.0125,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
F=T@face_matrix((0,0,0),(0,-1,0));SIDE=T@face_matrix((0,L,0),(-1,0,0));BACK=T@face_matrix((W,L,0),(0,1,0));PARTY=T@face_matrix((W,0,0),(1,0,0))
def mat(name,color,rough=.8,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
stone=mat('Weathered buff sandstone',(.54,.47,.32));light=mat('Sandstone arrises',(.65,.58,.42));shade=mat('Stone recesses',(.35,.30,.22));brick=mat('Rear red brick',(.41,.18,.12),texture='brick');slate=mat('Rear slate pitch',(.17,.20,.22),texture='slate');lead=mat('Shallow front roof lead',(.33,.34,.34));glass=mat('Opaque shaded window glass',(.23,.29,.30),.35);white=mat('Cream painted window frames',(.78,.77,.69));curtain=mat('Pale window curtains',(.59,.58,.51));iron=mat('Dark canopy iron',(.07,.065,.05));rust=mat('Weathered canopy fascia',(.24,.17,.09));canopyglass=mat('Weathered canopy glazing',(.39,.46,.46),.4);pink=mat('Treat Street pink',(.65,.19,.40));blue=mat('RDs blue',(.10,.30,.43));red=mat('AK red shop',(.42,.045,.035));black=mat('Barber dark shop',(.045,.04,.035));gold=mat('Sign gold',(.79,.62,.27));steel=mat('Dull duct metal',(.40,.44,.44));wood=mat('Yard timber',(.19,.15,.10))
def finish(m,part='frontage',material=stone,frame=None):
 if not m.faces:return
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric authored surface')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   uv.data[li].uv=(v[axes[0]]/4,v[axes[1]]/4) if material.name=='Dark charcoal shallow roof covering' else (v[axes[0]]/1.8,v[axes[1]]/(1.8 if material==slate else .6))
 ob.data.transform(frame if frame is not None else T);return ob
def box(name,c,size,material=stone,part='frontage',frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,material,frame)
def panel(name,p,out,material,part='frontage',frame=F):
 m=Mesh(name);m.add([(*v,out) for v in p],[tuple(range(len(p)))]);return finish(m,part,material,frame)
def wall(name,polygon,holes,frame=F,material=stone,part='frontage'):
 m=Mesh('Shell '+name)
 for pp in cut(polygon,holes):m.add([(*v,0) for v in pp],[tuple(range(len(pp)))]);m.add([(*v,-.24) for v in pp],[tuple(reversed(range(len(pp))))])
 for hp in holes:
  for a,b in zip(hp,hp[1:]+hp[:1]):m.add([(*a,0),(*b,0),(*b,-.24),(*a,-.24)],[(0,1,2,3)])
 return finish(conform({'wall':m})[0]['wall'],part,material,frame)
def border(name,outer,inner,out,material=white,part='frontage',frame=F):
 m=Mesh(name)
 for p in cut(outer,[inner]):m.add([(*v,out) for v in p],[tuple(range(len(p)))])
 return finish(m,part,material,frame)
def window(u,w,frame=F,part='frontage',bottom=None,spring=None,rise=None):
 z=D['window_bottom'] if bottom is None else bottom;t=D['window_spring'] if spring is None else spring;r=D['window_rise'] if rise is None else rise
 p=arch(u,z,t,w/2,r);panel('Glazing arched bay',p,-.16,glass,part,frame)
 border('Architecture arched window frame',p,arch(u,z+.08,t,w/2-.075,max(.01,r-.08)),-.065,white,part,frame)
 if not DETAIL:return
 # Each rail is clipped against the aperture. Cream painted spandrel with dark inset panels.
 for zz in (z+.10,7.45,7.62,8.33,8.46,9.55):
  if zz<z or zz>t+r:continue
  box('Architecture sash horizontal',(u,zz,-.048),(w-.14,.065,.055),white,part,frame)
 for dx in (-w*.27,0,w*.27):
  # Upper mullion terminates on the true ellipse, keeping its arch silhouette.
  top=t+r*math.sqrt(max(0,1-(dx/(w/2))**2))-.08
  for a,b in [(z+.08,7.42),(8.49,top)]:
   if b>a:box('Architecture sash upright',(u+dx,(a+b)/2,-.049),(.055,b-a,.055),white,part,frame)
 panel('Architecture painted spandrel',rect(u-w/2+.08,7.66,u+w/2-.08,8.29),-.055,white,part,frame)
 for dx,ww in [(-w*.36,.38),(0,w*.47),(w*.36,.38)]:
  panel('Fine spandrel dark inset',rect(u+dx-ww/2,7.76,u+dx+ww/2,8.18),-.043,glass,part,frame)
  panel('Fine spandrel centre',rect(u+dx-ww/2+.06,7.82,u+dx+ww/2-.06,8.12),-.030,white,part,frame)
 # Vertical curtain folds lie behind frames, in the glazing recess.
 for j in range(18):
  xx=u-w/2+.13+j*(w-.26)/18;ww=(w-.26)/18*.82
  for aa,bb in [(z+.15,7.38),(8.55,t+r)]:
   za=min(bb,t+r*math.sqrt(max(0,1-((xx-u)/(w/2))**2))-.10)
   zb=min(bb,t+r*math.sqrt(max(0,1-((xx+ww-u)/(w/2))**2))-.10)
   panel('Fine curtain fold',[(xx,aa),(xx+ww,aa),(xx+ww,zb),(xx,za)],-.14,curtain,part,frame)
 box('Architecture stone window sill',(u,z-.12,.12),(w+.26,.18,.30),light,part,frame)
 m=Mesh('Architecture arch voussoirs')
 for j in range(11):
  a=math.pi*j/11+.008;b=math.pi*(j+1)/11-.008
  pp=[(u+(w/2+q)*math.cos(t),D['window_spring']+(r+q)*math.sin(t)) for q,t in [(0,a),(0,b),(.38,b),(.38,a)]]
  m.outline(pp,.005,.085)
 finish(m,part,light,frame)
 box('Architecture arch keystone',(u,t+r+.16,.12),(.23,.64,.26),light,part,frame)

c=D['chamfer'];front_holes=[arch(u,D['window_bottom'],D['window_spring'],D['window_width']/2,D['window_rise']) for u in D['window_centres']]
wall('front stone',rect(c,4.25,W,H),front_holes)
for u in D['window_centres']:window(u,D['window_width'])
# Stanley return: one full stone arch, one narrow brick bay at the rear.
side_u=L-4.45;sidehole=arch(side_u,4.65,10.45,1.62,1.52)
wall('Stanley dressed stone',rect(3.0,4.25,L-c,H),[sidehole],SIDE)
window(side_u,3.24,SIDE)
smallholes=[rect(.95,z,1.85,z+1.8) for z in (5.25,9.25)]
wall('Stanley brick strip',rect(0,0,3.0,H),smallholes,SIDE,brick)
for z in (5.25,9.25):
 panel('Glazing narrow return',rect(.95,z,1.85,z+1.8),-.12,glass,frame=SIDE)
 border('Architecture narrow return frame',rect(.95,z,1.85,z+1.8),rect(1.01,z+.07,1.79,z+1.73),-.05,white,frame=SIDE)
 box('Architecture narrow return sill',(1.4,z-.08,.10),(1.10,.13,.25),light,frame=SIDE)
# Chamfer has a narrow double-height sash, continuous masonry and shop door.
CH=T@face_matrix((0,c,0),(-1,-1,0));cw=c*math.sqrt(2);chhole=rect(.30,4.65,cw-.30,11.85)
wall('chamfer',rect(0,4.25,cw,H),[chhole],CH)
panel('Glazing chamfer',chhole,-.16,glass,frame=CH)
border('Architecture chamfer sash',chhole,rect(.36,4.72,cw-.36,11.78),-.06,white,frame=CH)
for z in (7.45,8.42,10.1):box('Architecture chamfer rail',(cw/2,z,-.04),(cw-.60,.07,.06),white,frame=CH)
# Actual brick rear is visible from the service yard. Lower coverage is occluded.
rearholes=[rect(u-.44,z,u+.44,z+1.5) for u in (2.0,5.4,9.0,12.5,15.1) for z in (4.9,8.2) if not (u==12.5 and z==4.9)]
wall('rear brick',rect(0,0,W,D['rear_eave']),rearholes,BACK,brick,'rear')
for u in (2.0,5.4,9.0,12.5,15.1):
 for z in (4.9,8.2):
  if u==12.5 and z==4.9:continue # Unverified lower aperture conflicts with observed service projection.
  panel('Glazing estimated rear',rect(u-.44,z,u+.44,z+1.5),-.12,glass,'rear',BACK)
  border('Architecture rear sash',rect(u-.44,z,u+.44,z+1.5),rect(u-.39,z+.06,u+.39,z+1.44),-.05,white,'rear',BACK)
  box('Architecture rear sill',(u,z-.06,.06),(1.02,.11,.20),stone,'rear',BACK)
wall('party',[(0,0),(L,0),(L,D['rear_eave']),(D['ridge_v'],D['ridge']),(0,D['front_eave'])],[],PARTY,brick,'rear')
# Aerial review shows a dark charcoal shallow covering, not pale sheet metal.
membrane=mat('Dark charcoal shallow roof covering',(.065,.070,.075),rough=.92,texture='covering')
# Coordinated roof boundary; slate rear and hip, shallow membrane front.
for name,p in roof(D):
 m=Mesh('Shell roof '+name);m.add(p,[tuple(range(len(p)))]);finish(m,'roof',membrane if name=='front' else slate)
# Inward parapet closure on the Stanley end: the photographed raised side
# cornice stands above the descending hip. Close its back and cap explicitly.
m=Mesh('Shell Stanley parapet closure')
m.add([(0,c,H),(0,L,H),(.24,L,H),(.24,c,H)],[(0,1,2,3)])
m.add([(.24,c,H),(.24,L,H),(.24,L,D['rear_eave']),(.24,c,D['front_eave'])],[(0,1,2,3)])
finish(m,'roof',stone)
m=Mesh('Shell front parapet closure')
m.add([(c,0,H),(W,0,H),(W,.24,H),(c,.24,H)],[(0,1,2,3)])
m.add([(W,.24,H),(c,.24,H),(c,.24,D['front_eave']),(W,.24,D['front_eave'])],[(0,1,2,3)])
finish(m,'roof',stone)

# Shop ground apertures retain recesses even during massing.
shops=[(c,2.65,pink,'Treat Street'),(2.65,7.05,blue,'R.D.s Bar'),(7.05,12.0,red,'AK NAILS & SPA'),(12.0,W,black,'Istanbul Barber')]
for a,b,colour,label in shops:
 holes=[rect(a+.13,.28,b-.13,3.10)]
 wall('shop '+label,rect(a,0,b,4.25),holes,material=colour)
 panel('Glazing shop '+label,holes[0],-.20,glass)
 border('Architecture shop frame',holes[0],rect(a+.21,.39,b-.21,3.02),-.07,colour)
 for u in (a+(b-a)*.34,a+(b-a)*.65):box('Architecture shop mullion',(u,1.69,-.045),(.075,2.79,.08),colour)
 box('Architecture shop fascia',((a+b)/2,3.47,.06),(b-a-.03,.58,.18),colour)
wall('pink return shop',rect(3,0,L-c,4.25),[rect(3.8,.3,L-c-.3,2.8)],SIDE,pink)
panel('Glazing return shutter',rect(3.8,.3,L-c-.3,2.8),-.12,white,frame=SIDE)
wall('pink chamfer shop',rect(0,0,cw,4.25),[rect(.16,.12,cw-.16,2.9)],CH,pink)
panel('Glazing pink corner door',rect(.16,.12,cw-.16,2.9),-.15,glass,frame=CH)

if DETAIL:
 # Rusticated piers have recessed horizontal joints; no duplicate stone face.
 for frame,piers in [(F,[(1.6,.66),(6.67,.72),(11.61,.72),(16.35,.65)]),(SIDE,[(3.35,.65),(L-c-.35,.65)]),(CH,[(.14,.26),(cw-.14,.26)])]:
  for u,w in piers:
   for j in range(15):
    z=4.47+j*.53;box('Architecture rusticated pier',(u,z,.12),(w,.49,.25),light,frame=frame)
   for z,ww,hh,dep in [(4.29,w+.25,.16,.34),(12.40,w+.15,.22,.36),(12.70,w+.37,.20,.48),(13.05,w+.52,.18,.60),(13.39,w+.48,.25,.48)]:box('Architecture pier capital',(u,z,dep/2),(ww,hh,dep),light,frame=frame)
 # Continuous cornice profiles clipped to each actual wall face, at a chamfer.
 for frame,a,b in [(F,c,W),(SIDE,0,L-c),(CH,0,cw)]:
  for zz,hh,out in [(4.18,.10,.12),(4.38,.12,.18),(12.25,.13,.15),(12.55,.18,.23),(12.90,.18,.36),(13.20,.20,.22),(13.49,.12,.33)]:
   box('Architecture string cornice',((a+b)/2,zz,out/2),(b-a,hh,out),stone,frame=frame)
 # Fine fascias and readable tenant labels. Small logos are deliberately omitted.
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf')
 def letters(body,u,z,w,h,colour=gold,frame=F,out=.165):
  ob=text_object('Fine tenant '+body,body,(0,0,0),(0,0,1),h,w,font,colour,extrude=.002,collection=C['frontage'],fit_bounds=True);M=frame@Matrix.Translation((u,z,out))@ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);ob.data.transform(M);ob.matrix_world=Matrix.Identity(4)
  if not ob.data.uv_layers:ob.data.uv_layers.new()
  return ob
 for a,b,col,label in shops:letters(label,(a+b)/2,3.47,b-a-.25,.33,white if col==pink else gold)
 # Applied fascia follows the observed high strip, clear of the extraction run.
 box('Architecture return fascia pink',((3+L-c)/2,3.85,.045),(L-c-3,.56,.09),pink,frame=SIDE)
 box('Architecture return fascia blank',(0.6,3.85,.045),(1.2,.56,.09),white,frame=SIDE)
 box('Architecture return fascia dark',(2.1,3.85,.045),(1.8,.56,.09),black,frame=SIDE)
 ob=letters('Treat Street',6.05,3.86,4.5,.42,white,SIDE,.10);ob.name='Architecture return lettering'
 # Stanley entrance, extraction duct and observed downpipes; no invented rear doors.
 panel('Architecture Stanley entrance',rect(.72,.05,2.03,2.75),.015,black,frame=SIDE)
 border('Architecture Stanley door casing',rect(.60,.02,2.15,2.88),rect(.72,.05,2.03,2.75),.04,stone,frame=SIDE)
 letters('2',1.38,2.35,.16,.18,white,SIDE,.04)
 for z in (.6,1.25,1.95):border('Fine door recessed panel',rect(.83,z,1.89,z+.48),rect(.89,z+.06,1.83,z+.42),.03,iron,frame=SIDE)
 from return_services import build as build_return_services
 build_return_services((Mesh,finish,box,SIDE,steel,iron))
 for frame,u,height in [(SIDE,.13,12.7),(F,W-.06,12.3),(BACK,W-.15,10.5)]:
  m=Mesh('Fine rainwater pipe');m.tube([(u,.2,.19),(u,height,.19)],.045,sides=8);finish(m,'rear' if frame==BACK else 'frontage',iron,frame)

# Glazed canopy: open underneath, supported by slender columns. Fixed silhouette.
can=D['canopy'];a,b=can['start'],can['end'];v=-can['depth'];zi,zo=can['inner_z'],can['outer_z']
m=Mesh('Shell canopy glass');m.add([(a,0,zi),(a,v,zo),(b,v,zo),(b,0,zi)],[(0,1,2,3)]);finish(m,'roof',canopyglass)
for u in (a,b):
 m=Mesh('Architecture canopy end');m.tube([(u,0,zi),(u,v,zo)],.045,sides=6);finish(m,'roof',iron)
for vv,zz in [(0,zi),(v,zo)]:box('Architecture canopy fascia',((a+b)/2,vv,zz),(b-a,.12,.20),rust,'roof',T)
for u in (3.4,9.0,15.7):
 p=T@Vector((u,v,0));foot=GroundControls(REPO/'regions/southport/elevation/ground-controls.json').height(p.x,p.y)+.12-D['base_z']
 m=Mesh('Architecture canopy post');m.tube([(u,v,foot),(u,v,zo)],.045,sides=8);finish(m,'roof',iron)
if DETAIL:
 for j in range(33):
  u=a+(b-a)*j/32;m=Mesh('Fine canopy glazing bar');m.tube([(u,0,zi+.025),(u,v,zo+.025)],.018,sides=5);finish(m,'roof',iron)
 for j in range(1,4):
  t=j/4;box('Fine canopy cross rail',((a+b)/2,v*t,zi+(zo-zi)*t+.025),(b-a,.035,.035),iron,'roof',T)

# Research-backed yard attachment and boundary, with no duplicate court slab.
from courtyard import build as build_courtyard
build_courtyard((Mesh,finish,box,T,brick,wood,iron,stone,lead))

# Explicit single ownership of shared capital/cornice planes, including backs.
sys.path.insert(0,str(REPO/'tools'))
from surface_owner import partition
ownership=partition([o for group in C.values() for o in group.objects if o.type=='MESH'])
(ROOT/'research/surface-ownership.json').write_text(json.dumps(ownership,indent=2))
# Batch compatible features; shell and glazing names remain inspectable.
for part in C:
 groups={}
 for ob in list(C[part].objects):
  if ob.type=='MESH' and not ob.name.startswith(('Shell ','Glazing ','Architecture return ')):groups.setdefault('Fine' if ob.name.startswith('Fine ') else 'Architecture',[]).append(ob)
 for kind,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  obs[0].name=kind+' '+part
# Float32 conversion of newly split faces can expose a formerly sub-tolerance
# shared edge. Repartition the final batched topology, never offset its depth.
ownership['batched_passes']=[]
for _ in range(3):
 row=partition([o for group in C.values() for o in group.objects if o.type=='MESH']);ownership['batched_passes'].append(row)
 if not row['candidate_pairs']:break
(ROOT/'research/surface-ownership.json').write_text(json.dumps(ownership,indent=2))
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.3;sun.rotation_euler=(.4,.6,.4)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/nevill-street-16-22.blend'))
