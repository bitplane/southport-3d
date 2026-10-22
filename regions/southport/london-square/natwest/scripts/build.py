"""130 Lord Street: observed street elevations, estimated metric dimensions."""
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
from roof import joined_roof
from components import rectangle, arch_outline, wall, upper_window, arched_window, gable, foliage, parapet, urn, finial, arc, partition_window
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'
C={}
for name in ('architecture','roof','bank-frontage'):
    C[name]=bpy.data.collections.new(name)
    s.collection.children.link(C[name])


def material(name,colour,texture=None,roughness=.82):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*colour,1)
    shader.inputs['Roughness'].default_value=roughness
    if texture:
        node=mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'))
        mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    return mat

stone=material('Warm sandstone ashlar',(.63,.55,.40),'sandstone')
plain=[material('Sandstone relief '+str(i),(.61+i*.016,.53+i*.015,.385+i*.012)) for i in range(3)]
glass=material('Opaque glazing; no inferred interior',(.12,.18,.19),roughness=.28)
white=material('Painted window frames',(.90,.91,.86),roughness=.55)
black=material('Dark door and ironwork',(.035,.043,.039),roughness=.65)
metal=material('Weathered cash machine metal',(.34,.37,.35),roughness=.4)
purple=material('Bank sign purple',(.105,.026,.20),roughness=.5)
red=material('Bank emblem red',(.70,.024,.055),roughness=.5)
slate=material('Green grey slate',(.26,.29,.25),'slate')
lead=material('Lead flashing',(.25,.27,.25))
brick=material('Estimated hidden rear masonry',(.38,.27,.19),'rear-brick')
flat=material('Lower flat roof',(.085,.10,.10))
base=material('Dark grey stone plinth',(.28,.29,.27))
M=[plain[1],glass,white,black,metal]
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')


def finish(mesh,part='architecture',mats=None,transform=None):
    ob=mesh.finish(mats or [stone],C[part])
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric surface')
    for face in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv=(v[axes[0]]/4,v[axes[1]]/1.6)
    if transform is not None:ob.matrix_world=transform
    return ob


def box(name,centre,size,part='architecture',mat=None,transform=None):
    m=Mesh(name);m.box(centre,size)
    return finish(m,part,[mat or plain[1]],transform)


prototypes={}
trim_prototypes={}
def instance(key,factory,transform,part='architecture',mats=None):
    if key not in prototypes:
        mesh=factory()
        if mesh.name.startswith(('Window cross','Window narrow','Window low side')):
            surround,mesh=partition_window(mesh)
            trim_prototypes[key]=finish(surround,part,mats,transform)
        ob=finish(mesh,part,mats,transform)
        prototypes[key]=ob
    else:
        ob=prototypes[key].copy();ob.data=prototypes[key].data
        C[part].objects.link(ob);ob.matrix_world=transform
        if key in trim_prototypes:
            surround=trim_prototypes[key].copy();surround.data=trim_prototypes[key].data
            C[part].objects.link(surround);surround.matrix_world=transform
    return ob


def sign(name,text,width,height,transform,bg=True):
    m=Mesh('Sign '+name)
    m.box((0,0,-.025),(width,height,.05),0)
    # Lettering and logo are source geometry. Photograph pixels are never used.
    label=text_object('Temporary label',text,(width*.05,0,.015),(0,0,1),height*.60,width*.76,font,white,extrude=.009)
    bpy.ops.object.select_all(action='DESELECT');label.select_set(True)
    bpy.context.view_layer.objects.active=label;bpy.ops.object.convert(target='MESH')
    m.add([tuple(label.matrix_world@v.co) for v in label.data.vertices],[tuple(f.vertices) for f in label.data.polygons],1)
    bpy.data.objects.remove(label,do_unlink=True)
    # Three interlocking angular arrows, interpreted NatWest emblem.
    size=height*.32
    for i in range(3):
        theta=math.tau*i/3
        poly=[(-.4,-.2),(.1,-.2),(.1,-.45),(.7,.0),(.1,.45),(.1,.2),(-.4,.2)]
        points=[(-width*.40+size*(x*math.cos(theta)-y*math.sin(theta)),size*(x*math.sin(theta)+y*math.cos(theta)),.03) for x,y in poly]
        m.outline([(x,y) for x,y,z in points],.02,.035,2)
    return finish(m,'bank-frontage',[purple if bg else plain[1],white,red],transform)


xf,xn,yf,yb,z0=(D[k] for k in ('x_max','x_min','front_y','rear_y','base_z'))
front=face_matrix((xf,yf,z0),(0,1,0))
side=face_matrix((xn,yf,z0),(-1,0,0))
facades=[('lord',front,xf-xn,D['front_bays']),('london',side,yf-yb,D['side_bays'])]
for elevation,frame,width,bays in facades:
    front_face=elevation=='lord'
    holes=[]
    for i,u in enumerate(bays):
        if not front_face and i==1:
            for du in (-.83,.83):holes.append(rectangle(u+du-.48,1.9,u+du+.48,4.05))
            # The upper niche is stone and blind, not a missing glass window.
        else:
            radius=1.48 if front_face and i in (0,4) else 1.14
            bottom=.16 if front_face and i in (1,4) else 1.55
            holes.append(arch_outline(u,bottom,3.85,radius))
        if front_face and i in (0,4):
            for du in (-.9,.9):holes.append(rectangle(u+du-.49,6.8,u+du+.49,10.25))
        elif not front_face and i==1:
            pass
        else:holes.append(rectangle(u-1.225,6.8,u+1.225,10.25))
    # The front wall owns the shared corner; side masonry starts at its back.
    finish(wall('Envelope '+elevation,width,12.25,holes,start=0 if front_face else .42),mats=[stone],transform=frame)
    finish(wall('Ashlar '+elevation,width,12.25,holes,True),mats=plain,transform=frame)
    # Continuous courses establish floor levels and retain their shadow profiles.
    for z,h,dep in [(0.25,.50,.12),(5.95,.16,.24),(6.18,.16,.34),(6.38,.12,.24),
                    (11.42,.18,.22),(11.75,.28,.34),(11.96,.12,.46),(12.12,.16,.57),(12.35,.17,.40)]:
        box('Trim '+elevation,(width/2,z,dep/2),(width,h,dep),mat=base if z==.25 else plain[1],transform=frame)
    # End-bay turrets have a deep upper shaft and a suspended corbel below.
    tower_positions=[.25,width-.25]
    tower_positions += [5.55,17.35] if front_face else [5.5,10.7]
    for u in tower_positions:
        m=Mesh('Pier tower '+elevation)
        m.box((0,8.95,.17),(.62,6.9,.50))
        for z in [5.65,6.15,6.38,11.7,12.1,12.4,13.1]:
            m.box((0,z,.19),(.84,.14,.64))
        # Visible rusticated shaft bands, no deep protruding column volume.
        for j in range(18):m.box((0,6.0+j*.39,.445),(.65,.035,.06))
        m.outline([(-.40,5.65),(.40,5.65),(.32,5.15),(.12,4.80),(-.12,4.80),(-.32,5.15)],.10,.47)
        for z,w in [(5.58,.85),(5.4,.72),(5.20,.53),(4.98,.29)]:m.box((0,z,.46),(w,.09,.18))
        m.box((0,12.78,.15),(.82,.64,.74))
        finish(m,transform=frame@Matrix.Translation((u,0,.04)))
        crown=Mesh('Ornament turret crown')
        for j in range(8):
            a=math.tau*j/8
            crown.tube([(.35*math.cos(a),0,.35*math.sin(a)),(.25*math.cos(a),.30,.25*math.sin(a)),(0,.42,0)],.047,sides=6)
        crown.ellipsoid((0,.48,0),(.09,.13,.09),segments=12,rings=8)
        instance('crown',lambda:crown,frame@Matrix.Translation((u,13.18,.15)))
    # Upper Ionic pilasters divide the recessed central bays.
    for u in ([9.775,13.125] if front_face else [17.15,23.1]):
        m=Mesh('Pier Ionic pilaster')
        m.box((0,8.85,.12),(.42,4.55,.30))
        for z,w,h,d in [(6.5,.64,.16,.39),(6.7,.55,.12,.34),(10.98,.53,.10,.36),(11.18,.71,.16,.43),(11.30,.76,.08,.47)]:
            m.box((0,z,d/2),(w,h,d))
        finish(m,transform=frame@Matrix.Translation((u,0,.03)))
        capitals=Mesh('Ornament Ionic capital')
        for signum in (-1,1):
            pts=[]
            for j in range(45):
                t=j/44*math.tau*1.4;r=.13*(1-j/55)
                pts.append((signum*.22+r*math.cos(t),11.15+r*math.sin(t),.35))
            capitals.tube(pts,.025,sides=6)
        finish(capitals,transform=frame@Matrix.Translation((u,0,.03)),mats=[plain[1]])
    for i,u in enumerate(bays):
        if front_face and i in (0,4):
            for du in (-.9,.9):
                instance('narrow-window',lambda:upper_window('Window narrow',.98,3.45,True),frame@Matrix.Translation((u+du,8.525,.04)),mats=M)
        elif not front_face and i==1:
            # Blind shell-headed niche above the paired ground windows.
            m=Mesh('Trim blind niche')
            m.outline(arch_outline(0,7.25,9.7,.68),.01,.04)
            for x in (-.76,.76):m.box((x,8.5,.16),(.16,2.5,.27))
            arc(m,0,9.7,.68,.81,out=.20)
            m.box((0,7.16,.22),(1.85,.20,.65))
            for j in range(11):
                a=math.pi*j/10
                m.tube([(0,9.65,.10),(.65*math.cos(a),9.7+.65*math.sin(a),.16)],.018,sides=5)
            finish(m,transform=frame@Matrix.Translation((u,0,.03)))
            for du in (-.83,.83):
                instance('side-low-window',lambda:upper_window('Window low side',.96,2.15,False),frame@Matrix.Translation((u+du,2.975,.03)),mats=M)
        else:
            instance('upper-window',lambda:upper_window('Window cross',2.45,3.45),frame@Matrix.Translation((u,8.525,.04)),mats=M)
            if front_face:
                box('Trim balcony slab',(u,6.66,.40),(3.15,.18,.94),transform=frame)
                for du in (-1.05,1.05):box('Trim balcony console',(u+du,6.43,.24),(.28,.38,.48),transform=frame)
                rail=Mesh('Balcony rails')
                for zz in (.82,-.03):rail.tube([(-1.48,zz,0),(1.48,zz,0)],.035,sides=6)
                for x in (-1.48,0,1.48):rail.tube([(x,0,0),(x,.84,0)],.028,sides=6)
                for x in (-1.48,1.48):rail.tube([(x,.82,0),(x,.82,-.62)],.035,sides=6)
                instance('balcony-rails',lambda:rail,frame@Matrix.Translation((u,6.75,.80)),mats=[black])
                scroll=parapet('Fine balcony scrolls',2.85)
                scroll.vertices=[(x,y*1.4,z) for x,y,z in scroll.vertices]
                instance('balcony-scroll',lambda:scroll,frame@Matrix.Translation((u,6.75,.80)),mats=[black])
        if not front_face and i==1:continue
        radius=1.48 if front_face and i in (0,4) else 1.14
        bottom=.16 if front_face and i in (1,4) else 1.55
        # Doors and transoms occupy the recess, not a solid wall behind a decal.
        key=f'arch-{radius}-{bottom}'
        instance(key,lambda r=radius,b=bottom:arched_window('Window arch',r,b,3.85,r>1.4),frame@Matrix.Translation((u,0,.04)),mats=M)
        if front_face and i in (1,4):
            box('Door recessed '+str(i),(u,1.71,-.17),(radius*2-.08,3.1,.08),'bank-frontage',black if i==1 else white,frame)
            for du in (-radius*.48,radius*.48):
                for zz in (.65,1.60,2.65):
                    box('Door panel',(u+du,zz,-.105),(radius*.78,.77,.05),'bank-frontage',black if i==1 else glass,frame)
            box('Door transom',(u,3.4,-.10),(radius*2,.13,.15),'bank-frontage',plain[1],frame)
            for du in (-.12,.12):box('Fine door handle',(u+du,1.63,-.045),(.035,.35,.045),'bank-frontage',metal,frame)
            if i==1:
                for step in range(3):box('Trim entrance step',(u,.055+step*.09,.24+(.3-step*.1)),(2.4,.11,.45+(.3-step*.1)),transform=frame)
            else:
                sign('entrance','NatWest',2.55,.65,frame@Matrix.Translation((u,4.15,-.17)))
                # Main entrance hood and square vase-baluster pilasters.
                hood=Mesh('Trim main entrance hood')
                arc(hood,0,3.85,1.75,1.96,out=.47,depth=.44)
                for xx in (-1.74,1.74):
                    hood.outline([(xx-.18,.15),(xx+.18,.15),(xx+.18,1.7),(xx+.30,2.1),(xx+.19,2.65),(xx+.16,3.8),(xx-.16,3.8),(xx-.19,2.65),(xx-.30,2.1),(xx-.18,1.7)],.06,.38)
                    for yy in (.2,1.65,2.65,3.78):hood.box((xx,yy,.28),(.62,.12,.48))
                finish(hood,transform=frame@Matrix.Translation((u,0,0)))
        if front_face and i in (0,2,3):
            sign('window '+str(i),'NatWest',2.1,.48,frame@Matrix.Translation((u,1.93,-.14)))
        if front_face and i in (2,3):
            box('ATM surround',(u,.85,.04),(1.02,1.02,.16),'bank-frontage',plain[1],frame)
            box('ATM metal',(u,.85,.14),(.77,.83,.07),'bank-frontage',metal,frame)
            box('ATM screen',(u,1.04,.18),(.45,.27,.035),'bank-frontage',black,frame)
            box('ATM cash slot',(u,.66,.19),(.47,.055,.04),'bank-frontage',black,frame)
            box('ATM keypad',(u,.80,.19),(.22,.10,.04),'bank-frontage',black,frame)
    # Tall gables have genuine oculus holes, layered ring mouldings and foliage.
    gables=[3.0,width-3.0] if front_face else [8.1]
    for u in gables:
        instance('gable',lambda:gable('Gable Dutch silhouette'),frame@Matrix.Translation((u,0,.08)))
        instance('foliage',lambda:foliage('Ornament oculus foliage'),frame@Matrix.Translation((u,0,.08)),mats=[plain[1]])
        glazing=Mesh('Window oculus')
        glazing.outline([(.65*math.cos(math.tau*j/64),.65*math.sin(math.tau*j/64)) for j in range(64)],-.13,-.10,1)
        arc(glazing,0,0,.61,.66,0,math.tau,out=-.02,depth=.08,material=2)
        for x in (-.20,.20):glazing.box((x,0,-.03),(.045,1.16,.08),2)
        for y in (-.21,.21):glazing.box((0,y,-.03),(1.16,.045,.08),2)
        instance('oculus',lambda:glazing,frame@Matrix.Translation((u,14.35,.08)),mats=M)
        instance('finial',lambda:finial('Ornament heraldic finial'),frame@Matrix.Translation((u,19.08,.17)),mats=[plain[1]])
    spans=[(5.8,17.1)] if front_face else [(.7,5.2),(11.0,width-.65)]
    for a,b in spans:
        count=3 if b-a>7 else 1
        for i in range(count):
            width_part=(b-a)/count;u=a+(i+.5)*width_part
            instance('parapet-'+str(round(width_part,3)),lambda w=width_part:parapet('Parapet open strapwork',w-.24),frame@Matrix.Translation((u,12.57,.15)))
            if i<count-1:
                box('Trim urn pedestal',(a+(i+1)*width_part,12.87,.15),(.38,.7,.45),transform=frame)
                instance('urn',lambda:urn('Ornament parapet urn'),frame@Matrix.Translation((a+(i+1)*width_part,13.22,.15)),mats=[plain[1]])
    sign(elevation+' fascia','NatWest',3.2,.58,frame@Matrix.Translation((11.45 if front_face else 8.1,5.66,.09)),False)
    # Projecting purple corner signs face each approach.
    bracket=frame@Matrix.Translation((width-.55 if front_face else .65,4.75,.65))
    bracket=bracket@Matrix.Rotation(math.pi/2,4,'Y')
    sign(elevation+' projecting','',.72,.72,bracket)

# Rear/party wall is deliberately plain where no reliable street imagery exists.
rear_left=xn+.42;rear_right=xf-.36;party_front=yf-.42
box('Envelope rear',((rear_right+rear_left)/2,yb+.18,z0+6.15),(rear_right-rear_left,.36,12.3),mat=brick)
box('Envelope party',(xf-.18,(party_front+yb)/2,z0+6.15),(.36,party_front-yb,12.3),mat=brick)
R=D['roof_ranges']
xi=xn+R['side_width'];back=yf-R['front_depth']
court_front=back;court_rear=yb+.36;court_left=xi+.1
box('Roof lower flat deck',((court_left+rear_right)/2,(court_front+court_rear)/2,z0+10.25),(rear_right-court_left,court_front-court_rear,.25),'roof',flat)
# The party wall already encloses the right side. Do not duplicate its skin.
box('Roof inner wall',(xi-.05,(court_front+court_rear)/2,z0+11.16),(.30,court_front-court_rear,2.02),'roof',brick)
box('Roof rear parapet',((xf+xn)/2,yb+.12,z0+12.55),(xf-xn,.28,.50),'roof',plain[1])


# One closed roof skin: intersecting sheets must never be exported separately.
joined_roof(xn,xf,yf,yb,z0,lambda mesh:finish(mesh,'roof',[slate]),R)
ze=z0+12.35;zr=z0+R['front_ridge_height'];side_zr=z0+R['side_ridge_height'];yr=yf-R['front_depth']/2
xr=xn+R['side_width']/2
# Complete the inner attic returns between the low deck and the eaves.
box('Roof inner front return',((xi+rear_right)/2,back+.12,z0+11.16),(rear_right-xi,.24,2.02),'roof',brick)
for a,b in [((xr,yr,zr),(xf-2.5,yr,zr)),((xr,yr,side_zr),(xr,yb+3.4,side_zr))]:
    m=Mesh('Roof ridge cap');m.tube([a,b],.10,sides=8);finish(m,'roof',[lead])
# Chimney positions/pots interpreted from aerial plus street images.
for i,(x,y,w,d,h,pots) in enumerate([(20.5,yf-3.8,.95,.85,18.0,1),(29.0,yr,1.25,.8,17.3,2),(xr,yb+1.0,2.25,.9,16.8,4),(13.0,yf-8.0,1.9,.85,17.5,3)]):
    m=Mesh('Chimney stack '+str(i))
    bottom=12.0
    m.box((x,y,z0+(bottom+h)/2),(w,d,h-bottom))
    for z in (h-.8,h-.25,h):m.box((x,y,z0+z),(w+.24,d+.22,.18))
    finish(m,'roof',[stone])
    for j in range(pots):
        m=Mesh('Fine chimney pot')
        m.lathe((x+(j-(pots-1)/2)*.38,y),[(z0+h+.08,.14),(z0+h+.18,.16),(z0+h+.53,.13),(z0+h+.59,.17)],segments=16)
        finish(m,'roof',[plain[1]])
for x,y in [(24,-39),(26,-46)]:box('Roof estimated service upstand',(x,y,z0+10.55),(1.2,1.8,.45),'roof',lead)
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.3
ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(.45,-.55,-.6)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam
cam.data.type='ORTHO';s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/natwest.blend'))
