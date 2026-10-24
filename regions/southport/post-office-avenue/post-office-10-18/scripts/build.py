"""10–18 Post Office Avenue: mapped five-bay terrace, August 2024 exterior."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from components import rect,segment_arch,wall,ring,roof_shapes,roof_shell,profile,height
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('street-facade','roof','rear-and-ends'):
    C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
world=Matrix.Translation((*D['origin_site_xy'],D['base_z']))@Matrix.Rotation(math.radians(D['local_rotation_degrees']),4,'Z')
W=D['width'];DEP=max(D['depth_start'],D['depth_end']);E=D['eaves'];R=D['ridge'];BW=W/5
plan=[tuple(world.inverted()@Vector((x,y,D['base_z'])))[:2] for x,y in D['footprint_site_xy']]
shapes=roof_shapes(W,DEP,E,R)
# Miter every envelope corner on the common inward offset polygon. This makes
# walls share a seam instead of overlapping their exterior end caps.
boundary=[plan[1],plan[2],plan[3],plan[0]]
inset_boundary=[]
for i,p in enumerate(boundary):
    prev=boundary[i-1];nxt=boundary[(i+1)%4]
    d0=Vector((p[0]-prev[0],p[1]-prev[1])).normalized()
    d1=Vector((nxt[0]-p[0],nxt[1]-p[1])).normalized()
    n0=Vector((-d0.y,d0.x));n1=Vector((-d1.y,d1.x))
    offset=(n0+n1)*(.30/(1+n0.dot(n1)))
    inset_boundary.append((p[0]+offset.x,p[1]+offset.y))
def mitres(index):
    a=Vector(boundary[index]);b=Vector(boundary[(index+1)%4]);axis=(b-a).normalized()
    return ((Vector(inset_boundary[index])-a).dot(axis),(Vector(inset_boundary[(index+1)%4])-b).dot(axis))


def material(name,rgb,texture=None,rough=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'))
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    return m


brick=material('Red brick in horizontal courses',(.35,.13,.07),'brick')
slate=material('Grey slate',(.12,.13,.13),'slate');render=material('Rough cream infill',(.71,.69,.61),'render')
black=material('Near-black painted timber',(.025,.029,.027),rough=.55)
cream=material('Ivory sash paint',(.78,.76,.67));yellow=material('Ripley cafe ochre cream',(.61,.52,.29))
glass=material('Muted exterior glass',(.23,.29,.29),rough=.27);stone=material('Sandstone sills',(.46,.43,.36))
red=material('Projecting red brick mouldings',(.32,.115,.06));blue=material('Lynn Thompson blue',(.025,.16,.32))
white=material('Sign lettering',(.86,.85,.78));metal=material('Rainwater cast iron',(.035,.038,.034))


def finish(mesh,part='street-facade',mats=None,frame=None):
    frame=frame or Matrix.Identity(4)
    ob=mesh.finish(mats or [brick],C[part])
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric UV')
    for face in ob.data.polygons:
        n=frame.to_3x3()@face.normal
        for li in face.loop_indices:
            v=frame@ob.data.vertices[ob.data.loops[li].vertex_index].co
            if abs(n.z)>.4:
                # Roof courses run perpendicular to each roof plane's fall.
                uv.data[li].uv=(v.x/1.8,v.y/2.4) if abs(n.y)>=abs(n.x) else (v.y/1.8,v.x/2.4)
            else:uv.data[li].uv=((v.x if abs(n.y)>abs(n.x) else v.y)/2.15,v.z/.75)
    ob.matrix_world=world@frame
    ob["construction_frame"]=[float(v) for row in frame for v in row]
    return ob


def box(name,centre,size,mat=None,part='street-facade',frame=None):
    m=Mesh(name);m.box(centre,size);return finish(m,part,[mat or brick],frame)


def line(name,points,radius,mat,part='street-facade',frame=None,sides=4):
    m=Mesh(name);m.tube(points,radius,sides=sides);return finish(m,part,[mat],frame)


def board(name,text,centre,width,boardmat=black,fontmat=white,frame=None,height=.32,part='street-facade'):
    frame=frame or face_matrix((0,0,0),(0,-1,0))
    # Combined receiving panel and lettering support a shallow baked LoD proxy.
    m=Mesh('Sign '+name);m.box(centre,(width,height,.055))
    font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    ob=text_object('temporary letters',text,(centre[0],centre[1],centre[2]+.04),(0,0,1),min(height*.53,.24),width*.91,font,fontmat,extrude=.003,fit_bounds=False)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
    m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],1)
    bpy.data.objects.remove(ob,do_unlink=True)
    return finish(m,part,[boardmat,fontmat],frame)


front=face_matrix((0,0,0),(0,-1,0))
holes=[];features=[]
for i in range(5):
    start=i*BW
    shop=start+(1.90 if i%2==0 else BW-1.90)
    door=start+(BW-.80 if i%2==0 else .80)
    features.extend([(f'shop {i}',shop,2.72,.28,2.42,.43,'shop',i),
                     (f'door {i}',door,1.02,.02,2.22,.51,'door',i)])
    for j in (-1,1):features.append((f'first sash {i} {j}',start+BW/2+j*.74,1.08,3.90,5.55,.15,'sash',i))
for _,cx,w,bottom,spring,rise,kind,i in features:holes.append(segment_arch(cx,w,bottom,spring,rise))
finish(wall('Envelope front red brick',rect(0,-.06,W,D['upper_floor']),holes,mitres=mitres(0)),frame=front)

# Upper frame openings remain true openings; plaster does not cover the glazing.
upperholes=[]
for i in range(5):upperholes.append(rect(i*BW+.90,6.86,(i+1)*BW-.90,8.77))
top=profile(shapes,(0,0),(W,0))
upperpoly=[(0,D['upper_floor']),(W,D['upper_floor'])]+[(t*W,h) for t,h in reversed(top)]
finish(wall('Envelope front upper infill',upperpoly,upperholes,mitres=mitres(0)),mats=[render],frame=front)

# Shop windows and doors are recessed into the pierced brick wall, not pasted on.
for name,cx,w,bottom,spring,rise,kind,i in features:
    paint=yellow if i==2 else (cream if i==3 or kind=='sash' else black)
    inside=segment_arch(cx,w-.13,bottom+.065,spring-.045,max(.04,rise-.02))
    outside=segment_arch(cx,w,bottom,spring,rise)
    finish(ring('Frame '+name,inside,outside),mats=[paint],frame=front)
    m=Mesh('Window '+name);m.outline(inside,-.19,-.16);finish(m,mats=[glass],frame=front)
    # The brick arch is a shallow continuous band; radial joints are Detail-only.
    inner=segment_arch(cx,w,bottom,spring,rise)
    arch=inner[2:]
    outer=segment_arch(cx,w+.30,bottom,spring+.13,rise+.03)[2:]
    m=Mesh('Trim brick arch '+name)
    n=len(arch)
    for j in range(n-1):m.outline([arch[j],outer[j],outer[j+1],arch[j+1]],.001,.055)
    finish(m,mats=[red],frame=front)
    if kind=='shop':
        iw=w-.13;ir=rise-.02;radius=(iw*iw/4+ir*ir)/(2*ir)
        for x in (cx-w/6,cx+w/6):
            top=spring-.045+ir-radius+math.sqrt(radius*radius-(x-cx)**2)-.015
            box('Frame shop upper light',(x,(2.255+top)/2,-.11),(.05,top-2.255,.07),paint,frame=front)
        box('Frame shop transom',(cx,2.22,-.105),(w-.13,.07,.08),paint,frame=front)
        box('Frame shop middle',(cx,1.27,-.105),(.06,1.83,.08),paint,frame=front)
        box('Trim shop sill',(cx,.23,.035),(w+.16,.13,.34),black,frame=front)
    elif kind=='door':
        box('Frame door transom',(cx,2.17,-.105),(w-.13,.075,.08),paint,frame=front)
        box('Frame door bottom panel',(cx,.48,-.125),(w-.14,.80,.07),paint,frame=front)
        box('Frame door threshold',(cx,.025,.0),(w,.05,.32),stone,frame=front)
        line('Fine door handle',[(cx+w*.27,.98,-.04),(cx+w*.27,1.30,-.04)],.018,metal,frame=front,sides=6)
        board('number '+str(10+2*i),str(10+2*i),(cx,2.30,-.09),.32,paint,white,front,.16)
    else:
        box('Frame sash meeting rail',(cx,4.78,-.105),(w-.13,.055,.075),paint,frame=front)
        box('Trim first floor sill',(cx,3.84,.025),(w+.19,.13,.30),stone,frame=front)

# Upper-floor timber grid, projecting window band and gable fan braces.
for i in range(5):
    a=i*BW;b=(i+1)*BW;centre=(a+b)/2
    box('Trim upper sill',(centre,6.64,.055),(BW,.12,.19),red,frame=front)
    box('Frame timber rail',(centre,6.78,.035),(BW,.13,.13),black,frame=front)
    box('Frame timber head',(centre,8.87,.04),(BW,.14,.15),black,frame=front)
    for x in (a+.06,a+.52,b-.52,b-.06):
        box('Frame upper timber upright',(x,7.82,.04),(.10,1.97,.15),black,frame=front)
    for x0,x1 in ((a+.11,a+.85),(b-.85,b-.11)):
        box('Frame infill horizontal',((x0+x1)/2,7.75,.04),(x1-x0,.09,.15),black,frame=front)
    opening=(a+.90,b-.90);ow=opening[1]-opening[0]
    for j in range(4):
        l=opening[0]+j*ow/4;r=opening[0]+(j+1)*ow/4
        box('Window upper leaded glass',((l+r)/2,7.815,-.17),(r-l-.055,1.84,.04),glass,frame=front)
        for x in (l+.025,r-.025):box('Frame upper glazing',(x,7.815,-.08),(.05,1.91,.12),black if i!=2 else cream,frame=front)
        for z in (6.8875,8.7425):box('Frame upper glazing rail',((l+r)/2,z,-.08),(r-l-.10,.055,.12),black if i!=2 else cream,frame=front)
        box('Frame upper transom',((l+r)/2,8.31,-.075),(r-l-.1,.045,.12),black if i!=2 else cream,frame=front)
        # Fine leadwork stays modest; District omits it rather than decimating.
        for x in [l+.16+k*.17 for k in range(max(0,int((r-l-.26)/.17)))]:
            box('Fine lead came',(x,7.815,-.135),(.010,1.80,.012),black,frame=front)
        for z in [6.99+k*.18 for k in range(10)]:
            box('Fine lead came',((l+r)/2,z,-.135),(r-l-.10,.010,.012),black,frame=front)
    if i%2==0:
        half=2.30;peak=height(shapes,centre,0)-.12
        line('Frame gable verge',[(centre-half,9.02,.065),(centre,peak,.065),(centre+half,9.02,.065)],.09,black,frame=front)
        box('Frame gable tie',(centre,9.02,.065),(half*2,.15,.19),black,frame=front)
        for t in (-.70,-.36,0,.36,.70):
            x=centre+t*half;z=peak-abs(t)*(peak-9.02)
            line('Frame gable fan brace',[(centre,9.08,.065),(x,z-.06,.065)],.055,black,frame=front)
    for x in (a+.20,b-.20):
        line('Trim eaves bracket',[(x,8.66,.04),(x,8.98,.27),(x,9.04,.04)],.045,black,frame=front)

# Frontage names follow one observed date; no temporary poster facsimiles.
board('Lynn Thompson','Lynn Thompson LETTINGS',(BW,3.38,.10),BW*1.62,blue,white,front,.37)
board('Ripley','RIPLEYS CAFE',(BW*2.5,3.34,.09),2.10,white,black,front,.42)
board('AromDee','AROMDEE THAI MASSAGE',(BW*4-1.90,.88,-.09),2.35,black,yellow,front,.26)
board('VC Law','VCLAW',(BW*4.5,3.35,.09),2.70,white,black,front,.38)
board('VC Law upper board','VCLAW',(W-.65,5.0,.09),.95,white,black,front,1.45)
board('Post Office Avenue street plate','POST OFFICE AVENUE',(W-1.20,3.62,.10),1.95,blue,white,front,.18)
box('Trim painted first floor sill band',(BW,3.84,.025),(BW*2,.07,.08),cream,frame=front)
for i in (0,2,4):
    centre=(i+.5)*BW
    for z,width,depth in ((6.30,3.80,.08),(6.40,4.0,.11),(6.51,4.15,.14)):
        box('Trim stepped upper bay corbel',(centre,z,depth/2),(width,.10,depth),red,frame=front)
for i in range(6):
    x=min(W-.04,max(.04,i*BW))
    line('Fitting rainwater downpipe',[(x,.10,.11),(x,8.98,.11)],.035,metal,frame=front,sides=8)

# The other three walls follow the mapped skewed footprint. The rear is
# deliberately restrained: no unobserved rows of windows are invented.
for label,index in [('north',3),('rear',2),('Anchor',1)]:
    a=boundary[index];b=boundary[(index+1)%4]
    length=math.dist(a,b);dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length
    frame=face_matrix((*a,0),(dy,-dx,0))
    frame=Matrix(((dx,0,dy,a[0]),(dy,0,-dx,a[1]),(0,1,0,0),(0,0,0,1)))
    wallholes=[]
    if label=='Anchor':
        # Corner glazing is spaced along the full mapped Anchor return.
        for d,w,bot,spring,rise in [(2.0,2.30,.28,2.42,.43),(5.15,1.0,.65,2.28,.45),
                                   (2.9,1.03,3.90,5.55,.15),(5.0,1.03,3.90,5.55,.15)]:
            wallholes.append(segment_arch(d,w,bot,spring,rise))
            inside=segment_arch(d,w-.13,bot+.065,spring-.045,max(.04,rise-.02))
            finish(ring('Frame Anchor opening',inside,wallholes[-1]),'rear-and-ends',[black],frame)
            m=Mesh('Window Anchor opening');m.outline(inside,-.19,-.16);finish(m,'rear-and-ends',[glass],frame)
            box('Frame Anchor crossbar',(d,(bot+spring)/2,-.10),(w-.13,.055,.08),black,'rear-and-ends',frame)
            box('Trim Anchor sill',(d,bot-.05,.025),(w+.18,.13,.30),stone,'rear-and-ends',frame)
        for d in (1.65,4.15,6.65):wallholes.append(rect(d-.50,6.88,d+.50,8.76))
    walltop=profile(shapes,a,b)
    outline=[(0,-.06),(length,-.06)]+[(t*length,z) for t,z in reversed(walltop)]
    finish(wall('Envelope '+label+' wall',outline,wallholes,mitres=mitres(index)),'rear-and-ends',[brick],frame)
    if label=='Anchor':
        # Use plaster patches only between the real openings, with a tiny
        # exposed offset. Frame/paint is carried to the photographed rear corner of the return.
        upper=wall('Trim Anchor timber infill',rect(0,6.60,length,8.90),wallholes[4:],.035)
        finish(upper,'rear-and-ends',[render],frame@Matrix.Translation((0,0,.035)))
        for d in (1.65,4.15,6.65):
            box('Window Anchor upper',(d,7.82,-.17),(.98,1.86,.04),glass,'rear-and-ends',frame)
            for offset in (-.48,.48):box('Frame Anchor upper',(d+offset,7.82,.04),(.06,1.92,.13),black,'rear-and-ends',frame)
            for z in (6.91,8.73):box('Frame Anchor upper rail',(d,z,.04),(.90,.06,.13),black,'rear-and-ends',frame)
        for d in (.05,.85,2.45,3.35,4.95,5.85,7.45,length-.05):
            box('Frame Anchor timber upright',(d,7.78,.075),(.10,2.22,.15),black,'rear-and-ends',frame)
        for z in (6.67,8.85):box('Frame Anchor timber rail',(length/2,z,.075),(length,.13,.15),black,'rear-and-ends',frame)
        board('Anchor VC Law','VCLAW',(2.55,3.37,.10),2.1,white,black,frame,.35,'rear-and-ends')

roof=finish(roof_shell(shapes),'roof',[slate])
# Low ridge tiles and eaves retain the observed silhouette at all levels.
line('Roof main ridge',[(1.8,DEP/2,R+.025),(W-1.45,DEP/2,R+.025)],.055,red,'roof',sides=6)
for c in (W*.1,W*.5,W*.9):
    line('Roof gable ridge',[(c,-.38,R+.025),(c,DEP/2,R+.025)],.055,red,'roof',sides=6)
line('Roof front gutter',[(0,-.25,E),(W,-.25,E)],.065,metal,'roof',sides=6)
# Aerial and corner photographs show stacks along the main ridge. Pot counts
# are kept conservative where obscured, rather than filling every cap with pots.
for u in (BW*.8,BW*2.35,BW*3.8):
    v=DEP*.52;bottom=height(shapes,u,v)-.10
    box('Roof chimney stack',(u,v,(bottom+R+1.20)/2),(.58,.88,R+1.20-bottom),brick,'roof')
    box('Roof chimney cap',(u,v,R+1.22),(.72,1.02,.14),stone,'roof')
    for vv in (v-.23,v+.23):
        m=Mesh('Roof chimney pot');m.lathe((u,vv),[(R+1.29,.10),(R+1.65,.10),(R+1.69,.13),(R+1.77,.13),(R+1.77,.075),(R+1.33,.075)],segments=12)
        finish(m,'roof',[red])

for image in bpy.data.images:
    if image.source=='FILE':image.pack()
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(.55,-.45,-.6)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/post-office-10-18.blend'))
