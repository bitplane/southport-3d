"""Lloyds Bank exterior, based on the August 2024 street elevations."""
import json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh, face_matrix, text_object
sys.path.insert(0,str(ROOT/'scripts'))
from architecture import wall_mesh
from facade_prototype import arch_outline, arch_band
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'
c=bpy.data.collections.new('architecture'); s.collection.children.link(c)
def mat(n,col):
 m=bpy.data.materials.new(n); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1); return m
stone=mat('Pale limestone ashlar',(.62,.60,.54)); roof=mat('Flat roof',(.18,.19,.18))
im=bpy.data.images.load(str(ROOT/'textures/stone.png'));im.pack()
node=stone.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
stone.node_tree.links.new(node.outputs['Color'],stone.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
x=D['front_x']; y=D['side_y']; base=D['base_z']; w=D['width_m']; depth=D['main_depth_m']; h=D['upper_height_m']
rotation=Matrix.Translation((x,y,0)) @ Matrix.Rotation(D['registration_angle_rad'],4,'Z') @ Matrix.Translation((-x,-y,0))
def box(name,centre,size,material):
 m=Mesh(name);m.box(centre,size);o=m.finish([material],c);o.matrix_world=rotation
 uv=o.data.uv_layers.new(name='Metric')
 for f in o.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 return o
# Front composition uses the three arched upper lights and an inset banking
# entrance from August 2024. Dimensions are estimates; other elevations are
# still neutral and remain under review.
frame=face_matrix((x,y,base),(-1,0,0))
centres=[3.1,6.05,8.75]
holes=[arch_outline(u,1.05,5.25,7.45) for u in centres]
shop=[(2.5,.12),(9.55,.12),(9.55,3.20),(2.5,3.20)]
radius=.70
shifted=[[(u-radius,z) for u,z in hole] for hole in holes+[shop]]
m=wall_mesh('Envelope prototype front',w-radius,h,shifted,omit_outer_edges=(3,));o=m.finish([stone],c);o.matrix_world=rotation@frame@Matrix.Translation((radius,0,0))
def uv(ob):
 layer=ob.data.uv_layers.new(name='Elevation metres')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;axes=sorted(sorted(range(3),key=lambda i:abs(poly.normal[i]))[:2]);layer.data[li].uv=(v[axes[0]],v[axes[1]])
def elevation_box(name,u,z,width,height,thickness,out,material,wallframe=None):
 m=Mesh(name);m.box((u,z,out),(width,height,thickness));o=m.finish([material],c);o.matrix_world=rotation@(wallframe or frame);uv(o);return o
uv(o)
# Round the London/Anchor corner in plan. The adjacent wall edge caps are
# omitted so the curved skin owns the transition exactly once.
m=Mesh('Envelope rounded corner');steps=8;inner=radius-.30
for i in range(steps):
 a=math.pi-i*math.pi/(2*steps);b=math.pi-(i+1)*math.pi/(2*steps)
 def p(r,t,z):return (x+radius+r*math.cos(t),y-radius+r*math.sin(t),base+z)
 m.add([p(radius,a,0),p(radius,b,0),p(radius,b,h),p(radius,a,h)],[(3,2,1,0)])
 m.add([p(inner,a,0),p(inner,a,h),p(inner,b,h),p(inner,b,0)],[(3,2,1,0)])
 m.add([p(inner,a,h),p(radius,a,h),p(radius,b,h),p(inner,b,h)],[(3,2,1,0)])
 m.add([p(inner,b,0),p(radius,b,0),p(radius,a,0),p(inner,a,0)],[(3,2,1,0)])
o=m.finish([stone],c);o.matrix_world=rotation;uv(o)
# Neutral return/party shell for this construction checkpoint.
# Anchor Street is the other exposed elevation: regular upper sash bays and
# glazed lower bays. The deep rear end and gate still require refinement.
sideframe=face_matrix((x+depth,y,base),(0,1,0))
upper=[4.0,6.65,9.30,11.95,14.60,17.25,19.60]
lower=[12.00,14.05,16.10,18.15,20.00]
rect=lambda a,b,c,d:[(a,b),(c,b),(c,d),(a,d)]
sideholes=[rect(u-.52,5.35,u+.52,8.10) for u in upper]+[rect(u-.80,.65,u+.80,3.30) for u in lower]
m=wall_mesh('Envelope Anchor side',depth-radius,h,sideholes,omit_outer_edges=(1,3));ob=m.finish([stone],c);ob.matrix_world=rotation@sideframe;uv(ob)
partyframe=face_matrix((x+.30,y-w,base),(0,-1,0))
m=wall_mesh('Envelope party',depth-.60,h,[],omit_outer_edges=(1,3));ob=m.finish([stone],c);ob.matrix_world=rotation@partyframe;uv(ob)
box('Envelope rear',(x+depth-.15,y-w/2,base+h/2),(.3,w-.6,h),stone)
glass=mat('Muted window glass',(.12,.16,.16));white=mat('Pale painted frame',(.75,.75,.69));green=mat('Lloyds green fascia',(.015,.16,.055));dark=mat('Entrance recess',(.028,.04,.035))
for i,u in enumerate(upper):
 elevation_box('Window Anchor upper glass '+str(i),u,6.72,1.04,2.75,.035,-.20,glass,sideframe)
 for dx in [-.49,0,.49]:elevation_box('Window Anchor upper stile '+str(i),u+dx,6.72,.045,2.75,.08,-.09,white,sideframe)
 for z in [5.39,6.04,6.72,7.40,8.06]:
  for dx in [-.245,.245]:elevation_box('Window Anchor upper rail '+str(i),u+dx,z,.445,.04,.08,-.09,white,sideframe)
 elevation_box('Trim Anchor upper sill '+str(i),u,5.27,1.25,.12,.25,.06,stone,sideframe)
 for dx in [-.61,.61]:elevation_box('Trim Anchor window surround '+str(i),u+dx,6.725,.10,2.79,.13,.035,stone,sideframe)
 elevation_box('Trim Anchor window lintel '+str(i),u,8.18,1.32,.12,.13,.035,stone,sideframe)
for i,u in enumerate(lower):
 elevation_box('Window Anchor lower glass '+str(i),u,1.98,1.60,2.65,.035,-.20,glass,sideframe)
 for dx in [-.77,0,.77]:elevation_box('Window Anchor lower stile '+str(i),u+dx,1.98,.045,2.65,.08,-.09,white,sideframe)
 for z in [.69,2.0,3.26]:
  for dx in [-.385,.385]:elevation_box('Window Anchor lower rail '+str(i),u+dx,z,.725,.04,.08,-.09,white,sideframe)
elevation_box('Trim Anchor storey band',(depth-radius-.30)/2,4.33,depth-radius-.30,.16,.24,.04,stone,sideframe)
elevation_box('Trim Anchor parapet',(depth-radius-.30)/2,10.15,depth-radius-.30,.20,.26,.04,stone,sideframe)

for k,(centre,hole) in enumerate(zip(centres,holes)):
 m=Mesh('Window prototype glazing '+str(k));m.add([(u,v,-.20) for u,v in hole],[tuple(range(len(hole)))])
 o=m.finish([glass],c);o.matrix_world=rotation@frame;uv(o)
 stiles=[-.49,-.245,0,.245,.49]
 rails=[-.3675,-.1225,.1225,.3675]
 levels=[5.28,5.60,5.92,6.24,6.56,6.88,7.20,7.43]
 for i,dx in enumerate(stiles):elevation_box('Window prototype stile '+str(k)+' '+str(i),centre+dx,6.35,.045,2.2,.08,-.09,white)
 for i,z in enumerate(levels):
  for j,offset in enumerate(rails):elevation_box('Window prototype rail '+str(k)+' '+str(i)+' '+str(j),centre+offset,z,.200,.035,.08,-.09,white)
 # The first bay is the close-comparison prototype: four sash divisions,
 # a small concentric fanlight rail and a stepped two-band stone arch.
 fan=Mesh('Window prototype fan '+str(k))
 for angle in [math.pi/6,math.pi/3,math.pi/2,2*math.pi/3,5*math.pi/6]:
  dx,dz=math.cos(angle),math.sin(angle);nx,nz=-dz*.012,dx*.012
  spans=[(.075,.292),(.318,.49)]
  for lo,hi in spans:
   a=(centre+dx*lo,7.45+dz*lo);b=(centre+dx*hi,7.45+dz*hi)
   fan.add([(a[0]-nx,a[1]-nz,-.07),(b[0]-nx,b[1]-nz,-.07),(b[0]+nx,b[1]+nz,-.07),(a[0]+nx,a[1]+nz,-.07)],[(0,1,2,3)])
 if True:
  for i in range(12):
   a=math.pi*i/12;b=math.pi*(i+1)/12
   fan.add([(centre+r*math.cos(t),7.45+r*math.sin(t),-.07) for r,t in [(.292,a),(.292,b),(.318,b),(.318,a)]],[(0,1,2,3)])
 ob=fan.finish([white],c);ob.matrix_world=rotation@frame;uv(ob)
 bands=[(1.05,.06,.035),(1.17,.18,.055)]
 for j,(innerwidth,thick,out) in enumerate(bands):
  inner,outer=arch_band(centre,innerwidth,7.45,thick);m=Mesh('Trim prototype arch '+str(k)+' '+str(j))
  for a,b,c0,d in zip(inner,inner[1:],outer[1:],outer):m.add([(a[0],a[1],out),(b[0],b[1],out),(c0[0],c0[1],out),(d[0],d[1],out)],[(3,2,1,0)])
  ob=m.finish([stone],c);ob.matrix_world=rotation@frame;uv(ob)
 if True:
  for dx in [-.645,.645]:
   # Long open-ended jamb strips share their top/bottom with the arch and sill.
   u=centre+dx;v=[(u-.12,5.25,-.04),(u+.12,5.25,-.04),(u+.12,7.45,-.04),(u-.12,7.45,-.04),
                   (u-.12,5.25,.11),(u+.12,5.25,.11),(u+.12,7.45,.11),(u-.12,7.45,.11)]
   m=Mesh('Trim prototype window jamb');faces=[(4,5,6,7),(3,2,1,0)]+([(0,4,7,3)] if dx<0 else [(5,1,2,6)]);m.add(v,faces)
   ob=m.finish([stone],c);ob.matrix_world=rotation@frame;uv(ob)
  elevation_box('Trim prototype keystone',centre,8.12,.25,.26,.18,.07,stone)
 elevation_box('Trim window sill '+str(k),centre,5.18,1.35,.13,.25,.07,stone)
 if True:
  elevation_box('Trim prototype sill lower',centre,5.085,1.48,.06,.30,.08,stone)
  elevation_box('Trim prototype sill foot',centre,5.035,1.40,.04,.22,.06,stone)
# Storefront backing is continuous behind recessed glazing; no interior is implied.
elevation_box('Shop recessed backing',6.025,1.66,7.05,3.08,.035,-.37,dark)
elevation_box('Shop display glazing',4.55,1.62,4.10,3.0,.04,-.22,glass)
elevation_box('Shop entry shadow',7.60,1.60,1.72,2.96,.04,-.25,dark)
elevation_box('Shop entrance glazed door',7.60,1.40,1.34,2.42,.035,-.16,glass)
for u in [6.94,8.26]:elevation_box('Shop door stile',u,1.40,.05,2.46,.07,-.10,white)
for z in [.20,2.60]:elevation_box('Shop door rail',7.60,z,1.27,.05,.07,-.10,white)
elevation_box('Shop door handle',8.05,1.28,.04,.36,.08,-.05,white)
atm=wall_mesh('Shop ATM panel',1.08,2.96,[rect(.28,1.00,.80,1.87)],thickness=.04,omit_outer_edges=(0,3))
ob=atm.finish([green],c);ob.matrix_world=rotation@frame@Matrix.Translation((8.46,.12,-.22));uv(ob)
elevation_box('Shop ATM inset',9.00,1.55,.52,.87,.035,-.29,dark)
elevation_box('Shop ATM screen',9.00,1.72,.40,.30,.022,-.245,glass)
elevation_box('Shop ATM keypad',9.00,1.35,.37,.13,.025,-.24,white)
for i,u in enumerate([2.55,4.58,6.60,7.60,8.45,9.50]):elevation_box('Shop vertical frame '+str(i),u,1.62,.045,3.0,.08,-.10,white)
for i,u in enumerate([2.40,9.65]):
 elevation_box('Trim banking portal jamb '+str(i),u,1.665,.18,3.09,.25,.035,stone)
elevation_box('Trim banking portal lintel',6.025,3.30,7.43,.18,.25,.035,stone)
elevation_box('Shop horizontal transom',6.02,3.12,6.95,.07,.09,-.09,white)
elevation_box('Shop threshold',6.02,.10,6.95,.09,.30,-.10,stone)
# Fascia and pronounced projecting cornice with regularly spaced brackets.
elevation_box('Shop fascia',6.00,3.58,7.1,.48,.12,.07,green)
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
txt=text_object('Shop Lloyds Bank lettering','LLOYDS BANK',(6.35,3.58,.14),(0,0,1),.26,3.5,font,white,extrude=.003)
bpy.ops.object.select_all(action='DESELECT');txt.select_set(True);bpy.context.view_layer.objects.active=txt;bpy.ops.object.convert(target='MESH')
for old in list(txt.users_collection):old.objects.unlink(txt)
c.objects.link(txt);txt.matrix_world=rotation@frame@txt.matrix_world;uv(txt)

# The reference cornice has a stepped projecting lip; extrude one profile
# along the frontage instead of stacking coplanar cap boxes.
def profile(name,u0,u1,profile,material):
 m=Mesh(name);n=len(profile);raise_cornice=.16 if name.startswith(('Trim profiled cornice','Fine cornice bracket')) else 0
 verts=[(u,z+raise_cornice,out) for u in (u0,u1) for out,z in profile]
 m.add(verts,[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)])
 ob=m.finish([material],c);ob.matrix_world=rotation@frame;uv(ob);return ob
profile('Trim profiled cornice',radius,w,[(-.10,4.02),(.14,4.02),(.22,4.07),(.27,4.09),(.29,4.14),(.35,4.14),(.35,4.21),(.27,4.23),(.23,4.28),(-.10,4.28)],stone)
elevation_box('Trim upper parapet',(w+radius)/2,10.15,w-radius,.20,.32,.04,stone)
for i in range(14):
 u=.90+i*.63
 if True:
  for j,du in enumerate([-.08,0,.08]):
   profile('Fine cornice bracket prototype rib '+str(j),u+du-.0275,u+du+.0275,[(-.05,3.70),(.12,3.70),(.20,3.76),(.23,3.83),(.28,3.88),(.32,3.95),(.32,3.985),(-.05,3.985)],stone)
  elevation_box('Fine cornice bracket prototype head',u,4.1625,.24,.035,.45,.14,stone)
# Flat roof, with its front corner following the same rounded footprint.
r=.55;roofpts=[(x+radius+r*math.cos(math.pi-i*math.pi/16),y-radius+r*math.sin(math.pi-i*math.pi/16)) for i in range(9)]
roofpts += [(x+depth-.15,y-.15),(x+depth-.15,y-w+.15),(x+.15,y-w+.15)]
roofpts.reverse()
m=Mesh('Roof flat');n=len(roofpts);lo=base+h-.28;hi=lo+.08
m.add([(X,Y,hi) for X,Y in roofpts]+[(X,Y,lo) for X,Y in roofpts],
      [tuple(range(n))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)])
o=m.finish([roof],c);o.matrix_world=rotation;uv(o)
# Low rooflight curbs visible in the oblique imagery; sizes are estimated.
for i,offset in enumerate([4.0,9.0,14.0,18.5]):
 box('Roof rooflight curb '+str(i),(x+offset,y-w/2,base+h-.11),(1.15,1.15,.18),roof)
 box('Roof rooflight glass '+str(i),(x+offset,y-w/2,base+h-.01),(.95,.95,.02),glass)
# Restrained rear service strip: gated lower frontage and a raised end bay.
service=D['service_depth_m'];sw=D['service_width_m'];sh=D['service_height_m']
sframe=face_matrix((x+depth+service,y,base),(0,1,0))
gate=rect(1.0,.05,2.15,2.55)
m=wall_mesh('Envelope service side',service,sh,[gate]);ob=m.finish([stone],c);ob.matrix_world=rotation@sframe;uv(ob)
elevation_box('Shop service gate shadow',1.575,1.30,1.15,2.50,.035,-.18,dark,sframe)
for i in range(8):elevation_box('Fine gate vertical '+str(i),1.05+i*.15,1.30,.035,2.46,.05,-.10,white,sframe)
box('Envelope service party',(x+depth+service/2,y-sw+.15,base+sh/2),(service,.3,sh),stone)
box('Envelope service rear',(x+depth+service-.15,y-sw/2,base+sh/2),(.3,sw-.6,sh),stone)
m=Mesh('Roof service');m.add([(x+depth+3.05,y-.15,base+sh+.04),(x+depth+service-.15,y-.15,base+sh+.04),(x+depth+service-.15,y-sw+.15,base+sh+.04),(x+depth+3.05,y-sw+.15,base+sh+.04)],[(3,2,1,0)]);ob=m.finish([roof],c);ob.matrix_world=rotation;uv(ob)
# Upper return bay is seen in the Anchor Street panorama; its height and
# rear extent are approximate and its concealed faces are deliberately plain.
towerdepth=3.0;towerh=11.7;tf=face_matrix((x+depth+towerdepth,y,base),(0,1,0))
towerholes=[rect(.85,5.15,2.05,7.25),arch_outline(1.45,1.20,8.05,10.05)]
shifted_tower=[[(u,z-sh) for u,z in hole] for hole in towerholes]
m=wall_mesh('Envelope rear raised bay',towerdepth,towerh-sh,shifted_tower,omit_outer_edges=(0,1));ob=m.finish([stone],c);ob.matrix_world=rotation@tf@Matrix.Translation((0,sh,0));uv(ob)
# Close the round head from both faces; the rectangular pane below does not
# own the semi-circular aperture.
cap=[(1.45-.60,10.05),(1.45+.60,10.05)]+[(1.45+.60*math.cos(math.pi*i/12),10.05+.60*math.sin(math.pi*i/12)) for i in range(1,13)]
m=Mesh('Window rear fanlight');m.outline(cap,-.22,-.19);ob=m.finish([glass],c);ob.matrix_world=rotation@tf;uv(ob)
for i,(u,z,ww,hh) in enumerate([(1.45,6.20,1.20,2.10),(1.45,9.05,1.20,2.0)]):
 elevation_box('Window rear bay glass '+str(i),u,z,ww,hh,.035,-.20,glass,tf)
 for dx in [-.56,0,.56]:elevation_box('Window rear bay stile '+str(i),u+dx,z,.045,hh,.08,-.09,white,tf)
 for zbar in [z-hh/2+.04,z,z+hh/2-.04]:
  for dx in [-.28,.28]:elevation_box('Window rear bay rail '+str(i),u+dx,zbar,.515,.04,.08,-.09,white,tf)
# Dress the raised arched light as a real stone opening, with a divided fan.
inner,outer=arch_band(1.45,1.20,10.05,.14)
m=Mesh('Trim rear arched light')
for a,b,c0,d in zip(inner,inner[1:],outer[1:],outer):
 m.add([(a[0],a[1],.035),(b[0],b[1],.035),(c0[0],c0[1],.035),(d[0],d[1],.035)],[(3,2,1,0)])
ob=m.finish([stone],c);ob.matrix_world=rotation@tf;uv(ob)
for dx in [-.67,.67]:elevation_box('Trim rear window jamb',1.45+dx,9.05,.14,2.0,.12,.09,stone,tf)
for z in [5.09,7.99]:elevation_box('Trim rear window sill',1.45,z,1.48,.12,.20,.12,stone,tf)
fan=Mesh('Window rear fan divisions')
for angle in [math.pi/6,math.pi/3,math.pi/2,2*math.pi/3,5*math.pi/6]:
 dx,dz=math.cos(angle),math.sin(angle);nx,nz=-dz*.015,dx*.015
 a=(1.45+dx*.05,10.05+dz*.05);b=(1.45+dx*.57,10.05+dz*.57)
 fan.add([(a[0]-nx,a[1]-nz,-.07),(b[0]-nx,b[1]-nz,-.07),(b[0]+nx,b[1]+nz,-.07),(a[0]+nx,a[1]+nz,-.07)],[(0,1,2,3)])
ob=fan.finish([white],c);ob.matrix_world=rotation@tf;uv(ob)
# The bay's west face above the main roof is exposed and closes the
# otherwise dark opening; the lower contact is buried at the common wall.
m=Mesh('Envelope raised bay exposed end');m.add([(x+depth,y,base+h),(x+depth,y-sw,base+h),(x+depth,y-sw,base+towerh),(x+depth,y,base+towerh)],[(0,1,2,3)]);ob=m.finish([stone],c);ob.matrix_world=rotation;uv(ob)
box('Envelope raised bay party',(x+depth+(towerdepth+.30)/2,y-sw+.15,base+(sh+towerh)/2),(towerdepth-.30,.3,towerh-sh),stone)
box('Envelope raised bay rear',(x+depth+towerdepth-.15,y-sw/2,base+(sh+towerh)/2),(.3,sw-.6,towerh-sh),stone)
m=Mesh('Roof raised bay');m.add([(x+depth+.15,y-.15,base+towerh+.04),(x+depth+towerdepth-.15,y-.15,base+towerh+.04),(x+depth+towerdepth-.15,y-sw+.15,base+towerh+.04),(x+depth+.15,y-sw+.15,base+towerh+.04)],[(3,2,1,0)]);ob=m.finish([roof],c);ob.matrix_world=rotation;uv(ob)
# Deep horizontal masonry joints visible on the lower Anchor return.  Clip
# each narrow line to the wall so it never crosses a window aperture.
joint=mat('Recessed masonry joints',(.32,.30,.27))
def joints(wallframe,length,openings,levels):
 for z in levels:
  spans=[(0.01,length-.01)]
  for left,bottom,right,top in openings:
   if bottom < z < top:
    spans=[q for a,b in spans for q in ((a,min(b,left)),(max(a,right),b)) if q[1]-q[0]>.01]
  for a,b in spans:
   elevation_box('Trim masonry joint', (a+b)/2,z,b-a,.018,.004,.004,joint,wallframe)
joints(sideframe,depth-radius,[(u-.8,.65,u+.8,3.30) for u in lower],[.55,1.10,1.65,2.20,2.75,3.36,3.85])
joints(sframe,service,[(1,.05,2.15,2.55)],[.55,1.10,1.65,2.20,2.75,3.36])

# Triangulation before export gives tangent generation deterministic planar faces.
for ob in [o for o in c.objects if o.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(camera);camera.data.type='ORTHO';s.camera=camera
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/lloyds-bank.blend'))
