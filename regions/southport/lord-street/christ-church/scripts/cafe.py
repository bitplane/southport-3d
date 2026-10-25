"""Rounded cafe envelope from mapped corner and private frontage photographs."""
import math
import bpy
from mathutils import Matrix
from southport3d.geometry import Mesh, face_matrix, text_object
from components import wall, rect, roof


# Estimated from the 10m aerial scale and August 2024 Street View.
# Long ridge runs toward the recessed doors; the narrow gable faces the garden.
PORCH = {'x0':-88.475,'x1':-85.575,'y0':-29.57,'y1':-24.67,
         'eaves':3.02,'ridge':3.87,'pier_top':2.72,'pier_y':-25.03}

def build_cafe(finish, box, z0, brick, cladding, glass, frame_mat, wood, slate, metal):
    front=face_matrix((-76.68,-25.9,z0),(0,1,0))
    # Straight glazed frontage runs into a quarter-round corner, not a wide box.
    finish(wall('Envelope cafe front',rect(0,-.12,5.72,4.35),[rect(.45,.10,4.9,2.96)],.25),
           'modern-hall',[brick],front)
    arc=[(-82.4+2*math.cos(math.pi/2+i*math.pi/48),-27.9+2*math.sin(math.pi/2+i*math.pi/48)) for i in range(25)]
    for j,(a,b) in enumerate(zip(arc,arc[1:])):
        # Closed radial sectors share only their internal end faces.
        ia=(-82.4+(a[0]+82.4)*.875,-27.9+(a[1]+27.9)*.875)
        ib=(-82.4+(b[0]+82.4)*.875,-27.9+(b[1]+27.9)*.875)
        for lo,hi,mat,label in [(-.12,2.85,brick,'brick'),(2.85,4.35,cladding,'metal')]:
            m=Mesh('Envelope cafe curved '+label)
            v=[(x,y,z0+z) for z in (lo,hi) for x,y in (a,b,ib,ia)]
            m.add(v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            finish(m,'modern-hall',[mat])
    box('Envelope cafe corner return',(-84.275,-28.725,z0+2.115),(.25,1.65,4.47),'modern-hall',brick)
    # Cladding covers only solid fascia; masonry remains below the rounded corner.
    box('Trim cafe fascia metal',(2.86,3.655,.025),(5.72,1.39,.07),'modern-hall',cladding,front)
    box('Trim cafe return metal',(-84.415,-28.725,z0+3.60),(.035,1.65,1.5),'modern-hall',cladding)
    for j in range(1,8):
        theta=math.pi/2+j*math.pi/16
        x,y=-82.4+2.015*math.cos(theta),-27.9+2.015*math.sin(theta)
        box('Trim cafe metal seam',(x,y,z0+3.60),(.022,.022,1.5),'modern-hall',metal)
    # Roof cap follows the rounded footprint, and meets the rear annex at y=-29.55.
    plan=[(-76.55,-29.55),(-76.55,-25.78),(-82.4,-25.78)]
    plan += [(-82.4+2.12*math.cos(math.pi/2+i*math.pi/48),-27.9+2.12*math.sin(math.pi/2+i*math.pi/48)) for i in range(1,25)]
    plan += [(-84.52,-29.55)]
    m=Mesh('Roof cafe rounded flat');n=len(plan)
    m.add([(x,y,z0+z) for z in (4.13,4.30) for x,y in plan],
          [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)])
    finish(m,'roofs',[slate])
    # Full-height glazing, double central door, side lights and opening top lights.
    m=Mesh('Window cafe glazing');m.box((2.675,1.53,-.10),(4.47,2.88,.04))
    finish(m,'modern-hall',[glass],front)
    m=Mesh('Trim cafe glazing frames')
    for u in (.45,1.85,3.55,4.9):m.box((u,1.53,-.025),(.075,2.86,.09))
    for h in (.10,2.20,2.96):
        for a,b in ((.4875,1.8125),(1.8875,3.5125),(3.5875,4.8625)):
            m.box(((a+b)/2,h,-.025),(b-a,.075,.09))
    m.box((2.70,1.13,-.025),(.06,2.10,.09))
    finish(m,'modern-hall',[frame_mat],front)
    for u in (2.60,2.80):box('Trim cafe door handle',(u,1.02,.075),(.035,.34,.035),'modern-hall',metal,front)
    box('Door cafe threshold',(2.70,.04,.035),(1.70,.08,.30),'modern-hall',metal,front)
    # Authored two-line sign; no photographic pixels or copied temporary posters.
    m=Mesh('CafeSign identity');m.box((2.675,3.61,.10),(4.70,1.10,.10),0)
    sans=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    serif=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')
    for text,x,y,size,width,font in [('café',1.20,4.00,.26,.85,sans),('1821',2.675,3.52,.62,2.95,serif)]:
        ob=text_object('temporary cafe text',text,(x,y,.16),(0,0,1),size,width,font,frame_mat,extrude=.009,fit_bounds=True)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        m.add([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons],1)
        bpy.data.objects.remove(ob,do_unlink=True)
    m.box((3.13,4.00,.17),(2.28,.035,.025),1)
    m.box((2.675,3.16,.17),(3.22,.035,.025),1)
    finish(m,'modern-hall',[wood,frame_mat],front)
    # Noticeboard on the beginning of the rounded wall; unreadable posters omitted.
    t=face_matrix((-83.05,-25.98,z0),( -.325,.946,0))
    box('Trim cafe noticeboard',(0,1.68,.08),(1.02,1.13,.13),'modern-hall',wood,t)
    box('Trim cafe noticeboard inset',(0,1.68,.155),(.88,.99,.025),'modern-hall',metal,t)
    # Narrow, projecting timber-gabled porch. Side passages remain open.
    p=PORCH
    # The porch is reddish stained timber, not the almost black bell louvres.
    porchwood=bpy.data.materials.new('Porch reddish stained timber');porchwood.use_nodes=True
    porchwood.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.145,.065,.058,1)
    porchwood.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
    infill=bpy.data.materials.new('Porch warm timber boarding');infill.use_nodes=True
    infill.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.19,.105,.055,1)
    capmat=bpy.data.materials.new('Porch buff stone caps');capmat.use_nodes=True
    capmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.47,.39,.27,1)
    for x in (p['x0']+.30,p['x1']-.30):
        box('Pier cafe porch',(x,p['pier_y'],z0+p['pier_top']/2),(.40,.40,p['pier_top']),'modern-hall',brick)
        box('Trim porch pier capital',(x,p['pier_y'],z0+2.78),(.48,.48,.12),'modern-hall',capmat)
    box('Trim porch cross beam',((p['x0']+p['x1'])/2,p['pier_y'],z0+2.93),(2.66,.24,.18),'modern-hall',porchwood)
    middle=(p['x0']+p['x1'])/2
    # Thin folded roof, with a genuine recessed gable rather than a solid wedge.
    section=[(p['x0'],p['eaves']),(middle,p['ridge']-.10),(p['x1'],p['eaves']),
             (p['x1'],p['eaves']+.10),(middle,p['ridge']),(p['x0'],p['eaves']+.10)]
    m=Mesh('Roof cafe entrance canopy')
    m.add([(x,y,z0+z) for y in (p['y0'],p['y1']) for x,z in section],
          [tuple(range(6)),tuple(reversed(range(6,12)))],1)
    for i in range(6):
        j=(i+1)%6;m.add([(section[i][0],p['y0'],z0+section[i][1]),(section[i][0],p['y1'],z0+section[i][1]),
                       (section[j][0],p['y1'],z0+section[j][1]),(section[j][0],p['y0'],z0+section[j][1])],
                      [(0,1,2,3)],0 if i in (3,4) else 1)
    ob=finish(m,'roofs',[slate,porchwood])
    # Slate courses run parallel to the ridge; metric tile sizes, not facade UVs.
    for face in ob.data.polygons:
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            distance=math.hypot(v.x-middle,v.z-z0-p['ridge'])
            ob.data.uv_layers.active.data[li].uv=((v.y-p['y0'])/1.6,distance/1.6)
    # Separate horizontal infill boards sit behind the projecting barge boards.
    apex=p['ridge']-.12;bottom=p['eaves'];half=(p['x1']-p['x0'])/2-.035
    for i in range(math.ceil((apex-bottom)/.13)):
        lo=bottom+i*.13;hi=min(apex,lo+.126)
        if hi<=lo:continue
        w0=half*(apex-lo)/(apex-bottom);w1=half*(apex-hi)/(apex-bottom)
        m=Mesh('Trim porch recessed gable board')
        poly=[(middle-w0,lo),(middle+w0,lo),(middle+w1,hi),(middle-w1,hi)]
        m.add([(x,y,z0+z) for y in (p['y1']-.24,p['y1']-.20) for x,z in poly],
              [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
        finish(m,'roofs',[infill])
    # Tongue-and-groove backing closes the narrow joints; no daylight slivers.
    m=Mesh('Trim porch gable backing')
    m.add([(middle-half,p['y1']-.245,z0+bottom),(middle,p['y1']-.245,z0+apex),
           (middle+half,p['y1']-.245,z0+bottom)],[(0,1,2)])
    finish(m,'roofs',[porchwood])
    # Long fascia joins the verge, above the pier caps, as in the close view.
    for x in (p['x0']+.06,p['x1']-.06):
        box('Trim porch side fascia',(x,(p['y0']+p['y1'])/2,z0+2.93),(.12,p['y1']-p['y0'],.18),'modern-hall',porchwood)
    # Projecting timber verge boards frame the visible garden-facing gable.
    middle=(p['x0']+p['x1'])/2
    for left in (True,False):
        end=p['x0'] if left else p['x1'];direction=1 if left else -1
        poly=[(end-.06*direction,p['eaves']-.03),(middle,p['ridge']+.06),
              (middle,p['ridge']-.14),(end+.12*direction,p['eaves']-.14)]
        if not left:poly.reverse()
        m=Mesh('Trim porch timber verge')
        m.add([(x,y,z0+z) for y in (p['y1'],p['y1']+.12) for x,z in poly],
              [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        finish(m,'roofs',[porchwood])
    box('Door cafe porch backing',(-87.025,-29.52,z0+1.75),(4.30,.12,3.50),'modern-hall',wood)
    for x in (-88.45,-87.025,-85.6):box('Window cafe porch glazing',(x,-29.44,z0+1.90),(1.20,.035,2.80),'modern-hall',glass)
