"""Glebe Place lane, raised throat and rear parking courts.

The London Street asset ends at x=-4.3 in this mouth. No overlapping base asphalt
or yellow paint is exported. Dated imagery establishes shape/material families;
precise widths, levels, bay lengths and concealed boundaries remain estimates.
"""
import json
import math
import os
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(ROOT/'scripts')]
from southport3d.geometry import Mesh
from southport3d.planar import subtract,area,halfplane
from southport3d.conform import conform
from southport3d.road import marking_segments,parallel
from southport3d.landscape import capped_wall
from southport3d.street import furniture
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'
C={}
for name in ['lane-ground','court-ground','furniture']:
    C[name]=bpy.data.collections.new(name)
    s.collection.children.link(C[name])
PAVING=.7845
ROAD=.6645


def material(name,colour,texture=None):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value=(*colour,1)
    shader.inputs['Roughness'].default_value=.9
    if texture:
        node=mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image=bpy.data.images.load(str(ROOT/'textures'/(texture+'.png')))
        mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    return mat


mats={key:material(name,colour,key if key in ['asphalt','paving','blocks','tactile'] else None)
      for key,name,colour in [('asphalt','Authored service asphalt',(.19,.19,.17)),
      ('paving','Pale London Street approach',(.58,.56,.50)),('blocks','Dark raised mouth setts',(.22,.24,.23)),
      ('tactile','Buff tactile pads',(.60,.45,.26)),('kerb','Weathered kerb',(.43,.43,.39)),
      ('yellow','Faded yellow edge paint',(.66,.48,.13)),('white','Worn parking markings',(.60,.60,.55)),
      ('patch','Asphalt repairs',(.14,.15,.145)),('iron','Iron drainage covers',(.12,.13,.12)),
      ('render','Weathered pale yard wall',(.64,.61,.51)),('brick','Yard brick',(.38,.20,.12)),
      ('wood','Utility enclosure timber',(.41,.28,.16)),('metal','Galvanised fittings',(.40,.42,.39)),
      ('dark','Painted black furnishings',(.025,.03,.028))]}
rows=[]
verticals=[]
marking_report=[]


def ccw(points):
    points=[tuple(p) for p in points]
    signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    return points if signed>0 else list(reversed(points))


def surface(name,points,mat,priority=0,z=ROAD,part='lane-ground'):
    points=halfplane(ccw(points),(-4.3,-1000),(-4.3,1000),True)
    if len(points)<3 or area(points)<1e-8:
        return
    for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in points]]):
        poly=[points[v] if isinstance(v,int) else (v.x,v.y) for v in tri]
        rows.append((name,ccw(poly),mat,priority,z,part))


def rect(name,x0,y0,x1,y1,mat,priority=0,z=ROAD,part='lane-ground'):
    surface(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],mat,priority,z,part)


def strip(name,a,b,width,mat,priority=0,z=ROAD,part='lane-ground'):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    nx,ny=-dy/length*width/2,dx/length*width/2
    surface(name,[(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),
                 (b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],mat,priority,z,part)


def throat_grade(x,y):
    # Raised sett apron drops to the carriageway exactly at the ownership seam.
    if x>-5.1:
        return ROAD+.12*max(0,min(1,(-4.3-x)/.8))
    if x<-9.0:
        return ROAD+.12*max(0,min(1,(x+10.6)/1.6))
    return PAVING


# Compact mouth connects the actual building corner and the future Betfred edge.
# The parent London Street mesh has an exact rectangular cutout for this area.
surface('Glebe mouth ground',[(-4.3,-69.4),(-4.3,-63.4),(-10,-63.4),(-10,-69.4)],
        'blocks',20,throat_grade)
surface('Glebe narrow lane',[(-10,-63.4),(-29.9,-63.46),(-39.0,-64.0),
        (-39.0,-70.0),(-26.85,-69.37),(-10,-69.4)],'asphalt')
# Rear court reaches the terrace/Prezzo rear bounds; it is not a wide street.
surface('Rear parking court',[(-50.8,-71.3),(-50.8,-49.0),(-32.2,-49.0),
        (-32.2,-44.0),(-30.5,-44.0),(-30.5,-63.5),(-29.9,-63.5),(-29.9,-70),(-43,-70)],
        'asphalt',0,ROAD,'court-ground')
# A short southern service continuation and visible return parking, bounded for
# later adjoining building work rather than a speculative full alley network.
surface('South service return',[(-43,-70),(-43,-76),(-35.2,-80.7),(-26.5,-80.4),
        (-26.85,-69.37),(-29.9,-70)],'asphalt',0,ROAD,'court-ground')
surface('Service return triangular join',[(-39,-70),(-29.9,-70),(-26.85,-69.37)],'asphalt',0,ROAD,'court-ground')
# Narrow kerb strips, not the old broad invented pavements through the building.
north=[(-4.3,-63.4),(-4.3,-63.65),(-4.5,-63.9),(-4.9,-64.05),(-5.5,-64.1),(-9.8,-64.05),(-29.9,-64.1)]
south=[(-4.3,-69.4),(-4.3,-69.15),(-4.5,-68.9),(-4.9,-68.75),(-5.5,-68.7),(-9.8,-68.75),(-26.85,-68.92)]
for name,curve,inside in [('north',north,-1),('south',south,1)]:
    outer=parallel(curve,inside*.43)
    for a,b,c,d in zip(curve,curve[1:],outer,outer[1:]):
        surface('Glebe narrow kerb strip',[a,b,d,c],'kerb',50,PAVING)
        verticals.append((a,b))
    for offset,(a,b) in marking_segments(curve,-inside):
        strip('Glebe double yellow',a,b,.065,'yellow',200,throat_grade)
        marking_report.append({'edge':name,'offset':offset,'start':a,'end':b})
# The outer wedges share exact boundaries with parent footway pieces.
surface('North rounded approach',[(-10,-63.4),*north[:-1],(-10,-64.05)],'paving',40,PAVING)
surface('South rounded approach',[(-10,-69.4),*south[:-1],(-10,-68.75)],'paving',40,PAVING)
# Two buff pads are observed at the dropped corners. Dimensions are estimated.
rect('North tactile',-8.6,-63.83,-6.8,-63.4,'tactile',90,PAVING)
rect('South tactile',-8.6,-69.4,-6.8,-68.97,'tactile',90,PAVING)
# Central repaired trench stops short of the raised mouth; irregular edges are
# authored interpretation of the patchy asphalt, not a photograph projection.
surface('Patched service trench',[(-10.6,-66.0),(-16,-66.05),(-16.3,-65.9),(-24,-66.3),
        (-30,-66.1),(-38.2,-66.7),(-38.7,-67.5),(-29.9,-67.0),(-23.7,-67.2),
        (-15.8,-66.85),(-10.6,-66.9)],'patch',70)
# Keep parking bays behind the white boundary wall, with a clear service aisle.
for y in [-51,-53.5,-56,-58.5,-61]:
    strip('Rear bay stripe',(-37.1,y),(-31.3,y),.07,'white',160,ROAD,'court-ground')
strip('Rear bay aisle edge',(-37.1,-51),(-37.1,-61),.06,'white',160,ROAD,'court-ground')
# Drainage and access covers are flush, with no near-coplanar overlay.
for x,y,w,h in [(-9,-66.1,1.0,.8),(-32.8,-67.3,.55,.4),(-40,-62.2,.6,.4),(-39,-72,.6,.4)]:
    part='lane-ground' if x>-30 else 'court-ground'
    rect('Drain cover',x-w/2,y-h/2,x+w/2,y+h/2,'iron',170,throat_grade if x>-10.6 else ROAD,part)
    for i in range(4):
        rect('Drain slots',x-w*.37+i*w*.22,y-h*.35,x-w*.32+i*w*.22,y+h*.35,'patch',180,throat_grade if x>-10.6 else ROAD,part)
# All surface winners are clipped before export, including paint and raised
# paving. Float32 conformance joins their boundaries without bright cracks.
rows.sort(key=lambda row:row[3])
compiled={}
for i,(name,poly,mat,priority,z,part) in enumerate(rows):
    pieces=[poly]
    for _,cutter,_,_,_,_ in rows[i+1:]:
        pieces=[p for piece in pieces for p in subtract(piece,cutter)]
        if not pieces:
            break
    for piece in pieces:
        if area(piece)<1e-7:
            continue
        mesh=compiled.setdefault((part,mat),Mesh('Surface '+part+' '+mat))
        mesh.add([(x,y,z(x,y) if callable(z) else z) for x,y in piece],[tuple(range(len(piece)))])
for a,b in verticals:
    mesh=compiled.setdefault(('lane-ground','kerb'),Mesh('Surface lane-ground kerb'))
    za,zb=throat_grade(*a),throat_grade(*b)
    if abs(za-PAVING)<1e-7 and abs(zb-PAVING)<1e-7:
        continue
    mesh.add([(a[0],a[1],za),(b[0],b[1],zb),(b[0],b[1],PAVING),(a[0],a[1],PAVING)],[(0,1,2,3)])
compiled,report=conform(compiled)
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')


def finish(mesh,mat,part='furniture'):
    obj=mesh.finish([mats[mat]],C[part])
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    uv=obj.data.uv_layers.new(name='Metric repeat')
    for face in obj.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
        for loop in face.loop_indices:
            v=obj.data.vertices[obj.data.loops[loop].vertex_index].co
            scale=(4.8,4.8) if mat=='paving' else (1.6,.8) if mat=='blocks' else (1,1) if mat=='tactile' else (3.2,3.2)
            uv.data[loop].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
    return obj


for (part,mat),mesh in compiled.items():
    finish(mesh,mat,part)
# Low rendered retaining/boundary wall is distinct from the Halifax building.
wall=capped_wall([(-30.6,-44.2,ROAD),(-30.6,-60.9,ROAD)],1.45,.27,'Wall rear parking boundary')
finish(wall,'render')
cap=Mesh('Wall rear coping')
cap.box((-30.6,-52.55,ROAD+1.48),(.34,16.7,.09))
finish(cap,'iron')
# Timber utility enclosure observed at the end of the north parking row.
# No service internals or unreadable warning text are fabricated.
wood=Mesh('Envelope timber utility enclosure')
wood.box((-33.2,-62.7,ROAD+1.2),(3.7,3.0,2.4))
finish(wood,'wood')
boards=Mesh('Fine utility board joints')
for i in range(22):
    boards.box((-35.06,-64.15+i*.135,ROAD+1.2),(.018,.014,2.4))
finish(boards,'iron')
rails=Mesh('Fixture utility door ironwork')
for y in [-63.1,-62.35]:
    for h in [.55,1.55]:
        rails.box((-35.08,y,ROAD+h),(.035,.52,.07))
finish(rails,'metal')
# Ribbed black bollards at both sides of the throat are visible in 2020.
fm=[mats['dark'],mats['metal'],mats['white'],mats['dark'],mats['dark'],mats['dark']]
for i,(x,y) in enumerate([(-9.4,-63.55),(-9.4,-69.25)]):
    obj=furniture('bollard','detail','Furniture bollard '+str(i)).finish(fm,C['furniture'])
    obj.location=(x,y,PAVING)
    uv=obj.data.uv_layers.new(name='Furniture UV')
    for loop in obj.data.loops:
        v=obj.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(v.x,v.z)
(ROOT/'research/marking-centrelines.json').write_text(json.dumps(marking_report,indent=2)+'\n')
for im in bpy.data.images:
    if im.source=='FILE':
        im.pack()
s.render.engine='CYCLES'
s.cycles.samples=24
s.cycles.use_denoising=True
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
light=bpy.data.lights.new('Sun','SUN')
light.energy=2.5
obj=bpy.data.objects.new('Sun',light)
s.collection.objects.link(obj)
obj.rotation_euler=(-.6,.6,0)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
s.collection.objects.link(camera)
s.camera=camera
camera.data.type='ORTHO'
s.render.resolution_x=1440
s.render.resolution_y=1000
s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/glebe-place.blend'))
