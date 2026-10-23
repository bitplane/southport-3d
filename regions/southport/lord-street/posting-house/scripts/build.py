"""Former Southport Head Post Office; measured footprint, estimated elevations."""
import json
import math
import os
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh, face_matrix, text_object
from components import rect, opening, wall, ellipse_band, sash, surround, cross_window
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('historic-front','roof','rear-range','shopfronts','courtyard-ground'):
    C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])


def material(name,colour,texture=None,roughness=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=roughness
    if texture:
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'))
        m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    return m


stone=material('Pale weathered sandstone',(.552,.479,.337),'stone')
plain=material('Sandstone mouldings',(.552,.479,.337))
brick=material('Red brick',(.319,.074,.036),'brick')
slate=material('Blue grey slate',(.107,.130,.141),'slate')
white=material('White painted timber',(.85,.86,.81),roughness=.52)
glass=material('Opaque blue grey glazing',(.085,.135,.16),roughness=.30)
black=material('Dark door and iron fittings',(.025,.03,.028))
lead=material('Lead weathering',(.23,.25,.26))
flat=material('Flat roof felt',(.065,.075,.08))
cream=material('Rear render',(.66,.61,.50))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')


def finish(m,part='historic-front',mats=None,frame=None):
    ob=m.finish(mats or [plain],C[part]);bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric UV')
    for f in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(f.normal[i]))[:2])
        for li in f.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            period=1.05 if ob.data.materials[0].name=='Red brick' else 3.2
            uv.data[li].uv=(v[axes[0]]/period,v[axes[1]]/1.28)
    if frame is not None:ob.matrix_world=frame
    return ob


def box(name,centre,size,part='historic-front',mat=None,frame=None):
    m=Mesh(name);m.box(centre,size);return finish(m,part,[mat or plain],frame)


prototypes={}
def instance(key,m,frame,part='historic-front',mats=None):
    if key not in prototypes:prototypes[key]=finish(m,part,mats,frame);return prototypes[key]
    ob=prototypes[key].copy();ob.data=prototypes[key].data;C[part].objects.link(ob);ob.matrix_world=frame;return ob


def sign(name,body,width,height,frame,background=black,ink=white):
    m=Mesh('Sign '+name);m.box((0,0,-.025),(width,height,.05),0)
    ob=text_object('lettering',body,(0,0,.012),(0,0,1),height*.63,width*.90,font,ink,extrude=.006)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
    m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons],1);bpy.data.objects.remove(ob,do_unlink=True)
    return finish(m,'shopfronts',[background,ink],frame)


# One gently angled frame follows the mapped frontage, rather than forcing an
# axis-aligned box into the neighbouring street and bank.
x0,y0=D['front_east'];x1,y1=D['front_west'];z0=D['base_z']
width=math.hypot(x1-x0,y1-y0);ux=(x1-x0)/width;uy=(y1-y0)/width
front=Matrix(((ux,0,uy,x0),(uy,0,-ux,y0),(0,1,0,z0),(0,0,0,1)))
# The frontage runs east to west in face coordinates: outward normal is north.
# Helpers return global positions for roof/rear construction.
def site(u,depth,z):return tuple(front@Vector((u,z,-depth)))

edges=D['historic_bay_edges'];start=D['historic_start'];eave=D['eave_z'];ridge=D['ridge_z']
bays=[(a+b)/2 for a,b in zip(edges,edges[1:])]
# Individual facade planes carry real openings through the masonry. Projecting
# second/fourth bays move wall and glazing together, preserving window recesses.
for i,(a,b,c) in enumerate(zip(edges,edges[1:],bays)):
    projection=.42 if i in (1,3) else 0
    frame=front@Matrix.Translation((0,0,projection))
    holes=[]
    if i in (1,2,3):holes.append(opening(c,1.12,3.75,(b-a)/2-.57,1.25))
    else:holes.append(rect(c-1.05,.08,c+1.05,4.8))
    for level,h in [(8.0,3.65),(12.95,3.75)]:
        for u in ([c-.95,c+.95] if i in (1,3) else [c]):holes.append(rect(u-.63,level-h/2,u+.63,level+h/2))
    finish(wall('Envelope front bay '+str(i),rect(a,0,b,eave),holes),mats=[brick],frame=frame)
    finish(wall('Envelope ground ashlar '+str(i),rect(a,0,b,5.65),holes,back=.001,front=.055),mats=[stone],frame=frame)
    for level,h in [(8.0,3.65),(12.95,3.75)]:
        for u in ([c-.95,c+.95] if i in (1,3) else [c]):
            t=frame@Matrix.Translation((u,level,0))
            instance('sash-'+str(h),cross_window('Window upper sash',1.26,h),t,mats=[glass,white])
            instance('surround-'+str(h),surround('Trim upper window',1.26,h),t)
    # Ground arches remain geometry at every viewing scale.
    if i in (1,2,3):
        rx=(b-a)/2-.57;spring=3.75;ry=1.25
        m=Mesh('Arch ground arcade '+str(i));ellipse_band(m,c,spring,rx,ry,.25,.26)
        ellipse_band(m,c,spring,rx+.29,ry+.29,.12,.32)
        for side in (-1,1):
            u=c+side*(rx+.13);m.box((u,2.15,.12),(.26,3.20,.32));m.box((u,spring,.22),(.5,.16,.45))
        m.outline([(c-.14,4.82),(c+.14,4.82),(c+.28,5.48),(c-.28,5.48)],.08,.40)
        finish(m,frame=frame)
        m=Mesh('Glazing ground arch '+str(i));m.outline(opening(c,1.12,spring,rx,ry),-.24,-.20,0)
        for x in [c-rx+.06,c,c+rx-.06]:m.box((x,2.44,-.08),(.11,2.65,.16),1)
        for h in [1.15,3.72]:m.box((c,h,-.08),(2*rx,.10,.16),1)
        ellipse_band(m,c,spring,rx-.08,ry-.08,.08,-.025,mat=1)
        for k in range(-2,3):
            x=rx*k/3;top=spring+ry*math.sqrt(1-(x/rx)**2)
            m.box((c+x,(spring+top)/2,-.08),(.045,top-spring,.10),1)
        finish(m,'shopfronts',[glass,white],frame)
    else:
        m=Mesh('Door portal '+str(i))
        for side in (-1,1):
            u=c+side*1.18;m.box((u,2.4,.16),(.26,4.8,.40))
            m.box((u,.22,.22),(.42,.4,.54));m.box((u,4.52,.22),(.43,.18,.51))
        m.box((c,4.82,.23),(2.75,.22,.55));m.box((c,4.99,.18),(2.93,.12,.58))
        finish(m,frame=frame)
        m=Mesh('Door recessed entrance '+str(i));m.box((c,1.62,-.28),(1.98,3.14,.12),0)
        for side in (-1,1):
            u=c+side*.49;m.box((u,2.1,-.205),(.77,1.65,.025),1)
            m.box((u,.65,-.20),(.75,.65,.035),0)
        for u in [c-.98,c,c+.98]:m.box((u,1.6,-.16),(.10,3.2,.14),0)
        m.box((c,4,-.23),(2.05,1.45,.05),1)
        for u in [c-1,c-.34,c+.34,c+1]:m.box((u,4,-.12),(.06,1.45,.13),2)
        m.box((c,3.3,-.10),(2.1,.11,.16),2)
        finish(m,'shopfronts',[black,glass,white],frame)
        box('Door threshold '+str(i),(c,.06,-.09),(2.1,.12,.62),'shopfronts',plain,frame)
    # Major moulded storey bands: not paper-thin overlapping skins.
    for z,h,d in [(5.63,.20,.25),(5.85,.12,.34),(9.15,.13,.14),(10.02,.18,.18),(13.05,.13,.18),(14.18,.18,.20),(15.51,.18,.29),(15.76,.26,.46),(16.00,.16,.61),(16.20,.15,.40)]:
        box('Trim storey band',(c,z,d/2),(b-a,h,d),frame=frame)
    # Quoins and enrichment placed on the solid pier centres, away from glass.
    for u in (a+.16,b-.16):
        for j in range(16):
            z=6.0+j*.58
            box('Detail quoin joint',(u,z,.07),(.29,.045,.15),frame=frame)
    if i in (1,3):
        for u in (a+.04,b-.04):
            m=Mesh('Turret tourelle')
            m.outline([(u-.33,5.65),(u+.33,5.65),(u+.25,5.25),(u,4.85),(u-.25,5.25)],.10,.51)
            # Faceted octagonal shafts rise continuously, not freestanding posts.
            q=Mesh('column');q.lathe((0,0),[(5.65,.31),(6.0,.28),(16.75,.28),(17.0,.35),(17.28,.29)],segments=12)
            q.transform(Matrix(((1,0,0,u),(0,0,1,0),(0,-1,0,.21),(0,0,0,1))))
            m.add(q.vertices,q.faces)
            finish(m,frame=frame)
            for z in [6.1,10.05,14.2,16.23,16.84]:box('Trim tourelle ring',(u,z,.24),(.74,.13,.74),frame=frame)

# Tall stone cross windows, curved head mouldings and blind spandrel arcades.
for i,(a,b,c) in enumerate(zip(edges,edges[1:],bays)):
    frame=front@Matrix.Translation((0,0,.42 if i in (1,3) else 0))
    for level,h in [(8.0,3.65),(12.95,3.75)]:
        for u in ([c-.95,c+.95] if i in (1,3) else [c]):
            box('Trim stone window mullion',(u,level,-.015),(.105,h,.26),frame=frame)
            m=Mesh('Trim curved window head')
            m.tube([(u-.87,level+h/2+.14,.20),(u-.40,level+h/2+.30,.20),(u,level+h/2+.35,.20),(u+.40,level+h/2+.30,.20),(u+.87,level+h/2+.14,.20)],.065,sides=8)
            finish(m,frame=frame)
    if i in (1,3):
        m=Mesh('Detail blind spandrel arcade')
        for j in range(9):
            u=a+.35+j*(b-a-.7)/8
            ellipse_band(m,u,10.55,.18,.20,.055,.18,steps=12)
            for x in [u-.20,u+.20]:m.box((x,10.37,.1),(.06,.36,.20))
        finish(m,frame=frame)
    if i in (1,2,3):
        m=Mesh('Ornament arch egg moulding');rx=(b-a)/2-.57
        for j in range(31):
            t=math.pi*(j+.5)/31
            m.ellipsoid((c+(rx+.36)*math.cos(t),3.75+1.60*math.sin(t),.36),(.065,.11,.06),segments=8,rings=5)
        finish(m,frame=frame)

# The two principal gables have a round-headed attic window and curved pediment.
for i in (1,3):
    a,b,c=edges[i],edges[i+1],bays[i]
    frame=front@Matrix.Translation((c,0,.42));w=(b-a)/2-.12
    poly=[(-w,16.18),(w,16.18),(w-.15,17.0),(1.7,18.05),(1.65,19.75),(1.15,20.65),(-1.15,20.65),(-1.65,19.75),(-1.7,18.05),(-w+.15,17.0)]
    hole=opening(0,16.7,18.3,.82,.82)
    finish(wall('Gable main '+str(i),poly,[hole],-.48,.12),frame=frame)
    m=Mesh('Trim attic arch');ellipse_band(m,0,18.3,.84,.84,.19,.32)
    for u in [-.96,.96]:m.box((u,17.5,.20),(.24,1.7,.35));m.box((u,18.3,.23),(.43,.13,.40))
    m.box((0,16.6,.24),(2.35,.20,.50));m.outline([(-.12,18.93),(.12,18.93),(.23,19.43),(-.23,19.43)],.10,.42)
    for side in [-1,1]:
        u=side*1.42;m.box((u,18.85,.22),(.3,2.15,.35));m.box((u,17.85,.26),(.5,.14,.48));m.box((u,19.82,.26),(.53,.14,.51))
        m.tube([(side*w,16.3,.25),(side*(w-.17),16.95,.25),(side*1.65,18.05,.25)],.12,sides=8)
    m.outline([(1.55*math.cos(math.pi*j/32),20.12+1.2*math.sin(math.pi*j/32)) for j in range(33)],-.10,.12)
    m.ellipsoid((0,21.45,.13),(.16,.23,.14),segments=12,rings=8)
    m.box((0,19.95,.27),(3.6,.17,.55));m.box((0,20.12,.28),(3.85,.13,.58))
    ellipse_band(m,0,20.12,1.55,1.2,.16,.37)
    finish(m,frame=frame)
    instance('attic-arched',sash('Glazing attic arch',1.64,2.42,True),frame@Matrix.Translation((0,17.91,0)),mats=[glass,white])
    # Interpreted carved festoons within observed stone spandrel fields.
    m=Mesh('Ornament gable wreath')
    for side in (-1,1):
        for j in range(12):
            t=j/11;x=side*(1.04+.3*math.sin(t*math.pi));y=18.65+t*.84
            m.ellipsoid((x,y,.39),(.10,.16,.07),segments=12,rings=6)
    m.ellipsoid((0,20.62,.20),(.42,.47,.13),segments=20,rings=12)
    finish(m,frame=frame)

# Front cornice dentils are a close-range layer; the main cornice is retained.
for j in range(int((width-start)/.36)):
    box('Detail cornice dentil',(start+.18+j*.36,15.70,.38),(.14,.20,.24),frame=front)

# Wall returns and rear are separate planes, not a filled footprint solid.
depth=D['main_depth']
for u,name,normal in [(start,'east return',(1,0,0)),(width,'bank alley return',(-1,0,0))]:
    # Frame columns run along depth, upward and outward from each end.
    p=Vector(site(u,0,0));out=Vector((front[0][0],front[1][0],0))*(1 if u==width else -1)
    f=face_matrix(p,out)
    # Normals determine local direction: use signed depth coordinate accordingly.
    signum=1 if u==width else -1
    outline=rect(min(0,signum*depth),0,max(0,signum*depth),eave)
    finish(wall('Envelope '+name,outline,[]),mats=[brick],frame=f)
    for z in [5.8,10.05,14.18]:box('Trim return band',(signum*depth/2,z,.10),(depth,.17,.20),frame=f)

# The bank-alley end is gabled, as shown in oblique photography. The
# rear has three cross-gables, explicitly visible in the 2024 heritage report.
from roof import make_roof
roof=make_roof(start,width,depth,eave,ridge,finish,front,slate)
for u in (start,width):
    f=front@Matrix.Translation((u,0,0))@Matrix.Rotation(math.pi/2,4,'Y')
    m=Mesh('Envelope roof gable end')
    m.outline([(0,eave),(depth,eave),(depth/2,ridge)],-.10,.10)
    finish(m,'historic-front',[brick],f)
m=Mesh('Roof ridge cap');m.tube([site(start,depth/2,ridge+.045),site(width,depth/2,ridge+.045)],.10,sides=8);finish(m,'roof',[brick])

# Three steep hipped dormers occupy the recessed first, centre and fifth bays.
for i in (0,2,4):
    c=bays[i];f=front@Matrix.Translation((c,0,-1.1));z=eave+(ridge-eave)*1.1/(depth/2)+.08
    hole=rect(-.69,z+.12,.69,z+1.75)
    finish(wall('Dormer cheek front '+str(i),rect(-.88,z-.12,.88,z+1.92),[hole],-.24,.04),'roof',[plain],f)
    instance('dormer',sash('Glazing dormer sash',1.38,1.63),f@Matrix.Translation((0,z+.935,0)),'roof',[glass,white])
    # Cut the main slope behind the glazing; it formerly obscured the lower
    # panes. Solid cheeks close the opening back into the existing roof.
    cutter_mesh=Mesh('Temporary dormer opening')
    cutter_mesh.box((c,z+.96,-2.55),(1.40,1.92,2.9))
    cutter=cutter_mesh.finish([]);cutter.matrix_world=front
    bpy.context.view_layer.objects.active=roof
    mod=roof.modifiers.new('Dormer aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    for side in [-1,1]:
        box('Dormer closed side cheek',(side*.79,z+.96,-1.45),(.18,1.92,2.9),'roof',plain,f)
    box('Dormer sill',(0,z+.09,-.04),(1.82,.14,.42),'roof',plain,f)
    m=Mesh('Roof dormer hip '+str(i))
    m.add([(-1.03,z+1.91,.18),(1.03,z+1.91,.18),(1.03,z+1.91,-2.9),(-1.03,z+1.91,-2.9),(0,z+3.6,-1.1)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)])
    finish(m,'roof',[slate],f)
    m=Mesh('Ornament dormer finial');m.tube([(0,z+3.52,-1.1),(0,z+4.18,-1.1)],.045,sides=10);m.ellipsoid((0,z+3.93,-1.1),(.12,.15,.12),segments=12,rings=8)
    finish(m,'roof',[lead],f)

# Six ridge/party stacks are evidenced in the 2024 condition report; locations
# are calibrated from aerial/oblique photographs. They extend below roof skins.
for j,(u,dep,w,d,h) in enumerate([(start+.6,8.7,.72,1.10,23.3),(start+2.4,8.7,.72,1.10,23.4),(width-2.0,8.7,.76,1.05,23.7),(width-.5,8.7,.76,1.05,23.1),(start+7,14.8,1.10,.72,22.2),(width-7,14.8,1.10,.72,22.2)]):
    f=front@Matrix.Translation((u,0,-dep));box('Chimney stack '+str(j),(0,(15+h)/2,0),(w,h-15,d),'roof',brick,f)
    for z in [h-.30,h]:box('Chimney coping',(0,z,0),(w+.22,.16,d+.22),'roof',plain,f)
    for off in [-.21,.21]:
        m=Mesh('Detail chimney pot');m.lathe((0,0),[(0,.115),(.1,.145),(.53,.12),(.6,.16)],segments=14)
        m.transform(Matrix(((1,0,0,off),(0,0,1,h+.10),(0,-1,0,0),(0,0,0,1))))
        finish(m,'roof',[brick],f)

# Original stone lettering survives changes of occupier. No current service
# claim or unreadable modern window notices are invented.
for i in (1,3):
    for offset,word in [(-1.05,'POST'),(1.05,'OFFICE')]:
        sign('carved Post Office '+str(i)+word,word,1.55,.23,front@Matrix.Translation((bays[i]+offset,5.38,.50)),plain,black)

from historic_rear import build_historic_rear
build_historic_rear(globals())

# Modern redevelopment and raised courtyard follow the block evidence review.
from rear import build_rear
build_rear(globals())
from courtyard import build_courtyard
build_courtyard(globals())

from frontage132 import build_132
build_132(globals())


# Fit the redevelopment to the mapped taper and independently skew rear wall.
# Historic frontage/roof remain in their original frame.
def registered(p):
    q=front.inverted()@p
    t=max(0,(-q.z-depth)/(D['rear_depth']-depth))
    u=q.x/width
    original=front@Vector((q.x,q.y,-D['rear_depth']))
    east,west=D['rear_boundary']
    target=Vector(((1-u)*east[0]+u*west[0],(1-u)*east[1]+u*west[1],p.z))
    return p+Vector(((target.x-original.x)*t,(target.y-original.y)*t,0))
for ob in [o for col in C.values() for o in col.objects if o.type=='MESH']:
    old=ob.matrix_world.copy()
    if all((front.inverted()@(old@v.co)).z>=-depth-.01 for v in ob.data.vertices):continue
    origin=registered(old.translation)
    # Keep a true orthogonal local facade frame for baked receiving panels.
    u=(registered(old@Vector((1,0,0)))-origin).normalized()
    v=registered(old@Vector((0,1,0)))-origin;v=(v-u*v.dot(u)).normalized()
    n=u.cross(v).normalized()
    new=Matrix(((u.x,v.x,n.x,origin.x),(u.y,v.y,n.y,origin.y),(u.z,v.z,n.z,origin.z),(0,0,0,1)))
    ob.data=ob.data.copy();inv=new.inverted()
    for v in ob.data.vertices:v.co=inv@registered(old@v.co)
    ob.matrix_world=new;ob.data.update()
for im in bpy.data.images:
    if im.source=='FILE':im.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.3
ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(.45,-.55,-.6)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/posting-house.blend'))
