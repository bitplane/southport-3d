"""14–16 London Street: researched Betfred exterior, metric source."""
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
black=material('Recess shadow',(.025,.028,.03));blue=material('Betfred fascia blue',(.025,.04,.25));red=material('Red painted metal',(.55,.018,.025))
granite=material('Grey granite',(.45,.46,.43),'granite');felt=material('Pale weathered felt',(.35,.37,.35));wood=material('Service door timber',(.30,.16,.075));metal=material('Galvanized metal',(.43,.46,.45))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf')
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
         frame=front, out=.16):
    mesh = Mesh('Sign ' + name)
    mesh.box((0, 0, -.025), (w, height, .05), 0)
    text = text_object('Temporary sign glyphs', body, (0, 0, .035), (0, 0, 1),
                       height*.56, w*.93, font, foreground, extrude=.012)
    bpy.ops.object.select_all(action='DESELECT')
    text.select_set(True)
    bpy.context.view_layer.objects.active = text
    bpy.ops.object.convert(target='MESH')
    mesh.add([tuple(text.matrix_world @ v.co) for v in text.data.vertices],
             [tuple(f.vertices) for f in text.data.polygons], 1)
    bpy.data.objects.remove(text, do_unlink=True)
    return finish(mesh, 'shopfront', [background, foreground],
                  frame @ Matrix.Translation((u, h, out)))


# Six first-floor apertures; the much taller brick area above is deliberately blank.
centres=[width*(i+.5)/6 for i in range(6)]
openings=[(u-.59,u+.59,4.35,6.15) for u in centres]+[(0,width,0,3.95)]
wall_with_openings('six-bay front',front,width,D['front_parapet_height'],openings)
def window(name,frame,u,h,w,hh):
 m=Mesh(name);m.box((0,0,-.14),(w,hh,.035),1)
 for x in [-w/2+.025,w/2-.025]:m.box((x,0,-.03),(.05,hh,.13),0)
 for y in [-hh/2+.025,hh/2-.025,hh/2-.30]:m.box((0,y,-.03),(w-.1,.05,.13),0)
 m.box((0,-.13,-.10),(w-.1,hh-.36,.025),2)
 m.box((0,hh/2-.16,-.10),(w-.1,.22,.025),2)
 m.box((0,-hh/2-.035,.015),(w+.08,.07,.19),0)
 return finish(m,materials=[white,black,glass],transform=frame@Matrix.Translation((u,h,0)))
for i,u in enumerate(centres):window('Window front '+str(i),front,u,5.25,1.18,1.8)
elevation_box('Trim front coping',width/2,10.31,width+.08,.09,.43,-.14,coping)
elevation_box('Trim shop head stone',width/2,4.02,width,.14,.38,-.08,granite)
# The tall frontage wall returns only partway down Glebe before stepping down.
wall_with_openings('Glebe tall return',side@Matrix.Translation((.36,0,0)),4.99,10.3,[],mat=brick)
setback=D['upper_side_setback'];service_start=D['service_wall_start'];service_door=D['service_door_u']
inset_side=side@Matrix.Translation((0,0,-setback))
upper_side=inset_side@Matrix.Translation((5.35,0,0))
wall_with_openings('Glebe low upper return',upper_side,3.90,6.5,
 [(u-.48,u+.48,4.95,5.65) for u in [1.25,3.1]])
for i,u in enumerate([6.6,8.45]):window('Window Glebe clerestory '+str(i),inset_side,u,5.3,.96,.70)
# Low rear service enclosure follows the street edge; its wooden door is inset.
low_side=side@Matrix.Translation((service_start,0,0))
wall_with_openings('Glebe service wall',low_side,depth-service_start,3.35,[(service_door-service_start-.45,service_door-service_start+.45,0,2.2)],'rear')
elevation_box('Shop timber service door',service_door,1.1,.90,2.2,.08,-.16,wood,'rear',side)
for u in [service_door-.49,service_door+.49]:elevation_box('Trim service door jamb',u,1.12,.09,2.3,.13,-.025,black,'rear',side)
elevation_box('Trim service door lintel',service_door,2.25,1.1,.10,.17,-.02,black,'rear',side)
for a,b,h,frame in [(.40,5.35,10.31,side),(5.35,9.25,6.51,inset_side),(service_start,depth,3.37,side)]:
 elevation_box('Trim Glebe coping',(a+b)/2,h,b-a,.09,.43,-.14,coping,'rear',frame)
# Exposed return closes the upper setback above the low street-edge roof strip.
cheek=face_matrix((xf-5.35,yn-.18,base),(-1,0,0))
wall_with_openings('upper setback cheek',cheek,setback-.18,6.5,[(0,setback-.18,0,3.35)],'rear')
# Conservative rear closing elevation. Door is a service opening, not an invented shop.
wall_with_openings('rear service elevation',rear,width,3.35,[(width*.7-.5,width*.7+.5,0,2.15)],'rear')
elevation_box('Shop rear steel door',width*.7,1.075,1,2.15,.06,-.12,metal,'rear',rear)
# South party boundary: stepped heights matching the roof envelope.
south=face_matrix((xr,ys,base),(0,-1,0))
wall_with_openings('party lower wall',south,depth,6.5,[],mat=brick)
# Front roof zone slopes behind the raised parapet, closing at the lower rear roof.
# Exact pitch is estimated from the high return and aerial dark/pale roof boundary.
x0=xf-.36;x1=xf-5.35;z0=base+9.95;z1=base+6.52
m=Mesh('Roof front slope')
v=[(x0,ys+.16,z0),(x0,yn-.16,z0),(x1,yn-.16,z1),(x1,ys+.16,z1)]
m.add(v+[(x,y,z-.14) for x,y,z in v],[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
finish(m,'roof',[slate],roof_uv=True)
# Roof levels avoid overlapping deck faces. Low rear zone is visually separated.
box('Roof middle deck',((xf-5.35+xr+5.90)/2,(ys+yn-setback)/2,base+6.40),(depth-11.25,width-setback-.35,.18),felt,'roof')
box('Roof recessed side strip',((xf-5.35+xr+5.72)/2,yn-setback/2-.10,base+3.25),(depth-11.07,setback-.16,.18),felt,'roof')
box('Roof low rear deck',((xr+.18+xr+5.72)/2,(ys+yn)/2,base+3.25),(5.54,width-.35,.18),felt,'roof')
# Rear upper return closes the height step, with two modest casements seen obliquely.
step=face_matrix((xr+5.72,yn-setback-.18,base),(-1,0,0))
wall_with_openings('upper rear step',step,width-setback-.36,6.50,[(0,width-setback-.36,0,3.35)],'rear')
# South roof wedge under the sloping plane.
m=Mesh('Envelope party roof wedge')
m.outline([(0,6.5),(5,6.5),(5,9.95)],-.26,0)
finish(m,materials=[brick],transform=south@Matrix.Translation((depth-5.35,0,0)))
# Shopfront: grey stone ends, red cylindrical mullions and recessed central doors.
for u in [.18,width-.18]:
 elevation_box('Shop granite pier',u,1.6,.36,3.2,.46,-.10,granite,'shopfront')
 for h in [.8,1.6,2.4]:elevation_box('Fine granite joint',u,h,.35,.012,.012,.135,black,'shopfront')
entry=width*.31
for a,b in [(.36,entry-.75),(entry+.75,width-.36)]:
 elevation_box('Shop display glass',(a+b)/2,1.55,b-a,3.0,.035,-.19,glass,'shopfront')
 for h in [.18,2.65,3.05]:elevation_box('Shop red glazing rail',(a+b)/2,h,b-a,.055,.10,-.10,red,'shopfront')
 n=max(1,round((b-a)/1.55))
 for k in range(1,n):elevation_box('Shop red display mullion',a+(b-a)*k/n,1.55,.055,3.0,.11,-.10,red,'shopfront')
for u in [entry-.79,entry+.79]:
 m=Mesh('Shop red round entrance post');m.lathe((xf+.035,ys+u),[(base,.11),(base+3.10,.11)],20)
 finish(m,'shopfront',[red])
elevation_box('Shop recessed entrance shadow',entry,1.50,1.50,3.0,.03,-.72,black,'shopfront')
elevation_box('Shop threshold',entry,.04,1.5,.08,.75,-.35,granite,'shopfront')
for u in [entry-.37,entry+.37]:
 elevation_box('Shop entrance glass leaf',u,1.23,.70,2.40,.03,-.52,glass,'shopfront')
 for offset in [-.35,.35]:elevation_box('Shop entrance stile',u+offset,1.23,.045,2.44,.07,-.48,red,'shopfront')
 for h in [.06,2.42]:elevation_box('Shop door rail',u,h,.70,.055,.07,-.48,red,'shopfront')
 elevation_box('Fine door pull',u+.23,1.2,.025,.45,.07,-.43,metal,'shopfront')
elevation_box('Shop entrance transom',entry,2.72,1.50,.49,.04,-.52,glass,'shopfront')
elevation_box('Shop entrance header rail',entry,2.45,1.50,.06,.09,-.47,red,'shopfront')
for u in [entry-.75,entry+.75]:
 elevation_box('Shop entrance side return',u,1.525,.055,3.05,.57,-.435,red,'shopfront')
elevation_box('Shop entrance soffit',entry,3.06,1.55,.06,.77,-.335,blue,'shopfront')
elevation_box('Shop continuous glazing head',width/2,3.105,width-.72,.11,.24,-.12,red,'shopfront')
for a,b in [(.36,entry-.75),(entry+.75,width-.36)]:
 elevation_box('Shop display sill',(a+b)/2,.025,b-a,.05,.12,-.19,granite,'shopfront')
elevation_box('Shop blue fascia backing',width/2,3.55,width,.78,.12,.025,blue,'shopfront')
# One material identity at all levels; raised lettering is baked on lower levels.
sign('Betfred main','BETFRED',width*.29,3.55,width*.55,.78,background=blue,out=.13)
sign('Betfred web','betfred.com',width*.82,3.55,width*.28,.78,background=blue,out=.13)
elevation_box('Shop fascia centre fill',width*.61,3.55,width*.10,.78,.05,.105,blue,'shopfront')
for h in [3.13,3.97]:elevation_box('Trim fascia red edge',width/2,h,width,.045,.32,.055,red,'shopfront')
# Minor observed side services, kept separate for reasoned omission at distance.
m=Mesh('Fine side drainage')
for u in [5.6,9.1]:m.tube([(xf-u,yn-setback+.06,base+.1),(xf-u,yn-setback+.06,base+6.4)],.038,0,8)
finish(m,'rear',[black])
for u,h in [(6.1,6.8),(8.1,6.3)]:
 m=Mesh('Fine satellite dish')
 # Shallow elliptical dish silhouette on the north elevation, attached by a bracket.
 n=20;verts=[(0,0,.055)]+[(.32*math.cos(i*2*math.pi/n),.42*math.sin(i*2*math.pi/n),0) for i in range(n)]
 m.add(verts,[(0,i+1,(i+1)%n+1) for i in range(n)])
 m.box((0,-.35,-.13),(.05,.45,.3))
 finish(m,'rear',[metal],inset_side@Matrix.Translation((u,h,.22)))
# Align the mapped slightly oblique frontage and the Glebe wall, once only.
registration=Matrix.Translation((xf,yn,0))@Matrix.Rotation(.02418,4,'Z')@Matrix.Translation((-xf,-yn,0))
for obj in list(s.objects):
 if obj.type=='MESH':obj.matrix_world=registration@obj.matrix_world
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.76,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
light=bpy.data.lights.new('Sun','SUN');light.energy=2.5;o=bpy.data.objects.new('Sun',light);s.collection.objects.link(o);o.rotation_euler=(-.45,.6,.4)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(camera);s.camera=camera;camera.data.type='ORTHO'
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-14-16.blend'))
