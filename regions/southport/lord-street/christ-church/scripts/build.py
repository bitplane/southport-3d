"""Retained Victorian Gothic facade and modern church behind, metres/Z-up."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix,text_object
from cafe import build_cafe
from components import rect,pointed,wall,gothic_window,leadwork,arch_ring,roundel,roof,ring,clipped
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ['historic-front','modern-hall','roofs']:
    C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,c,texture=None,rough=.82):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'));m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    return m
stone=material('Weathered buff sandstone',(.377,.328,.209),'stone')
trim=material('Darker dressed sandstone',(.27,.27,.215))
glass=material('Muted opaque leaded glazing',(.17,.21,.22),rough=.3)
lead=material('Dark leadwork',(.055,.064,.06))
wood=material('Dark painted timber and bell louvres',(.095,.08,.064))
brick=material('Rebuilt hall red brick',(.26,.08,.045),'brick')
newbrick=material('Modern cafe buff brick',(.43,.30,.20),'buff-brick')
cladding=material('Weathered cafe metal cladding',(.42,.43,.40),'cafe-metal')
slate=material('Dark grey roof slates',(.092,.104,.102),'slate')
metal=material('Rainwater goods and iron',(.055,.063,.061))
doorwood=material('Burgundy painted church doors',(.105,.022,.027))
cream=material('Pale window frames',(.69,.65,.53))
blue=material('Cafe blue plaque',(.02,.12,.23))

def finish(mesh,part='historic-front',mats=None,transform=None):
    ob=mesh.finish(mats or [stone],C[part]);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric UV')
    for face in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/4,v[axes[1]]/2.4)
    if transform is not None:ob.matrix_world=transform
    return ob

def box(name,c,size,part='historic-front',mat=None,transform=None):
    m=Mesh(name);m.box(c,size);return finish(m,part,[mat or stone],transform)

protos={}
def instance(key,factory,transform,mats=None,part='historic-front'):
    if key not in protos:protos[key]=finish(factory(),part,mats,transform);return protos[key]
    ob=protos[key].copy();ob.data=protos[key].data;C[part].objects.link(ob);ob.matrix_world=transform;return ob

z0=D['base_z'];cx=D['tower']['centre_x'];front=-23.5;back=-29.3;tw=5.23
# Bell tower uses real holes in all elevations. The four sides are separate
# wall prisms meeting at corners, never solid boxes with pasted-on windows.
faces=[('front',(cx,front,z0),(0,1,0),tw),('right',(cx-tw/2,(front+back)/2,z0),(-1,0,0),front-back-.96),('left',(cx+tw/2,(front+back)/2,z0),(1,0,0),front-back-.96),('back',(cx,back,z0),(0,-1,0),tw)]
for label,origin,normal,width in faces:
    tr=face_matrix(origin,normal)
    bells=[pointed(x,15.15,18.45,.80) for x in [-1.05,1.05]]
    middle=pointed(0,7.4,9.4,.96)
    holes=bells+[middle]
    if label!='back':holes.append([(.69*math.cos(i*2*math.pi/48),13.1+.69*math.sin(i*2*math.pi/48)) for i in range(48)])
    if label=='front':holes.append(pointed(0,0,2.2,.95))
    finish(wall('Envelope tower '+label,rect(-width/2,0,width/2,21.1),holes,.48),transform=tr)
    for x in [-1.05,1.05]:
        instance('bell',lambda:gothic_window('Louvre paired belfry',1.6,15.15,18.45,'louvre'),tr@Matrix.Translation((x,0,0)),[trim,wood,wood])
    instance('middle-'+('blocked' if label=='left' else 'glass'),lambda:gothic_window('Window tower '+label,1.92,7.4,9.4,'blocked' if label=='left' else 'glass'),tr,[trim,glass,wood])
    if label!='left':instance('middle-lead',lambda:leadwork('Fine tower diamond lead',1.92,7.4,9.4),tr,[lead])
    if label!='back':instance('roundel',lambda:roundel('Roundel diamond window'),tr@Matrix.Translation((0,13.1,0)),[trim,glass,wood])
    for h,w,d in [(1.0,width+.26,.18),(6.85,width+.12,.12),(14.8,width+.15,.13),(20.9,width+.30,.22)]:
        # Plinth interrupted across entrance rather than blocking the doorway.
        if label=='front' and h<2:
            for sign in [-1,1]:box('Trim interrupted tower plinth',(sign*(width/4+.52),h,.08),(width/2-1.04,.22,d),transform=tr)
        else:box('Trim tower stringcourse',(0,h,.055),(w,.15,d),transform=tr)
    # Crenellated parapet has real gaps and a recessed walkable-looking roof deck.
    box('Parapet base '+label,(0,21.42,0),(width+(.48 if label in ['left','right'] else 0),.75,.48),transform=tr)
    for i in (range(5) if label in ['front','back'] else range(1,4)):
        x=-width/2+i*width/4
        corner=i in [0,4]
        # Begin at the base's top: overlapping coplanar outer faces caused black streaks.
        merlon_bottom=21.42+.75/2;merlon_top=22.90 if corner else 22.30
        box('Parapet merlon '+label,(x,(merlon_bottom+merlon_top)/2,.0),(.52,merlon_top-merlon_bottom,.48),transform=tr)
        box('Trim merlon coping '+label,(x,22.91 if corner else 22.31,.015),(.62,.12,.58),transform=tr)
    # Quoin strips make the tower's corners read without ashlar overdraw.
    for side in [-1,1]:
        for h in [1.5+i*.48 for i in range(39)]:
            # Wall owns the embedded portion: retain the .063 m exposed relief
            # without duplicating its outer corner face below the wall surface.
            box('Fine tower quoin',(side*(width/2-.16),h,.0315),(.32,.44,.063),transform=tr,mat=trim)
# Closed shallow inner roof below battlements, never a missing face seen from above.
box('Roof tower lead deck',(cx,(front+back)/2,z0+21.15),(tw-.8,front-back-.8,.18),'roofs',metal)

# Main pointed doorway and three receding orders of moulding.
tr=face_matrix((cx,front,z0),(0,1,0))
m=Mesh('Door main pointed timber');m.outline(pointed(0,0,2.2,.95),-.42,-.37,0)
for x in [-.45,0,.45]:m.box((x,1.05,-.33),(.045,1.95,.07),1)
for h in [.3,1.9]:m.box((0,h,-.32),(1.75,.08,.08),1)
finish(m,mats=[doorwood,doorwood],transform=tr)
for r,dep in [(1.00,.18),(1.15,.26),(1.31,.32)]:
    m=Mesh('Trim pointed entrance order');arch_ring(m,0,0,2.2,r,.095,dep,dep);finish(m,mats=[trim],transform=tr)
# Crockets on the entrance arch: small stone buds, not speculative sculpture.
m=Mesh('Ornament entrance crockets')
for side in [-1,1]:
    for i in range(6):
        t=(i+.5)/6;a=t*math.pi/3
        x=side*(-1.42+2.84*math.cos(a));h=2.2+2.84*math.sin(a)
        m.ellipsoid((x,h,.30),(.095,.12,.08),segments=8,rings=4)
m.box((0,4.8,.20),(.16,.55,.16));m.box((0,4.92,.20),(.48,.12,.16));finish(m,mats=[trim],transform=tr)

# Buttresses taper in stages, with shallow gable caps and drip ledges.
for x in [cx-tw/2-.20,cx+tw/2+.20]:
    m=Mesh('Buttress tower front')
    for lo,hi,w,d in [(0,1.2,.95,1.0),(1.2,6.8,.68,.80),(6.8,13.9,.52,.64),(13.9,19.9,.40,.50)]:
        m.box((x,front+.10,z0+(lo+hi)/2),(w,d,hi-lo))
        m.box((x,front+.1,z0+hi),(w+.14,d+.14,.15))
    # Small pointed cap stops beneath the parapet.
    cap=Mesh('cap');cap.outline([(-.27,0),(.27,0),(0,.64)],-.25,.25)
    cap.vertices=[(a+x,b+z0+19.95,c+front+.1) for a,b,c in cap.vertices]
    # Use explicit world-coordinate pyramid instead of rotating ambiguous axes.
    m.add([(x-.27,front-.2,z0+20),(x+.27,front-.2,z0+20),(x+.27,front+.4,z0+20),(x-.27,front+.4,z0+20),(x,front+.1,z0+20.65)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)])
    finish(m,mats=[trim])
from facade_detail import tower_detail
tower_detail(finish,box,cx,front,z0,tw,trim,stone)
# Rearward corner buttresses and distinctive projecting octagonal stair turret.
for x in [cx-tw/2-.1,cx+tw/2+.1]:
    box('Buttress tower rear',(x,back+.25,z0+9.7),(.48,.72,19.4),mat=trim)
m=Mesh('Turret octagonal stair')
# Cafe-side octagonal stair, verified in the supplied oblique photograph.
m.lathe((cx+tw/2+.42,back+1.35),[(z0,.64),(z0+12,.64),(z0+12.18,.73),(z0+12.35,.64),(z0+17.9,.64),(z0+18.1,.73),(z0+18.2,.64)],segments=8)
finish(m)
m=Mesh('Roof stair turret cap')
m.lathe((cx+tw/2+.42,back+1.35),[(z0+18.16,.75),(z0+18.28,.75),(z0+19.45,.04)],segments=8)
finish(m,'roofs',[slate])
for h in [6.2,11.8,15.4]:
    trt=face_matrix((cx+tw/2+1.04,back+1.35,z0),(1,0,0))
    box('Window turret slit',(0,h,-.012),(.12,.75,.06),mat=wood,transform=trt)
    for dx in [-.12,.12]:box('Trim turret slit',(dx,h,.02),(.09,.92,.12),mat=trim,transform=trt)

# Retained front wings: each has a sloping battlemented inner bay and an outer gable.
# Local facade right coordinates translate to negative world X.
for sign in [-1,1]:
    tr=face_matrix((cx,back,z0),(0,1,0))
    a=tw/2;b=9.57;inner_c=sign*4.25;outer_c=sign*7.65
    poly=[(sign*a,0),(sign*b,0),(sign*b,8.4),(sign*7.65,10.35),(sign*5.85,8.5),(sign*a,9.9)]
    if sign<0:poly.reverse()
    holes=[pointed(inner_c,3.5,6.15,1.0),pointed(outer_c,4.35,6.75,1.02),pointed(outer_c,0,1.85,.68)]
    finish(wall('Envelope Gothic wing',poly,holes),transform=tr)
    for xc,bottom,spring in [(inner_c,3.5,6.15),(outer_c,4.35,6.75)]:
        instance('wing-'+str(bottom),lambda b=bottom,sp=spring:gothic_window('Window Gothic wing '+('inner' if b==3.5 else 'outer'),2.0,b,sp),tr@Matrix.Translation((xc,0,0)),[trim,glass,wood])
        instance('wing-lead-'+str(bottom),lambda b=bottom,sp=spring:leadwork('Fine wing diamond lead',2,b,sp),tr@Matrix.Translation((xc,0,0)),[lead])
    m=Mesh('Door wing pointed');m.outline(pointed(outer_c,0,1.85,.68),-.32,-.28,2);arch_ring(m,outer_c,0,1.85,.68,.16,.18,.12)
    m.box((outer_c,.36,-.23),(1.32,.72,.10),1)
    for dx in [-.61,0,.61]:m.box((outer_c+dx,1.2,-.21),(.075,2.4,.10),1)
    m.box((outer_c,.76,-.21),(1.28,.075,.10),1)
    for dx in [-.31,.31]:
        m.box((outer_c+dx,.36,-.17),(.42,.44,.035),1)
    arch_ring(m,outer_c,.75,1.85,.59,.06,.10,-.18,16,1)
    # Rectangular square hood and small carved spandrels above each side doorway.
    for x in [outer_c-.96,outer_c+.96]:m.box((x,1.56,.09),(.12,3.12,.22))
    m.box((outer_c,3.15,.09),(2.04,.16,.22));finish(m,mats=[trim,doorwood,glass],transform=tr)
    for x in [sign*5.8,sign*9.57]:
        m=Mesh('Buttress wing')
        for h0,h1,w,d in [(0,.55,.90,.70),(.55,3.2,.62,.50),(3.2,7.9,.44,.34),(7.9,10.0,.38,.30)]:
            m.box((x,(h0+h1)/2,d/2),(w,h1-h0,d));m.box((x,h1,d/2),(w+.12,.12,d+.1))
        finish(m,mats=[trim],transform=tr)
    # Sloping coping is geometric; low merlons leave the recognisable silhouette.
    m=Mesh('Parapet wing coping')
    for p,q in [((sign*a,9.9,.10),(sign*5.85,8.5,.10)),((sign*5.85,8.5,.10),(sign*7.65,10.35,.10)),((sign*7.65,10.35,.10),(sign*b,8.4,.10))]:m.tube([p,q],.13,sides=4)
    for t in [.15,.45,.75]:
        x=sign*(a+(5.85-a)*t);h=9.9+(8.5-9.9)*t
        m.box((x,h+.18,0),(.46,.46,.43))
    for u0,h0,u1,h1 in [(5.85,8.5,7.65,10.35),(7.65,10.35,b,8.4)]:
        for t in [.25,.65]:
            x=sign*(u0+(u1-u0)*t);h=h0+(h1-h0)*t
            m.box((x,h+.22,0),(.42,.55,.43))
    for x in [sign*7.65]:m.box((x,10.55,.0),(.38,.55,.43))
    finish(m,mats=[trim],transform=tr)
    from facade_detail import wing_detail
    wing_detail(finish,box,tr,sign,a,b,inner_c,outer_c,trim,doorwood,glass,metal)

# Modern hall follows OSM perimeter at base, with visible tall glazed side bays.
foot=D['mapped_footprint']
# Modern rebuilt body is behind the Victorian facade. Keep its front at y=-29.72
# to avoid a second coplanar stone/brick front skin or filled Gothic windows.
# South side: the five large modern windows are visible in the 2013 photograph.
westx=-112.0;side_y0=-30;side_y1=-52
tr=face_matrix((westx,side_y0,z0),(-1,0,0))
sideholes=[rect(c-.66,.7,c+.66,5.6) for c in [2.1,6.3,10.5,14.7,18.9]]
finish(wall('Envelope red brick side',rect(0,0,22,6.65),sideholes,.30),'modern-hall',[brick],tr)
for c in [2.1,6.3,10.5,14.7,18.9]:
    m=Mesh('Window modern hall');m.box((c,3.15,-.20),(1.32,4.9,.06),1)
    for dx in [-.72,.72]:m.box((c+dx,3.15,.02),(.12,5.08,.14),0)
    for h in [.64,5.66]:m.box((c,h,.02),(1.55,.12,.14),0)
    for dx in [-.44,0,.44]:m.box((c+dx,3.15,-.10),(.035,4.90,.10),2)
    for h in [1.8,3.4,4.7]:m.box((c,h,-.10),(1.32,.035,.10),2)
    finish(m,'modern-hall',[cream,glass,wood],tr)
for y in [-30,-34,-38.2,-42.4,-46.6,-51.6]:
    box('Pier modern brick',(westx-.05,y,z0+3.3),(.32,.32,6.6),'modern-hall',brick)
    box('Trim modern pier cap',(westx-.05,y,z0+6.1),(.46,.46,.16),'modern-hall',cream)
# Rear envelopes: only masses/openings supported by aerial; no invented rows.
# Rear walls and real gable openings are authored with the transverse roof below.
box('Envelope hall shoulder',(-112.5,-52.1,z0+3.3),(2.8,.32,6.6),'modern-hall',brick)
# Aerial confirms three flat-roof heights along the eastern annex, not a hip.
for y0,y1,h in [(-35,-26,4.15),(-54,-35,5.4),(-71.4,-54,3.9)]:
    box('Envelope east party',(-76.7,(y0+y1)/2,z0+h/2),(.32,y1-y0,h),'modern-hall',brick)
for y,h in [(-35,5.4),(-54,5.4)]:
    box('Envelope annex roof step',(-83.1,y,z0+h/2),(12.8,.20,h),'modern-hall',brick)
box('Envelope annex rear',(-83.2,-71.4,z0+1.95),(13.0,.32,3.9),'modern-hall',brick)
box('Envelope annex return',(-89.39,-66.4,z0+1.95),(.32,10.3,3.9),'modern-hall',brick)
# Close the hall side and front shoulder behind the cafe. Previously a short
# partial-height return left a visible void beneath the main roof.
box('Envelope cafe porch return',(-91.335,-29.72,z0+3.35),(3.57,.30,6.70),'modern-hall',brick)
# The continuous hall side and cross-gable are built together in rear_hall.py.
box('Envelope cafe connector',(-86.975,-29.72,z0+2.075),(4.85,.30,4.15),'modern-hall',newbrick)
build_cafe(finish,box,z0,newbrick,cladding,glass,cream,wood,slate,metal)
# Separate closed roofs do not intersect: lower annex roof ends at nave wall.
from rear_hall import build_rear
build_rear(globals())
for ya,yb,h in [(-35,-29.55,4.15),(-54,-35,5.4),(-71.5,-54,3.9)]:
    box('Roof modern annex flat',(-83.05,(ya+yb)/2,z0+h),(13.0,yb-ya,.18),'roofs',slate)
# Low cafe roof outside the high roof footprints.
# Rounded cafe cap is authored in cafe.py.
# Low step in rear hall (mapped southern offset) and lead valley between ranges.
box('Roof valley flashing',(-89.47,-45.2,z0+6.65),(.24,31.2,.10),'roofs',metal)
for x in [-112.2]:
    box('Trim hall eaves',(x,-45.5,z0+6.63),(.16,31,.16),'roofs',cream)
    m=Mesh('Fine downpipe');m.tube([(x,-50,z0+.15),(x,-50,z0+6.6)],.052,sides=8);finish(m,'modern-hall',[metal])
# Distinct rooflight arrays read directly from the fresh satellite view.
for xs,ys,h in [([-86.2,-80.0],[-39,-45,-51],5.4),([-85.5,-79.5],[-58,-63,-68],3.9),([-86,-82,-78],[-32],4.15)]:
    for x in xs:
        for y in ys:
            box('Roof annex rooflight kerb',(x,y,z0+h+.16),(1.25,1.35,.23),'roofs',cream)
            box('Window annex rooflight',(x,y,z0+h+.29),(1.03,1.13,.05),'roofs',glass)
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.70,.75,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.4;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(.45,-.50,-.5)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/christ-church.blend'))
