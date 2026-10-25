"""One floor owner for the church side court and Corporation Street link."""
import bpy,bmesh,json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.road import parallel
from southport3d.street import furniture
from plan_geometry import Plan
from components import tree,hedge
from boundary import continuous_wall
from datum import grade
D=json.loads((ROOT/'research/layout.json').read_text())
G=json.loads((REPO/D['garden_handover_source']).read_text())
CH=json.loads((REPO/D['building_source']).read_text())
ST=json.loads((REPO/D['station_ground_source']).read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';cols={}
for name in ['court-ground','passage-ground','court-furniture','passage-furniture']:
    c=bpy.data.collections.new(name);s.collection.children.link(c);cols[name]=c


def rect(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def ribbon(points,width):return parallel(points,-width/2)+list(reversed(parallel(points,width/2)))
P=Plan();x0,x1,y0,y1=D['bounds']
region=P.polygons([rect(x0,x1,y0,y1),G['approach_handover_polygon']])
cutters=[CH['mapped_footprint'],*ST['ground_polygons']]
for path in D['block_plans']:cutters += [b['footprint']for b in json.loads((REPO/path).read_text())['blocks']]
available=P.difference(region,P.polygons(cutters))
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
            cuts=[lo,*[v for v in [-36]if lo<v<hi],hi]
            for a,b in zip(cuts,cuts[1:]):
                cell=P.polygons([rect(x0,x1,a,b)])
                for tri in P.triangles(P.intersection(g,cell)):m.add([(x,y,0)for x,y in tri],[(0,1,2)])
        if m.faces:compiled[(part,mat)]=m
P.close()
# Shared slab, grass and ownership vertices are conformed on the plan first.
import southport3d.conform as cf
cf.GRID=1e-4;cf.TOLERANCE=2e-4
for m in compiled.values():m.vertices=np.asarray(m.vertices,dtype=np.float32).tolist()
compiled,report=cf.conform(compiled)
for (part,mat),m in compiled.items():m.vertices=[(x,y,grade(x,y)+(rise(x,y)if mat=='grass'else 0))for x,y,z in m.vertices]
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
mats={'paving':material('Pale passage slabs',(.56,.54,.48),'paving'),'strip':material('Dark longitudinal slab bands',(.21,.23,.23)),'brick':material('Church court brick pavers',(.44,.30,.23),'brick'),'grass':material('Estimated raised lawn',(.24,.31,.12)),'edging':material('Low garden stone edge',(.42,.41,.35))}
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

w=D['wall'];points=[(x,y,grade(x,y))for x,y in w['xy']];mesh=continuous_wall(points,w['height_m'],w['width_m'],'Wall continuous side garden')
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
