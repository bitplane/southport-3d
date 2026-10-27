"""Chapel pedestrian ground: one owner per face, open entrances at every LOD."""
import bpy,bmesh,json,math,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'lib'),str(ROOT/'scripts'),str(REPO/'regions/southport/lord-street/corridor-public-realm/scripts')]
from southport3d.geometry import Mesh
from southport3d.elevation import Elevations
from plan_geometry import Plan
from furniture_lod import furniture,finish
from bhs_arcade_support import station_polygon,station_mesh
D=json.loads((ROOT/'research/layout.json').read_text());B=json.loads((REPO/D['block_plan']).read_text());OLD=json.loads((REPO/D['existing_block_plan']).read_text())
arcade=json.loads((REPO/'regions/southport/corporation-street/former-bhs/research/arcade-support.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
surface=Elevations(REPO/D['elevation_plan']).surface('chapel-pedestrian')
def grade(x,y):
 return surface.height(x,y)
cols={}
for region in ['west','middle','east']:
 for kind in ['ground','furniture']:
  name=region+'-'+kind;c=bpy.data.collections.new(name);s.collection.children.link(c);cols[name]=c

def material(name,colour,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*colour,1)
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Roughness'].default_value=.85
 if texture:
  im=bpy.data.images.load(str(ROOT/'textures'/texture));im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  im=bpy.data.images.load(str(ROOT/'textures/paving-normal.png'),check_existing=True);im.colorspace_settings.name='Non-Color';im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
 return m
mats={'paving':material('Chapel pale slab paving',(.48,.46,.42),'pale.png'),'route':material('Chapel grey slab route',(.34,.35,.34),'mixed.png'),'strip':material('Chapel dark furniture bands',(.16,.18,.19),'dark.png'),'border':material('Chapel stone margin',(.40,.40,.37))}
fcols=[(.07,.08,.085),(.42,.44,.44),(.65,.64,.58),(.7,.55,.08),(.3,.02,.01),(.6,.22,.01),(.02,.2,.04),(.10,.13,.11),(.1,.13,.14)]
fm=[material('Chapel furnishing '+str(i),c) for i,c in enumerate(fcols)]
def rect(a,b,c,d):return [(a,c),(b,c),(b,d),(a,d)]
def ribbon(points,width,offset=0):
 # Long mitred borders share one pair of offset polylines at every bend.
 def edge(d):
  out=[]
  for i,p in enumerate(points):
   a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
   if i==0:a=p;b=points[1]
   if i==len(points)-1:a=points[-2];b=p
   dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
   out.append((p[0]-dy/l*d,p[1]+dx/l*d))
  return out
 return edge(offset-width/2)+list(reversed(edge(offset+width/2)))
P=Plan();available=P.polygons(D['ground_polygons'])
cutters=list(D['exclusions'])+[b['footprint'] for b in B['blocks'] if not b.get('clearance_above_ground_m')]+[b['footprint'] for b in OLD['blocks']]
cutters.append(station_polygon(arcade))
available=P.difference(available,P.polygons(cutters))
route=P.intersection(available,P.polygons([ribbon(D['centreline'],D['route_width_m'])]))
strips=P.intersection(available,P.polygons([ribbon(D['centreline'],D['furniture_strip_width_m'],side*D['furniture_strip_offset_m']) for side in [-1,1]]))
strips=P.difference(strips,route)
paved=P.difference(P.difference(available,route),strips)
compiled={}
for name,lo,hi in zip(['west','middle','east'],D['tile_cuts'],D['tile_cuts'][1:]):
 cell=P.polygons([rect(lo,hi,-300,0)])
 for mat,g in [('paving',paved),('route',route),('strip',strips)]:
  m=Mesh('Ground '+name+' '+mat)
  # The ramp break is a real shared edge, not a sloping giant triangle.
  cuts=[lo,hi]
  for a,b in zip(cuts,cuts[1:]):
   patch=P.intersection(g,P.polygons([rect(a,b,-300,0)]))
   for tri in P.triangles(patch):
    for lifted in surface.lift_triangle(tri):m.add(lifted,[(0,1,2)])
  if m.faces:compiled[(name,mat)]=m
P.close()
# The station floor is lower than the BHS entrance. This bounded ramp shares
# the building edge, the Chapel threshold and the approach's north seam.
station_mesh(compiled[('middle','paving')],surface,arcade)
# Noded ground boundaries remain exact after float32 conversion.
import southport3d.conform as cf
cf.GRID=1e-6;cf.TOLERANCE=1e-7
compiled,report=cf.conform(compiled,preserve_triangles=True,weld_distance=5e-5)
for (name,mat),m in compiled.items():
 ob=m.finish([mats[mat]],cols[name+'-ground']);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
 uv=ob.data.uv_layers.new(name='Metric slabs')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/3.6,v.y/3.6)
# Furniture is separate from ground ray casting. A local generator keeps LODs consistent.
for i,row in enumerate(D['placements']):
 x,y=row['xy'];region='west' if x<-170 else 'middle' if x<-95 else 'east';name=f"Furniture {row['kind']} {i:02d}"
 ob=finish(furniture(row['kind'],'detail',name),fm,cols[region+'-furniture']);ob.location=(x,y,grade(x,y));ob.rotation_euler.z=math.radians(row['rotation_degrees'])
 uv=ob.data.uv_layers.new(name='Local furnishing UV')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.z)
(ROOT/'research/conform.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
