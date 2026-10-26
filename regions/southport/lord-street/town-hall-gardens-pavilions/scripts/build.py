"""Estimated Town Hall Gardens pavilion exteriors; no interiors or tenant signs."""
import bpy,bmesh,math,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72;return m
materials=[mat('Painted pale panels',(.70,.69,.62)),mat('Iron posts',(.10,.11,.10)),mat('Glazing',(.27,.36,.36)),mat('Lead roof',(.36,.38,.37))]
for b in D['pavilions']:
 name=b['id'];p=b['footprint'];N=len(p);cx=sum(x for x,y in p)/N;cy=sum(y for x,y in p)/N;z=b['base_m'];e=z+b['eave_m'];apex=z+b['ridge_m']
 collection=bpy.data.collections.new(name);s.collection.children.link(collection)
 wall=Mesh('Architecture '+name);fine=Mesh('Fine '+name);roofdetail=Mesh('Ornament '+name)
 winding=1 if sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(p,p[1:]+p[:1]))>0 else -1
 def q(a,t,side,zv):
  (x,y),(tx,ty),(nx,ny)=a;return(x+tx*t+nx*side,y+ty*t+ny*side,zv)
 for i,(ax,ay) in enumerate(p):
  bx,by=p[(i+1)%N];L=math.hypot(bx-ax,by-ay);tx=(bx-ax)/L;ty=(by-ay)/L;normal=(-ty*winding,tx*winding);a=((ax,ay),(tx,ty),normal)
  # Recessed backing behind framed glazing closes the exterior without
  # competing with the near face and supplies a bounded District receiver.
  wall.add([q(a,0,.15,z+.02),q(a,L,.15,z+.02),q(a,L,.15,e-.20),q(a,0,.15,e-.20)],[(0,1,2,3)],1)
  # A shallow footing skirt bridges the bounded grade while the roof and
  # glazing remain level; its base is below the estimated surrounding datum.
  wall.add([q(a,0,0,z-.18),q(a,L,0,z-.18),q(a,L,0,z+.02),q(a,0,0,z+.02)],[(0,1,2,3)],0)
  # Slender but substantial outside posts and a continuous layered fascia.
  wall.tube([q(a,0,0,z-.18),q(a,0,0,e)],.085,1,8)
  wall.add([q(a,0,0,e-.20),q(a,L,0,e-.20),q(a,L,0,e+.05),q(a,0,0,e+.05)],[(0,1,2,3)],1)
  bays=max(1,round(L/1.5));width=L/bays;door=i in b['entrance_edges']
  for k in range(bays):
   left=k*width+.11;right=(k+1)*width-.11;mid=(left+right)/2;half=(right-left)/2
   if k:wall.tube([q(a,k*width,-.01,z),q(a,k*width,-.01,e-.20)],.055,1,8)
   # Entry door occupies one central bay on selected observed frontages.
   entry=door and k==bays//2;low=.08 if entry else .56
   wall.add([q(a,left,0,z+.02),q(a,right,0,z+.02),q(a,right,0,z+low),q(a,left,0,z+low)],[(0,1,2,3)],0)
   wall.add([q(a,left,.025,z+low),q(a,right,.025,z+low),q(a,right,.025,z+2.20),q(a,left,.025,z+2.20)],[(0,1,2,3)],2)
   for t in [left,right,mid]:wall.tube([q(a,t,-.015,z+low),q(a,t,-.015,z+2.20)],.035,1,8)
   wall.tube([q(a,left,-.015,z+2.20),q(a,right,-.015,z+2.20)],.035,1,8)
   # Semicircular fanlight with radial bars and a pale curved spandrel.
   arc=[(mid+half*math.cos(j*math.pi/12),z+2.20+.48*math.sin(j*math.pi/12)) for j in range(13)]
   fan=[q(a,mid,.025,z+2.20)]+[q(a,t,.025,h) for t,h in arc]
   wall.add(fan,[(0,j+1,j+2) for j in range(12)],2)
   for j in range(12):
    t0,h0=arc[j];t1,h1=arc[j+1];wall.add([q(a,t0,0,h0),q(a,t1,0,h1),q(a,t1,0,e-.20),q(a,t0,0,e-.20)],[(0,1,2,3)],0)
   fine.tube([q(a,t,-.025,h) for t,h in arc],.025,1,6)
   for j in (3,6,9):fine.tube([q(a,mid,-.026,z+2.20),q(a,arc[j][0],-.026,arc[j][1])],.018,1,6)
   if entry:
    # Paired leaves, a lock rail and discreet handles; the actual door state is
    # time-dependent and is represented closed.
    wall.tube([q(a,left,-.025,z+.08),q(a,right,-.025,z+.08)],.035,1,8)
    fine.tube([q(a,left,-.03,z+1.08),q(a,right,-.03,z+1.08)],.025,1,6)
    for t in (mid-.08,mid+.08):fine.tube([q(a,t,-.04,z+.95),q(a,t,-.04,z+1.10)],.02,1,6)
   if not entry:
    fine.tube([q(a,left+.06,-.02,z+.10),q(a,right-.06,-.02,z+.10),q(a,right-.06,-.02,z+.46),q(a,left+.06,-.02,z+.46),q(a,left+.06,-.02,z+.10)],.015,1,6)
 # Shallow multi-faceted roof, long ridge and projecting eaves.
 over=[]
 for x,y in p:
  dx=x-cx;dy=y-cy;L=math.hypot(dx,dy);over.append((x+.48*dx/L,y+.48*dy/L,e+.04))
 ridge=[(cx,cy-1.8,apex),(cx,cy+1.8,apex)];verts=over+ridge
 for i,(x,y) in enumerate(p):
  j=(i+1)%N;a=0 if y<cy else 1;c=0 if p[j][1]<cy else 1
  wall.add([verts[t] for t in ((i,j,N+c,N+a) if a!=c else (i,j,N+a))],[(0,1,2,3)] if a!=c else [(0,1,2)],3)
  # Restrained standing seams on the visible grey roof covering.  Endpoints
  # are inset from eaves and ridge to avoid coincident ironwork faces.
  u=over[i];v=over[j];sections=max(2,round(math.dist(u,v)/1.2))
  for k in range(1,sections):
   t=k/sections;outer=tuple(u[d]*(1-t)+v[d]*t for d in range(3))
   inner=tuple(ridge[a][d]*(1-t)+ridge[c][d]*t for d in range(3))
   start=tuple(inner[d]*.78+outer[d]*.22+(0.018 if d==2 else 0) for d in range(3))
   end=tuple(inner[d]*.06+outer[d]*.94+(0.018 if d==2 else 0) for d in range(3))
   roofdetail.tube([start,end],.009,1,4)
  # Eave fascia is a vertical skirt and iron crest omitted from massing.
  u=over[i];v=over[j];wall.add([(u[0],u[1],e-.12),(v[0],v[1],e-.12),v,u],[(0,1,2,3)],1)
  # Separate canopy corner column and curved bracket, based on the 2008
  # north and 2025 south photographs.  Other unseen brackets remain estimated.
  wall.rect_profile((u[0],u[1]),[(z-.18,.13,.13),(e-.12,.13,.13)],1)
  roofdetail.tube([(u[0],u[1],e-.60),(u[0],u[1],e-.30),(x,y,e-.18)],.03,1,6)
  roofdetail.tube([(u[0]+(v[0]-u[0])*.015,u[1]+(v[1]-u[1])*.015,e+.055),(v[0]+(u[0]-v[0])*.015,v[1]+(u[1]-v[1])*.015,e+.055)],.018,1,6)
 # Light roof-edge cresting and a restrained ridge finial: photographed
 # fabric, not the temporary café sign.  Repetition has a fixed spacing.
 for i,u in enumerate(over):
  v=over[(i+1)%N];length=math.dist(u,v);count=max(1,int(length/.42))
  for j in range(1,count):
   t=j/count;x=u[0]*(1-t)+v[0]*t;y=u[1]*(1-t)+v[1]*t
   roofdetail.tube([(x,y,e+.06),(x,y,e+.15)],.012,1,4)
 for x,y,h in ridge:
  roofdetail.tube([(x,y,h),(x,y,h+.22)],.025,1,6)
 for m in [wall,fine,roofdetail]:
  ob=m.finish(materials,collection);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();ob.data.update()
  uv=ob.data.uv_layers.new(name='Metric surfaces')
  for poly in ob.data.polygons:
   axes=sorted(sorted(range(3),key=lambda i:abs(poly.normal[i]))[:2])
   for li in poly.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.7,.75,1)
l=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));l.data.energy=2.5;l.rotation_euler=(.6,-.4,-.7);s.collection.objects.link(l)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);c.data.type='ORTHO';s.camera=c
s.render.resolution_x=1200;s.render.resolution_y=850
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/pavilions.blend'))
