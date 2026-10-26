"""15 Nevill Street: current shopfronts and independently observed small-scale shell."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from southport3d.geometry import Mesh,face_matrix
from southport3d.planar import subtract
from plan import world,outline,roofs,bay_line
D=json.loads((ROOT/'research/layout.json').read_text());DETAIL=D['phase']=='detail';W=D['width'];L=D['depth'];E=D['eave'];MD=D['main_depth'];x,y,z=D['origin'];T=Matrix(((0,-1,0,x),(1,0,0,y),(0,0,1,z),(0,0,0,1)));F=T@face_matrix((0,0,0),(0,-1,0));SIDE=T@face_matrix((W,0,0),(1,0,0))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';C={}
for k in ('frontage','rear','roof'):C[k]=bpy.data.collections.new(k);s.collection.children.link(C[k])
def material(name,color,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.75
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
cream=material('Cream painted brick',(.72,.71,.63),'render');white=material('White window joinery',(.83,.83,.77));dark=material('Black gutters and trim',(.035,.042,.039));glass=material('Blue grey glazing',(.12,.19,.20));shadow=material('Interior shade',(.06,.055,.04));slate=material('Grey green slate',(.24,.26,.24),'slate');red=material('Red canopy stripe',(.65,.07,.08));green=material('Green canopy stripe',(.05,.34,.13));yellow=material('Yellow canopy stripe',(.85,.62,.12));pink=material('Pink canopy stripe',(.66,.23,.37));metal=material('Galvanised fittings',(.42,.45,.42));tan=material('Wafer cone',(.65,.37,.15));signs={a:material(a+' printed fascia',(1,1,1),a)for a in ('salaars','antonios','rock')}
def finish(m,part='frontage',mat=cream,frame=T,uvscale=1):
 if not m.faces:return
 ob=m.finish([mat],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Authored metric UV')
 for p in ob.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/uvscale,v[axes[1]]/uvscale)
 ob.data.transform(frame);return ob

def box(name,c,size,mat=white,part='frontage',frame=F):
 m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame)
def quad(name,points,mat=cream,part='frontage',frame=T):
 m=Mesh(name);points=list(reversed(points)) if name in ('Architecture striped canopy','Architecture striped valance','Architecture corner canopy') else points;m.add(points,[tuple(range(len(points)))]);return finish(m,part,mat,frame)
def rect(a,b,c,d):return[(a,b),(c,b),(c,d),(a,d)]
def wall(name,polygon,holes=(),frame=F,part='frontage',mat=cream):
 pieces=[polygon]
 for hole in holes:pieces=[v for p in pieces for v in subtract(p,hole)]
 m=Mesh('Shell '+name)
 for p in pieces:m.add([(*v,0)for v in p],[tuple(range(len(p)))] )
 for hole in holes:
  for a,b in zip(hole,hole[1:]+hole[:1]):m.add([(*a,0),(*b,0),(*b,-.19),(*a,-.19)],[(0,1,2,3)])
 return finish(m,part,mat,frame)
def window(name,a,bottom,width,height,frame=F,part='frontage',columns=2):
 quad('Glazing '+name,[(a,bottom,-.13),(a+width,bottom,-.13),(a+width,bottom+height,-.13),(a,bottom+height,-.13)],glass,part,frame)
 # Adjacent joinery pieces own disjoint rectangles, eliminating coplanar overlaps.
 bw=.045
 for h in [bottom,bottom+height-bw]:box('Architecture '+name+' horizontal',(a+width/2,h+bw/2,-.055),(width,bw,.10),white,part,frame)
 for u in [a,a+width-bw]+[a+width*i/columns-bw/2 for i in range(1,columns)]:box('Architecture '+name+' upright',(u+bw/2,bottom+height/2,-.055),(bw,height-2*bw,.10),white,part,frame)
 for i in range(columns):
  lo=a+bw if i==0 else a+width*i/columns+bw/2;hi=a+width-bw if i==columns-1 else a+width*(i+1)/columns-bw/2
  box('Architecture '+name+' transom',((lo+hi)/2,bottom+height*.73,-.055),(hi-lo,.035,.10),white,part,frame)
 box('Architecture '+name+' sill',(a+width/2,bottom-.055,.055),(width,.08,.22),white,part,frame)
def poster(name,a,b,z0,z1,tex,frame=F,part='frontage',out=.19):
 # Side/back box behind an outward sign plane, with explicit separation.
 box('Architecture '+name+' board',((a+b)/2,(z0+z1)/2,out-.035),(b-a,z1-z0,.06),dark,part,frame)
 ob=quad('Architecture '+name,[(a,z0,out),(b,z0,out),(b,z1,out),(a,z1,out)],signs[tex],part,frame)
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   # Original vertices retained by triangulation; transform back for planar UV.
   v=frame.inverted()@ob.data.vertices[ob.data.loops[li].vertex_index].co;ob.data.uv_layers[0].data[li].uv=((v.x-a)/(b-a),(v.y-z0)/(z1-z0))
def pipe(name,points,r=.035,part='frontage',mat=dark):
 m=Mesh(name)
 for a,b in zip(points,points[1:]):
  A=Vector(a);B=Vector(b);axis=(B-A).normalized();u=axis.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=axis.cross(u);verts=[tuple(P+r*(math.cos(i*math.tau/8)*u+math.sin(i*math.tau/8)*v))for P in (A,B)for i in range(8)]
  m.add(verts,[(i,(i+1)%8,(i+1)%8+8,i+8)for i in range(8)]+[tuple(reversed(range(8))),tuple(range(8,16))])
 return finish(m,part,mat,T)
# Piecewise walls retain actual upper bay apertures. Ground belongs to storefronts.
upperholes=[rect(c-w/2,D['upper_bottom'],c+w/2,D['upper_top'])for c,w,d in D['bays']]+[rect(3.72,3.8,4.47,4.94)] if DETAIL else []
wall('street upper',rect(0,3.55,W,E),upperholes)
if not DETAIL:wall('street base',rect(0,-.25,W,3.55))
# Main gable and rear wing are distinct; no fictitious whole-height rear block.
sideholes=[rect(5.55,3.75,6.4,4.78),rect(4.65,.05,5.65,2.65),rect(5.85,.05,6.95,2.65),rect(.25,.1,4.35,2.65)] if DETAIL else []
wall('Cable gable',[(0,-.25),(MD,-.25),(MD,E),(D['ridge_v'],D['ridge']),(0,E)],sideholes,SIDE,'rear')
wall('Cable rear lean-to',[(MD,-.25),(L,-.25),(L,4.02),(MD,4.77)],frame=SIDE,part='rear')
# South side and rear surfaces; unknown courtyard openings are not fabricated.
left=T@face_matrix((0,D['wing_depth'],0),(-1,0,0));B=D['wing_depth']
wall('south side',[(0,-.25),(B,-.25),(B,E),(B-D['ridge_v'],D['ridge']),(B-MD,E),(B-MD,4.77),(0,4.17)],frame=left,part='rear')
back=T@face_matrix((W,MD,0),(0,1,0));wall('rear upper strip',rect(0,4.85,W,E-.08),frame=back,part='rear')
for name,A,B,h in [('rear main',(W,L),(D['wing_width'],L),4.02),('wing return',(D['wing_width'],L),(D['wing_width'],D['wing_depth']),4.17),('wing end',(D['wing_width'],D['wing_depth']),(0,D['wing_depth']),4.17)]:
 du=B[0]-A[0];dv=B[1]-A[1];ln=math.hypot(du,dv);frame=T@face_matrix((*A,0),(dv,-du,0));wall(name,[(0,-.25),(ln,-.25),(ln,h),(0,4.77-.60*(L-MD)/(D['wing_depth']-MD) if name=='wing return' else h)],frame=frame,part='rear')
for name,p in roofs(D):
 # Closed roof slab with outward top, 8 cm fascia; source and receiver same topology.
 m=Mesh('Shell roof '+name);n=len(p);bottom=[(u,v,h-.08)for u,v,h in p];m.add(p+bottom,[tuple(range(n)),tuple(reversed(range(n,n*2)))]+[(i,(i+n)%n+n,((i+1)%n)+n,(i+1)%n)for i in range(n)])
 ob=finish(m,'roof',slate,T,1.6);ob['closed_shell']=True
if DETAIL:
 for c,w,depth in D['bays']:
  line=bay_line(c,w,depth);lo=D['upper_bottom'];hi=D['upper_top']
  for j,(A,B) in enumerate(zip(line,line[1:])):
   du=B[0]-A[0];dv=B[1]-A[1];ln=math.hypot(du,dv);frame=T@face_matrix((*A,0),(dv,-du,0));window('upper bay '+str(c)+' '+str(j),.075,lo,ln-.15,hi-lo,frame,columns=3 if j==1 else 1)
  for pu,pv in line[1:-1]:pipe('Architecture bay corner post',[(pu,pv,lo+.01),(pu,pv,hi-.01)],.065,mat=white)
  # Window face replaces the wall opening. Solid sill/head own their lower/upper bands.
  poly=[(*q,hi+.08)for q in line]+[(c+w/2,0,hi+.08),(c-w/2,0,hi+.08)]
  # Roof cap is deliberately a single non-overlapping footprint.
  quad('Architecture bay cap '+str(c),[(*q,hi+.12)for q in line],slate)
 window('small upper',3.72,3.8,.75,1.14,columns=1)
 window('Cable upper',5.55,3.75,.85,1.03,SIDE,'rear',1)
 # Shop floor openings and actual end piers, not a wall hidden behind glazing.
 shop_holes=[rect(a,.02,b,2.65)for a,b in [(.14,1.28),(1.33,2.85),(2.9,4.48),(4.65,8.85),(8.98,12.84)]]
 wall('shop masonry',rect(0,-.25,W,3.55),shop_holes)
 # Salaars entrance and glazing is set into the opening beneath the fascia.
 for a,b,door in [(.14,1.28,True),(1.33,2.85,False),(2.9,4.48,False)]:
  low=.04 if door else .43;window('Salaars shop',a,low,b-a,2.55-low,columns=1)
  if not door:box('Architecture Salaars stallriser',((a+b)/2,.17,-.05),(b-a,.30,.20),dark)
 for a,b,tex in [(4.65,8.85,'antonios'),(8.98,12.84,'rock')]:
  # Deep shade at back of serving opening, display case at front.
  box('Shell shop recess',((a+b)/2,1.8,-.48),(b-a,1.7,.08),shadow)
  poster(tex+' counter',a,b,.08,.85,tex,out=.06)
  box('Architecture glass display',((a+b)/2,1.21,-.08),(b-a, .65,.07),glass)
  for h in (.90,1.51):box('Architecture display rail',((a+b)/2,h,.01),(b-a,.045,.08),metal)
  for u in [a+.04,(a+b)/2,b-.04]:box('Architecture display upright',(u,1.205,.01),(.035,.56,.08),metal)
  # Authored trays/jars, restrained detail behind clear counter lines.
  for i in range(10):
   u=a+.2+(b-a-.4)*i/9;box('Architecture sweet display',(u,1.42,-.16),(.18,.12,.17),[yellow,pink,white,green][i%4])
 for a,b in [(4.65,8.85),(8.98,12.84)]:
  for level in (1.82,2.22):
   box('Architecture shop shelf',((a+b)/2,level-.08,-.31),(b-a-.12,.035,.26),white)
   for i in range(12):
    u=a+.18+(b-a-.36)*i/11;box('Architecture confectionery packet',(u,level+.03,-.34),(.16,.18,.09),[yellow,pink,red,green,white][i%5])
 for a,b,tex in [(0,4.6,'salaars'),(4.65,8.9,'antonios'),(8.94,W,'rock')]:poster(tex+' fascia',a,b,2.85,3.73,tex,out=.20)
 # Cable access doors and shutter observed in the older unobstructed panorama.
 window('Cable corner shutter',.25,.10,4.10,2.55,SIDE,'rear',1)
 for a in (4.65,5.85):
  box('Architecture Cable access door',(a+.50,1.35,-.07),(1,2.6,.10),white,'rear',SIDE)
  for i in range(6):box('Architecture Cable door groove',(a+.08+i*.16,1.35,-.005),(.009,2.45,.008),cream,'rear',SIDE)
  box('Architecture Cable door handle',(a+.84,1.15,.035),(.03,.14,.05),metal,'rear',SIDE)
 poster('Cable rock sign',0,MD,2.85,3.73,'rock',SIDE,'rear',.20)
 # Adjacent stripe panels meet edge-to-edge; no transparent overlay meshes.
 def canopy(a,b,frame,part,colors):
  n=max(2,round((b-a)/.28));ww=(b-a)/n
  for i in range(n):
   aa=a+i*ww;bb=aa+ww;mat=colors[i%len(colors)]
   quad('Architecture striped canopy',[(aa,2.84,.22),(bb,2.84,.22),(bb,2.57,1.13),(aa,2.57,1.13)],mat,part,frame)
   quad('Architecture striped valance',[(aa,2.57,1.13),(bb,2.57,1.13),(bb,2.39,1.13),(aa,2.39,1.13)],mat,part,frame)
 canopy(4.65,8.90,F,'frontage',[green,white,red,white]);canopy(8.94,W,F,'frontage',[yellow,white,pink,white]);canopy(0,MD,SIDE,'rear',[yellow,white,pink,white])
 for i in range(6):
  aa=-math.pi/2+i*math.pi/12;bb=aa+math.pi/12;col=[yellow,white,pink,white][i%4]
  points=[(W+.22*math.cos(aa),.22*math.sin(aa),2.84),(W+.22*math.cos(bb),.22*math.sin(bb),2.84),(W+1.13*math.cos(bb),1.13*math.sin(bb),2.57),(W+1.13*math.cos(aa),1.13*math.sin(aa),2.57)]
  quad('Architecture corner canopy',points,col,'frontage')
  A,B=points[3],points[2];quad('Architecture corner valance',[(A[0],A[1],2.39),(B[0],B[1],2.39),B,A],col,'frontage')
 # Rainwater pipes are offset from render, with modest joints and no coincident wall faces.
 for u in (.08,4.62,8.94,12.94):pipe('Architecture downpipe '+str(u),[(u,-.105,.1),(u,-.105,5.18),(u,-.22,5.35)],.035)
 pipe('Architecture front gutter',[(0,-.20,5.32),(W,-.20,5.32)],.065,'roof')
 # Recognisable decorative gelato cone beside Antonio’s fascia; authored geometry.
 for cx in (4.74,12.68):
  m=Mesh('Architecture gelato cone');n=16;v=[(cx,-.38,2.55)]+[(cx+.17*math.cos(i*math.tau/n),-.38+.17*math.sin(i*math.tau/n),3.14)for i in range(n)];m.add(v,[(0,1+i,1+(i+1)%n)for i in range(n)]+[tuple(range(1,n+1))]);finish(m,mat=tan)
  for j in range(5):
   rr=.18*(1-j*.13);zz=3.14+j*.10;m=Mesh('Architecture soft ice swirl');verts=[]
   for h,r in [(zz,rr),(zz+.105,rr*.80)]:verts.extend([(cx+r*math.cos(i*math.tau/12),-.38+r*math.sin(i*math.tau/12),h)for i in range(12)])
   m.add(verts,[(i,(i+1)%12,(i+1)%12+12,i+12)for i in range(12)]);finish(m,mat=white)
 box('Architecture low roof stump',(7.8,D['ridge_v'],6.69),(.48,.52,.40),cream,'roof',T)
 box('Architecture stump cap',(7.8,D['ridge_v'],6.925),(.57,.61,.07),slate,'roof',T)
 for u in (5.4,9.1):
  pipe('Fine television mast',[(u,2.8,6.35),(u,2.8,8.1)],.012,'roof',metal)
  for zz in (7.55,8.0):
   pipe('Fine television boom',[(u-.42,2.8,zz),(u+.42,2.8,zz)],.010,'roof',metal)
   for k in range(6):pipe('Fine aerial element',[(u-.36+k*.14,2.65,zz),(u-.36+k*.14,2.95,zz)],.006,'roof',metal)
# Consolidate render batches per part while keeping closed roof shells separate.
# This also avoids selected-to-active baking one tiny joinery object at a time.
for part,collection in C.items():
 for kind in ('Architecture','Fine'):
  obs=[o for o in collection.objects if o.type=='MESH' and not o.get('closed_shell') and (o.name.startswith('Fine ') == (kind=='Fine'))]
  if not obs:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  obs[0].name=kind+' '+part
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2.4;sun.rotation_euler=(.4,.5,.4)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/nevill-street-15.blend'))
