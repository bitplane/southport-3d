"""One floor owner for the church side court and Corporation Street link."""
import bpy,bmesh,json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.elevation import Elevations
from southport3d.road import parallel
from southport3d.street import furniture
from plan_geometry import Plan
from components import tree,hedge
from boundary import continuous_wall
from datum import grade
sys.path.insert(0,str(REPO/'regions/southport/station-quarter/public-realm/scripts'))
from bhs_arcade_support import approach_polygon,approach_mesh,outer_x
D=json.loads((ROOT/'research/layout.json').read_text())
G=json.loads((REPO/D['garden_handover_source']).read_text())
CH=json.loads((REPO/D['building_source']).read_text())
ST=json.loads((REPO/D['station_ground_source']).read_text())
arcade=json.loads((REPO/'regions/southport/corporation-street/former-bhs/research/arcade-support.json').read_text())
station=Elevations(REPO/'regions/southport/elevation/station-approach.json').surface('chapel-pedestrian')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';cols={}
for name in ['court-ground','passage-ground','court-furniture','passage-furniture']:
    c=bpy.data.collections.new(name);s.collection.children.link(c);cols[name]=c


def rect(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def ribbon(points,width):return parallel(points,-width/2)+list(reversed(parallel(points,width/2)))
P=Plan();x0,x1,y0,y1=D['bounds']
region=P.polygons([rect(x0,x1,y0,y1),G['approach_handover_polygon'],D['former_bhs_court'],D['former_bhs_arcade']])
clip_x0=min(x0,min(x for x,y in D['former_bhs_court']),min(x for x,y in D['former_bhs_arcade']))
cutters=[CH['mapped_footprint']]
for path in D['block_plans']:cutters += [b['footprint']for b in json.loads((REPO/path).read_text())['blocks'] if b['id'] not in ('hugo-frontage','hugo-rear-range')]
cutters += D['former_bhs_occupied']
station_claim=P.intersection(P.polygons(ST['ground_polygons']),P.polygons([rect(*ST['bounds'])]))
available=P.difference(P.difference(region,P.polygons(cutters)),station_claim)
arcade_shape=P.polygons([approach_polygon(arcade)])
arcade_clip=P.intersection(available,arcade_shape)
arcade_tris=P.triangles(arcade_clip)
arcade_area=sum(abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2 for a,b,c in arcade_tris)
assert abs(arcade_area-arcade['width_m']*(arcade['approach_end_y']-arcade['wall_station_edge'][1]))<.0001,arcade_area
available=P.difference(available,arcade_shape)
# West of the station's clipped arcade floor, this owner's narrow strip must
# follow the same rough surface along their shared edge. It previously retained
# the higher approach datum and made a visible step in the passage.
south=arcade['wall_south'];north=arcade['wall_station_edge']
west_shape=P.polygons([rect(south[0]-8,south[0]-1,south[1]-.5,north[1])])
arcade_west=P.intersection(available,west_shape)
available=P.difference(available,west_shape)
lawn=P.intersection(available,P.polygons([D['lawn']]))
brick=P.difference(P.intersection(available,P.polygons([D['brick_court']])),lawn)
remaining=P.difference(P.difference(available,lawn),brick)
# Photograph shows longitudinal dark slab bands through Corporation Street.
strips=P.intersection(remaining,P.polygons([ribbon(p,.15)for p in [[(-130,-72),(-129,-122)],[(-125.2,-72),(-125.2,-122)]]]))
paving=P.difference(remaining,strips)


def segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)


def rise(x,y):
    q=D['lawn'];d=min(segment_distance((x,y),a,b)for a,b in zip(q,q[1:]+q[:1]))
    return min(.45,.07+.28*d)

compiled={}
for part,lo,hi in [('court',D['split_y'],-18.0),('passage',y0,D['split_y'])]:
    for mat,g in [('paving',paving),('strip',strips),('brick',brick),('grass',lawn)]:
        m=Mesh('Surface '+part+' '+mat)
        if mat=='grass':
            # A metre grid represents the estimated raised margins explicitly.
            for x in range(-128,-116):
                for y in range(-59,-17):
                    aa,bb=max(y,lo),min(y+1,hi)
                    if aa>=bb:continue
                    cell=P.polygons([rect(x,x+1,aa,bb)])
                    for tri in P.triangles(P.intersection(g,cell)):m.add([(x,y,0)for x,y in tri],[(0,1,2)])
        else:
            cuts=[lo,*[v for v in [-95,-93,-45,-36,-35,-29.72]if lo<v<hi],hi]
            for a,b in zip(cuts,cuts[1:]):
                cell=P.polygons([rect(clip_x0,x1,a,b)])
                for tri in P.triangles(P.intersection(g,cell)):m.add([(x,y,0)for x,y in tri],[(0,1,2)])
        if m.faces:compiled[(part,mat)]=m
arcade_ground=Mesh('Surface passage arcade-transition');approach_mesh(arcade_ground,station,arcade)
# Conform all owners in plan; restore the authored ramp heights below.
arcade_ground.vertices=[(x,y,0) for x,y,z in arcade_ground.vertices]
compiled[('passage','arcade-transition')]=arcade_ground
west_ground=Mesh('Surface passage arcade-west')
for tri in P.triangles(arcade_west):
 for lifted in station.lift_triangle(tri):west_ground.add([(x,y,0)for x,y,z in lifted],[(0,1,2)])
if west_ground.faces:compiled[('passage','arcade-west')]=west_ground
P.close()
# Shared slab, grass and ownership vertices are conformed on the plan first.
import southport3d.conform as cf
cf.GRID=1e-4;cf.TOLERANCE=2e-4
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled)
# The station ground retains a finer plan grid. Re-project the west handover
# vertices to that shared source edge after the approach's coarser conformance,
# so float32 exports meet without a microscopic overlapping strip.
west0,west1=ST['ground_polygons'][3][0],ST['ground_polygons'][3][3]
def west_edge(y):return west0[0]+(y-west0[1])*(west1[0]-west0[0])/(west1[1]-west0[1])
west=compiled.get(('passage','arcade-west'))
if west:
 west.vertices=[(float(np.float32(west_edge(y))) if abs(x-west_edge(y))<.00011 else x,y,z)for x,y,z in west.vertices]
# Blend the bounded arcade support to the retained rough station surface at
# its actual y=-95 edge over two metres; elsewhere preserve approach grade.
def support_grade(x,y):
 if -168<=x<=-158 and -95.0001<=y<-93:
  f=max(0,min(1,(y+95)/2))
  # Keep the edge beside the new BHS transition linear on the same seam.
  slope=(arcade['wall_station_edge'][0]-arcade['wall_south'][0])/(arcade['wall_station_edge'][1]-arcade['wall_south'][1])
  return (1-f)*station.height(x-slope*(y+95),-95)+f*grade(x,y)
 return grade(x,y)
def arcade_grade(x,y):
 y0=arcade['wall_station_edge'][1];y1=arcade['approach_end_y']
 u=max(0,min(1,(x-outer_x(arcade,y))/arcade['width_m']));v=max(0,min(1,(y-y0)/(y1-y0)))
 base=station.height(outer_x(arcade,y0),y0)
 return base+max(u,v)*(arcade['building_grade_m']-base)
for (part,mat),m in compiled.items():
 m.vertices=[(x,y,arcade_grade(x,y) if mat=='arcade-transition' else station.height(x,y) if mat=='arcade-west' else support_grade(x,y)+(rise(x,y)if mat=='grass'else 0))for x,y,z in m.vertices]
# Frontage transition owns its bounded patch; its outer edge follows the existing
# rough station surface including control-grid break points, and inner edge meets
# the level architectural datum. It is an estimate, not a terrain refinement.
threshold=Mesh('Surface passage threshold');innerL,innerR,outerR,outerL=D['former_bhs_threshold']
station=Elevations(REPO/'regions/southport/elevation/station-approach.json').surface('chapel-pedestrian')
outer=list(station.edge_points(outerL,outerR));dx=outerR[0]-outerL[0];dy=outerR[1]-outerL[1];den=dx*dx+dy*dy
for a,b in zip(outer,outer[1:]):
 def inside(p):
  t=((p[0]-outerL[0])*dx+(p[1]-outerL[1])*dy)/den
  return (innerL[0]+t*(innerR[0]-innerL[0]),innerL[1]+t*(innerR[1]-innerL[1]),.7845)
 ia,ib=inside(a),inside(b);threshold.add([a,b,ib,ia],[(0,1,2),(0,2,3)])
compiled[('passage','threshold')]=threshold
# The turf has a small physical edge inside this owner's paved footprint.
# Ownership cuts remain separate from the photographed lawn boundaries.
edge=Mesh('Surface court lawn edging')
for a,b in zip(D['lawn'],D['lawn'][1:]+D['lawn'][:1]):
    edge.add([(a[0],a[1],grade(*a)),(b[0],b[1],grade(*b)),(b[0],b[1],grade(*b)+.07),(a[0],a[1],grade(*a)+.07)],[(0,1,2,3)])
compiled[('court','edging')]=edge


def material(name,colour,texture=None):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*colour,1)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=.85
    if texture:
        for suffix,normal in [('',False),('-normal',True)]:
            im=bpy.data.images.load(str(ROOT/'textures'/(texture+suffix+'.png')),check_existing=True);im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im
            if normal:
                im.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
            else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    return m
mats={'paving':material('Pale passage slabs',(.56,.54,.48),'paving'),'strip':material('Dark longitudinal slab bands',(.21,.23,.23)),'brick':material('Church court brick pavers',(.44,.30,.23),'brick'),'grass':material('Estimated raised lawn',(.24,.31,.12)),'edging':material('Low garden stone edge',(.42,.41,.35)),'threshold':material('Estimated frontage threshold',(.56,.54,.48),'paving')}
mats['arcade-transition']=mats['paving']
mats['arcade-west']=mats['paving']
wallm=[material('Observed red-brick boundary',(.39,.23,.17),'wallbrick'),material('Pale stone coping',(.45,.44,.37),'stone')]
fm=[material('Approach furnishing '+str(i),c)for i,c in enumerate([(.025,.033,.031),(.45,.48,.47),(.53,.56,.50),(.8,.48,.015),(.14,.008,.008),(.16,.075,.005),(.004,.10,.035),(.25,.20,.13),(.006,.008,.008)])]
fol=[material('Planting bark',(.14,.11,.075)),material('Foliage dark',(.075,.13,.035)),material('Foliage green',(.14,.23,.07)),material('Foliage light',(.19,.27,.085))]


def finish(m,materials,c,uv_scale=3.6):
    ob=m.finish(materials,cols[c]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.update();uv=ob.data.uv_layers.new(name='Metric surface UV')
    for face in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/uv_scale,v[axes[1]]/uv_scale)
    return ob
for (part,mat),m in compiled.items():finish(m,[mats[mat]],part+'-ground')
bpy.context.view_layer.update()

def turf_contact(x,y):
    from mathutils import Vector
    heights=[]
    for ob in cols['court-ground'].objects:
        hit,p,n,index=ob.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
        if hit and n.z>.2:heights.append(p.z)
    assert heights,(x,y,'no authored turf beneath furniture')
    return max(heights)

w=D['wall'];wall_xy=[]
for a,b in zip(w['xy'],w['xy'][1:]):
    wall_xy.append(a)
    for y in sorted([v for v in [-45,-35] if min(a[1],b[1])<v<max(a[1],b[1])],reverse=b[1]<a[1]):
        t=(y-a[1])/(b[1]-a[1]);wall_xy.append((a[0]+t*(b[0]-a[0]),y))
wall_xy.append(w['xy'][-1]);points=[(x,y,grade(x,y))for x,y in wall_xy];mesh=continuous_wall(points,w['height_m'],w['width_m'],'Wall continuous side garden')
for i in range(2,len(mesh.faces)):mesh.indices[i]=1 if (i-2)%8 in [2,3,4,5,6]else 0
finish(mesh,wallm,'court-furniture',2.4)
placements=[];prototypes={}


def item(kind,x,y,yaw=0,scale=(1,1,1),grass=False):
    part='court'if y>=D['split_y']else'passage';name='Furniture '+kind+' '+str(len(placements))
    if kind not in prototypes:
        factory={'tree':tree,'hedge':hedge}.get(kind);m=factory('detail',name)if factory else furniture(kind,'detail',name);materials=fol if kind=='tree'else fol[1:]if kind=='hedge'else fm
        ob=finish(m,materials,part+'-furniture');prototypes[kind]=ob
    else:
        ob=prototypes[kind].copy();ob.data=prototypes[kind].data;cols[part+'-furniture'].objects.link(ob);ob.name=name
    ob.location=(x,y,turf_contact(x,y)if grass else grade(x,y));ob.rotation_euler.z=math.radians(yaw);ob.scale=scale
    if kind=='hedge':
        # Shear the prototype along the ground slope. Adjacent segments keep
        # vertical end faces instead of overlapping when their slopes differ.
        t=math.radians(yaw);dx=math.cos(t)*scale[0]/2;dy=math.sin(t)*scale[0]/2
        rise=grade(x+dx,y+dy)-grade(x-dx,y-dy)
        if abs(rise)>.025:
            ob.data=ob.data.copy();ob.name=name.replace('Furniture hedge ','Furniture sloped-hedge ')
            for v in ob.data.vertices:v.co.z+=rise*v.co.x/scale[2]
    ob['evidence']='Photographed family; estimated placement, May2011 pedestrian inventory';placements.append({'kind':kind,'xy':[x,y],'grass':grass,'scale':scale,'rotation_degrees':yaw})
for row in D['placements']:item(row['kind'],*row['xy'],row['rotation_degrees'],grass=row['surface']=='grass')
for row in D['bollard_rows']:
    for x,y in row['xy']:item('bollard',x,y,scale=(.55,.55,.9))
for row in D['trees']:item('tree',*row['xy'],scale=(row['scale'],)*3,grass=True)
for row in D['hedges']:
    for a,b in zip(row['xy'],row['xy'][1:]):
        length=math.dist(a,b);n=math.ceil(length/1.5)
        for i in range(n):
            t=(i+.5)/n;item('hedge',a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),(length/n,row['width_m']/.75,row['height_m']),True)
# Restrained two-post notice-board silhouette; unreadable lettering omitted.
row=D['notice_board'];x,y=row['xy'];m=Mesh('Street blank church noticeboard')
for side in [-1,1]:m.box((side*.48,0,.525),(.07,.07,1.05),0)
m.box((0,0,1.45),(1.05,.09,.8),2);ob=finish(m,fm,'court-furniture');ob.location=(x,y,turf_contact(x,y));ob.rotation_euler.z=math.radians(row['rotation_degrees'])
(ROOT/'research/geometry-report.json').write_text(json.dumps({'conform':report,'placements':placements,'wall':D['wall'],'limits':D['limits']},indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c;s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
