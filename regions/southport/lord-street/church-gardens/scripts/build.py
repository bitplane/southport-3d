"""Two bounded Lord Street gardens, with explicit surfaces and open entrances."""
import json
import math
import os
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(Path(os.environ['SOUTHPORT_REPO_ROOT']) / 'lib'), str(ROOT / 'scripts')]
from southport3d.geometry import Mesh
from southport3d.landscape import capped_wall, tree
from southport3d.street import furniture
from southport3d.planar import subtract, area, halfplane
from southport3d.road import marking_segments
from southport3d.conform import conform
from components import hedge, lantern

D = json.loads((ROOT / 'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
collections = {}
for place in ['christ', 'george']:
    for kind in ['ground', 'furniture']:
        name = place + '-' + kind
        collections[name] = bpy.data.collections.new(name)
        scene.collection.children.link(collections[name])


def material(name, colour, texture=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = .85
    if texture:
        image = mat.node_tree.nodes.new('ShaderNodeTexImage')
        image.image = bpy.data.images.load(str(ROOT / 'textures' / (texture + '.png')))
        mat.node_tree.links.new(image.outputs['Color'], shader.inputs['Base Color'])
        normal = mat.node_tree.nodes.new('ShaderNodeTexImage')
        normal.image = bpy.data.images.load(str(ROOT / 'textures' / (texture + '-normal.png')))
        normal.image.colorspace_settings.name = 'Non-Color'
        decode = mat.node_tree.nodes.new('ShaderNodeNormalMap')
        mat.node_tree.links.new(normal.outputs['Color'], decode.inputs['Color'])
        mat.node_tree.links.new(decode.outputs['Normal'], shader.inputs['Normal'])
    return mat


mats = {
    'paving': material('Authored pale garden slabs', (.6,.58,.52), 'paving'),
    'path': material('Authored buff church path blocks',(.46,.43,.36),'path'),
    'brick': material('Authored red-brown forecourt pavers', (.44,.30,.23), 'brick'),
    'asphalt': material('Authored Lord Street asphalt', (.08,.09,.09), 'asphalt'),
    'grass': material('Late summer lawn', (.27,.32,.14)),
    'bed': material('Planted earth', (.13,.10,.065)),
    'kerb': material('Pale granite kerb', (.40,.40,.36)),
    'stone': material('Weathered garden sandstone', (.39,.37,.28), 'stone'),
    'wallbrick': material('Weathered red boundary brick', (.39,.23,.17), 'wallbrick'),
    'yellow': material('Faded yellow road marking', (.65,.47,.10)),
    'white': material('Worn white road marking', (.69,.68,.60)),
}
fm = [material('Dark painted iron',(.025,.033,.031)), material('Galvanised metal',(.45,.48,.47)),
      material('Pale glazing',(.53,.56,.50)), material('Button edging',(.8,.48,.015)),
      material('Red lens',(.14,.008,.008)), material('Amber lens',(.16,.075,.005)),
      material('Green lens',(.004,.10,.035)), material('Bench timber',(.25,.20,.13)),
      material('Dark openings',(.006,.008,.008))]
foliage = [material('Hedge dark',(.075,.13,.035)), material('Hedge green',(.14,.23,.07)), material('Hedge leaf variation',(.19,.27,.085))]
tm = [material('Tree bark',(.14,.11,.075)), *foliage]
rows, verticals, placements, walls = [], [], [], []


def grade(y):
    return D['grade']['origin_z'] + D['grade']['dz_dy'] * max(-36,min(36,y))


def surface(place, points, mat, priority=0, drop=0):
    points = [tuple(p) for p in points]
    x0,_,x1,y1=D['bounds'][place]
    ymin=D['bounds'][place][1] if place=='christ' else -27
    for a,b in [((x0,ymin),(x1,ymin)),((x1,ymin),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,ymin))]:
        points=halfplane(points,a,b,True)
    if len(points)<3:return
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])) < 0:
        points.reverse()
    for triangle in tessellate_polygon([[Vector((x,y,0)) for x,y in points]]):
        poly = [points[p] if isinstance(p,int) else (p.x,p.y) for p in triangle]
        rows.append((place, poly, mat, priority, drop))


def rect(place, x0,y0,x1,y1,mat,priority=0,drop=0):
    surface(place, [(x0,y0),(x1,y0),(x1,y1),(x0,y1)], mat, priority, drop)


def strip(place, points, width, mat, priority=0, drop=0):
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        nx,ny=-dy/length*width/2,dx/length*width/2
        surface(place,[(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],mat,priority,drop)
    # Round joins, clipped into the same surface batch (no stacked faces).
    for x,y in points[1:-1]:
        surface(place,[(x+width/2*math.cos(t*math.tau/12),y+width/2*math.sin(t*math.tau/12)) for t in range(12)],mat,priority,drop)


def kerb(place, points, inside=1):
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        nx,ny=-dy/length*.19*inside,dx/length*.19*inside
        surface(place,[a,b,(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)],'kerb',180)
        verticals.append((place,a,b))


def paint(place, points, side, bounds=None):
    for offset,segment in marking_segments(points,side,bounds):
        strip(place,segment,.075,'yellow',300,-.12)


def wall(place, points, height=.70, brick=False):
    mesh=capped_wall([(x,y,grade(y)) for x,y in points],height,.32,'Wall '+place+' boundary')
    ob=mesh.finish([mats['wallbrick' if brick else 'stone']],collections[place+'-furniture'])
    # Vertical masonry uses metres, not a stretched facade atlas.
    uv=ob.data.uv_layers.new(name='Masonry metric repeat')
    for face in ob.data.polygons:
        for loop in face.loop_indices:
            p=ob.data.vertices[ob.data.loops[loop].vertex_index].co
            uv.data[loop].uv=((p.x if abs(face.normal.y)>.5 else p.y)/2.4,p.z/2.4)
    walls.append({'place':place,'xy':points,'height':height})


prototypes={}

def item(place, kind,x,y,yaw=0,scale=(1,1,1)):
    if kind not in prototypes:
        if kind=='tree': mesh,materials=tree('detail','Tree '+place),tm
        elif kind=='hedge': mesh,materials=hedge('detail','Hedge '+place),foliage
        elif kind=='lantern': mesh,materials=lantern('detail','Lantern '+place),fm
        else: mesh,materials=furniture(kind,'detail','Furniture '+kind+' '+place),fm
        ob=mesh.finish(materials,collections[place+'-furniture'])
        prototypes[kind]=ob
    else:
        ob=prototypes[kind].copy()
        ob.data=prototypes[kind].data
        collections[place+'-furniture'].objects.link(ob)
    ob.location=(x,y,grade(y)+(.45 if place=='christ' and kind=='tree' else 0))
    ob.rotation_euler.z=math.radians(yaw)
    ob.scale=scale
    ob['evidence']='Street View family; placement/dimensions visually estimated'
    placements.append({'kind':kind,'place':place,'xy':[x,y]})
    return ob


def hedge_line(place,points,height=.85):
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b)
        count=max(1,math.ceil(length/2))
        for i in range(count):
            t=(i+.5)/count
            item(place,'hedge',a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),
                 math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),(length/count,1,height))


for place,bounds in D['bounds'].items():
    x0,y0,x1,y1=bounds
    rect(place,x0,y0,x1,y1,'paving')
    rect(place,x0,21,x1,31,'asphalt',100,-.12)
    kerb(place,[(x0,31),(x1,31)],1)
    if place=='christ':
        # Garden entrances are flush block paving. Yellow lines continue across
        # these accesses as observed, while no physical kerb obstructs them.
        for a,b in [(x0,-134),(-128.6,-103),(-98.6,x1)]:
            kerb(place,[(a,21),(b,21)],-1)
        paint(place,[(x0,21),(x1,21)],1,bounds)
        rect(place,-77,-27,-73,-23.6,'paving')
    else:
        kerb(place,[(x0,21),(x1,21)],-1)
        # No guessed double yellow across the observed church-side parking /
        # pedestrian-crossing area. Junction mouth separates this from old tile.
    for x in range(math.floor(x0/6)*6,math.ceil(x1/6)*6,6):
        start,end=max(x0,x),min(x1,x+2)
        if end>start:strip(place,[(start,25.6),(end,25.6)],.10,'white',300,-.12)
    for path in D['paths'][place]:
        strip(place,path['xy'],path['width'],'path' if place=='christ' else 'paving',80)
    for x,y,scale in D['trees'][place]:item(place,'tree',x,y,0,(scale,scale,scale))
    for x,y,yaw in D['benches'][place]:item(place,'bench',x,y,yaw)

# Christ Church lawns and two intersecting approaches. The path widths and
# rounded corners are interpreted from aerial and ground views, not a survey.
def raised_lawn(points, south, west, east):
    # Low path edge blends into a raised plateau. The road-facing end is retained.
    def rise(x,y):return min(.45,.07+max(0,y-south)*.28,.07+max(0,x-west)*.28,.07+max(0,east-x)*.28)
    for x in range(math.floor(min(p[0] for p in points)),math.ceil(max(p[0] for p in points)),2):
        for y in range(math.floor(min(p[1] for p in points)),math.ceil(max(p[1] for p in points)),2):
            cell=points[:]
            for a,b in [((x,y),(x+2,y)),((x+2,y),(x+2,y+2)),((x+2,y+2),(x,y+2)),((x,y+2),(x,y))]:cell=halfplane(cell,a,b,True)
            if len(cell)>2:surface('christ',cell,'grass',40,rise)

raised_lawn([(-128,-17.8),(-105,-17.8),(-103,-13),(-104,16.9),(-127.7,16.9)],-17.8,-128,-103)
raised_lawn([(-97.4,-16.0),(-79.5,-16.0),(-77,-15.2),(-75.5,-13.0),(-75.5,17.5),(-97.7,17.5)],-16,-97.7,-72.5)
strip('christ',[(-73,-20.4),(-86.8,-20.34),(-99.9,-20.47),(-115.25,-22.06),(-128,-22.6)],5.0,'path',85)
# Retaining wall follows the service-road end; only low kerb edging follows
# the pedestrian approach. Keep the entry beside BHF open.
wall('christ',[(-75.3,-13.0),(-75.3,17.8)],.55,True)
wall('christ',[(-97.4,-16),(-79.5,-16),(-77,-15.2),(-75.5,-13)],.085)
# Raise only the short entrance landings out of the road, keeping a continuous
# accessible apron. Ramped meshes below replace the carriageway in each mouth.
for x,width in [(-100.9,4.2),(-131.3,5.2)]:
    rect('christ',x-width/2,19,x+width/2,21.5,'path',210,lambda x,y:-.12*max(0,min(1,(y-19)/2)))
for a,b in [(-127.6,-104.2),(-97.5,-73)]:
    wall('christ',[(a,17.8),(b,17.8)],.70)
wall('christ',[(-127.7,-17.5),(-127.7,16.9)],.52,True)
# Former diagonal brick wall removed: this is an open pedestrian path edge.
for x in [-103.2,-98.4]:
    wall('christ',[(x,17.5),(x,18.1)],.90)
for x in [-102.2,-100.8,-99.4]:item('christ','bollard',x,12.6)
for y in [-22.7,-20.8,-18.9]:item('christ','bollard',-74.0,y)
for x,y in [(-104,20.0),(-126,19.8),(-75,-18.5)]:item('christ','bin',x,y)
item('christ','lantern',-77.5,-16.8)
item('christ','streetlight',-118,32.1)
item('christ','streetlight',-86,32.1)
hedge_line('christ',[(-105,13.5),(-105,16.6)],.9)
hedge_line('christ',[(-97,13.5),(-97,16.6)],.9)

# St George's hedge garden follows the mapped park edge. Church and the
# neighbouring building are reserved for later architecture assets.
surface('george',[(156.1,-11.0),(165.9,-14.8),(179,-14.8),(185.9,-13.9),(204.2,-13.1),(214,-13.1),(214.6,14.8),(212.3,18.7),(155.5,18.7)],'grass',40,.02)
strip('george',[(155,-10),(169,-13),(179,-13)],4.0,'paving',85)
strip('george',[(167,1),(177,1),(180,-12)],2.2,'paving',85)
# Dark beds back the clipped hedges; patches are deliberately simple, with no
# invented flower species or photographic textures.
for x0,x1 in [(156.5,163),(173,184),(197,213)]:
    rect('george',x0,13.6,x1,17.7,'bed',50,.025)
hedge_line('george',[(155.9,-9.5),(155.6,6.2)],.85)
hedge_line('george',[(156.6,17.6),(164.7,17.6)],.9)
hedge_line('george',[(169.1,17.6),(188.9,17.6)],1.0)
hedge_line('george',[(193.2,17.6),(213.0,17.6)],.9)
hedge_line('george',[(156.4,-10.5),(164,-13.8)],.8)
wall('george',[(181,-13.5),(187,-13.5)],.45,True)
for x,y in [(166,19.6),(191,19.8)]:item('george','bin',x,y)
for x,y in [(163,32.1),(200,32.1)]:item('george','streetlight',x,y)
# White flagpole is visible beside the church entrance; neither flag nor text
# is invented where the reference does not establish it.
flag=Mesh('Street St George flagpole')
flag.lathe((163,-5),[(grade(-5),.055),(grade(-5)+7.2,.025)],12)
flag.finish([mats['paving']],collections['george-furniture'])

# Partition all surfaces by material priority, so paving, lawns, paint and paths
# occupy one visible surface. Conform the clipped fragments before GLB float32.
compiled={}
for i,(place,poly,mat,priority,drop) in enumerate(rows):
    fragments=[poly]
    minx,miny=min(p[0] for p in poly),min(p[1] for p in poly)
    maxx,maxy=max(p[0] for p in poly),max(p[1] for p in poly)
    for j,(other,cut,_,other_priority,_) in enumerate(rows):
        if other!=place or (other_priority,j)<=(priority,i):continue
        if max(p[0] for p in cut)<minx or min(p[0] for p in cut)>maxx or max(p[1] for p in cut)<miny or min(p[1] for p in cut)>maxy:continue
        fragments=[piece for fragment in fragments for piece in subtract(fragment,cut)]
        if not fragments:break
    mesh=compiled.setdefault((place,mat),Mesh('Surface '+place+' '+mat))
    for poly in fragments:
        if area(poly)>1e-7:
            mesh.add([(x,y,grade(y)+(drop(x,y) if callable(drop) else drop)) for x,y in poly],[tuple(range(len(poly)))])
for place,a,b in verticals:
    mesh=compiled.setdefault((place,'kerb'),Mesh('Surface '+place+' kerb'))
    mesh.add([(a[0],a[1],grade(a[1])-.12),(b[0],b[1],grade(b[1])-.12),(b[0],b[1],grade(b[1])),(a[0],a[1],grade(a[1]))],[(0,1,2,3)])
compiled,report=conform(compiled)
for (place,mat),mesh in compiled.items():
    if not mesh.faces:continue
    ob=mesh.finish([mats[mat]],collections[place+'-ground'])
    uv=ob.data.uv_layers.new(name='Metric surface repeat')
    for face in ob.data.polygons:
        for loop in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[loop].vertex_index].co
            uv.data[loop].uv=(v.x/3.6,v.y/3.6)
(ROOT/'research/geometry-report.json').write_text(json.dumps({'conform':report,'placements':placements,'walls':walls},indent=2))
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.70,.75,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.5
sun=bpy.data.lights.new('Sun','SUN')
sun.energy=2.5
ob=bpy.data.objects.new('Sun',sun)
scene.collection.objects.link(ob)
ob.rotation_euler=(-.6,.6,0)
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
scene.collection.objects.link(camera)
scene.camera=camera
camera.data.type='ORTHO'
scene.render.resolution_x=1440
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
