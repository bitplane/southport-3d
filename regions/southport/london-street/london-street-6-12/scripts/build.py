"""Research-led exterior of the complete 6–12 London Street block."""
import json
import math
import os
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(Path(os.environ['SOUTHPORT_REPO_ROOT']) / 'lib'), str(ROOT / 'scripts')]
from southport3d.geometry import Mesh, face_matrix, text_object
from components import casement,sash, cornice, rooflight
from roof import build_roof, roof_height, party_return, eave_return
D = json.loads((ROOT / 'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
C = {}
for name in ['architecture', 'roof', 'shopfront', 'rear']:
    C[name] = bpy.data.collections.new(name)
    s.collection.children.link(C[name])


def material(name, colour, texture=None, roughness=.82):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = roughness
    if texture:
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(ROOT / 'textures' / (texture + '.png')))
        mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    return mat


brick = material('Authored warm red brick', (.45, .22, .14), 'brick')
slate = material('Authored grey slate courses', (.20, .22, .24), 'slate')
white = material('Weathered white paint', (.79, .79, .74))
sill = material('Grey painted stone sills', (.45, .46, .43))
glass = material('Opaque grey exterior glazing', (.105, .15, .18), roughness=.28)
black = material('Dark recesses and seals', (.028, .032, .035))
blue = material('Halifax fascia blue', (.035, .12, .39), roughness=.48)
granite = material('Grey granite shopfront', (.49, .50, .48), 'granite')
charcoal = material('Number six dark stone', (.105, .12, .115))
metal = material('Pale rear metalwork', (.58, .61, .57), roughness=.6)
felt = material('Rear felt and lead flashings', (.19, .21, .21))
pale_deck = material('Pale southern service roof', (.58, .59, .55))
rust = material('Brick-coloured louvres', (.34, .13, .075))
font = bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
base, xf, ys, yn, xr = [D[k] for k in ['base_z', 'front_x', 'south_y', 'north_y', 'rear_x']]
width = yn - ys
front = face_matrix((xf, ys, base), (1, 0, 0))
rear_north=D['rear_wall_north_y']
rear_offset=yn-rear_north
rear = face_matrix((D['upper_rear_x'], rear_north, base), (-1, 0, 0))
side = face_matrix((xr+.36, ys, base), (0, -1, 0))


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
        # Hand-authored crossing bands behind the raised word, observed in 2024.
        for direction in [-1, 1]:
            for k in range(6):
                yy = -.40*height + k*.16*height
                xx = direction * yy * .95
                mesh.box((xx, yy, .008), (w*.63, .025, .012), 1)
    text = text_object('Temporary sign glyphs', body, (0, 0, .035), (0, 0, 1),
                       height*(.38 if logo else .56), w*.93, font, foreground, extrude=.012, fit_bounds=True)
    bpy.ops.object.select_all(action='DESELECT')
    text.select_set(True)
    bpy.context.view_layer.objects.active = text
    bpy.ops.object.convert(target='MESH')
    mesh.add([tuple(text.matrix_world @ v.co) for v in text.data.vertices],
             [tuple(f.vertices) for f in text.data.polygons], 1)
    bpy.data.objects.remove(text, do_unlink=True)
    return finish(mesh, 'shopfront', [background, foreground],
                  frame @ Matrix.Translation((u, h, out)))


# Twelve regular bays: nine Halifax bays and three at number 6. First-floor
# hood mouldings accent every third window; second-floor heads are segmental.
spacing = width / D['upper_bays']
centres = [spacing*(i+.5) for i in range(D['upper_bays'])]
openings = []
for lo, hi in [D['first_window'], D['second_window']]:
    openings += [(u-D['window_width']/2, u+D['window_width']/2, lo, hi) for u in centres]
# The shopfront is independently assembled; upper wall starts at fascia height.
openings.append((0, width, 0, 3.95))
wall_with_openings('London Street brick wall', front, width, D['eaves_height'], openings)
window_prototypes = {}
for storey, (lo, hi) in enumerate([D['first_window'], D['second_window']], 1):
    for i, u in enumerate(centres):
        transform = front @ Matrix.Translation((u, (lo+hi)/2, 0))
        if storey not in window_prototypes:
            mesh = sash(f'Window front {storey} {i:02d}', D['window_width'], hi-lo)
            proto = finish(mesh, materials=[white, black, glass, sill], transform=transform)
            window_prototypes[storey] = proto
        else:
            proto = window_prototypes[storey]
            obj = proto.copy()
            obj.data = proto.data
            obj.name = f'Window front {storey} {i:02d}'
            C['architecture'].objects.link(obj)
            obj.matrix_world = transform
        if storey == 1 and i % 3 == 1:
            mesh = cornice('Trim hooded first-floor lintel', D['window_width']+.32)
            finish(mesh, materials=[white], transform=front @ Matrix.Translation((u, hi+.11, 0)))
            for x in [u-.56, u+.56]:
                elevation_box('Trim hood corbel', x, hi-.15, .11, .31, .22, .08, white)
        if storey == 2:
            mesh = Mesh('Trim segmental second-floor head')
            # Shallow curved intrados beneath a level white lintel.
            points = [(-.70, .17), (.70, .17), (.70, -.035)]
            points += [(x, .075-.11*(x/.70)**2) for x in [.70-j*1.4/16 for j in range(17)]]
            mesh.outline(points, -.045, .08)
            finish(mesh, materials=[white], transform=front @ Matrix.Translation((u, hi-.04, 0)))
        if i < 11 and storey == 1:
            elevation_box('Fine brick air vent', u+spacing/2, 6.48, .13, .13, .02, .012, black)
for h in [3.95, 4.02]:
    elevation_box('Trim continuous sill course', width/2, h, width+.10, .075, .25, .065, white)
finish(cornice('Trim continuous eaves', width+.20), materials=[white],
       transform=front @ Matrix.Translation((width/2, D['eaves_height'], 0)))
mesh = Mesh('Fine eaves dentils')
for k in range(int(width/.24)):
    mesh.box((.12+k*.24, D['eaves_height']-.17, .08), (.13, .13, .20))
finish(mesh, materials=[sill], transform=front)

# South return onto Glebe: blank brick with a pair of small casements, two
# brick-filled openings above and the granite/glazed shop corner below.
side_width = xf-xr-.36
side_openings = [(side_width-2.65, side_width, 0, 3.95),
                 (0,D['upper_rear_x']-xr-.36,4.65,D['rear_eaves_height'])]
side_openings += [(u-.46, u+.46, 5.0, 6.2) for u in [side_width-5.1, side_width-7.1]]
wall_with_openings('Glebe brick return', side, side_width-.36, D['rear_eaves_height']-.15, side_openings)
for u in [side_width-5.1, side_width-7.1]:
    mesh = casement('Window Glebe casement', .92, 1.2, 1,.78)
    finish(mesh, materials=[white, black, glass, sill], transform=side @ Matrix.Translation((u, 5.6, -.05)))
for u in [side_width-5.1, side_width-7.1]:
    elevation_box('Envelope bricked side opening', u, 7.6, .95, 1.4, .025, .018, brick, frame=side)
mesh = Mesh('Fine Glebe louvre blades')
mesh.box((side_width-3.3, .8, .01), (1.05, 1.02, .035), 0)
for k in range(13):
    mesh.box((side_width-3.3, .37+k*.067, .045), (.95, .028, .075), 1)
finish(mesh, materials=[black, rust], transform=side)
finish(eave_return(D,'Envelope south eaves wedge',(D['upper_rear_x'],ys),(xf-.36,ys),
                   (0,.36),D['rear_eaves_height']-.15))
# The neighbouring stair wells interrupt the party line behind number six.
finish(party_return(D))
rx=D['ridge_x'];ry=D['ridge_end_y'];ze=base+D['eaves_height']
zr=base+D['ridge_height'];zb=base+D['rear_eaves_height']
build_roof(D,lambda mesh:finish(mesh,'roof',[slate],roof_uv=True))
mesh = Mesh('Roof lead ridge and hip seams')
mesh.tube([(rx,-44.15,zr+.025),(rx,ry,zr+.025),(xf+.12,ys-.12,ze+.025)], .055, 0, 8)
hip_x=D['upper_rear_x'];hip_y=ry+(ys-.12-ry)*(hip_x-rx)/(xr-rx)
mesh.tube([(rx,ry,zr+.025),(hip_x,hip_y,roof_height(D,hip_x,hip_y)+.025)], .055, 0, 8)
finish(mesh, 'roof', [felt])
# Roof vents are small authored fittings, not invented decorative chimneys.
mesh = Mesh('Fine roof vent terminals')
for x,y in [(-18.4,-45.2),(-20.4,-48.7),(-20,-58.4)]:
    z=roof_height(D,x,y)
    mesh.lathe((x,y),[(z,.065),(z+.48,.065),(z+.52,.09)],10)
finish(mesh, 'roof', [metal])

# Rear upper wall: mixed casements and barred service windows visible Nov2020.
rear_windows=D['rear_windows']
rear_height=roof_height(D,D['upper_rear_x'],-50)-base-.14
wall_with_openings('rear upper brick',rear,rear_north+55.7,rear_height,
                   [(q['u']-q['w']/2,q['u']+q['w']/2,q['h']-q['hh']/2,q['h']+q['hh']/2) for q in rear_windows],'rear')
# The pale southern service deck remains exposed all the way to Glebe.
# Close its upper wall at the same setback as the window court, following the hip.
finish(eave_return(D,'Envelope southern rear upper return',
                   (D['upper_rear_x'],ys+.36),(D['upper_rear_x'],-55.7),
                   (.36,0),4.65),part='rear')
for i,q in enumerate(rear_windows):
    u,h,w,hh,bars=[q[k] for k in ['u','h','w','hh','bars']]
    mesh=casement('Window rear casement '+str(i),w,hh,q['columns'])
    if bars:
        for k in range(max(3,int(w/.12))):
            x=-w/2+.08+k*(w-.16)/(max(3,int(w/.12))-1)
            mesh.box((x,0,.11),(.018,hh+.08,.025),0)
        for yy in [-hh*.28,hh*.28]:
            mesh.box((0,yy,.115),(w+.08,.025,.025),0)
    finish(mesh,'rear',[white,black,glass,sill],rear@Matrix.Translation((u,h,0)))
# Prominent external red-brick stack with one dark flue, seen from Glebe.
box('Envelope rear chimney',(-25.15,D['rear_chimney_y'],base+7.9),(.95,.8,7.5),part='rear')
box('Trim chimney cap',(-25.15,D['rear_chimney_y'],base+11.72),(1.08,.95,.12),sill,'rear')
mesh=Mesh('Fine chimney flue')
mesh.lathe((-25.15,D['rear_chimney_y']),[(base+11.76,.11),(base+12.2,.11)],12)
finish(mesh,'rear',[black])
box('Envelope service wing northern return',((xr+.36-24.8)/2,rear_north-.14,base+1.925),(-24.8-xr-.36,.25,3.85),part='rear')
# Two flat service wings and the observed pitched rooflight.
for name,ya,yb,height in [('rooflight wing',-55.7,rear_north,3.85),('south wing',ys,-55.7,4.65)]:
    frame=face_matrix((xr,yb,base),(-1,0,0))
    n=1 if name=='rooflight wing' else 2
    centres_rear=[(yb-ya)*(k+1)/(n+1) for k in range(n)]
    window_w,window_h,window_z=(1.04,1.3,1.85) if name=='rooflight wing' else (1.60,.85,3.0)
    openings=[(u-window_w/2,u+window_w/2,window_z-window_h/2,window_z+window_h/2) for u in centres_rear]
    wall_with_openings(name,frame,yb-ya,height,openings,'rear')
    for u in centres_rear:
        m=casement('Window low rear barred',window_w,window_h,2)
        for k in range(10):
            m.box((-window_w/2+.06+k*(window_w-.12)/9,0,.11),(.021,window_h+.05,.03),0)
        finish(m,'rear',[white,black,glass,sill],frame@Matrix.Translation((u,window_z,0)))
    if name!='south wing':
        box('Envelope '+name+' side',((xr-24.8)/2,ya+.14,base+height/2),(-24.8-xr,.28,height),part='rear')
    # Keep concealed deck end inside the full-height Glebe wall, not coplanar
    # with its exterior face (which otherwise exposes a black horizontal line).
    deck_start=ya+.20 if name=='south wing' else ya+.02
    deck_end=yb-.02
    deck_left=xr+.20;deck_right=-24.78
    box('Roof '+name+' flat deck',((deck_left+deck_right)/2,(deck_start+deck_end)/2,base+height),(deck_right-deck_left,deck_end-deck_start,.16),pale_deck if name=='south wing' else felt,'rear')
    box('Trim '+name+' coping',(xr-.035,(ya+yb)/2,base+height+.09),(.25,yb-ya+.1,.12),sill,'rear')
finish(rooflight('Roof rear pyramidal rooflight',2.7,2.7,.75),'rear',[metal,glass],
       Matrix.Translation((-27.2,-49.5,base+3.95)))
# Open guardrails and caged access ladder are physical; never bake as a solid wall.
rails=Mesh('Fixture rear roof guardrail')
for y in [-46,-48.1,-50.2,-52.3,-54.6]:
    rails.box((-29.55,y,base+4.45),(.045,.045,1.0))
for h in [4.0,4.48,4.92]:
    rails.tube([(-29.55,-46,base+h),(-29.55,-54.7,base+h)],.023,0,6)
finish(rails,'rear',[metal])
ladder=Mesh('Fixture rear access ladder')
for y in [-54.85,-55.5]:
    ladder.box((-30.0,y,base+3.15),(.05,.05,5.6))
for k in range(18):
    ladder.box((-30.0,-55.175,base+.5+k*.29),(.045,.65,.035))
for h in [2.2,3.2,4.2,5.2,5.85]:
    points=[(-30.0-.4*math.sin(t),-55.175+.4*math.cos(t),base+h) for t in [j*math.pi/12 for j in range(13)]]
    ladder.tube(points,.02,0,6)
for y in [-55.5,-55.175,-54.85]:
    ladder.box((-30.35,y,base+4),(.024,.024,3.7))
finish(ladder,'rear',[metal])
# Pipes drop to the roof surfaces, with estimated positions calibrated to photos.
mesh=Mesh('Fine rear drainage')
for y in [-46.1,-53.4,-61.5]:
    x=D['upper_rear_x']-.10
    height=roof_height(D,D['upper_rear_x'],y)-base-.14
    mesh.tube([(x,y,base+.2),(x,y,base+height)],.045,0,8)
mesh.tube([(-24.95,-55.7,base+rear_height),(-24.95,rear_north,base+rear_height)],.065,0,8)
mesh.tube([(D['upper_rear_x']-.06,y,roof_height(D,D['upper_rear_x'],y)-.14) for y in [ys,-61.48,-55.7]],.065,0,8)
finish(mesh,'rear',[black])

# Halifax occupies nine upper bays, with five ground bays and real entrance depth.
hw=spacing*D['halifax_bays']
pier_centres=[0,3.35,6.70,10.05,13.4,hw]
for i,u in enumerate(pier_centres):
    pw=.46 if i in (0,5) else .55
    elevation_box('Shop granite pier',u,1.62,pw,3.24,.52,-.12,granite,'shopfront')
    for h in [.72,1.48,2.24]:
        elevation_box('Fine granite course joint',u,h,pw,.012,.014,.148,sill,'shopfront')
for i,(a,b) in enumerate(zip(pier_centres,pier_centres[1:])):
    centre=(a+b)/2
    # Continuous reveal and head close the recess right back to the glazing.
    elevation_box('Shop soffit beneath fascia',centre,3.10,b-a-.5,.16,1.0,-.34,metal,'shopfront')
    if i==2:
        elevation_box('Shop recessed entrance shadow',centre,1.545,b-a-.5,3.09,.03,-.82,black,'shopfront')
        elevation_box('Shop entrance threshold',centre,.035,b-a-.50,.07,.95,-.35,charcoal,'shopfront')
        for u in [a+.37,b-.37]:
            elevation_box('Shop entrance jamb',u,1.545,.10,3.09,.75,-.30,metal,'shopfront')
        elevation_box('Shop entrance transom',centre,2.45,b-a-.6,.065,.12,-.14,metal,'shopfront')
        for u in [centre-.58,centre+.58]:
            elevation_box('Shop recessed door leaf',u,1.2,1.12,2.30,.035,-.65,glass,'shopfront')
            elevation_box('Fine entrance pull',u+.40,1.2,.035,.55,.055,-.60,metal,'shopfront')
        sign('entrance number','8-12',centre,2.82,.60,.22,black,white,out=-.14)
    else:
        elevation_box('Shop display glass',centre,1.56,b-a-.5,3.06,.035,-.19,glass,'shopfront')
        for u in [centre-.51,centre+.51]:
            elevation_box('Shop display mullion',u,1.56,.040,3.06,.085,-.13,metal,'shopfront')
        for h in [.18,2.67]:
            elevation_box('Shop display rail',centre,h,b-a-.5,.045,.07,-.12,metal,'shopfront')
# Small manifestation dots are nearby detail, not invented advertising text.
mesh=Mesh('Fine glazing manifestation')
for u in [j*.22 for j in range(int(hw/.22)) if not 6.7<j*.22<10.05]:
    mesh.box((u,1.24,-.145),(.03,.03,.012))
finish(mesh,'shopfront',[white],front)
elevation_box('Shop blue continuous fascia',hw/2,3.57,hw,.78,.28,.05,blue,'shopfront')
for h in [3.16,3.97]:
    elevation_box('Trim Halifax fascia edge',hw/2,h,hw+.10,.045,.36,.07,blue,'shopfront')
sign('Halifax main','HALIFAX',hw/2,3.58,2.15,.74,logo=True,out=.215)
# Photo-led machines have separate display, sloping control recess and backboard.
from frontage import cash_machine
for i,u in enumerate([11.13,12.35]):
    cash_machine(finish,front,u,white,metal,black,blue,glass,font)
# Corner returns into Glebe, as visibly glazed in the November2020 panorama.
for u in [side_width-2.45,side_width-.22]:
    elevation_box('Shop Glebe corner granite',u,1.62,.44,3.24,.5,-.12,granite,'shopfront',side)
elevation_box('Shop Glebe return glass',side_width-1.33,1.56,1.78,3.06,.03,-.18,glass,'shopfront',side)
elevation_box('Shop Glebe fascia return',side_width-1.33,3.57,2.66,.78,.25,.03,blue,'shopfront',side)
elevation_box('Shop Glebe soffit',side_width-1.33,3.10,1.78,.16,.60,-.18,metal,'shopfront',side)
# Number six: dark surround, lower shop fascia, side access door to offices.
shop6=width-hw
# The granite pier owns the shared lower face; a second full-height dark
# pier here placed two different materials on exactly the same plane.
elevation_box('Shop six shared pier head',hw+.10,3.42,.24,.36,.44,-.08,charcoal,'shopfront')
elevation_box('Shop six stone pier',width-.10,1.8,.24,3.6,.44,-.08,charcoal,'shopfront')
elevation_box('Shop six upper dark fascia',hw+shop6/2,3.57,shop6,.78,.32,.03,charcoal,'shopfront')
from frontage import number_six
number_six(elevation_box,finish,front,hw,width,charcoal,metal,black,glass,white)
sign('Post and Packing','Post & Packing',hw+shop6*.40,2.96,shop6*.72,.46,white,blue,out=.13)
# Projecting Halifax sign panels have two separate visible faces.
for u in [.18,hw-.18]:
    frame=face_matrix((xf+.37,ys+u,base+3.57),(0,-1,0))
    sign('Halifax projecting front','HALIFAX',0,0,.62,.38,frame=frame,out=.025)
    frame=face_matrix((xf+.37,ys+u+.06,base+3.57),(0,1,0))
    sign('Halifax projecting back','HALIFAX',0,0,.62,.38,frame=frame,out=.025)

for image in bpy.data.images:
    if image.source == 'FILE':
        image.pack()
s.render.engine = 'CYCLES'
s.cycles.samples = 32
s.cycles.use_denoising = True
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.65,.70,.76,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
light=bpy.data.lights.new('Sun','SUN')
light.energy=2.5
obj=bpy.data.objects.new('Sun',light)
s.collection.objects.link(obj)
obj.rotation_euler=(-.45,.6,.4)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
s.collection.objects.link(camera)
s.camera=camera
camera.data.type='ORTHO'
s.render.resolution_x=1440
s.render.resolution_y=1000
s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-6-12.blend'))
