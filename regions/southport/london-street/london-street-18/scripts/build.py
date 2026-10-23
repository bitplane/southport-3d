"""18 London Street: researched Skipton exterior, metric source."""
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
# Rendered four-bay street wall with actual apertures in both upper storeys.
centres=[width*(i+.5)/4 for i in range(4)]
openings=[(u-.56,u+.56,4.95,6.85) for u in centres]+[(u-.56,u+.56,8.12,9.62) for u in centres]+[(.38,width-.38,0,3.95)]
wall_with_openings('four-bay rendered front',front,width,D['wall_height'],openings,mat=cream)
window_meshes={}
def window(name,frame,u,h,w,hh,mat=framecream):
 m=Mesh(name)
 m.box((0,0,-.165),(w,hh,.035),1)
 for x in [-w/2+.025,w/2-.025]:m.box((x,0,-.055),(.05,hh,.14),0)
 for y in [-hh/2+.025,hh/2-.025,hh/2-.24,-hh/2+.27]:m.box((0,y,-.055),(w-.1,.045,.14),0)
 m.box((0,0,-.055),(.042,hh-.48,.12),0)
 m.box((0,0,-.125),(w-.1,hh-.1,.03),2)
 obj=finish(m,materials=[mat,black,glass],transform=frame@Matrix.Translation((u,h,0)))
 key=(w,hh,mat.name)
 if key in window_meshes:obj.data=window_meshes[key]
 else:window_meshes[key]=obj.data
 return obj
for floor,h,hh in [(1,5.90,1.9),(2,8.87,1.5)]:
 for i,u in enumerate(centres):
  window('Window front %d %d'%(floor,i),front,u,h,1.12,hh)
  # Shallow painted reveal surrounds: sills project, jambs stay almost flush.
  for dx in [-.62,.62]:elevation_box('Trim window reveal',u+dx,h,.11,hh+.12,.07,.015,cream)
  elevation_box('Trim window lintel',u,h+hh/2+.06,1.34,.13,.10,.02,cream)
  elevation_box('Trim projecting sill',u,h-hh/2-.055,1.34,.11,.24,.065,cream)
# Pale parapet and its shallow top cap, matching the plain architecture.
elevation_box('Trim parapet cap',width/2,10.64,width+.03,.12,.41,-.12,cream)
elevation_box('Trim shop stringcourse',width/2,4.34,width,.11,.15,.015,cream)
# Side/party walls are plain. Main rear upper elevation is conservative: no invented window grid.
mainrear=xf-D['main_depth'];rearframe=face_matrix((mainrear,yn,base),(-1,0,0))
for label,frame in [('north',side@Matrix.Translation((.36,0,0))),('south',face_matrix((mainrear+.36,ys,base),(0,-1,0)))]:
 wall_with_openings('party '+label,frame,D['main_depth']-.72,10.40,[],mat=brick)
wall_with_openings('main rear',rearframe,width,10.4,[],'rear',brick)
# Northern half of the common18–20 hipped roof; southern boundary is a matching roof section.
xe=xf-.20;xb=mainrear+.15;ridge=(xe+xb)/2
ze=base+10.40;zr=base+D['ridge_height'];hip=2.15
a=(xe,ys,ze);b=(xe,yn-.12,ze);c=(xb,yn-.12,ze);d=(xb,ys,ze);e=(ridge,ys,zr);f=(ridge,yn-hip,zr)
m=Mesh('Roof main hip shell');v=[a,b,c,d,e,f]
m.add(v+[(x,y,z-.14) for x,y,z in v],[(0,1,5,4),(1,2,5),(2,3,4,5),(6,10,11,7),(7,11,8),(8,11,10,9),(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,4,10,9),(4,0,6,10)])
finish(m,'roof',[slate],roof_uv=True)
box('Trim ridge cap',(ridge,(ys+yn-hip)/2,zr+.025),(.16,width-hip,.10),slate,'roof')
# Narrow deep service wing, inferred from aerial and published ground-floor area.
# Southern strip extends toward Glebe courtyard; north cutback preserves open yard.
wingwidth=5.8;wingnorth=ys+wingwidth;wingfront=mainrear+.3;wingrear=xr;wingheight=3.30
wnorth=face_matrix((wingfront,wingnorth,base),(0,1,0));wsouth=face_matrix((wingrear,ys,base),(0,-1,0));wr=face_matrix((wingrear,wingnorth,base),(-1,0,0))
# End wall owns the rear corners; side walls stop at its inner face.
wall_with_openings('rear wing north',wnorth,wingfront-wingrear-.36,wingheight,[],'rear',brick)
wall_with_openings('rear wing south',wsouth@Matrix.Translation((.36,0,0)),wingfront-wingrear-.36,wingheight,[],'rear',brick)
wall_with_openings('rear service end',wr,wingwidth,wingheight,[(1.0,2.0,0,2.15)],'rear',brick)
elevation_box('Shop rear service door',1.5,1.075,1,2.15,.08,-.15,metal,'rear',wr)
# Shallow dual pitched wing roof with one visible rooflight, all estimated heights.
ry=(ys+wingnorth)/2;rz=base+4.15;ez=base+3.3
m=Mesh('Roof rear wing shell');v=[(wingrear,ys,ez),(wingfront,ys,ez),(wingfront,wingnorth,ez),(wingrear,wingnorth,ez),(wingrear,ry,rz),(wingfront,ry,rz)]
m.add(v+[(x,y,z-.12) for x,y,z in v],[(0,1,5,4),(4,5,2,3),(6,10,11,7),(10,9,8,11),(0,6,7,1),(2,8,9,3),(0,4,10,6),(4,3,9,10),(1,7,11,5),(5,11,8,2)])
finish(m,'roof',[slate],roof_uv=True)
for label,x in [('rear',wingrear),('front',wingfront-.18)]:
 m=Mesh('Envelope wing '+label+' gable');m.add([(x,ys,ez),(x,wingnorth,ez),(x,ry,rz),(x+.18,ys,ez),(x+.18,wingnorth,ez),(x+.18,ry,rz)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);finish(m,'rear',[brick])
# Rooflight oriented to the actual northward roof slope, not horizontal through tiles.
rl=Matrix.Translation((wingrear+4.8,ry+1.1,rz-.85*1.1/(wingwidth/2)+.04))@Matrix.Rotation(-math.atan(.85/(wingwidth/2)),4,'X')
box('Roof rear rooflight curb',(0,0,0),(1.1,1.35,.10),roofmetal,'roof',rl)
box('Roof rear rooflight glass',(0,0,.065),(.94,1.19,.025),glass,'roof',rl)
# Buff ground storey cladding: flat piers and head, subtle panel joints.
for u in [.19,width-.19]:
 elevation_box('Shop stone pier',u,3.695/2,.38,3.695,.34,-.03,stone,'shopfront')
 for h in [.7,1.4,2.1,2.8]:elevation_box('Fine stone pier joint',u,h,.375,.009,.008,.145,black,'shopfront')
elevation_box('Shop stone fascia surround',width/2,3.99,width,.59,.31,-.03,stone,'shopfront')
for i in range(1,9):elevation_box('Fine fascia stone joint',width*i/9,4.0,.009,.57,.008,.13,black,'shopfront')
# Door at north (right when facing elevation); a narrow frosted side panel at south.
left=.40;right=width-.40;door=width-1.35;shopheight=2.78
for a,b in [(left,left+1.1),(left+1.48,door-.55),(door-.5,right)]:
 if b<=door-.5:elevation_box('Shop display glass',(a+b)/2,1.4,b-a,shopheight,.04,-.18,glass,'shopfront')
 for u in [a,b]:elevation_box('Shop blue glazing stile',u,1.4,.055,shopheight+.1,.12,-.10,blue,'shopfront')
 for h in [.04,2.78]:elevation_box('Shop blue glazing rail',(a+b)/2,h,b-a,.06,.12,-.10,blue,'shopfront')
# Pale solid dividing pier, clearly visible in auction frontage.
elevation_box('Shop pale dividing pier',left+1.29,1.45,.38,2.9,.28,-.055,cream,'shopfront')
elevation_box('Shop frosted side pane',left+.55,1.35,.99,2.15,.025,-.145,roofmetal,'shopfront')
# Main shop glazing mullions and horizontal base rails; blank interior panels only.
for u in [3.10,4.28,5.46]:elevation_box('Shop main glazing mullion',u,1.4,.045,2.73,.085,-.115,blue,'shopfront')
elevation_box('Shop display base rail',4.0,.28,4.0,.06,.1,-.11,blue,'shopfront')
elevation_box('Shop entrance transom',door,2.61,1.0,.30,.035,-.35,glass,'shopfront')
# Recess entry behind outer frame (no inaccessible fictitious internal room).
elevation_box('Shop entry shadow',door,1.25,1.00,2.50,.03,-.42,black,'shopfront')
elevation_box('Shop door glass',door,1.20,.90,2.32,.03,-.35,glass,'shopfront')
for u in [door-.48,door+.48]:elevation_box('Shop door blue frame',u,1.2,.045,2.4,.07,-.30,blue,'shopfront')
for h in [.04,2.38]:elevation_box('Shop door blue rail',door,h,1,.055,.07,-.30,blue,'shopfront')
elevation_box('Fine door pull',door+.30,1.14,.025,.34,.06,-.24,metal,'shopfront')
elevation_box('Shop threshold',door,.035,1.04,.07,.48,-.18,stone,'shopfront')
# Close the exterior recess, not an invented interior. The dated frontage photo
# shows a narrow right sidelight and a continuous fascia between its stone piers.
elevation_box('Shop fascia infill',width/2,3.25,width-.76,.92,.30,-.13,blue,'shopfront')
elevation_box('Shop front sill',width/2,.025,width-.76,.05,.12,-.16,blue,'shopfront')
for a,b in [(door-.55,door-.48),(door+.48,right)]:
 elevation_box('Shop recessed side glazing',(a+b)/2,1.39,b-a,2.78,.04,-.35,glass,'shopfront')
for u in [door-.55,right]:
 elevation_box('Shop entry side reveal',u,1.39,.055,2.78,.35,-.255,blue,'shopfront')
elevation_box('Shop entry soffit',(door-.55+right)/2,2.79,right-(door-.55),.05,.46,-.21,blue,'shopfront')
# Long sign has raised source lettering with baked lower LoDs.
sign('Skipton bank fascia','SKIPTON BUILDING SOCIETY',width/2,3.21,width-.85,.65,background=white,foreground=blue,out=.16,logo=True)
for h in [2.84,3.58]:elevation_box('Trim blue sign edge',width/2,h,width-.75,.045,.09,.175,blue,'shopfront')
for u in [.39,width-.39]:elevation_box('Trim blue sign end',u,3.21,.045,.78,.09,.175,blue,'shopfront')
# Observed small alarm housing and drainage, independent district omissions.
elevation_box('Fine alarm housing',width-.44,4.72,.19,.23,.10,.09,cream)
m=Mesh('Fine rainwater pipe');m.tube([(xf+.06,ys+.10,base+.1),(xf+.06,ys+.10,base+10.45)],.035,0,8);finish(m,materials=[cream])
# Apply neighbour-agreed common block registration exactly once.
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
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-18.blend'))
