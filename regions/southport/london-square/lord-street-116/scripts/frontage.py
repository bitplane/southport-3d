"""Two entrances and faceted display windows from user-supplied Street View.

Measurements are estimates; screenshots establish topology and two step risers.
All access surfaces here belong to the building, not the public pavement mesh.
"""
import math
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh,text_object


def build_frontage(D,finish,frontbox,sign,emblem,frame,mats,font):
    redtile,red,cream,dark,glass,metal,stone,grout,tread=mats
    width=D['x_near']-D['x_far'];top=4.35
    a,b,dep=D['entry_left'],D['entry_right'],D['entry_depth']
    def box(name,u,z,w,h,depth,out,mat):
        return frontbox(name,u,z,w,h,depth,out,mat,'shopfront')
    def segment(name,p,q,z,h,t,mat):
        du,dv=q[0]-p[0],q[1]-p[1];L=math.hypot(du,dv);ux,uz=du/L,dv/L
        m=Mesh(name);m.box((0,z,0),(L,h,t))
        m.vertices=[((p[0]+q[0])/2+x*ux-out*uz,y,(p[1]+q[1])/2+x*uz+out*ux) for x,y,out in m.vertices]
        return finish(m,'shopfront',[mat],frame)
    seen_jambs=set()
    def glazing(label,points,divisions=1):
        for p,q in zip(points,points[1:]):
            segment('Shop '+label+' glass',p,q,2.45,top-.55,.035,glass)
            segment('Shop '+label+' plinth',p,q,.275,.55,.16,dark)
            # Continuous rails with uprights between them, avoiding crossed faces.
            for z in [.575,top-.025]:segment('Shop '+label+' rail',p,q,z,.065,.09,red)
            for i in range(divisions+1):
                t=i/divisions;u=p[0]+(q[0]-p[0])*t;out=p[1]+(q[1]-p[1])*t
                key=(round(u,5),round(out,5))
                if key not in seen_jambs:
                    box('Shop '+label+' mullion',u,2.45,.055,top-.63,.085,out,red);seen_jambs.add(key)
    for u,w in [(.23,.46),(8.15,.60),(16.55,.60),(width-.23,.46)]:
        box('Shop red tiled pier',u,top/2,w,top,.50,-.12,redtile)
        box('Shop dark pier plinth',u,.28,w+.025,.56,.53,-.12,dark)
    # Left bay is set back with its OWN entrance at the right-hand end.
    glazing('left display',[(.46,-.30),(5.65,-.30)],3)
    glazing('left entrance return',[(5.65,-.30),(5.85,-.95)])
    glazing('left pier return',[(7.60,-.95),(7.85,.0)])
    # Two faceted projecting showcases flank the deeper central entrance.
    glazing('central left showcase',[(8.45,.0),(8.70,.25),(10.25,.25),(a,-dep)])
    glazing('central right showcase',[(b,-dep),(15.0,.25),(16.0,.25),(16.25,.0)])
    # Right display is also set back behind its outer red piers.
    glazing('right display return',[(16.85,.0),(17.15,-.32)])
    glazing('right display',[(17.15,-.32),(width-.46,-.32)],4)
    glazing('right end return',[(width-.46,-.32),(width-.46,.0)])
    box('Shop entrance soffit',12.35,top-.045,7.8,.09,dep+.43,(.34-dep)/2,stone)
    box('Shop projecting canopy fascia',width/2,4.41,width,.12,.38,.19,stone)
    box('Shop left entrance soffit',4.12,top-.045,7.3,.09,1.10,-.48,stone)
    # Glazing stays opaque, but both independent door arrangements are recessed.
    for label,start,end,depth,count in [('main',a,b,dep,3),('left',5.85,7.60,.95,2)]:
        name='Shop recessed doors' if label=='main' else 'Shop left recessed doors'
        box(name,(start+end)/2,1.68,end-start,2.64,.035,-depth,glass)
        box('Shop '+label+' transom',(start+end)/2,3.69,end-start,1.28,.035,-depth,glass)
        for i in range(count+1):box('Shop '+label+' door jamb',start+(end-start)*i/count,2.35,.065,3.92,.09,-depth+.03,red)
        for z in [.395,3.035,top-.025]:box('Shop '+label+' door rail',(start+end)/2,z,end-start,.08,.10,-depth+.03,red)
    # Two dark tiled risers and a deep landing, as the close screenshot resolves.
    step_left,step_right=10.25,15.0;step_w=step_right-step_left
    for z,out,depth in [(.09,.75,.50),(.27,-.425,1.85)]:
        box('Shop entrance step',(step_left+step_right)/2,z,step_w,.18,depth,out,tread)
    # The church-side display stands behind two pale steps / raised apron.
    for z,out,depth in [(.09,.73,.54),(.27,.015,.89)]:
        box('Shop right display apron',(16.85+width-.46)/2,z,width-.46-16.85,.18,depth,out,stone)
    # Left raised access ramp: sloping solid, continuous top and end landing.
    u0,u1=.80,6.2;o0,o1=-.25,1.45;h0,h1=.045,.36
    m=Mesh('Shop left access ramp')
    verts=[(u0,0,o0),(u1,0,o0),(u1,0,o1),(u0,0,o1),(u0,h0,o0),(u1,h1,o0),(u1,h1,o1),(u0,h0,o1)]
    m.add(verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
    # Local Y is height: reverse the original Z-up prism winding.
    m.faces=[tuple(reversed(f)) for f in m.faces]
    finish(m,'shopfront',[tread],frame)
    box('Shop left access landing',7.0,.18,1.6,.36,2.40,.25,tread)
    # Fill the wedge between the angled left display return and the door.
    # Its front edge meets the ramp slope; its rear reaches the .36 m threshold.
    polygon=[(5.65,-.30),(5.85,-.95),(6.2,-.95),(6.2,-.25),(5.65,-.25)]
    heights=[h0+(h1-h0)*(5.65-u0)/(u1-u0),h1,h1,h1,h0+(h1-h0)*(5.65-u0)/(u1-u0)]
    m=Mesh('Shop left threshold infill');n=len(polygon)
    vertices=[(u,0,out) for u,out in polygon]+[(u,h,out) for (u,out),h in zip(polygon,heights)]
    faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    m.add(vertices,faces)
    # Resolve polygon orientation using signed volume, independent of plan order.
    from mathutils import Vector
    volume=sum(Vector(vertices[f[0]]).dot(Vector(vertices[f[j]]).cross(Vector(vertices[f[j+1]])))/6 for f in faces for j in range(1,len(f)-1))
    if volume<0:m.faces=[tuple(reversed(f)) for f in m.faces]
    finish(m,'shopfront',[tread],frame)
    # Solid outer retaining cheek follows the slope; thin red rail follows it too.
    m=Mesh('Shop left ramp retaining wall')
    m.add([(u0,0,o1),(u1,0,o1),(u1,0,o1+.09),(u0,0,o1+.09),(u0,h0+.18,o1),(u1,h1+.18,o1),(u1,h1+.18,o1+.09),(u0,h0+.18,o1+.09)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
    m.faces=[tuple(reversed(f)) for f in m.faces]
    finish(m,'shopfront',[dark],frame)
    box('Shop left landing retaining cheek',7.0,.27,1.6,.54,.09,1.495,dark)
    m=Mesh('Shop red ramp railing')
    def rz(u):return h0+(h1-h0)*min(1,max(0,(u-u0)/(u1-u0)))+.65
    m.tube([(u0,rz(u0),o1+.04),(u1,rz(u1),o1+.04),(7.8,rz(u1),o1+.04)],.025,0,8)
    for i in range(10):
        u=u0+(7.8-u0)*i/9;m.box((u,rz(u)-.245,o1+.04),(.035,.49,.035))
    m.tube([(7.8,rz(u1),o1+.04),(7.8,rz(u1),.20)],.025,0,8)
    m.box((7.8,(.36+rz(u1))/2,.20),(.035,rz(u1)-.36,.035))
    finish(m,'shopfront',[red],frame)
    sign('charity name','British Heart Foundation',width*.225,4.92,width*.365,.85,red,cream,out=.08)
    sign('furniture name','Furniture & Electrical',width*.745,4.92,width*.425,.85,red,cream,out=.08)
    def board(name,u,z,w,h,lines,out):
        m=Mesh('Sign '+name);m.box((0,0,-.020),(w,h,.040),0)
        for text,y,hh in lines:
            t=text_object('Temporary frontage text',text,(0,y,.014),(0,0,1),hh,w*.90,font,cream,extrude=.006)
            ys=[v[1] for v in t.bound_box];t.matrix_world=t.matrix_world@Matrix.Translation((0,-(min(ys)+max(ys))/2,0))
            bpy.ops.object.select_all(action='DESELECT');t.select_set(True);bpy.context.view_layer.objects.active=t;bpy.ops.object.convert(target='MESH')
            m.add([tuple(t.matrix_world@v.co) for v in t.data.vertices],[tuple(f.vertices) for f in t.data.polygons],1);bpy.data.objects.remove(t,do_unlink=True)
        return finish(m,'shopfront',[red,cream],frame@Matrix.Translation((u,z,out)))
    board('entrance main welcome',(a+b)/2,3.70,1.72,1.06,[('WELCOME',.33,.24),('to BHF',.01,.25),('Southport',-.32,.23)],-dep+.10)
    board('entrance left welcome',6.725,3.70,1.72,1.06,[('WELCOME to',.31,.17),('British Heart Foundation',0,.17),('Southport',-.31,.20)],-.85)
    emblem('central heart',width*.465,4.92,.92,.08,red)
    emblem('window heart',width-3.56,2.35,1.70,-.301,glass)
    sign('window strapline','FIGHT FOR EVERY HEARTBEAT',width-3.56,1.36,1.90,.16,glass,cream,out=-.300,extrude=.001)
    for text,z in [('FREE & FAST',2.78),('COLLECTION',2.43)]:sign('left window '+text,text,3.055,z,1.60,.28,glass,cream,out=-.281,extrude=.001)
    # Exterior grilles and door fittings; stock/posters and interiors stay omitted.
    m=Mesh('Fine frontage hardware')
    for start,end,depth,count in [(a,b,dep,3),(5.85,7.60,.95,2)]:
        for i in range(count):
            u=start+(end-start)*(i+.82)/count
            m.tube([(u,1.3,-depth+.12),(u,1.85,-depth+.12)],.017,0,8)
        for u in [start,end]:
            for z in [.8,2.7]:m.box((u,z,-depth+.10),(.05,.08,.04))
    for u,out in [(9.2,.34),(15.55,.34)]:
        m.box((u,.28,out),(.38,.16,.02))
        for j in range(4):m.box((u,.225+j*.035,out+.013),(.32,.009,.008),1)
    finish(m,'shopfront',[metal,dark],frame)
    # Original three visible circular downlights, now within the corrected recess.
    m=Mesh('Fine circular soffit downlights')
    for u in [a+.8,(a+b)/2,b-.8]:
        for radius in [.09,.065]:
            m.tube([(u+radius*math.cos(math.tau*i/32),top-.099,-.55+radius*math.sin(math.tau*i/32)) for i in range(33)],.010,0,6)
        verts=[(u,top-.096,-.55)]+[(u+.065*math.cos(math.tau*i/32),top-.096,-.55+.065*math.sin(math.tau*i/32)) for i in range(32)]
        m.add(verts,[(0,1+i,1+(i+1)%32) for i in range(32)],1)
    finish(m,'shopfront',[metal,dark],frame)
    # Two-dimensional tile grid on the landing and risers, isolated to Detail.
    m=Mesh('Micro threshold tile joints')
    for z,out,depth in [(.09,.75,.50),(.27,-.425,1.85)]:
        for i in range(1,20):
            u=step_left+step_w*i/20
            m.box((u,z,out+depth/2+.001),(.004,.176,.002))
            m.box((u,z+.091,out),(.004,.002,depth-.008))
        n=max(1,int(depth/.25))
        for j in range(1,n):m.box(((step_left+step_right)/2,z+.091,out-depth/2+depth*j/n),(step_w-.008,.002,.004))
    finish(m,'shopfront',[grout],frame)
