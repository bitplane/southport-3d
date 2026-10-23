"""St George's Mansions: Tudor Revival bays, recessed portals and rear wings."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from components import rect,roundtop,wall,ring,leaded,oriel_frame,sash_aperture,sash_panel_aperture
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for n in ('frontage','roof','rear-wings'):
 C[n]=bpy.data.collections.new(n);s.collection.children.link(C[n])
world=Matrix.Translation((*D['origin_site_xy'],D['base_z']))@Matrix.Rotation(math.radians(D['local_rotation_degrees']),4,'Z')
W=D['width'];E=D['eaves'];R=D['ridge'];DEP=D['main_depth'];BAYS=D['bay_centres'];FLATS=D['flat_centres'];WINGS=D['rear_wings']
def mat(name,rgb,texture=None,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
brick=mat('Historic red water shot brick',(.26,.08,.04),'brick');slate=mat('Natural slate',(.08,.085,.082),'slate')
white=mat('Ivory painted timber',(.80,.79,.72));black=mat('Black painted timber',(.022,.025,.024),rough=.58)
glass=mat('Muted pale blue glass',(.22,.30,.30),rough=.36);leadedglass=mat('Leaded transom glass',(.43,.49,.46),rough=.42)
stone=mat('Sandstone thresholds and sills',(.52,.45,.34));terracotta=mat('Terracotta dressings',(.37,.13,.065));gold=mat('Gold lettering',(.62,.44,.16))
blue=mat('Dark blue doors',(.014,.025,.11));teal=mat('BTR blue green fascia',(.035,.22,.31));pink=mat('HW magenta board',(.47,.025,.14));metal=mat('Grey metal',(.25,.28,.27));lead=mat('Dark lead came',(.065,.071,.067))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')

def finish(m,part='frontage',mats=None,frame=None,authored_winding=False):
 ob=m.finish(mats or [brick],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 # Conformed wall fragments already carry outward winding; disconnected
 # reveal triangles cannot have their normals reliably inferred in isolation.
 if not authored_winding:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv=ob.data.uv_layers.new(name='Metric UV')
 for f in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/2.95,p[axes[1]]/1.92)
 ob.matrix_world=world@(frame or Matrix.Identity(4));return ob

box_prototypes={}
def box(name,p,size,part='frontage',material=None,frame=None):
 material=material or brick;key=(name,tuple(round(v,7) for v in size),part,material.name)
 placement=(frame or Matrix.Identity(4))@Matrix.Translation(p)
 if key not in box_prototypes:
  m=Mesh(name);m.box((0,0,0),size);ob=finish(m,part,[material],placement);ob.data.use_fake_user=True;box_prototypes[key]=ob.data
 else:
  ob=bpy.data.objects.new(name,box_prototypes[key]);C[part].objects.link(ob);ob.matrix_world=world@placement
 return ob
proto={}
def instance(key,factory,frame,part='frontage',mats=None):
 if key not in proto:ob=finish(factory(),part,mats,frame);ob.data.use_fake_user=True;proto[key]=(ob.name,ob.data)
 else:ob=bpy.data.objects.new(proto[key][0],proto[key][1]);C[part].objects.link(ob);ob.matrix_world=world@frame
 return ob

def label(name,body,origin,normal,height,width,material,part='frontage'):
 ob=text_object(name,body,origin,normal,height,width,font,material,extrude=.008,collection=C[part]);ob.matrix_world=world@ob.matrix_world
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);uv=ob.data.uv_layers.new(name='Text UV')
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
 return ob

assemblies={}
def assemble(name,objects,frame,part,key=None):
 # Join in a deliberate local facade frame, preserving all source materials/UVs.
 mesh=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,mesh);C[part].objects.link(ob);ob.matrix_world=world@frame
 bpy.ops.object.select_all(action='DESELECT')
 for item in objects:item.select_set(True)
 ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.join();bpy.ops.object.material_slot_remove_unused();ob.select_set(False)
 if key in assemblies:
  old=ob.data;ob.data=assemblies[key];bpy.data.meshes.remove(old)
 elif key is not None:assemblies[key]=ob.data
 return ob

# Storeys and true recesses, based on existing elevation rather than a solid box.
ff=face_matrix((W,0,0),(0,1,0));holes=[]
for x in BAYS:holes.append(rect(W-x-1.7,.35,W-x+1.7,11.0))
for x in FLATS:
 holes.append([(u+W-x,z) for u,z in roundtop(2.7,.12,3.08,.65)])
 for dx in (-.96,.96):
  for z in (4.02,7.60):holes.append([(u+W-x-dx,zz) for u,zz in sash_panel_aperture(1.12,z,2.52)])
 for dx in (-1.12,0,1.12):holes.append(rect(W-x-dx-.43,11.73,W-x-dx+.43,12.94))
finish(wall('Envelope street wall',rect(0,0,W,E),holes),frame=ff,authored_winding=True)
# Main side elevations and upper rear strip; lower rear wall breaks at the wings.
for side,origin,normal in [('north',(W,-DEP,0),(1,0,0)),('south',(0,0,0),(-1,0,0))]:
 frame=face_matrix(origin,normal);holes=[]
 for u in (2.4,5.4,8.2):
  for z in (4.05,7.62,11.72):holes.append(rect(u-.55,z,u+.55,z+(1.2 if z>11 else 2.4)))
 finish(wall('Envelope main '+side,rect(0,0,DEP,E),holes),'rear-wings',frame=frame)
 for u in (2.4,5.4,8.2):
  for z in (4.05,7.62,11.72):
   h=1.2 if z>11 else 2.4
   box('Window main side glazing',(u,z+h/2,-.12),(1.08,h-.03,.1),'rear-wings',glass,frame)
   for xx in (u-.56,u+.56):box('Window main side frame',(xx,z+h/2,-.02),(.07,h+.1,.1),'rear-wings',white,frame)
   # Rails stop at the inner faces of the full-height stiles.
   for zz in (z,z+h/2,z+h):box('Window main side transom',(u,zz,-.02),(1.05,.065,.10),'rear-wings',white,frame)
# Plain rectangular sash bays and terracotta arches / carved keystones.
def sash(frame,u,z,width=1.12,height=2.52,part='frontage'):
 before=set(C[part].objects)
 af=frame@Matrix.Translation((u,0,0))
 # Brick receiver around the full sash ensures the later bake retains surrounding negative space.
 finish(wall('Window sash backing',rect(-width/2-.2,z-.35,width/2+.2,z+height+.5),[sash_aperture(width,z,height)],thickness=.08),part,[brick],af@Matrix.Translation((0,0,.006)),authored_winding=True)
 m=Mesh('Window sash glazing');m.outline(roundtop(width,z,z+height,.15),-.14,-.10);finish(m,part,[glass],af)
 finish(ring('Window sash frame',width,z,z+height,.15,.07,.01),part,[white],af)
 box('Window sash meeting rail',(0,z+height*.47,-.015),(width,.07,.12),part,white,af)
 box('Course sash sill',(0,z-.09,.10),(width+.30,.15,.36),part,stone,af)
 # Three stepped terracotta voussoir blocks and centre key follow shallow head.
 for dx,zz in [(-.46,z+height+.12),(0,z+height+.20),(.46,z+height+.12)]:
  box('Course terracotta window head',(dx,zz,.075),(.52,.13,.20),part,terracotta,af)
 box('Ornament terracotta keystone',(0,z+height+.24,.12),(.18,.28,.26),part,terracotta,af)
 for dx in (-.32,0,.32):
  m=Mesh('Ornament sill pendant');m.ellipsoid((dx,z-.25,.03),(.12,.055,.07),segments=8,rings=4);finish(m,part,[terracotta],af)
 assemble('Assembly sash '+('front' if part=='frontage' else 'rear'),set(C[part].objects)-before,frame@Matrix.Translation((u,z,0)),part,('sash',width,height,part))
for x in FLATS:
 for dx in (-.96,.96):
  for z in (4.02,7.6):sash(ff,W-x-dx,z)
 for dx in (-1.12,0,1.12):
  af=ff@Matrix.Translation((W-x-dx,0,0));box('Window attic glass',(0,12.335,-.13),(.84,1.18,.10),material=glass,frame=af)
  for xx in (-.46,.46):box('Window attic stile',(xx,12.335,-.02),(.08,1.30,.11),material=white,frame=af)
  # Continuous stiles own the rail corners.
  for zz in (11.71,12.93):box('Window attic rail',(0,zz,-.02),(.84,.08,.11),material=white,frame=af)
  box('Window attic mullion',(0,12.335,-.02),(.055,1.2,.1),material=white,frame=af)
for z in (3.50,7.15,10.99):box('Course sandstone string',(W/2,.025,z),(W,.10,.10),material=terracotta)
# Six polygonal bays. Their glass faces are separate inset surfaces, not painted boxes.
baywidth=3.45;frontwidth=2.46;projection=1.08
outline=[(-baywidth/2,0),(-frontwidth/2,projection),(frontwidth/2,projection),(baywidth/2,0)]
def bay(x,index):
 # Ground brick plinth and splayed display glazing.
 m=Mesh('Envelope bay brick plinth');m.outline([(a+x,b) for a,b in outline],0,.42);finish(m)
 for storey,(z,h) in enumerate(((.42,2.78),(3.55,3.58),(7.13,3.835))):
  for seg,(a,b) in enumerate(zip(outline,outline[1:])):
   before=set(C['frontage'].objects)
   dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);normal=(-dy/length,dx/length,0)
   frame=face_matrix((x+b[0],b[1],z),normal)
   # Lower apron and top cornice run around all three sides of each bay.
   apron=.12 if storey==0 else .40
   box('Bay white apron',(length/2,apron/2,-.03),(length,apron,.14),material=white,frame=frame)
   for zz in (0,apron,h-.18,h-.10):box('Bay black cornice',(length/2,zz,.06),(length+.04,.075,.20),material=black,frame=frame)
   for xx in (0,length):box('Bay black corner post',(xx,h/2,.035),(.09,h,.18),material=black,frame=frame)
   # Main glass below upper transoms, thin white vertical mullions.
   top=2.12 if storey==0 else 2.35
   box('Window bay lower glazing',(length/2,(apron+top)/2,-.12),(length-.15,top-apron-.06,.08),material=glass,frame=frame)
   lights=3 if seg==1 else 1
   for k in range(lights+1):box('Window bay lower stile',(.075+k*(length-.15)/lights,(apron+top)/2,-.035),(.055,top-apron,.12),material=white,frame=frame)
   box('Window bay transom bar',(length/2,top,-.02),(length-.05,.10,.15),material=white,frame=frame)
   # Above: round-headed Georgian-bar glass, retained curved receiver at District.
   lw=(length-.16)/lights-.045
   for k in range(lights):
    u=.08+(k+.5)*(length-.16)/lights
    af=frame@Matrix.Translation((u,top+.07,0))
    typ='front' if seg==1 else 'side'
    instance('lead-'+typ,lambda:leaded('Leaded transom '+typ,lw),af,mats=[leadedglass,lead])
    instance('transom-ring-'+typ,lambda:ring('Window bay upper arch '+typ,lw,0,.85,lw/2,.035,.035,steps=10),af,mats=[white])
   # Ivory spandrels fill the area outside the actual rounded transom openings.
   cutouts=[]
   for k in range(lights):
    u=.08+(k+.5)*(length-.16)/lights
    cutouts.append([(xx+u,zz+top+.07) for xx,zz in roundtop(lw,0,.85,lw/2,10)])
   instance('spandrel-'+str(storey)+'-'+typ,lambda:wall('Bay ivory transom spandrel',rect(.04,top+.02,length-.04,h-.13),cutouts,thickness=.07),frame,mats=[white])
   # Thin white inner sill around the lower glass.
   box('Window bay inner sill',(length/2,apron+.03,-.02),(length-.10,.075,.13),material=white,frame=frame)
   assemble('Assembly bay '+typ+' storey '+str(storey),set(C['frontage'].objects)-before,frame,'frontage',('bay',storey,typ))
 # Four higher oriels continue into half-timbered attic; outer two stop below attic.
 tall=index not in (0,5);top=13.55 if tall else 11.15
 if tall:
  box('Bay attic white body',(x,.52,12.27),(baywidth,1.04,2.55),material=white)
  for xx in (x-baywidth/2+.08,x+baywidth/2-.08):box('Bay attic black upright',(xx,1.10,12.27),(.12,.10,2.55),material=black)
  for dx in (-1.1,1.1):box('Bay attic inner black upright',(x+dx,1.13,12.27),(.08,.10,2.55),material=black)
  for zz in (11.04,11.54,13.50):box('Bay attic black rail',(x,1.11,zz),(baywidth,.12,.10),material=black)
  # Rectangular triple sash on face of attic box, slightly projecting cheeks.
  for k in range(3):
   xx=x+(k-1)*.67;box('Window attic oriel glass',(xx,1.145,12.47),(.58,.035,1.55),material=glass)
  instance('attic-oriel-frame',lambda:oriel_frame('Window attic oriel frame'),
           face_matrix((x,1.235,0),(0,1,0)),mats=[white])
 # Gabled fronts have layered black verges and white triangular fields.
 m=Mesh('Bay white gable');m.outline([(-baywidth/2,top),(baywidth/2,top),(0,top+1.65)],-.13,.02)
 frame=face_matrix((x,1.225,0),(0,1,0));finish(m,mats=[white],frame=frame)
 for lift,rad in ((0,.075),(.12,.05),(.22,.045)):
  m=Mesh('Bay black gable verge');m.tube([(-baywidth/2-.10,top+lift,.11),(0,top+1.70+lift,.11),(baywidth/2+.10,top+lift,.11)],rad,sides=6);finish(m,mats=[black],frame=frame)
 box('Bay gable base cornice',(x,1.14,top),(baywidth+.30,.32,.18),material=black)
 return top
baytops=[bay(x,i) for i,x in enumerate(BAYS)]
# Pairs share a timber apron/arch and patterned spandrels below attic.
for x0,x1 in ((BAYS[1],BAYS[2]),(BAYS[3],BAYS[4])):
 mid=(x0+x1)/2;gap=x1-x0-baywidth
 box('Bay pair white bridge',(mid,.55,11.30),(x1-x0+baywidth,1.1,.55),material=white)
 for z in (11.02,11.58):box('Bay pair black bridge rail',(mid,1.13,z),(x1-x0+baywidth,.15,.12),material=black)
 af=face_matrix((mid,1.1,0),(0,1,0))
 # Bridge arch is the negative space between the projecting oriels.
 m=Mesh('Ornament pair arch')
 points=[(gap*.7*math.cos(a*math.pi/24),10.72+gap*.9*math.sin(a*math.pi/24),.08) for a in range(25)]
 m.tube(points,.075,sides=6);finish(m,mats=[black],frame=af)
 for sign in (-1,1):
  m=Mesh('Ornament pair spandrel')
  for j in range(3):m.ellipsoid((sign*(gap*.40+j*.13),11.12,.08),(.08,.09,.04),segments=8,rings=4)
  finish(m,mats=[black],frame=af)
 # Square date hopper and cast downpipe, unreadable date not fabricated.
 box('Fitting square hopper',(mid,.16,10.5),(.27,.28,.34),material=black)
 box('Fitting square rainwater pipe',(mid,.11,5.4),(.09,.12,10.5),material=black)
# Recessed shared entrance portals with three steps and visible inner doors.
for i,x in enumerate(FLATS):
 af=ff@Matrix.Translation((W-x,0,0))
 # Curved brick outer opening is already cut from facade; deep jambs now line it.
 finish(ring('Portal brick rounded reveal',2.7,.12,3.08,.65,.18,.03),mats=[brick],frame=af)
 for sign in (-1,1):box('Portal deep brick jamb',(sign*1.33,1.55,-.62),(.16,3.0,1.24),frame=af)
 box('Portal pale soffit',(0,2.93,-.62),(2.5,.18,1.24),material=white,frame=af)
 box('Door recessed timber',(0,1.53,-1.28),(2.47,2.82,.14),material=blue if i==1 else black,frame=af)
 for dx in (-.61,.61):box('Door inset glazing',(dx,1.76,-1.18),(.96,1.7,.04),material=glass,frame=af)
 for z in (.42,2.71):box('Door recessed horizontal rail',(0,z,-1.13),(2.44,.10,.1),material=white,frame=af)
 box('Door centre stile',(0,1.54,-1.12),(.14,2.85,.12),material=white,frame=af)
 for k in range(3):box('Portal entrance step',(x,.88-k*.28,.05+k*.065),(2.7,.30,.10+k*.13),material=stone)
 # No interior rooms, only externally visible threshold finish and door numerals.
 if i==2:label('Lettering entrance 140','140',(x,-1.10,2.73),(0,1,0),.24,.65,gold)
# Continuous carved fascia zone in black and ivory.
fascia_before=set(C['frontage'].objects)
for a,b in ((0,12.5),(12.5,25),(25,W)):
 box('Sign ivory fascia',((a+b)/2,1.14,3.43),(b-a,.20,.43),material=white)
for z in (3.18,3.69):box('Sign black fascia rail',(W/2,1.18,z),(W+.15,.31,.11),material=black)
for i in range(90):box('Ornament fascia dentil',(.15+i*(W-.3)/89,1.22,3.76),(.15,.25,.10),material=black)
for x in [0]+FLATS+[W]:
 m=Mesh('Ornament fascia bracket');m.outline([(-.15,2.82),(.15,2.82),(.33,3.22),(-.33,3.22)],0,.46);finish(m,mats=[black],frame=face_matrix((x,.65,0),(0,1,0)))
# Observed August2024 occupancy labels, not a claim of permanent future use.
label('Lettering BTR','BTR  Brown Turner Ross',(35.3,1.30,3.43),(0,1,0),.24,4.3,teal)
label('Lettering solicitors','Solicitors',(31.2,1.30,3.43),(0,1,0),.23,2.8,black)
label('Lettering HW fascia','HW COMMERCIAL',(27.05,1.30,3.43),(0,1,0),.31,3.65,black)
label('Lettering Brighouses fascia','BRIGHOUSES',(18.8,1.30,3.43),(0,1,0),.33,10.4,blue)
for a,b in ((0,12.5),(12.5,25),(25,W)):
 members={o for o in set(C['frontage'].objects)-fascia_before if o.name.startswith(('Sign ivory fascia','Lettering ')) and a<=(world.inverted()@o.matrix_world).translation.x<=b}
 assemble('Assembly street fascia '+str(int(a)),members,face_matrix((b,1.14,0),(0,1,0)),'frontage')
box('Sign HW magenta field',(BAYS[4],1.115,.85),(2.2,.06,.52),material=pink)
label('Lettering HW board','HW COMMERCIAL',(BAYS[4],1.16,.85),(0,1,0),.21,2.05,white)
label('Lettering Brighouses glazing','BRIGHOUSES\nSOLICITORS',(BAYS[3],1.16,1.6),(0,1,0),.43,1.9,gold)
# Roof helper produces closed solids; all roof intersections hidden inside mass.
def hip(name,x0,x1,y0,y1,eave,ridge,axis='x'):
 if axis=='y':
  # Generate in swapped XY, then undo orientation by normals recalculation.
  ob=hip(name,y0,y1,x0,x1,eave,ridge,'x')
  for v in ob.data.vertices:v.co.x,v.co.y=v.co.y,v.co.x
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();return ob
 h=min((x1-x0)*.28,(y1-y0)*.48);yc=(y0+y1)/2
 v=[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),(x0+h,yc,ridge),(x1-h,yc,ridge),(x0,y0,eave-.18),(x1,y0,eave-.18),(x1,y1,eave-.18),(x0,y1,eave-.18)]
 f=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4),(6,9,8,7),(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,9,6,0)]
 m=Mesh(name);m.add(v,f);return finish(m,'roof',[slate])
mainroof=hip('Roof main hipped range',-.06,W+.06,-DEP-.08,-.10,E,R)
for x,top in zip(BAYS,baytops):
 m=Mesh('Roof projecting bay gable')
 yback=-3.3 if top>12 else -.15
 cross=[(x-baywidth/2-.10,top+.05),(x,top+1.84),(x+baywidth/2+.10,top+.05)]
 v=[(xx,yy,zz) for yy in (yback,1.20) for xx,zz in cross];m.add(v,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);finish(m,'roof',[slate])
# Main rear upper wall above smaller rear ranges.
rf=face_matrix((0,-DEP,0),(0,-1,0));finish(wall('Envelope main rear upper',rect(0,10.9,W,E),[]),'rear-wings',frame=rf)
# Lower rear wall fills the gaps between mapped perpendicular wings.
for a,b in zip([0]+[q[1] for q in WINGS],[q[0] for q in WINGS]+[W]):
 if b-a>.1:finish(wall('Envelope rear court wall',rect(a,0,b,10.9),[]),'rear-wings',frame=rf)
for wi,(x0,x1,depth) in enumerate(WINGS):
 height=11.45 if wi else 12.4
 for side,origin,normal,length in [('west',(x0,-DEP,0),(-1,0,0),depth-DEP),('east',(x1,-depth,0),(1,0,0),depth-DEP),('end',(x0,-depth,0),(0,-1,0),x1-x0)]:
  frame=face_matrix(origin,normal);us=[(j+.5)*length/(4 if length>15 else 3) for j in range(4 if length>15 else 3)];holes=[]
  for u in us:
   for z in (1.0,4.3,7.8):holes.append([(x+u,y) for x,y in sash_panel_aperture(1.0,z,1.9)])
  finish(wall('Envelope rear wing '+str(wi)+' '+side,rect(0,0,length,height),holes),'rear-wings',frame=frame,authored_winding=True)
  for u in us:
   for z in (1.0,4.3,7.8):sash(frame,u,z,1.0,1.9,'rear-wings')
  for z in (3.7,7.2):box('Course rear wing floor band',(length/2,z,.035),(length,.10,.08),'rear-wings',terracotta,frame)
 hip('Roof rear wing '+str(wi),x0-.08,x1+.08,-depth-.08,-DEP+.12,height,height+2.5,'y')
 # Plain shared brick chimney with six terracotta pots.
 xx=(x0+x1)/2;yy=-depth+1.6
 box('Envelope rear chimney',(xx,yy,height+2.7),(1.45,.64,2.4),'roof',brick)
 for zz in (height+3.75,height+3.95):box('Course rear chimney cap',(xx,yy,zz),(1.65,.82,.13),'roof',terracotta)
 for j in range(4):
  m=Mesh('Silhouette rear chimney pot');m.lathe((xx-.55+j*.36,yy),[(height+4.0,.10),(height+4.6,.105),(height+4.67,.15),(height+4.76,.13)],segments=12);finish(m,'roof',[terracotta])
# Three party stacks on main ridge, with rectangular sandstone coping.
for x in (5.0,18.78,32.5):
 box('Envelope main chimney',(x,-DEP/2,R+.55),(1.35,.74,1.55),'roof',brick)
 box('Course main chimney coping',(x,-DEP/2,R+1.37),(1.55,.94,.16),'roof',terracotta)
 for j in range(4):
  m=Mesh('Silhouette main chimney pot');m.lathe((x-.51+j*.34,-DEP/2),[(R+1.45,.095),(R+2.05,.10),(R+2.10,.14),(R+2.19,.12)],segments=12);finish(m,'roof',[terracotta])
# Ornamental ridge course and drainage follow the long street range.
m=Mesh('Course terracotta ridge');m.tube([(4.9,-DEP/2,R+.08),(W-4.9,-DEP/2,R+.08)],.09,sides=8);finish(m,'roof',[terracotta])
for x in (0,W):
 m=Mesh('Fitting front drainpipe');m.tube([(x,.07,13.4),(x,.07,.3)],.045,sides=8);finish(m,mats=[black])
# Bake the mapped side skew into vertices: Blender object transforms cannot
# retain shear, so assigning a sheared matrix would separate attached features.
a=math.radians(D['local_rotation_degrees'])
registered_world=Matrix(((math.cos(a),D['north_basis'][0],0,D['origin_site_xy'][0]),
                         (math.sin(a),D['north_basis'][1],0,D['origin_site_xy'][1]),
                         (0,0,1,D['base_z']),(0,0,0,1)))
registration=registered_world@world.inverted()
registered_meshes={}
for ob in [o for col in C.values() for o in col.objects if o.type=='MESH']:
    old=ob.matrix_world.copy();new=old.copy();new.translation=registration@old.translation
    linear=old.inverted().to_3x3()@registration.to_3x3()@old.to_3x3()
    key=(ob.data.name,tuple(round(v,6) for row in linear for v in row))
    if key not in registered_meshes:
        mesh=ob.data.copy()
        for vertex in mesh.vertices:vertex.co=linear@vertex.co
        mesh.update();registered_meshes[key]=mesh
    ob.data=registered_meshes[key];ob.matrix_world=new

for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.68,.74,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.6;o=bpy.data.objects.new('Sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.6)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/st-georges-place-terrace.blend'))
