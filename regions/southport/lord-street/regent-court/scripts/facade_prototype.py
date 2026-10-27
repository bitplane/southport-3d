# Prototype wall apertures and storefront; repeated full-height bay in isolation.
# Scene coordinates are the registered site frame. Glazing lies inside apertures.
from mathutils import Vector
PROTOTYPE=True
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
 m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
 return m
brick=material('Red brown brick',(.34,.135,.105));tex=brick.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/brick.png'));tex.image.pack();brick.node_tree.links.new(tex.outputs['Color'],brick.node_tree.nodes['Principled BSDF'].inputs['Base Color']);tan=material('Tan brick at recess',(.47,.36,.25));white=material('Cream painted concrete',(.75,.73,.67));glass=material('Window dark reflection',(.12,.18,.2));frame=material('Window pale frame',(.78,.8,.77));black=material('Shop fascia',(.035,.045,.045));red=material('Farmfoods red',(.65,.035,.025));yellow=material('Farmfoods yellow',(.89,.68,.08))
def face(name,coords,material,part='tower'):
 m=Mesh(name);m.add([(x,y,z+base) for x,y,z in coords],[(0,1,2,3)]);o=m.finish([material],cols[part]);uv=o.data.uv_layers.new(name='Metric')
 for p in o.data.polygons:
  axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/1.92,v[axes[1]]/.96) if material==brick else (v[axes[0]],v[axes[1]])
 return o
def q(name,a,b,y,lo,hi,material,front=True):
 if hi<=lo or b<=a:return
 p=[(a,y,lo),(b,y,lo),(b,y,hi),(a,y,hi)]
 face(name,list(reversed(p)) if front else p,material)
def fbox(name,c,size,material,part='tower'):
 old=mat
 # Reuse massing builder; switch its assigned material, never alter geometry.
 o=box(name,c,size,part)
 o.data.materials.clear();o.data.materials.append(material)
 return o
# Every opening is cut from its masonry skin. Frames and reveals occupy the
# opening; no opaque backing wall sits immediately behind the glazing.
def elevation(a,b,y,front):
 sign=1 if front else -1
 centers=[a+1.6,(a+b)/2,b-1.6]
 for floor in range(10):
  z=6.5+2.8*floor;last=a
  for k,cx in enumerate(centers):
   balcony=k==1;w=2.05 if balcony else 1.75;left=cx-w/2;right=cx+w/2
   low=z+.12 if balcony else z+.65;high=z+2.26 if balcony else z+2.10
   q('Wall span '+str((a,y,floor,k)),last,left,y,z,z+2.8,brick,front)
   q('Wall sill '+str((a,y,floor,k)),left,right,y,z,low,brick,front)
   q('Wall head '+str((a,y,floor,k)),left,right,y,high,z+2.8,brick,front)
   q('Window glass '+str((a,y,floor,k)),left,right,y-sign*.12,low,high,glass,front)
   for x in (left,right):
    face('Window reveal '+str((x,y,floor)),[(x,y,low),(x,y-sign*.12,low),(x,y-sign*.12,high),(x,y,high)],brick)
    fbox('Window vertical '+str((x,y,floor)),(x,y-sign*.07,(low+high)/2),(.07,.08,high-low),frame)
   for h in (low+.035,high-.035):fbox('Window horizontal '+str((left,y,floor,h)),(cx,y-sign*.07,h),(w-.07,.08,.07),frame)
   for xx in ((cx,) if balcony else (left+w*.33,left+w*.67)):
    fbox('Window mullion '+str((xx,y,floor)),(xx,y-sign*.07,(low+high)/2),(.055,.08,high-low-.14),frame)
   fbox('Window pale sill '+str((left,y,floor)),(cx,y+sign*.04,low-.025),(w+.12,.2,.07),frame)
   if balcony:
    fbox('Balcony slab '+str((cx,y,floor)),(cx,y+sign*.58,z+.10),(w+.18,1.18,.18),white)
    for x in (left,right):fbox('Balcony post '+str((x,y,floor)),(x,y+sign*1.08,z+.65),(.045,.05,1.0),frame)
    for h in (z+.32,z+1.10):fbox('Balcony rail '+str((cx,y,floor,h)),(cx,y+sign*1.08,h),(w-.045,.05,.05),frame)
    for x in (left+.35,cx,right-.35):fbox('Fine balcony bar '+str((x,y,floor)),(x,y+sign*1.08,z+.70),(.028,.035,.75),frame)
    # The observed guard consists of two light rectangular X panels.
    for panel in (0,1):
     x0=left+panel*w/2;x1=x0+w/2
     for rise in (True,False):
      # Crossing rails are mitred apart, with one continuous crossing owner.
      for t0,t1 in ([(.05,.95)] if rise else [(.05,.46),(.54,.95)]):
       xx0=x0+(x1-x0)*t0;xx1=x0+(x1-x0)*t1
       zz0=z+.34+.72*(t0 if rise else 1-t0);zz1=z+.34+.72*(t1 if rise else 1-t1)
       xmid=(xx0+xx1)/2;zmid=(zz0+zz1)/2;dx=xx1-xx0;dz=zz1-zz0
       length=(dx*dx+dz*dz)**.5
       o=fbox('Fine balcony diagonal '+str((cx,y,floor,panel,rise,t0)),(xmid,y+sign*1.09,zmid),(length,.035,.035),frame)
       from mathutils import Matrix
       o.data.transform(Matrix.Translation((xmid,y+sign*1.09,base+zmid)) @ Matrix.Rotation(-__import__('math').atan2(dz,dx),4,'Y') @ Matrix.Translation((-xmid,-y-sign*1.09,-base-zmid)))
   last=right
  q('Wall span final '+str((a,y,floor)),last,b,y,z,z+2.8,brick,front)
for a,b in ((481.5,492.5),(495.9,506.9)):
 elevation(a,b,-10.6,True);elevation(a,b,-28.6,False)
# Deep central recess and its returns on both principal elevations.
for yy,front in ((-13.6,True),(-25.6,False)):
 for floor in range(10):
  z=6.5+floor*2.8;last=492.5
  for left,right in ((493.0,493.55),(494.85,495.4)):
   q('Core masonry '+str((yy,floor,left)),last,left,yy,z,z+2.8,tan,front)
   q('Core sill '+str((yy,floor,left)),left,right,yy,z,z+1.1,tan,front)
   q('Core head '+str((yy,floor,left)),left,right,yy,z+2,z+2.8,tan,front)
   q('Core window '+str((yy,floor,left)),left,right,yy+(-.10 if front else .10),z+1.1,z+2,glass,front)
   for x in (left,right):fbox('Core window frame '+str((yy,floor,x)),(x,yy,z+1.55),(.055,.08,.9),frame)
   for h in (z+1.1,z+2):fbox('Core window rail '+str((yy,floor,left,h)),((left+right)/2,yy,h),(right-left-.055,.08,.055),frame)
   last=right
  q('Core masonry end '+str((yy,floor)),last,495.9,yy,z,z+2.8,tan,front)
for x in (492.5,495.9):
 for a,b in ((-13.6,-10.6),(-28.6,-25.6)):
  face('Core return '+str((x,a)),[(x,a,6.5),(x,b,6.5),(x,b,34.5),(x,a,34.5)],tan)
# End elevations. The west return is recessed between two projecting ends,
# as visible in the opposing 3D orbit; the depth is an estimate.
def end_section(x,a,b,center):
 for floor in range(10):
  z=6.5+floor*2.8;lo=z+.65;hi=z+2.1;left=center-.8;right=center+.8
  def side(name,u,v,h0,h1,m,xx=x):
   p=[(xx,u,h0),(xx,v,h0),(xx,v,h1),(xx,u,h1)];face(name,list(reversed(p)) if x<490 else p,m)
  side('End wall outer '+str((x,floor,a)),a,left,z,z+2.8,tan if x==485 else brick)
  side('End wall inner '+str((x,floor,b)),right,b,z,z+2.8,tan if x==485 else brick)
  side('End wall sill '+str((x,floor,center)),left,right,z,lo,tan if x==485 else brick)
  side('End wall head '+str((x,floor,center)),left,right,hi,z+2.8,tan if x==485 else brick)
  inset=x+(.12 if x<490 else -.12)
  side('End glazing '+str((x,floor,center)),left,right,lo,hi,glass,inset)
  for yy in (left,center,right):fbox('End frame '+str((x,yy,floor)),(inset,yy,(lo+hi)/2),(.08,.06,hi-lo-(.14 if yy==center else 0)),frame)
  for h in (lo+.035,hi-.035):fbox('End rail '+str((x,h,center)),(inset,center,h),(.08,1.46,.07),frame)
end_section(506.9,-28.6,-10.6,-19.6)
end_section(481.5,-28.6,-24,-26.3)
end_section(485,-24,-14,-19.0)
face('End front projection',[(481.5,-14,6.5),(481.5,-10.6,6.5),(481.5,-10.6,34.5),(481.5,-14,34.5)],brick)
for y in (-24,-14):
 face('End recess return '+str(y),[(481.5,y,6.5),(485,y,6.5),(485,y,34.5),(481.5,y,34.5)],brick)
# The podium side skins end at the structural floor slabs to avoid coincident
# faces at the slab interfaces. Their solid sections have no observed openings.
for x in (481.4,507.4):
 for lo,hi in ((.24,3.175),(3.525,6.20)):
  face('Podium end skin '+str((x,lo)),[(x,-29.6,lo),(x,-9.6,lo),(x,-9.6,hi),(x,-29.6,hi)],white)
for lo,hi in ((.24,3.175),(3.525,6.20)):
 q('Podium rear skin '+str(lo),481.4,507.4,-29.6,lo,hi,white,False)
# Street-level facade uses actual gaps between structural piers, glazing set back.
for x in (481.5,485.8,490.1,494.4,498.7,503,507.3):
 fbox('Podium front pier '+str(x),(x,-9.6,3.2),(.35,.50,6.1),white)
for a,b in ((481.68,485.62),(485.98,489.92),(490.28,494.22),(494.58,498.52),(498.88,502.82),(503.18,507.12)):
 q('Shop window '+str(a),a,b,-9.82,.18,3.1,glass)
 for x in (a,b):fbox('Shop frame '+str(x),(x,-9.75,1.64),(.08,.10,2.92),black)
 fbox('Shop sill '+str(a),((a+b)/2,-9.75,.20),(b-a-.08,.10,.10),black)
 fbox('Shop transom '+str(a),((a+b)/2,-9.75,2.25),(b-a-.08,.10,.06),black)
# Dark double entrance leaves, threshold and handles. Entrance is one 4.3 m bay.
for x in (490.4,491.55,492.3):fbox('Door frame '+str(x),(x,-9.70,1.35),(.065,.10,2.65),black)
for z in (.12,2.58):
 for a,b in ((490.435,491.5175),(491.5825,492.265)):
  fbox('Door rail '+str((z,a)),((a+b)/2,-9.70,z),(b-a,.10,.065),black)
fbox('Door handle',(491.15,-9.63,1.12),(.035,.05,.38),frame)
fbox('Door kickplate',(491.8,-9.70,.50),(.82,.04,.52),white)
fbox('Entrance threshold',(491.35,-9.64,.08),(1.95,.35,.08),frame)
fbox('Entrance fascia',(492.15,-9.65,3.00),(3.7,.18,.54),black)
for x in (490.52,493.78):
 fbox('Fascia yellow stripe '+str(x),(x,-9.54,3.07),(.55,.04,.10),yellow)
 fbox('Fascia red stripe '+str(x),(x,-9.53,2.96),(.55,.04,.10),red)
# Source text is legible in the 2024 close-up; promotional posters remain blank.
from mathutils import Matrix
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
def sign(name,material,bevel,depth):
 curve=bpy.data.curves.new(name,'FONT');curve.body='farmfoods';curve.font=font;curve.size=.62;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.002;curve.bevel_depth=bevel
 ob=bpy.data.objects.new(name,curve);cols['tower'].objects.link(ob);ob.data.materials.append(material);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-8],context='FACES');bm.to_mesh(ob.data);bm.free()
 ob.data.transform(Matrix(((-1,0,0,492.15),(0,0,1,-9.51+depth),(0,1,0,base+3.00),(0,0,0,1))));bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-7],context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.uv_layers.new(name='Metric');ob.select_set(False)
sign('Farmfoods yellow outline',yellow,.025,0);sign('Farmfoods red lettering',red,0,.035)
# Parking level is open with individual dark vertical bars behind the columns.
for i in range(100):
 x=481.75+i*.255
 fbox('Fine parking bar '+str(i),(x,-9.75,4.85),(.025,.035,2.7),black)
for z in (3.65,4.6,5.75):fbox('Parking gate horizontal '+str(z),(494.4,-9.75,z),(25.5,.04,.045),black)
# Drooping chains hang between the structural bays in the 2024 view.
import math
from mathutils import Matrix
for start in (481.68,485.98,490.28,494.58,498.88,503.18):
 length=3.94
 for j in range(12):
  x0=start+length*j/12;x1=start+length*(j+1)/12
  h0=6.08-.7*math.sin(math.pi*j/12);h1=6.08-.7*math.sin(math.pi*(j+1)/12)
  cx=(x0+x1)/2;cz=(h0+h1)/2;dx=x1-x0;dz=h1-h0
  # A single ribbon per segment shares only edges with neighbours.
  face('Fine parking chain '+str((start,j)),list(reversed([(x0,-9.74,h0-.018),(x1,-9.74,h1-.018),(x1,-9.74,h1+.018),(x0,-9.74,h0+.018)])),black)
# Attached single-storey service range (way 372055265). Street View shows a
# white lower service wall, louvres and darker masonry parapet; the opposite
# side is partly concealed by the adjacent buildings. The OSM-derived boundary
# retains the service lane along the south-east side.
# The free end is clipped in plan, approximating the rounded roof edge.
plan=[(483.5,-29.9),(499.1,-29.9),(499.1,-49.4),(496.8,-51.9),(485.8,-51.9),(483.5,-49.4)]
for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
 face('Service wall '+str(i),list(reversed([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],4.1),(a[0],a[1],4.1)])),white)
 face('Service parapet '+str(i),list(reversed([(a[0],a[1],4.1),(b[0],b[1],4.1),(b[0],b[1],4.65),(a[0],a[1],4.65)])),brick)
# Polygon top uses a fan over a convex outline.
for i in range(len(plan)):
 a,b=plan[i],plan[(i+1)%len(plan)]
 m=Mesh('Service roof '+str(i));m.add([(491.3,-40.9,base+4.65),(a[0],a[1],base+4.65),(b[0],b[1],base+4.65)],[(0,2,1)]);o=m.finish([black],cols['roof']);o.data.uv_layers.new(name='Metric')
# The long pale wall has large horizontally louvred service doors.
for cy in (-46,-42,-38):
 fbox('Service louvre backing '+str(cy),(499.14,cy,1.55),(.12,3.2,2.0),frame)
 for j in range(9):fbox('Fine service louvre '+str((cy,j)),(499.22,cy,.70+j*.20),(.06,3.05,.045),white)
fbox('Service door',(499.14,-33.5,1.2),(.12,1.25,2.4),black)
# Observed roof details: two shallow square openings, two small brick stacks,
# a glazed roof lantern, and the large red painted chevron on the flat deck.
for a,b in ((484,486),(502.4,504.4)):
 for yy in (-23,-21):
  face('Roof opening edge '+str((a,yy)),[(a,yy,33.7),(b,yy,33.7),(b,yy,34.15),(a,yy,34.15)],white,'roof')
 for xx in (a,b):
  face('Roof opening return '+str((xx,a)),[(xx,-23,33.7),(xx,-21,33.7),(xx,-21,34.15),(xx,-23,34.15)],white,'roof')
 face('Roof opening bottom '+str(a),[(a,-23,33.7),(b,-23,33.7),(b,-21,33.7),(a,-21,33.7)],black,'roof')
for x,y in ((496,-16),(501,-25)):
 fbox('Roof stack '+str(x),(x,y,35.15),(.75,.75,1.3),brick,'roof')
 fbox('Roof stack cap '+str(x),(x,y,35.84),(.9,.9,.08),white,'roof')
# The access cover is pitched glazing with visible pale ribs.
fbox('Roof access cap',(489.8,-20.8,35.84),(4.2,2.6,.10),white,'roof')
fbox('Roof access window',(489.8,-19.55,35.2),(2.9,.08,.72),glass,'roof')
for x in (488.55,489.35,490.15,490.95):fbox('Roof access window mullion '+str(x),(x,-19.49,35.2),(.05,.05,.60),frame,'roof')
face('Roof lantern slope one',[(491.7,-19.5,34.6),(495.4,-19.5,34.6),(495.4,-20.35,35.35),(491.7,-20.35,35.35)],glass,'roof')
face('Roof lantern slope two',[(495.4,-21.2,34.6),(491.7,-21.2,34.6),(491.7,-20.35,35.35),(495.4,-20.35,35.35)],glass,'roof')
for x in (491.7,492.45,493.2,493.95,494.7,495.4):
 for yy in (-19.5,-21.2):
  dy=-20.35-yy;dz=.75;length=(dy*dy+dz*dz)**.5
  o=fbox('Roof lantern rib '+str((x,yy)),(x,(yy-20.35)/2,34.975),(.06,length-.12,.06),frame,'roof')
  o.data.transform(Matrix.Translation((x,(yy-20.35)/2,base+34.975)) @ Matrix.Rotation(math.atan2(dz,dy),4,'X') @ Matrix.Translation((-x,-(yy-20.35)/2,-base-34.975)))
fbox('Roof lantern ridge',(493.55,-20.35,35.35),(3.7,.1,.07),frame,'roof')
# Painted chevron consists of two broad red strokes, with no inferred lettering.
face('Roof red stroke one',[(494,-14,34.507),(495,-14,34.507),(499,-19,34.507),(498,-19,34.507)],red,'roof')
face('Roof red stroke two',[(498,-19,34.508),(499,-19,34.508),(501,-14,34.508),(500,-14,34.508)],red,'roof')
