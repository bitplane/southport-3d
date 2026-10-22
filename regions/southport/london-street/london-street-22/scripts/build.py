"""22 London Street: stone and glazed Art Deco exterior, metric source."""
import json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh,face_matrix,text_object
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ['architecture','roof','shopfront','rear']:
 C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,colour,texture=None,roughness=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=roughness
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
brick=material('Warm brick',(.45,.20,.13),'brick')
slate=material('Dark roof',(.06,.075,.08),'slate')
coping=material('Dark coping',(.11,.125,.125))
white=material('Pale aluminium',(.70,.72,.70));glass=material('Exterior glass',(.10,.15,.17),roughness=.25)
black=material('Recess shadow',(.025,.028,.03));blue=material('Skipton blue',(.015,.12,.28));red=material('Red painted metal',(.55,.018,.025))
granite=material('Grey granite',(.45,.46,.43),'granite');felt=material('Pale weathered felt',(.35,.37,.35));wood=material('Service door timber',(.30,.16,.075));metal=material('Galvanized metal',(.43,.46,.45))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
base=D['base_z'];xf=D['front_x'];xr=D['rear_x'];yn=D['north_y'];ys=D['south_y'];width=yn-ys;depth=xf-xr
front=face_matrix((xf,ys,base),(1,0,0))
side=face_matrix((xf,yn,base),(0,1,0))
rear=face_matrix((xr,yn,base),(-1,0,0))
def finish(mesh, part='architecture', materials=None, transform=None, roof_uv=False):
    obj = mesh.finish(materials or [brick], C[part])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    uv = obj.data.uv_layers.new(name='Authored metric repeat')
    for face in obj.data.polygons:
        axes = sorted(sorted(range(3), key=lambda i: abs(face.normal[i]))[:2])
        mat = obj.data.materials[face.material_index]
        for loop in face.loop_indices:
            v = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            if roof_uv:
                # Courses run parallel to their own eaves on each hip/slope.
                if abs(face.normal.y) > abs(face.normal.x):
                    u, h = v.x / 2.4, v.y / 2.2
                else:
                    u, h = v.y / 2.4, v.x / 2.2
            else:
                scale = (1.8, .6) if mat == brick else (2.4, 2.2) if mat == slate else (1, 1)
                u, h = v[axes[0]] / scale[0], v[axes[1]] / scale[1]
            uv.data[loop].uv = (u, h)
    if transform is not None:
        obj.matrix_world = transform
    return obj


def box(name, centre, size, mat=brick, part='architecture', transform=None):
    mesh = Mesh(name)
    mesh.box(centre, size)
    return finish(mesh, part, [mat], transform)


def elevation_box(name, u, h, w, height, depth=.25, out=-.125,
                  mat=brick, part='architecture', frame=front):
    return box(name, (u, h, out), (w, height, depth), mat, part, frame)


def wall_with_openings(name, frame, length, height, openings, part='architecture', mat=brick):
    """Split the wall around actual apertures; no panels hidden inside solid walls."""
    openings=[(max(0,a),min(length,b),max(0,c),min(height,d))
              for a,b,c,d in openings if min(length,b)>max(0,a) and min(height,d)>max(0,c)]
    xs = sorted({0, length, *(q for a, b, c, d in openings for q in (a, b))})
    zs = sorted({0, height, *(q for a, b, c, d in openings for q in (c, d))})
    mesh = Mesh('Envelope ' + name)
    for a, b in zip(xs, xs[1:]):
        for lo, hi in zip(zs, zs[1:]):
            if any(c < (a+b)/2 < d and e < (lo+hi)/2 < f for c, d, e, f in openings):
                continue
            mesh.box(((a+b)/2, (lo+hi)/2, -.18), (b-a, hi-lo, .36))
    return finish(mesh, part, [mat], frame)


def sign(name, body, u, h, w, height, background=blue, foreground=white,
         frame=front, out=.16, logo=False):
    mesh = Mesh('Sign ' + name)
    mesh.box((0, 0, -.025), (w, height, .05), 0)
    if logo:
        # Approximate small castle emblem visible on the 2020 fascia.
        x=w*.435
        mesh.box((x,-.035,.016),(.34,height*.32,.025),1)
        for dx in [-.14,0,.14]:
            mesh.box((x+dx,height*.13,.016),(.09,height*.18,.025),1)
        mesh.box((x,-height*.10,.032),(.07,height*.16,.012),0)
    text = text_object('Temporary sign glyphs', body, (-w*.045 if logo else 0, 0, .003), (0, 0, 1),
                       height*.56, w*(.81 if logo else .93), font, foreground, extrude=.002)
    bpy.ops.object.select_all(action='DESELECT')
    text.select_set(True)
    bpy.context.view_layer.objects.active = text
    bpy.ops.object.convert(target='MESH')
    mesh.add([tuple(text.matrix_world @ v.co) for v in text.data.vertices],
             [tuple(f.vertices) for f in text.data.polygons], 1)
    bpy.data.objects.remove(text, do_unlink=True)
    return finish(mesh, 'shopfront', [background, foreground],
                  frame @ Matrix.Translation((u, h, out)))


# The 2011 photograph shows a continuous glazed shaft between broad pale piers.
stone=material('Warm pale stone cladding',(.59,.58,.51))
lightstone=material('Pale cap and reveals',(.70,.69,.62))
framegrey=material('Slim grey painted steel',(.46,.49,.47))
yellow=material('Money Shop yellow fascia',(.91,.64,.005))
darkglass=material('Blue grey upper glazing',(.09,.135,.16),roughness=.65)
darkglass.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.15
H=13.1
gl=1.34;gr=width-1.34;gc=width/2
wall_with_openings('stone front',front,width,H,[(.90,width-.90,3.81,H),(0,gl,12.25,H),(gr,width,12.25,H),(.16,width-.16,0,3.18)],mat=stone)
# Frontal2024 photo resolves perspective ambiguity: symmetric shoulders and cylindrical bay.
for u in [.45,width-.45]:
 elevation_box('Trim outer stone pier',u,8.0,.90,8.50,.25,.045,stone)
 elevation_box('Trim pier cap',u,12.25,.96,.18,.36,.06,lightstone)
 m=Mesh('Trim pier central rib');m.tube([(u,3.90,.23),(u,11.38,.23)],.065,sides=10);finish(m,materials=[lightstone],transform=front)
 pts=[(u-.24,11.36),(u+.24,11.36)]+[(u+.24*math.cos(i*math.pi/12),11.40+.12*math.sin(i*math.pi/12)) for i in range(13)]
 n=len(pts);v=[(x,h,o) for o in [.17,.34] for x,h in pts]
 m=Mesh('Trim rib capital');m.add(v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);finish(m,materials=[lightstone],transform=front)
 for h in [4.15+i*.58 for i in range(14)]:elevation_box('Fine stone joint',u,h,.89,.009,.009,.173,black)
# Seven chordal glazing strips approximate the visible continuous round bay.
radius=1.45;half=math.radians(65);segments=7
for floor,(bottom,top) in enumerate([(3.96,6.48),(6.48,6.84),(6.84,9.50),(9.50,9.86),(9.86,12.72),(12.72,13.10),(3.81,3.96)]):
 for j in range(segments):
  angle=-half+(j+.5)*2*half/segments;ww=2*radius*math.sin(half/segments);hh=top-bottom
  chord_r=radius*math.cos(half/segments)
  u=gc+chord_r*math.sin(angle);out=-.28+chord_r*math.cos(angle)-radius*math.cos(half)
  mat=Matrix(((math.cos(angle),0,math.sin(angle),u),(0,1,0,(bottom+top)/2),(-math.sin(angle),0,math.cos(angle),out),(0,0,0,1)))
  is_window=floor in [0,2,4]
  name=('Window glazed shaft' if is_window else 'Trim curved spandrel')+' %d %d'%(floor,j)
  m=Mesh(name);m.box((0,0,-.045),(ww,hh,.03),0)
  for x in [-ww/2+.015,ww/2-.015]:m.box((x,0,-.012),(.030,hh,.045),1)
  for z in ([-hh/2+.025,hh/2-.025,-hh*.28,hh*.28,-hh*.10,hh*.10] if is_window else [-hh/2+.015,hh/2-.015]):m.box((0,z,0),(ww,.035,.05),1)
  surface=darkglass if is_window else (lightstone if floor>=5 else black)
  finish(m,materials=[surface,framegrey if floor<5 else lightstone],transform=front@mat)
# A continuous underside closes the projecting bay above the fascia crown.
# Its bottom must clear the sign rather than sweep through its face.
pts=[(gc-radius*math.sin(half),-.42),(gc+radius*math.sin(half),-.42)]
pts += [(gc+radius*math.sin(half-i*2*half/segments),-.28+radius*(math.cos(half-i*2*half/segments)-math.cos(half))) for i in range(segments+1)]
m=Mesh('Trim curved bay soffit');m.add([(u,3.81,o) for u,o in pts],[tuple(range(len(pts)))]);finish(m,materials=[lightstone],transform=front)
# Pale swept return strips with small dark inset lights, retained at every LoD.
for right in [False,True]:
 edge=gc-radius*math.sin(half)
 u0=.90 if not right else width-edge;u1=edge if not right else width-.90
 z0=0 if not right else -.28;z1=-.28 if not right else 0
 length=math.hypot(u1-u0,z1-z0);tx=(u1-u0)/length;tz=(z1-z0)/length
 f=front@Matrix(((tx,0,-tz,u0),(0,1,0,0),(tz,0,tx,z0),(0,0,0,1)))
 holes=[(length/2-.085,length/2+.085,h-.18,h+.18) for h in [4.1,5.0,5.9,7.1,8.0,8.9,10.1,11.0,11.9]]
 wall_with_openings('swept return '+str(right),f,length,12.25,holes+[(0,length,0,3.70)],mat=lightstone)
 for h in [4.1,5.0,5.9,7.1,8.0,8.9,10.1,11.0,11.9]:elevation_box('Shop inset return light',length/2,h,.17,.36,.025,-.10,darkglass,'architecture',f)
# Round slab crown follows the same bay arc, rather than a flat full-width canopy.
for h,thickness,rad in [(12.98,.16,1.52),(13.20,.18,1.68)]:
 pts=[(gc+rad*math.sin(-half),-.42),(gc+rad*math.sin(half),-.42)]
 pts += [(gc+rad*math.sin(half-i*2*half/24),-.28+rad*(math.cos(half-i*2*half/24)-math.cos(half))) for i in range(25)]
 n=len(pts);verts=[(u,h-thickness/2,o) for u,o in pts]+[(u,h+thickness/2,o) for u,o in pts]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 m=Mesh('Trim rounded terminal '+('upper' if h>13 else 'lower'));m.add(verts,faces);finish(m,materials=[lightstone],transform=front)
# Conservative full-depth block. Aerial shows a long flat roof with rooflights;
# no unsupported pitched roof or rear window grid is invented.
for label,frame in [('north',side@Matrix.Translation((.36,0,0))),('south',face_matrix((xr+.36,ys,base),(0,-1,0)))]:
 wall_with_openings('party '+label,frame,depth-.72,11.94,[],mat=brick)
wall_with_openings('rear wall',rear,width,11.94,[(.55,1.5,0,2.12)],'rear',brick)
elevation_box('Shop rear service door',1.025,1.06,.95,2.12,.05,-.10,metal,'rear',rear)
# Roof deck, parapets and three rooflights observed in the shared aerial; sizes estimated.
box('Roof flat deck',((xf+xr)/2,(yn+ys)/2,base+11.76),(depth-.08,width-.08,.20),coping,'roof')
for y in [ys+.13,yn-.13]:
 box('Roof side parapet',((xf+xr)/2,y,base+12.06),(depth,.26,.30),brick,'roof')
 box('Trim parapet cap',((xf+xr)/2,y,base+12.25),(depth,.33,.08),coping,'roof')
box('Roof rear parapet',(xr+.13,(yn+ys)/2,base+12.06),(.26,width-.26,.30),brick,'roof')
box('Trim rear coping',(xr+.13,(yn+ys)/2,base+12.25),(.33,width-.26,.08),coping,'roof')
for i,x in enumerate([xf-5,xf-12.5,xf-21]):
 box('Roof rooflight curb %d'%i,(x,(yn+ys)/2,base+11.96),(1.7,1.65,.20),metal,'roof')
 # Four pitched glass faces, closed underpane, low pyramid silhouette.
 z=base+12.07;v=[(x-.73,(yn+ys)/2-.70,z),(x+.73,(yn+ys)/2-.70,z),(x+.73,(yn+ys)/2+.70,z),(x-.73,(yn+ys)/2+.70,z),(x,(yn+ys)/2,z+.23)]
 m=Mesh('Roof rooflight glazing %d'%i);m.add(v,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]);finish(m,'roof',[glass])
# Observed historical shop frontage. Current Merkur identity is documented separately;
# insufficient pixels exist to assert its present fitout.
for u in [.12,width-.12]:elevation_box('Shop stone jamb',u,1.58,.24,3.16,.28,-.03,stone,'shopfront')
elevation_box('Shop yellow fascia backing',width/2,3.34,width,.74,.14,.035,yellow,'shopfront')
sign('Money Shop fascia','The Money Shop',width/2,3.34,width-.32,.65,yellow,black,out=.125)
elevation_box('Trim fascia crown',width/2,3.75,width,.09,.32,.06,lightstone,'shopfront')
# Dated photo shows the pale recessed entrance on the south/left side.
# Its function as shop or upper-floor access remains unresolved.
shop_left=1.82;shop_right=width-.24
for a,b in [(shop_left,3.48),(3.53,shop_right)]:
 elevation_box('Shop display glass',(a+b)/2,1.58,b-a,2.78,.04,-.17,glass,'shopfront')
 for u in [a,b]:elevation_box('Shop slim window stile',u,1.58,.055,2.83,.10,-.10,white,'shopfront')
 for h in [.19,2.97]:elevation_box('Shop slim window rail',(a+b)/2,h,b-a,.055,.10,-.10,white,'shopfront')
door=1.01;dw=1.48
paledoor=material('Pale recessed entrance',(.51,.50,.44))
elevation_box('Shop entrance recess',door,1.47,dw+.08,2.94,.03,-.44,black,'shopfront')
elevation_box('Shop pale entrance leaf',door,1.36,dw,2.65,.03,-.36,paledoor,'shopfront')
for u in [door-dw/2-.025,door+dw/2+.025]:elevation_box('Shop entrance stile',u,1.36,.06,2.72,.10,-.30,white,'shopfront')
for h in [.035,2.68]:elevation_box('Shop entrance rail',door,h,dw+.10,.06,.10,-.30,white,'shopfront')
elevation_box('Shop entrance transom',door,2.85,dw+.05,.25,.03,-.35,paledoor,'shopfront')
elevation_box('Fine entrance handle',door-.33,1.23,.025,.40,.085,-.23,metal,'shopfront')
elevation_box('Shop threshold',door,.035,dw+.12,.07,.54,-.20,granite,'shopfront')
for u in [.24,shop_left]:
 elevation_box('Shop entrance side return',u,1.485,.06,2.97,.39,-.275,white,'shopfront')
elevation_box('Shop entrance soffit',(.24+shop_left)/2,2.97,shop_left-.24,.05,.48,-.23,white,'shopfront')
elevation_box('Shop display plinth',(shop_left+shop_right)/2,.10,shop_right-shop_left,.20,.25,-.045,stone,'shopfront')
# Separate access to22a verified by brochure; exact historical door not resolved,
# so no speculative second door cut through the visible stone piers.
pivot=D['registration_pivot'];registration=Matrix.Translation((*pivot,0))@Matrix.Rotation(D['registration_radians'],4,'Z')@Matrix.Translation((-pivot[0],-pivot[1],0))
for obj in list(s.objects):
 if obj.type=='MESH':obj.matrix_world=registration@obj.matrix_world
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.76,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
light=bpy.data.lights.new('Sun','SUN');light.energy=2.5;o=bpy.data.objects.new('Sun',light);s.collection.objects.link(o);o.rotation_euler=(-.45,.6,.4)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(camera);s.camera=camera;camera.data.type='ORTHO'
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-22.blend'))
