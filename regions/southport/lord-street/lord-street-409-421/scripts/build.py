"""Burlington Buildings: four unequal front divisions and cross-gabled rear wings."""
from pathlib import Path
import bpy,bmesh,json,math,os,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from southport3d.conform import conform
from shapes import rect,cuts,transform,roofs,exterior,canopy_profile,bays,box_bays,facade_x
D=json.loads((ROOT/'research/layout.json').read_text());W=D['front_width'];DETAIL=D['phase']=='detail'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for p in ['front','rear','roof','canopy']:
 C[p]=bpy.data.collections.new(p);s.collection.children.link(C[p])
T=Matrix(((1,D['side_shear'],0,D['front_origin'][0]),(D['front_shear'],1,0,D['front_origin'][1]),(0,0,1,D['floor_z']),(0,0,0,1)))
F=face_matrix((0,0,0),(0,-1,0))
NEW_CAFE=False
FM=Matrix.Translation((D['cafe']['width'],0,0)) @ Matrix.Diagonal(((W-D['cafe']['width'])/W,1,1,1))
def mat(name,rgb,rough=.8,tex=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;nt=m.node_tree;p=nt.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if tex:
  uv=nt.nodes.new('ShaderNodeTexCoord');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'textures'/('slate.png' if tex=='slate' else 'stone.png' if tex=='stone' else 'brick.png')));im.extension='REPEAT';nt.links.new(uv.outputs['UV'],im.inputs['Vector']);nt.links.new(im.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Warm red brick',(.33,.13,.075),tex=True);cream=mat('Pale painted dressings',(.79,.77,.67));infill=mat('Modern pale infill',(.66,.67,.63));glass=mat('Muted window glass',(.17,.23,.26),.26);white=mat('White joinery',(.84,.85,.81),.45);slate=mat('Grey slate',(.16,.18,.20),tex='slate');lead=mat('Dark membrane and flashing',(.14,.15,.16));iron=mat('Dark iron',(.035,.055,.046),.48);roofglass=mat('Opaque canopy glass',(.34,.40,.39),.3);black=mat('Dark shop joinery',(.035,.045,.047));green=mat('The Works green',(.09,.30,.12));brown=mat('Cafe dark joinery',(.075,.07,.06));stone=mat('Foundation stone',(.33,.31,.28));pot=mat('Chimney terracotta',(.38,.17,.09));gold=mat('Muted lettering',(.63,.54,.29))
def finish(m,part,material,M=None):
 if not m.faces:return
 if m.name.startswith('Shell'):m=conform({'m':m})[0]['m']
 ob=m.finish([material],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.0,v[axes[1]]/1.2)
 ob.data.transform(T@(FM if part=='front' and not NEW_CAFE else Matrix.Identity(4))@(M if M is not None else Matrix.Identity(4)));return ob

def box(name,c,sz,material=cream,part='front',M=F):
 bound=D['cafe']['width'] if NEW_CAFE else W
 if M is F and name.startswith('Trim'):
  a=max(0,c[0]-sz[0]/2);b=min(bound,c[0]+sz[0]/2);c=((a+b)/2,c[1],c[2]);sz=(b-a,sz[1],sz[2])
 m=Mesh(name);m.box(c,sz)
 if name.startswith('Trim') and M is not None:
  # Attached dressings own the outward skin; their buried back is the wall's surface.
  m.faces.pop(0);m.indices.pop(0)
 if M is F and name.startswith('Shop pier'):
  m.faces=[f for f in m.faces if not any(all(abs(m.vertices[i][0]-edge)<1e-8 for i in f)for edge in (0,bound)) and not all(abs(m.vertices[i][1]-4.34)<1e-8 for i in f)];m.indices=[0]*len(m.faces)
 if (M is F and name.startswith('Trim')) or (name in ('Canopy longitudinal beam','Canopy beam') and abs(c[1])<1e-8):
  # Shared party-line end skin belongs to the structural wall, not attached trim.
  m.faces=[f for f in m.faces if not any(all(abs(m.vertices[i][0]-edge)<1e-8 for i in f) for edge in (0,bound))];m.indices=[0]*len(m.faces)
 return finish(m,part,material,M)
def plane(name,p,material,part='front',M=F):
 from mathutils.geometry import tessellate_polygon
 m=Mesh(name);vs=[Vector(v)for v in p]
 for tri in tessellate_polygon([vs]):m.add([tuple(vs[v]if isinstance(v,int)else v)for v in tri],[(0,1,2)])
 return finish(m,part,material,M)
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
  for a,b in zip(poly,poly[1:]+poly[:1]):
   low,high=min(v[1]for v in p),max(v[1]for v in p)
   if abs(a[1]-b[1])<1e-8:
    if not low+1e-6<a[1]<high-1e-6:continue
   else:
    a=(a[0],max(low,min(high,a[1])));b=(b[0],max(low,min(high,b[1])))
    if abs(a[1]-b[1])<1e-8:continue
   m.add([(*a,0),(*b,0),(*b,-.22),(*a,-.22)],[(0,1,2,3)])
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
  box('Joinery '+name+' transom',(xx,z+h*(.78 if name.startswith('bay') or 'first' in name else .50),-.112+out),(w/divide-.07,.055,.15),material,part,M)
 if DETAIL and not name.startswith(('shop','door')):
  box('Trim '+name+' sill',(x,z-.065,.21+out),(w+.16,.13,.42),TR,part,M)
  if 'second' not in name or name=='name second':box('Trim '+name+' lintel',(x,z+h+.12,.12+out),(w+.16,.24,.24),TR,part,M)


sand=mat('Weathered pink sandstone',(.49,.31,.24),tex='stone');sandlight=mat('Sandstone cut mouldings',(.60,.43,.33));blue=mat('Blue Connard fascia',(.045,.13,.19));tile=mat('Bay hanging terracotta',(.37,.16,.105));BM=brick if D['kind']=='red' else sand;TR=cream if D['kind']=='red' else sandlight
# Footprint/openings first: central windows and physical projected bay volumes.
holes=[];flat=[]
if D['kind']=='red':
 for i,cx in enumerate(D['bay_centres'][1:3]):
  holes.append(rect(cx-1.6,4.4,cx+1.6,8.0))
  for j,dx in enumerate([-.72,.72]):flat.append((f'centre second {i} {j}',cx+dx,9.0,1.05,2.4))
else:
 for i,cx in enumerate(D['bay_centres'][1:]):flat.append((f'bank second {i}',cx,8.0,1.28,1.5))
for _,x,z,w,h in flat:holes.append(rect(x-w/2,z,x+w/2,z+h))
for x,w,z,h,proj in bays(D):holes.append(rect(x-w/2,z,x+w/2,h))
wall('front main',rect(0,4.34,W,D['front_eaves']),holes,BM)
for name,x,z,w,h in flat:
 if z+h<=D['front_eaves']+.01:window(name,x,z,w,h,material=white,divide=3 if w>2 else 1)
# Bays are actual faceted walls with recessed glazing, not overlapping boxes.
for bi,(cx,ww,z0,z1,proj) in enumerate(bays(D)):
 chain=[(cx-ww/2,0),(cx-ww/2+.48,-proj),(cx+ww/2-.48,-proj),(cx+ww/2,0)]
 levels=[(4.7,7.2),(9.0,11.5)] if D['kind']=='red' else ([(7.2,10.0)] if bi==0 else [(4.55,7.1)])
 for si,(a,b) in enumerate(zip(chain,chain[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);tx,ty=dx/length,dy/length
  M=Matrix(((tx,0,ty,a[0]),(ty,0,-tx,a[1]),(0,1,0,0),(0,0,0,1)))
  hs=[rect(.20,lo+.12,length-.20,hi-.12)for lo,hi in levels]
  wall(f'bay {bi} face {si}',rect(0,z0,length,z1),hs,BM,'front',M)
  for li,(lo,hi) in enumerate(levels):window(f'bay {bi} {si} {li}',length/2,lo+.12,length-.40,hi-lo-.24,M,'front',material=white,divide=3 if si==1 else 1)

 for zz,rev in [(z0,True),(z1,False)]:plane('Bay cap '+str(bi),[(x,y,zz)for x,y in chain][::-1]if rev else[(x,y,zz)for x,y in chain],lead if zz==z1 else BM,'front',None)
 if DETAIL:
  # One continuous mitred band owns each bay corner: no overlapping cap boxes.
  ns=[]
  for a,b in zip(chain,chain[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);ns.append((dy/L,-dx/L))
  def offset(k,distance):
   if k==0:n=ns[0];factor=distance
   elif k==len(chain)-1:n=ns[-1];factor=distance
   else:
    a,b=ns[k-1],ns[k];n=(a[0]+b[0],a[1]+b[1]);factor=distance/(1+a[0]*b[0]+a[1]*b[1])
   return(chain[k][0]+factor*n[0],chain[k][1]+factor*n[1])
  for z in [z0-.1,z1+.06]+([7.42,8.8]if D['kind']=='red'else[]):
   for k in range(len(chain)-1):
    a,b=offset(k,.17),offset(k+1,.17);c,d=offset(k+1,-.03),offset(k,-.03)
    plane('Trim mitred bay band front',[(a[0],a[1],z-.07),(b[0],b[1],z-.07),(b[0],b[1],z+.07),(a[0],a[1],z+.07)],TR,'front',None)
    plane('Trim mitred bay band top',[(x,y,z+.07)for x,y in [a,b,c,d]],TR,'front',None)
    plane('Trim mitred bay band bottom',[(x,y,z-.07)for x,y in [d,c,b,a]],TR,'front',None)
 # Each canted bay skirt is a solid relief surface below the glazing.
 if DETAIL and D['kind']=='red':
  for si,(a,b)in enumerate(zip(chain,chain[1:])):
   dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
   for j in range(max(1,int(L/.23))):
    t=(j+.5)/max(1,int(L/.23));x=a[0]+t*dx;y=a[1]+t*dy
    tube('Fine bay tile scallop',[(x-.07,y-.018,7.85),(x,y-.026,7.77),(x+.07,y-.018,7.85)],.015,tile,'front',None,n=5)
# Central first-floor box oriels have real projection, tile skirts and roofs.
for cx,faces in box_bays(D):
 for name,poly in faces:
  if name=='front':
   M=face_matrix((0,-.65,0),(0,-1,0))
   wall('box bay face',rect(cx-1.6,4.8,cx+1.6,7.4),[rect(cx-1.51,4.87,cx+1.51,7.30)],white,'front',M)
   window('shop first box bay',cx,4.87,3.02,2.43,M,'front',out=.205,divide=3)
  else:plane('Bay box '+name,poly,tile if name in ('roof','skirt')else brick if name=='bottom'else white,'front',None)
 # Dark fascia beneath the red tile roof; side return is deliberately narrow.
 box('Bay box fascia',(cx,-.69,7.36),(3.30,.10,.08),iron,'front',None)
 if DETAIL:
  for j in range(1,9):
   t=j/9;y=-.65*(1-t);z=7.4+.6*t
   tube('Fine box roof tile course',[(cx-1.58,y-.006,z+.009),(cx+1.58,y-.006,z+.009)],.008,lead,'front',None,n=4)
# Main upper fronts, parapet gables, bank dormer faces and prominent oriel tower.
if D['kind']=='red':
 cx=W/2;poly=[(cx-2.75,12.0),(cx+2.75,12.0),(cx+2.75,12.55),(cx+2.15,12.85),(cx,14.8),(cx-2.15,12.85),(cx-2.75,12.55)]
 wall('central gable parapet',poly,[],brick)
 if DETAIL:
  tube('Trim central gable coping',[(x,-.04,z+.08)for x,z in poly[2:]+poly[:1]],.10,TR,'front',None,n=8)
  # Two-line inscription and arched crest are legible in the user's photograph.
  plaque=mat('Weathered inscription stone',(.43,.43,.32));letter=mat('Incised lettering shadow',(.23,.25,.20))
  outline=[(cx-1.60,12.78),(cx+1.60,12.78),(cx+1.60,13.68),(cx+.73,13.68)]
  outline += [(cx+.73*math.cos(t),13.68+.61*math.sin(t))for t in [i*math.pi/20 for i in range(1,21)]]
  outline += [(cx-1.60,13.68)]
  inner=[(cx+(x-cx)*.96,13.35+(z-13.35)*.94)for x,z in outline]
  plane('Tablet inset face',[(x,z,.18)for x,z in inner],plaque)
  for i,a in enumerate(outline):
   j=(i+1)%len(outline)
   plane('Tablet border',[(x,z,.20)for x,z in [a,outline[j],inner[j],inner[i]]],plaque)
  for a,b in zip(outline,outline[1:]+outline[:1]):plane('Tablet edge',[(*a,.02),(*b,.02),(*b,.20),(*a,.20)],plaque)
  for a,b in zip(inner,inner[1:]+inner[:1]):plane('Tablet inset edge',[(*a,.18),(*b,.18),(*b,.20),(*a,.20)],plaque)
  font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
  for body,z in [('MASONIC',13.44),('BUILDING',13.02)]:
   ob=text_object('Inscription '+body,body,(cx,z,.183),(0,0,1),.32,2.85,font,letter,extrude=.0005,collection=C['front'])
   bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.data.transform(T@FM@F@ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.select_set(False)

else:
 for i,cx in enumerate(D['bay_centres'][1:]):
  a,c=cx-1.65,cx+1.65;poly=[(a,8.65),(a,9.35),(cx,10.95),(c,9.35),(c,8.65)]
  wall('bank gable '+str(i),poly,[rect(cx-.64,8.0,cx+.64,9.5)],sand,'front',face_matrix((0,-.68,0),(0,-1,0)))
  window('bank gable window '+str(i),cx,8.0,1.28,1.5,face_matrix((0,-.68,0),(0,-1,0)),'front',material=white,divide=2)
  if DETAIL:
   tube('Trim bank gable coping',[(a,-.74,9.35),(cx,-.74,11.03),(c,-.74,9.35)],.095,TR,'front',None,n=8)
   for xx in (a+.12,c-.12):box('Trim bank gable shoulder',(xx,9.12,.79),(.26,.3,.22),TR)
 # Higher southwest bay over the former bank entry, including its corbelled oriel.
 x0,x1=0,3.9
 wall('bank tower',rect(x0,8.65,x1,12.05),[rect(.65,8.65,3.25,10)],sand)
 plane('Roof tower cap',[(0,0,12.05),(3.9,0,12.05),(3.9,.22,12.05),(0,.22,12.05)],lead,'roof',None)
 plane('Shell tower parapet back',[(3.9,.22,8.65),(0,.22,8.65),(0,.22,12.05),(3.9,.22,12.05)],sand,'front',None)
 for xx,rev in [(0,True),(3.9,False)]:
  plane('Shell tower parapet edge',[(xx,0,8.65),(xx,.22,8.65),(xx,.22,12.05),(xx,0,12.05)][::-1]if rev else [(xx,0,8.65),(xx,.22,8.65),(xx,.22,12.05),(xx,0,12.05)],sand,'front',None)
 for a,b in [(0,3.9)]:
  if DETAIL:box('Trim tower cornice',((a+b)/2,11.8,.16),(b-a,.32,.32),TR)
 if DETAIL:
  # The observed large stepped corbel and shield are restrained authored relief.
  for j in range(6):
   z=6.05+j*.17;ww=1.3+j*.22;box('Trim tower oriel corbel',(1.95,z,.12+j*.065),(ww,.15,.24+j*.13),TR)
  box('Trim bank name panel',(1.95,4.82,.1),(3.55,.42,.20),TR)
  shield=[(1.55,5.75,.24),(2.35,5.75,.24),(2.3,5.15,.24),(1.95,4.96,.24),(1.6,5.15,.24)]
  plane('Fine bank shield',shield,TR,'front',F)
# Shop fronts retain recessed doors and the actual current shop divisions.
shops=([('Saltrock',.12,10.28,black),('Covet & Crave',10.52,15.48,brown),('CONNARD & SON',15.72,W-.12,blue)] if D['kind']=='red' else [('Wine & Words',.12,8.0,brown),('vacant',8.24,W-.12,black)])
doors=[]
for name,a,b,material in shops:
 cx=(a+b)/2;dw=1.35;da,db=cx-dw/2,cx+dw/2;doors.append((name,da,db))
 box('Shop fascia '+name,(cx,3.37,.01),(b-a,.5,.24),material)
 wall('shop upper infill '+name,rect(a,3.62,b,4.34),[],BM)
 for j,(lo,hi)in enumerate([(a,da),(db,b)]):
  box('Shop plinth '+name,((lo+hi)/2,.22,-.02),(hi-lo,.44,.2),material)
  window('shop '+name+str(j),(lo+hi)/2,.44,hi-lo,2.68,out=-.10,material=material,divide=max(1,round((hi-lo)/1.2)))
 window('door '+name,cx,0,dw,3.12,out=-.38,material=material,divide=2)
 for xx,rev in [(da,False),(db,True)]:
  pp=[(xx,0,0),(xx,3.12,0),(xx,3.12,-.42),(xx,0,-.42)];plane('Door reveal '+name,pp[::-1]if rev else pp,material)
 for xx in (a-.06,b+.06):box('Shop pier '+name,(xx,2.12,.02),(.12,4.44,.4),BM)
from southport3d.elevation import Elevations
support=Elevations(REPO/'regions/southport/elevation/lord-corridor.json').surface(D['ground_surface'])
for name,a,b in doors:
 pp=[]
 for x,y in [(a,0),(b,0),(b,.55),(a,.55)]:
  X,Y,_=transform(D,(x,y,0));z=support.height(X,Y)-D['floor_z']if y==0 else 0;pp.append((x,y,z))
 plane('Entrance threshold '+name,pp,stone,'front',None)
# Plain uncertain walls; only confidently observed rear-window groups are added.
for name,p in exterior(D):
 if D['kind']=='bank' and name=='rear front range':
  M=face_matrix((W,D['main_depth'],0),(0,1,0));poly=[(W-x,z)for x,y,z in p]
  ws=[]
  for i in range(8):ws.append((1.0+i*1.98,6.8,.9,1.5))
  for i in [0,2,4,6]:ws.append((1.0+i*1.98,3.8,.82,1.25))
  wall(name,poly,[rect(x-w/2,z,x+w/2,z+h)for x,z,w,h in ws],brick,'rear',M)
  for i,(x,z,w,h)in enumerate(ws):window('rear observed '+str(i),x,z,w,h,M,'rear',divide=1)
 else:plane('Shell '+name,p,brick,'rear',None)
for name,p in roofs(D):plane('Roof '+name,p,roofglass if 'glass'in name or 'lantern'in name else slate,'roof',None)
# Distinctive hall lantern mullions follow its four real slopes, leaving no tiled clutter.
if DETAIL and D['kind']=='bank':
 seen_hips=set()
 for name,p in roofs(D):
  if 'lantern'not in name:continue
  for a,b in zip(p,p[1:]+p[:1]):
   key=tuple(sorted([tuple(round(v,5)for v in a),tuple(round(v,5)for v in b)]))
   if key not in seen_hips and not(abs(a[2]-8.75)<1e-6 and abs(b[2]-8.75)<1e-6):tube('Roof lantern hip',[a,b],.045,lead,'roof',None,n=6);seen_hips.add(key)
  if len(p)==4:
   a,b,c,d=p
   for j in range(1,24):
    t=j/24;u=tuple(a[k]*(1-t)+b[k]*t for k in range(3));v=tuple(d[k]*(1-t)+c[k]*t for k in range(3));tube('Roof lantern glazing bar',[u,v],.026,cream,'roof',None,n=6)
if DETAIL and D['kind']=='bank':
 h=D['hall'];a,c,y,end=h['x0']+2.6,h['x1']-2.6,h['y0']+3.5,h['ridge_y']-3.0
 m=Mesh('Roof lantern continuous perimeter');pts=[Vector(v)for v in [(a,y,8.75),(c,y,8.75),(c,end,8.75),(a,end,8.75)]];vv=[]
 for i,p in enumerate(pts):
  tangent=(pts[(i+1)%4]-pts[i-1]).normalized();side=tangent.cross(Vector((0,0,1))).normalized();other=tangent.cross(side).normalized()
  for j in range(6):vv.append(tuple(p+.045*(side*math.cos(j*math.tau/6)+other*math.sin(j*math.tau/6))))
 m.add(vv,[(i*6+j,i*6+(j+1)%6,((i+1)%4)*6+(j+1)%6,((i+1)%4)*6+j)for i in range(4)for j in range(6)]);finish(m,'roof',lead)
# Canopy remains open beneath and follows the shared street support at each foot.
profile=canopy_profile(D)
for j,((p,z),(q,zz))in enumerate(zip(profile,profile[1:])):
 plane('Canopy glass top '+str(j),list(reversed([(0,-p,z),(W,-p,z),(W,-q,zz),(0,-q,zz)])),roofglass,'canopy',None)
 plane('Canopy glass underside '+str(j),list(reversed([(0,-q,zz-.035),(W,-q,zz-.035),(W,-p,z-.035),(0,-p,z-.035)])),roofglass,'canopy',None)
for x in D['canopy_posts']:
 X,Y,_=transform(D,(x,-3.18,0));base=support.height(X,Y)-D['floor_z']
 tube('Canopy column',[(x,-3.18,base+(.5 if DETAIL else 0)),(x,-3.18,3.56)],.065,iron,'canopy',None,n=12)
 if DETAIL:
  box('Canopy column pedestal',(x,-3.18,base+.25),(.19,.19,.5),iron,'canopy',None)
  for sign in (-1,1):
   pts=[(x+sign*.8*(1-t),-3.18,3.49-.60*t*t)for t in [i/10 for i in range(11)]]
   if min(p[0]for p in pts)>0 and max(p[0]for p in pts)<W:tube('Canopy bracket',pts,.03,cream,'canopy',None,n=6)
if DETAIL:
 for i in range(round(W/.53)+1):
  x=W*i/round(W/.53);tube('Canopy glazing bar',[(x,-p,z+.035)for p,z in profile],.023,cream,'canopy',None,n=6)
 for y,z in [(0,4.34),(-3.18,3.62)]:box('Canopy beam',(W/2,y,z-.08),(W,.10,.16),iron,'canopy',None)
 for i in range(round(W/.20)):
  x=(i+.5)*W/round(W/.20);tube('Fine canopy pendant',[(x,-3.18,3.5),(x,-3.18,3.39)],.011,cream,'canopy',None,n=5)
 # Observed masonry articulation, not synthetic facade noise.
 if D['kind']=='bank':
  for cx in D['bay_centres'][1:]:
   for xx in [cx-1.73,cx+1.73]:
    box('Trim bank bay pier',(xx,6.0,.11),(.20,3.05,.22),sandlight)
    for z in [4.56,7.20,7.48]:box('Trim bank pier capital',(xx,z,.20),(.32,.16,.40),sandlight)
   box('Trim bank apron',(cx,7.38,.17),(3.45,.27,.34),sandlight)
   for j in range(12):
    xx=cx-1.5+j*3/11
    box('Fine bank dentil',(xx,7.15,.30),(.10,.13,.16),sandlight)
  for xx in [.18,3.72]:
   box('Trim tower pilaster',(xx,8.18,.13),(.32,7.6,.26),sandlight)
   for z in [5.2,6.1,10.4,11.65]:box('Trim tower capital',(xx,z,.23),(.46,.22,.46),sandlight)
  for z,ww in [(10.45,2.95),(10.62,3.15),(11.45,3.40)]:box('Trim tower band',(1.95,z,.18),(ww,.16,.36),sandlight)
  for xx in [.78,3.12]:
   pts=[(xx+.18*math.cos(t),-.27,5.5+.25*math.sin(t))for t in [i*math.tau/24 for i in range(25)]]
   tube('Fine bank relief scroll',pts,.037,sandlight,'front',None,n=6)
 if D['kind']=='red':
  for x in [i*.25+.12 for i in range(int(W/.25))]:
   if .4<x<W-.4 and all(abs(x-edge)>.26 for edge in D['bay_edges']):box('Fine brick cornice dentil',(x,11.67,.12),(.11,.16,.24),brick)
  # Terracotta diamond panels below the bay sashes.
  for cx in [D['bay_centres'][0],D['bay_centres'][3]]:
   for row in range(3):
    for col in range(9):
     xx=cx-1.0+col*.25;zz=7.75+row*.23
     plane('Fine bay lozenge',[(xx-.10,zz,.59),(xx,zz+.10,.59),(xx+.10,zz,.59),(xx,zz-.10,.59)],tile,'front',F)
 # Continuous horizontal banding and projecting pier caps.
 for z in ([4.43,8.12,8.65,11.85]if D['kind']=='red' else [4.38,7.25,7.55]):box('Trim continuous course',(W/2,z,.07),(W,.11,.14),TR)
 for i,x in enumerate(D['bay_edges']):
  xx=min(W-.14,max(.14,x));height=D['front_eaves']-4.55
  box('Trim facade pier',(xx,4.55+height/2,.045),(.28,height,.09),BM)
  for z in [4.53,D['front_eaves']-.25]:box('Trim pier collar',(xx,z,.12),(.37,.18,.24),TR)
 for i,ch in enumerate(D['chimneys']):
  x,y,base,top,w,depth=[ch[k]for k in ['x','y','base','top','w','d']]
  box('Roof chimney '+str(i),(x,y,(base+top)/2),(w,depth,top-base),brick,'roof',None)
  box('Roof chimney cap',(x,y,top+.08),(w+.16,depth+.16,.16),brick,'roof',None)
  for dx in [-.22,.22]:
   m=Mesh('Roof chimney pot');m.lathe((x+dx,y),[(top+.16,.11),(top+.57,.10),(top+.64,.14)],10);finish(m,'roof',pot)
 for x in [.11,W-.11]:tube('Drain front pipe',[(x,-.20,4.4),(x,-.20,D['front_eaves'])],.043,iron,'front',None,n=8)
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
 for name,a,b,material in shops:
  if name=='vacant':continue
  ob=text_object('Shop lettering '+name,name.upper(),((a+b)/2,3.24,.15),(0,0,1),.22,b-a-.45,font,cream,collection=C['front']);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.data.transform(T@FM@F@ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.select_set(False)
NEW_CAFE=True
from cafe import build_cafe
build_cafe(globals())
NEW_CAFE=False
# Keep semantic mesh groups for validation while eliminating bake traversal overhead.
for part,col in C.items():
 groups={}
 for ob in list(col.objects):
  if ob.type!='MESH' or ob.name.startswith('Shop lettering'):continue
  key=(ob.name.split()[0],ob.data.materials[0].name);groups.setdefault(key,[]).append(ob)
 for (prefix,material),objects in groups.items():
  if len(objects)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=prefix+' '+part+' '+material
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.6;l.rotation_euler=(.6,-.4,-.6);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));c.data.type='ORTHO';s.collection.objects.link(c);s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/building.blend'))
