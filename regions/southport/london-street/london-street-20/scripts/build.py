"""20 London Street: former Britannia/Co-operative Bank exterior, metric source."""
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
    text = text_object('Temporary sign glyphs', body, (-w*.045 if logo else 0, 0, .035), (0, 0, 1),
                       height*.56, w*(.81 if logo else .93), font, foreground, extrude=.012)
    bpy.ops.object.select_all(action='DESELECT')
    text.select_set(True)
    bpy.context.view_layer.objects.active = text
    bpy.ops.object.convert(target='MESH')
    mesh.add([tuple(text.matrix_world @ v.co) for v in text.data.vertices],
             [tuple(f.vertices) for f in text.data.polygons], 1)
    bpy.data.objects.remove(text, do_unlink=True)
    return finish(mesh, 'shopfront', [background, foreground],
                  frame @ Matrix.Translation((u, h, out)))



cream=material('Pale painted render',(.72,.73,.68))
stone=material('Buff shop stone',(.57,.48,.35))
framecream=material('Cream timber frames',(.69,.62,.43))
roofmetal=material('Rooflight metal',(.31,.34,.34))
# Three compositional bays, with paired narrow central sashes on both floors.
window_meshes={}
def window(name,frame,u,h,w,hh):
 m=Mesh(name);m.box((0,0,-.17),(w,hh,.035),1)
 for x in [-w/2+.024,w/2-.024]:m.box((x,0,-.055),(.048,hh,.13),0)
 for z in [-hh/2+.025,0,hh/2-.025]:m.box((0,z,-.045),(w-.09,.045,.15),0)
 m.box((0,0,-.115),(.035,hh-.08,.045),0)
 m.box((0,0,-.14),(w-.09,hh-.08,.025),2)
 obj=finish(m,materials=[white,black,glass],transform=frame@Matrix.Translation((u,h,0)))
 key=(w,hh)
 if key in window_meshes:obj.data=window_meshes[key]
 else:window_meshes[key]=obj.data
 return obj
bays=[(1.18,1.16),(3.32,.64),(4.18,.64),(6.32,1.16)]
openings=[(u-w/2,u+w/2,4.90,6.98) for u,w in bays]+[(u-w/2,u+w/2,8.12,9.50) for u,w in bays]+[(.25,width-.25,0,3.30)]
wall_with_openings('classical cream front',front,width,10.68,openings,mat=cream)
for floor,h,hh in [(1,5.94,2.08),(2,8.81,1.38)]:
 for i,(u,w) in enumerate(bays):
  window('Window front %d %d'%(floor,i),front,u,h,w,hh)
  for dx in [-w/2-.055,w/2+.055]:elevation_box('Trim sash reveal',u+dx,h,.095,hh+.14,.07,.015,cream)
  elevation_box('Trim sash lintel',u,h+hh/2+.065,w+.23,.13,.09,.025,cream)
  elevation_box('Trim sash sill',u,h-hh/2-.055,w+.24,.11,.23,.065,cream)
# Shallow end pilasters and the broad frieze/cornice differentiate this from18.
for u in [.13,width-.13]:
 elevation_box('Trim end pilaster',u,7.45,.26,5.62,.14,.035,cream)
 elevation_box('Trim pilaster capital',u,10.12,.36,.16,.26,.065,cream)
 elevation_box('Trim pilaster foot',u,4.63,.36,.14,.23,.055,cream)
for h,hh,depth in [(4.47,.14,.27),(4.59,.07,.19),(9.85,.09,.18),(10.14,.12,.25),(10.43,.16,.40),(10.61,.11,.49)]:
 elevation_box('Trim facade moulding',width/2,h,width,hh,depth,.06,cream)
elevation_box('Trim frieze',width/2,10.00,width,.23,.13,.015,cream)
# Repeated dentils are detailed geometry nearby, deliberately omitted at District.
for i in range(37):elevation_box('Fine cornice dentil',.13+i*(width-.26)/36,10.29,.09,.13,.17,.13,cream)
# Plain party surfaces and a closed conservative rear facade.
mainrear=xf-D['main_depth'];rearframe=face_matrix((mainrear,yn,base),(-1,0,0))
for label,frame in [('north',side@Matrix.Translation((.36,0,0))),('south',face_matrix((mainrear,ys,base),(0,-1,0)))]:wall_with_openings('party '+label,frame,D['main_depth']-.36,10.4,[],mat=brick)
wall_with_openings('main rear',rearframe,width,10.4,[],'rear',brick)
# Southern end of the common18–20 hipped roof. The northern cross-section meets18.
xe=xf-.20;xb=mainrear+.15;ridge=(xe+xb)/2;ze=base+10.40;zr=base+D['ridge_height'];hip=2.15
v=[(xe,ys+.12,ze),(xe,yn,ze),(xb,yn,ze),(xb,ys+.12,ze),(ridge,ys+hip,zr),(ridge,yn,zr)]
m=Mesh('Roof common main shell');m.add(v+[(x,y,z-.14) for x,y,z in v],[(0,1,5,4),(2,3,4,5),(3,0,4),(6,10,11,7),(8,11,10,9),(9,10,6),(0,6,7,1),(2,8,9,3),(3,9,6,0),(1,5,11,7),(5,2,8,11)]);finish(m,'roof',[slate],roof_uv=True)
box('Trim ridge cap',(ridge,(ys+hip+yn)/2,zr+.025),(.16,width-hip,.10),slate,'roof')
# Lower rear range observed in aerial, kept plain where ground views are obscured.
wingnorth=yn-.9;wingwidth=width-.9;wingfront=mainrear+.2;wingrear=xr;wh=3.4
nf=face_matrix((wingfront,wingnorth,base),(0,1,0));sf=face_matrix((wingrear,ys,base),(0,-1,0));rf=face_matrix((wingrear,wingnorth,base),(-1,0,0))
wall_with_openings('rear wing north',nf,wingfront-wingrear,wh,[],'rear',brick)
wall_with_openings('rear wing south',sf,wingfront-wingrear,wh,[],'rear',brick)
wall_with_openings('rear wing end',rf,wingwidth,wh,[(1.1,2.1,0,2.15)],'rear',brick)
elevation_box('Shop rear service door',1.6,1.075,1,2.15,.06,-.10,metal,'rear',rf)
box('Roof rear deck',((wingfront+wingrear)/2,(ys+wingnorth)/2,base+wh-.12),(wingfront-wingrear-.04,wingwidth-.04,.16),felt,'roof')
for yy in [ys+.1,wingnorth-.1]:box('Trim rear parapet',((wingfront+wingrear)/2,yy,base+wh+.15),(wingfront-wingrear,.20,.30),brick,'rear')
box('Roof rear rooflight curb',(wingrear+4.2,(ys+wingnorth)/2,base+wh+.10),(1.4,1.2,.20),roofmetal,'roof')
box('Roof rear rooflight pane',(wingrear+4.2,(ys+wingnorth)/2,base+wh+.22),(1.23,1.03,.035),glass,'roof')
# Vacant2020 shop: white signboard, pale covered display and separate north flats door.
shopright=width-1.35;shopdoor=shopright-.58
for u in [.14,shopright+.17,width-.14]:elevation_box('Shop pale cladding pier',u,1.65,.28,3.30,.31,-.025,cream,'shopfront')
elevation_box('Shop plain fascia lower backing',width/2,3.10,width,.52,.16,.045,white,'shopfront')
elevation_box('Shop blank fascia',width/2,3.81,width,.91,.16,.045,white,'shopfront')
elevation_box('Trim fascia top',width/2,4.30,width,.08,.27,.08,cream,'shopfront')
# Large former banking window, lightly green covered glass in the2020 photograph.
covered=material('Pale covered display glass',(.40,.62,.58))
a=.28;b=shopdoor-.51
elevation_box('Shop covered display',(a+b)/2,1.40,b-a,2.75,.04,-.20,covered,'shopfront')
for u in [a,(a+b)/2,b]:elevation_box('Shop display mullion',u,1.42,.055,2.83,.11,-.12,white,'shopfront')
for h in [.045,2.82]:elevation_box('Shop display rail',(a+b)/2,h,b-a,.06,.11,-.12,white,'shopfront')
elevation_box('Shop bank door glass',shopdoor,1.23,.94,2.42,.035,-.27,covered,'shopfront')
for u in [shopdoor-.49,shopdoor+.49]:elevation_box('Shop bank door stile',u,1.25,.05,2.5,.09,-.20,white,'shopfront')
for h in [.025,2.46]:elevation_box('Shop bank door rail',shopdoor,h,1,.05,.09,-.20,white,'shopfront')
elevation_box('Shop bank transom',shopdoor,2.65,1,.35,.03,-.27,glass,'shopfront')
elevation_box('Fine bank door handle',shopdoor+.30,1.15,.025,.32,.07,-.14,metal,'shopfront')
# Slim access to upper flats, as seen beside the vacant bank frontage.
flat=width-.72;doorblue=material('Dark blue flats door',(.025,.035,.075))
elevation_box('Shop flats entrance shadow',flat,1.25,.88,2.5,.03,-.30,black,'shopfront')
elevation_box('Shop flats timber door',flat,1.15,.80,2.3,.065,-.26,doorblue,'shopfront')
for u in [flat-.43,flat+.43]:elevation_box('Shop flats door frame',u,1.18,.055,2.4,.11,-.16,cream,'shopfront')
for h in [.03,2.36]:elevation_box('Shop flats door rail',flat,h,.9,.06,.11,-.16,cream,'shopfront')
elevation_box('Shop flats transom',flat,2.65,.85,.47,.035,-.24,glass,'shopfront')
elevation_box('Fine flats handle',flat-.27,1.05,.025,.15,.06,-.19,metal,'shopfront')
elevation_box('Shop entrance threshold',flat,.035,.9,.07,.40,-.17,granite,'shopfront')
# Readable architectural joinery only; no speculative notice text.
for h in [.60,1.45]:elevation_box('Fine flats door recessed panel',flat,h,.60,.55,.012,-.218,black,'shopfront')
for u in [.14,shopright+.17,width-.14]:
 for h in [.8,1.6,2.4]:elevation_box('Fine cladding joint',u,h,.275,.009,.008,.135,black,'shopfront')
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
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-20.blend'))
