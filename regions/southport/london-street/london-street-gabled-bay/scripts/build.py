"""Observed cream gabled bay immediately south of 24 London Street, metric source."""
import json, math, os, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh,face_matrix
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
black=material('Recess shadow',(.025,.028,.03))
felt=material('Pale weathered felt',(.35,.37,.35));metal=material('Galvanized metal',(.43,.46,.45))
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


cream=material('Cream lintels and soffit',(.68,.67,.61))
stone=material('Grey cast stone sill',(.45,.46,.43))
# Two upper sash windows in the cream bay; brick edge piers are observed.
bays=[1.55,width-1.55]
openings=[(u-.49,u+.49,4.80,6.25) for u in bays]+[(.23,width-.23,0,3.19)]
wall_with_openings('cream gabled street face',front,width,7.25,openings,mat=cream)
for u in [.15,width-.15]:
 elevation_box('Trim brick edge pier',u,5.25,.30,4.0,.17,.035,brick)
 elevation_box('Trim brick pier foot',u,3.30,.37,.16,.25,.045,brick)
for i,u in enumerate(bays):
 m=Mesh('Window upper sash %d'%i);m.box((0,0,-.14),(.98,1.45,.025),0)
 for x in [-.46,.46]:m.box((x,0,-.07),(.06,1.45,.10),1)
 for h in [-.70,0,.70]:m.box((0,h,-.055),(.92,.05,.13),1)
 m.box((0,0,-.095),(.035,1.35,.05),1)
 finish(m,materials=[glass,white],transform=front@Matrix.Translation((u,5.525,0)))
 elevation_box('Trim upper lintel',u,6.32,1.16,.14,.14,-.025,cream)
 elevation_box('Trim upper sill',u,4.74,1.18,.12,.24,.045,stone)
# Continuous roof wing: ridge is parallel to street and continues toward26/28.
mainrear=xf-D['main_depth'];rf=face_matrix((mainrear,yn,base),(-1,0,0))
wall_with_openings('main rear wall',rf,width,7.25,[],'rear')
for label,frame in [('north',side@Matrix.Translation((.36,0,0))),('south',face_matrix((mainrear+.36,ys,base),(0,-1,0)))]:wall_with_openings('party '+label,frame,D['main_depth']-.72,7.25,[])
xe=xf+.12;xb=mainrear-.10;ridge=(xe+xb)/2;ze=base+7.25;zr=base+9.20
# Roof union: cross-gable and main pitch meet on shared valley edges, not overlapping planes.
cy=(ys+yn)/2
v=[(xe,ys,ze),(xe,yn,ze),(ridge,yn,zr),(ridge,ys,zr),(xb,ys,ze),(xb,yn,ze),(xe,cy,zr),(ridge,cy,zr)]
top=[(0,6,7),(6,1,7),(0,7,3),(1,2,7),(3,7,2,5,4)]
boundary=[0,6,1,2,5,4,3]
faces=top+[tuple(i+8 for i in reversed(f)) for f in top]+[(i,j,j+8,i+8) for i,j in zip(boundary,boundary[1:]+boundary[:1])]
m=Mesh('Roof continuous pitched shell');m.add(v+[(x,y,z-.14) for x,y,z in v],faces);finish(m,'roof',[slate],roof_uv=True)
# Cream triangular front with real shallow vent recess; plinth below is the open-window wall.
m=Mesh('Envelope cream front gable');m.add([(0,7.25,-.36),(width,7.25,-.36),(width/2,9.12,-.36),(0,7.25,0),(width,7.25,0),(width/2,9.12,0)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);finish(m,materials=[cream],transform=front)
# Dark bargeboard follows the two pitched edges. Box beams are oriented in facade XY.
for a,b in [((0,7.28),(width/2,9.24)),((width/2,9.24),(width,7.28))]:
 du,dh=b[0]-a[0],b[1]-a[1];m=Mesh('Trim gable bargeboard');m.box((0,0,0),(math.hypot(du,dh),.13,.14));finish(m,materials=[coping],transform=front@Matrix.Translation(((a[0]+b[0])/2,(a[1]+b[1])/2,.08))@Matrix.Rotation(math.atan2(dh,du),4,'Z'))
elevation_box('Fixture gable vent shadow',width/2,7.78,.24,.44,.012,.005,black)
for h in [7.62+i*.075 for i in range(5)]:elevation_box('Fine gable vent slat',width/2,h,.23,.025,.025,.025,stone)
box('Trim ridge cap',(ridge,(ys+yn)/2,zr+.025),(.16,width,.10),slate,'roof')
# Close triangular end wall below the roof without assuming a visible decorative gable.
for yy,dy in [(yn-.12,.24),(ys+.12,.24)]:
 m=Mesh('Envelope roof end infill');m.add([(xf-.15,yy-dy/2,ze-.05),(mainrear+.15,yy-dy/2,ze-.05),(ridge,yy-dy/2,zr-.12),(xf-.15,yy+dy/2,ze-.05),(mainrear+.15,yy+dy/2,ze-.05),(ridge,yy+dy/2,zr-.12)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);finish(m,materials=[brick])
# No straight fascia across the cream front gable.
box('Trim rear fascia',(mainrear-.04,(ys+yn)/2,base+7.15),(.15,width,.20),coping,'roof')
# Gutter and downpipe deliberately authored low-cost sections, not generic furniture.
# Gable edge drains toward the adjoining valley; no horizontal gutter across its face.
elevation_box('Fixture rainwater pipe',width-.31,3.65,.075,7.15,.09,.16,coping)
for h in [.55,2.25,4.15,6.1]:elevation_box('Fine rainwater bracket',width-.31,h,.13,.06,.08,.205,metal)
# Conservative lower rear store follows the aerial massing; detailed access is estimated.
wh=3.42;wingdepth=mainrear-xr
box('Roof rear flat deck',((mainrear+xr)/2,(ys+yn)/2,base+wh-.09),(wingdepth-.03,width-.06,.18),felt,'roof')
for label,frame in [('north',face_matrix((mainrear,yn,base),(0,1,0))),('south',face_matrix((xr+.36,ys,base),(0,-1,0)))]:wall_with_openings('rear store '+label,frame,wingdepth-.36,wh,[],'rear')
wall_with_openings('rear loading wall',rear,width,wh,[(1.75,3.05,0,2.25)],'rear')
elevation_box('Shop rear loading door',2.4,1.125,1.3,2.25,.06,-.10,metal,'rear',rear)
for y in [ys+.10,yn-.10]:box('Trim rear low coping',((mainrear+xr)/2,y,base+wh+.06),(wingdepth,.23,.15),coping,'roof')
box('Trim rear end coping',(xr+.10,(ys+yn)/2,base+wh+.06),(.23,width-.20,.15),coping,'roof')
# Observed dark shop fascia and glazing; tenant lettering is not legible.
for u in [.12,width-.12]:elevation_box('Shop brick entrance pier',u,1.62,.24,3.24,.28,-.035,brick,'shopfront')
elevation_box('Shop dark fascia',width/2,3.46,width-.35,.63,.15,.015,black,'shopfront')
# Shop lettering is unreadable in the retained image; deliberately not invented.
elevation_box('Trim shop fascia cap',width/2,3.83,width-.15,.09,.25,.06,white,'shopfront')
# Main display to south, recessed single entrance at northern side.
door=width-.86;left=.26;right=door-.57
for a,b in [(left,(left+right)/2),((left+right)/2,right)]:
 elevation_box('Shop display glazing',(a+b)/2,1.55,b-a,2.77,.03,-.17,glass,'shopfront')
 for u in ([a,b] if a==left else [b]):elevation_box('Shop display stile',u,1.55,.045,2.83,.07,-.105,coping,'shopfront')
 for h in [.17,2.94]:elevation_box('Shop display rail',(a+b)/2,h,b-a,.05,.07,-.105,coping,'shopfront')
elevation_box('Shop low painted plinth',(left+right)/2,.09,right-left,.18,.22,-.04,cream,'shopfront')
elevation_box('Shop door recess',door,1.45,1.12,2.90,.03,-.40,black,'shopfront')
elevation_box('Shop door glass',door,1.32,1.0,2.60,.03,-.32,glass,'shopfront')
for u in [door-.52,door+.52]:elevation_box('Shop door stile',u,1.33,.055,2.66,.09,-.255,coping,'shopfront')
for h in [.025,2.63]:elevation_box('Shop door rail',door,h,1.10,.05,.09,-.255,coping,'shopfront')
elevation_box('Shop door transom',door,2.82,1.10,.29,.03,-.31,glass,'shopfront')
elevation_box('Shop entry threshold',door,.035,1.14,.07,.45,-.17,stone,'shopfront')
elevation_box('Fine shop handle',door-.33,1.15,.025,.35,.06,-.19,metal,'shopfront')
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
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-street-gabled-bay.blend'))
