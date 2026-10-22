"""St George's, Southport: Gothic exterior reconstructed from linked evidence."""
import json
import math
import os
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,face_matrix
from components import rectangle,pointed,regions,wall,arch_ring,circle_band,foil,window_surround,diamond_leads,pinnacles
D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
collections={}
for name in ('nave','tower','spire'):
    collections[name]=bpy.data.collections.new(name);scene.collection.children.link(collections[name])


def material(name,rgb,texture=None,roughness=.86):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*rgb,1)
    shader.inputs['Roughness'].default_value=roughness
    if texture:
        node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(ROOT/'textures'/f'{texture}.png'))
        mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    return mat


stone=material('Coursed warm sandstone',(.36,.28,.17),'sandstone')
ashlar=material('Dressed sandstone',(.412,.332,.209),'ashlar')
# Albedo matches mean sRGB texture once decoded, avoiding LoD colour jumps.
plain=material('Carved warm sandstone',(.402,.323,.200))
slate=material('Blue grey slate',(.08,.095,.10),'slate')
brick=material('Rear hall brick',(.23,.09,.05),'brick')
glass=material('Dark leaded exterior glass',(.065,.081,.075),roughness=.4)
lead=material('Lead came and rainwater goods',(.072,.076,.073),roughness=.66)
wood=material('Dark red brown doors',(.115,.041,.027),roughness=.76)
louvre=material('Weathered bell louvres',(.18,.19,.17))
black=material('Belfry dark recess',(.022,.025,.022))


def finish(mesh,part='nave',mats=None,transform=None):
    ob=mesh.finish(mats or [stone],collections[part])
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric surfaces')
    for face in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(face.normal[i]))[:2])
        for li in face.loop_indices:
            p=ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv=((p.y/3.2,abs(p.x-D['centre_x'])*1.3/3.2) if mesh.name=='Roof nave closed shell' else (p[axes[0]]/3.2,p[axes[1]]/3.2))
    if transform is not None:ob.matrix_world=transform
    return ob


def box(name,centre,size,part='nave',mat=None,transform=None):
    m=Mesh(name);m.box(centre,size);return finish(m,part,[mat or ashlar],transform)


prototypes={}
def instance(key,factory,frame,part='nave',mats=None):
    if key not in prototypes:
        ob=finish(factory(),part,mats,frame);prototypes[key]=ob
    else:
        ob=prototypes[key].copy();ob.data=prototypes[key].data
        collections[part].objects.link(ob);ob.matrix_world=frame
    return ob


def arch_window(key,radius,bottom,spring,frame,part='nave',lights=3,style=0,bell=False):
    instance(key+'-surround',lambda:window_surround('Window stone '+key,radius,bottom,spring,lights,style),frame,part,[ashlar])
    backing=Mesh('Window arch glass '+key)
    backing.outline(pointed(radius,bottom,spring),-.30,-.26)
    instance(key+'-glass',lambda:backing,frame,part,[black if bell else glass])
    if bell:
        blades=Mesh('Louvre blades '+key)
        for z in [bottom+.18+i*.30 for i in range(int((spring-bottom)/.30))]:
            # Sloped closed blades, visible recess retained independently.
            for dx in (-radius*.47,radius*.47):
                w=radius*.83
                blades.add([(dx-w/2,z,-.18),(dx+w/2,z,-.18),(dx+w/2,z+.14,-.04),(dx-w/2,z+.14,-.04),
                            (dx-w/2,z+.10,-.21),(dx+w/2,z+.10,-.21),(dx+w/2,z+.24,-.07),(dx-w/2,z+.24,-.07)],
                           [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
        instance(key+'-blades',lambda:blades,frame,part,[louvre])
    else:
        # Repeat one compatible glazing/lead prototype; stone tracery stays real.
        h=spring-bottom-.48
        instance(key+'-leads',lambda:diamond_leads('Glazing panel '+key,2*radius-.03,h),frame@Matrix.Translation((0,bottom,0)),part,[glass,lead])


cx=D['centre_x'];width=D['nave_width'];xl=cx-width/2;xr=cx+width/2
front=D['nave_front_y'];rear=D['rear_y'];base=D['base_z'];eave=D['eaves'];ridge=D['ridge']
tw=D['tower_width'];tf=D['tower_front_y'];tb=D['tower_back_y'];tp=D['tower_parapet']
# The rear of the tower overlaps the nave footprint; its front is an independent
# projection. The nave front is clipped behind the tower, with no duplicate skin.
for name,origin,normal,length in [('south',(xl,front,base),(-1,0,0),front-rear),('north',(xr,rear,base),(1,0,0),front-rear)]:
    frame=face_matrix(origin,normal)
    centres=[(i+.5)*length/5 for i in range(5)]
    holes=[pointed(1.35,2.45,5.75,u) for u in centres]
    finish(wall('Envelope nave '+name,rectangle(0,0,length,eave),holes),transform=frame)
    for i,u in enumerate(centres):arch_window('nave-'+str(i%2),1.35,2.45,5.75,frame@Matrix.Translation((u,0,0)),style=i)
    for i in range(6):
        u=i*length/5
        butt=Mesh('Buttress nave '+name)
        # Four set-backs, sloping weatherings and narrow pinnacle cap.
        for a,b,d,w in [(0,1.3,.95,.92),(1.3,4.7,.78,.78),(4.7,7.4,.57,.67),(7.4,9.35,.34,.55)]:
            butt.box((u,(a+b)/2,d/2),(w,b-a,d))
            butt.outline([(u-w/2,b),(u+w/2,b),(u+w/2,b+.21),(u-w/2,b+.21)],0,d+.09)
        butt.add([(u-.34,9.35,0),(u+.34,9.35,0),(u+.34,9.35,.52),(u-.34,9.35,.52),(u-.34,9.68,.10),(u+.34,9.68,.10)],
                 [(0,3,2,1),(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)])
        finish(butt,mats=[ashlar],transform=frame)
    for z,h,dep in [(.32,.30,.18),(1.2,.12,.12),(eave-.15,.27,.18)]:
        box('Course nave '+name,(length/2,z,dep/2),(length,h,dep),transform=frame)
    # Gutters/downpipes remain distinct from masonry; omit small fittings far away.
    gutter=Mesh('Fitting gutter '+name);gutter.tube([(0,eave+.02,.22),(length,eave+.02,.22)],.075,sides=8)
    for u in (.3,length-.3):gutter.tube([(u,eave,.25),(u,.3,.25)],.055,sides=8)
    finish(gutter,mats=[lead],transform=frame)

# Front gable with genuine door and window apertures on each side of tower.
ff=face_matrix((xr,front,base),(0,1,0))
front_poly=[(0,0),(width,0),(width,eave),(width/2,ridge),(0,eave)]
holes=[rectangle(width/2-tw/2-.01,0,width/2+tw/2+.01,ridge+.1)]
for u in (3.1,width-3.1):holes += [pointed(.86,.15,2.55,u),pointed(.94,5.25,7.6,u)]
finish(wall('Envelope front gable',front_poly,holes),transform=ff)
for u in (3.1,width-3.1):
    arch_window('front-flank',.94,5.25,7.6,ff@Matrix.Translation((u,0,0)),lights=2)
    doorway=Mesh('Door flank moulding')
    arch_ring(doorway,.86,.15,2.55,.18,.15,.38)
    arch_ring(doorway,1.07,.15,2.55,.10,.21,.38,sill=False)
    circle_band(doorway,0,3.48,.28,.06,.02,.12)
    instance('flank-door-stone',lambda:doorway,ff@Matrix.Translation((u,0,0)),mats=[ashlar])
    leaf=Mesh('Door flank timber');leaf.outline(pointed(.83,.15,2.5),-.28,-.22)
    instance('flank-door',lambda:leaf,ff@Matrix.Translation((u,0,0)),mats=[wood])
# Copings follow both straight gable slopes; ridge finial is a cross.
for x0,x1 in [(0,width/2),(width/2,width)]:
    z0=eave if x0==0 else ridge;z1=eave if x1==width else ridge
    m=Mesh('Course front gable coping');m.tube([(x0,z0,.03),(x1,z1,.03)],.13,sides=6)
    finish(m,mats=[ashlar],transform=ff)

# Rear gable is estimated, retained as plain envelope until clearer evidence.
rf=face_matrix((xl,rear,base),(0,-1,0))
finish(wall('Envelope rear gable',front_poly,[]),transform=rf)

# A closed, constant-thickness two-slope roof; no crossing planar sheets.
roof=Mesh('Roof nave closed shell');x0=xl-.15;x1=xr+.15;y0=rear-.12;y1=front+.06
section=[(x0,eave+.12),(cx,ridge+.12),(x1,eave+.12),(x1,eave-.08),(cx,ridge-.08),(x0,eave-.08)]
verts=[(x,y,base+z) for y in (y0,y1) for x,z in section]
faces=[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
roof.add(verts,faces);finish(roof,mats=[slate])
cap=Mesh('Roof ridge cap');cap.tube([(cx,rear-.1,base+ridge+.18),(cx,front+.05,base+ridge+.18)],.105,sides=8);finish(cap,mats=[ashlar])
for yy in (front-.15,rear+.1):
    cross=Mesh('Silhouette roof cross');cross.box((cx,yy,base+ridge+.65),(.10,.15,1.05));cross.box((cx,yy,base+ridge+.83),(.65,.15,.10));finish(cross,mats=[ashlar])

# Attached brick school/hall seen clearly in November 2020 car-park imagery.
# Cross-gabled roof is perpendicular to the nave; footprint estimated from aerial.
hx0,hx1,hy0,hy1=D['rear_hall']['bounds_xy']
hy=(hy0+hy1)/2;he=D['rear_hall']['eaves'];hr=D['rear_hall']['ridge'];hw=hy1-hy0
hallroof=Mesh('Roof rear hall closed shell')
sect=[(hy0-.15,he+.1),(hy,hr+.1),(hy1+.15,he+.1),(hy1+.15,he-.10),(hy,hr-.10),(hy0-.15,he-.10)]
hallroof.add([(x,y,base+z) for x in (hx0-.12,hx1+.12) for y,z in sect],
             [tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)])
finish(hallroof,mats=[slate])
# Narrow low connector, visible in the gap behind the church's high rear gable.
box('Envelope hall connector',((hx0+hx1)/2,(rear+hy1)/2,base+2.8),(hx1-hx0,abs(rear-hy1),5.6),mat=brick)
box('Roof hall connector',((hx0+hx1)/2,(rear+hy1)/2,base+5.64),(hx1-hx0,abs(rear-hy1)+.12,.14),mat=slate)
def hallwindow(frame,u,z,w,h):
    af=frame@Matrix.Translation((u,z,0))
    box('Window hall dark glazing',(0,h/2,-.10),(w,h,.06),mat=glass,transform=af)
    m=Mesh('Window hall sash')
    for xx in (-w/2,w/2):m.box((xx,h/2,.035),(.075,h+.1,.13))
    for zz in (0,h/2,h):m.box((0,zz,.035),(w+.1,.075,.13))
    m.box((0,h/2,.055),(.035,h,.06))
    finish(m,mats=[wood],transform=af)
    box('Course hall window sill',(0,-.09,.12),(w+.30,.14,.4),mat=ashlar,transform=af)
# North gable facing parking: three first-floor sashes, two below and red door.
for side,origin,normal in [('north',(hx1,hy0,base),(1,0,0)),('south',(hx0,hy1,base),(-1,0,0))]:
    hf=face_matrix(origin,normal)
    poly=[(0,0),(hw,0),(hw,he),(hw/2,hr),(0,he)]
    holes=[]
    if side=='north':
        for u in (3.2,hw/2,hw-3.2):holes.append(rectangle(u-.55,5.0,u+.55,7.7))
        for u in (3.2,6.3):holes.append(rectangle(u-.55,.7,u+.55,3.2))
        holes.append(rectangle(hw-4.2,.15,hw-2.5,3.0))
    finish(wall('Envelope hall '+side,poly,holes),'nave',[brick],hf)
    if side=='north':
        for u in (3.2,hw/2,hw-3.2):hallwindow(hf,u,5.0,1.1,2.7)
        for u in (3.2,6.3):hallwindow(hf,u,.7,1.1,2.5)
        box('Door hall red leaf',(hw-3.35,1.57,-.16),(1.68,2.83,.15),mat=wood,transform=hf)
        for u in (hw-4.32,hw-2.38):box('Portal hall door jamb',(u,1.6,.10),(.18,3.2,.28),mat=ashlar,transform=hf)
        for z,w in ((3.16,2.25),(3.38,2.65)):
            box('Portal hall door entablature',(hw-3.35,z,.19),(w,.19,.46),mat=ashlar,transform=hf)
        for z in (4.05,7.9):
            bandwidth=hw if z<he else hw*(hr-z-.12)/(hr-he)
            box('Course hall stone band',(hw/2,z,.04),(bandwidth,.19,.12),mat=ashlar,transform=hf)
        # Brick arched attic vent, no unverified lettering.
        m=Mesh('Window hall attic vent')
        # The car-park photograph shows a semicircular brick vent, not a lancet.
        vent=[(-.48,9.1),(.48,9.1)]+[(.48*math.cos(j*math.pi/20),9.18+.48*math.sin(j*math.pi/20)) for j in range(21)]
        m.outline(vent,.01,.035)
        finish(m,mats=[lead],transform=hf@Matrix.Translation((hw/2,0,0)))
    m=Mesh('Course hall gable verge');m.tube([(0,he,.08),(hw/2,hr,.08),(hw,he,.08)],.105,sides=6);finish(m,mats=[lead],transform=hf)
# Six tall side sashes visible on the long rear wall; nave-facing wall is plain.
for side,origin,normal in [('rear',(hx0,hy0,base),(0,-1,0)),('front',(hx1,hy1,base),(0,1,0))]:
    hf=face_matrix(origin,normal);length=hx1-hx0
    centres=[1.6+i*(length-3.2)/5 for i in range(6)]
    holes=[rectangle(u-.57,1.2,u+.57,5.15) for u in centres] if side=='rear' else []
    finish(wall('Envelope hall '+side,rectangle(0,0,length,he),holes),'nave',[brick],hf)
    if side=='rear':
        for u in centres:hallwindow(hf,u,1.2,1.14,3.95)
    m=Mesh('Fitting hall gutter');m.tube([(0,he,.2),(length,he,.2)],.065,sides=8);finish(m,mats=[lead],transform=hf)

# Three-stage square tower with open belfry apertures on all four elevations.
tower_frames=[('front',face_matrix((cx+tw/2,tf,base),(0,1,0)),tw),
              ('south',face_matrix((cx-tw/2,tf,base),(-1,0,0)),tf-tb),
              ('back',face_matrix((cx-tw/2,tb,base),(0,-1,0)),tw),
              ('north',face_matrix((cx+tw/2,tb,base),(1,0,0)),tf-tb)]
for name,frame,length in tower_frames:
    holes=[]
    if name=='front':holes.append(pointed(1.27,.12,3.6,length/2))
    if name in ('south','north'):
        for dx in (-.77,.77):holes.append(pointed(.57,5.6,7.7,length/2+dx))
        holes.append([(length/2+.67*math.cos(a*math.tau/32),2.85+.67*math.sin(a*math.tau/32)) for a in range(32)])
    for u in (length/2-1.14,length/2+1.14):holes.append(pointed(.89,15.45,18.75,u))
    # Rear lower wall remains inside nave; suppress it below ridge to avoid
    # duplicate facade strips showing through the gable/roof intersection.
    poly=rectangle(0,ridge if name=='back' else 0,length,22.2)
    finish(wall('Envelope tower '+name,poly,holes,.50),'tower',transform=frame)
    if name in ('south','north'):
        for dx in (-.77,.77):
            af=frame@Matrix.Translation((length/2+dx,0,0))
            m=Mesh('Window stone tower lancet');arch_ring(m,.57,5.6,7.7,.14,.15,.33);arch_ring(m,.76,5.55,7.7,.07,.22,.2)
            instance('tower-lancet-stone',lambda:m,af,'tower',[ashlar])
            m=Mesh('Window arch glass tower lancet');m.outline(pointed(.57,5.6,7.7),-.27,-.23)
            instance('tower-lancet-glass',lambda:m,af,'tower',[glass])
            instance('tower-lancet-leads',lambda:diamond_leads('Glazing panel tower lancet',1.12,2.07),af@Matrix.Translation((0,5.6,0)),'tower',[glass,lead])
        af=frame@Matrix.Translation((length/2,2.85,0))
        m=Mesh('Window stone tower rose');circle_band(m,0,0,.67,.17,.18,.35);circle_band(m,0,0,.88,.055,.23,.15);foil(m,0,0,.55,4,.02,.075)
        instance('tower-rose-stone',lambda:m,af,'tower',[ashlar])
        m=Mesh('Window arch glass tower rose');m.outline([(.66*math.cos(a*math.tau/40),.66*math.sin(a*math.tau/40)) for a in range(40)],-.26,-.22)
        instance('tower-rose-glass',lambda:m,af,'tower',[glass])
    for u in (length/2-1.14,length/2+1.14):arch_window('bell',.89,15.45,18.75,frame@Matrix.Translation((u,0,0)),'tower',2,bell=True)
    # Triple blind pointed niches in stage two are read as recessed stone,
    # not glass. Narrow pointed canopies/crockets form the recognisable group.
    if name in ('front','south','north'):
        niche=Mesh('Niche triple '+name)
        for dx in (-.70,0,.70):
            h=.18 if dx==0 else 0
            niche.outline(pointed(.28,10.1,11.85+h,dx),.015,.045,1)
            arch_ring(niche,.28,10.1,11.85+h,.075,.16,.17,cx=dx)
            niche.tube([(dx-.42,11.85+h,.18),(dx,13.18+h,.18),(dx+.42,11.85+h,.18)],.065,sides=6)
        niche.box((0,10.0,.14),(2.5,.14,.33))
        finish(niche,'tower',[ashlar,plain],frame@Matrix.Translation((length/2,0,0)))
    for z,h,dep in [(.22,.35,.18),(5.2,.16,.20),(9.25,.16,.15),(14.7,.20,.26),(21.95,.18,.26),(22.18,.18,.34),(22.45,.12,.39)]:
        if name=='front' and z<6.0:
            course=Mesh('Course tower '+name)
            for fragment in regions(rectangle(0,z-h/2,length,z+h/2),[pointed(1.34,0,3.6,length/2)]):
                course.outline(fragment,0,dep)
            finish(course,'tower',[ashlar],frame)
        else:
            box('Course tower '+name,(length/2,z,dep/2),(length,h,dep),'tower',ashlar,frame)
    # Open parapet has actual spaced piers and diagonal quatrefoil motifs.
    parapet=Mesh('Parapet open '+name)
    parapet.box((length/2,23.0,.13),(length,.20,.52))
    for i in range(9):
        u=.28+i*(length-.56)/8
        parapet.box((u,22.70,.12),(.17,.48,.34))
        if i<8:
            mid=u+(length-.56)/16
            parapet.tube([(mid-.19,22.54,.20),(mid,22.80,.20),(mid+.19,22.54,.20)],.04,sides=5)
    finish(parapet,'tower',[ashlar],frame)
    arcade=Mesh('Ornament arcaded frieze '+name)
    for i in range(17):
        u=.18+i*(length-.36)/16
        arcade.tube([(u-.12,21.90,.16),(u,21.57,.16),(u+.12,21.90,.16)],.045,sides=6)
        arcade.ellipsoid((u,21.54,.16),(.08,.085,.065),segments=8,rings=5)
    finish(arcade,'tower',[plain],frame)

# Angle buttresses have sloped weatherings, raised shafts and crocketed peaks.
for x in (cx-tw/2,cx+tw/2):
    for y in (tf,tb):
        centre=(x,y)
        butt=Mesh('Buttress tower angle')
        butt.rect_profile(centre,[(base,.95,.95),(base+1.0,.95,.95),(base+1.15,.82,.82),
                                 (base+5.2,.82,.82),(base+5.55,.67,.67),(base+9.2,.67,.67),
                                 (base+9.55,.57,.57),(base+14.8,.57,.57),(base+15.1,.45,.45),
                                 (base+21.5,.45,.45),(base+21.7,.60,.60),(base+23.3,.60,.60)])
        finish(butt,'tower',[ashlar])
        instance('pinnacle',lambda:pinnacles('Pinnacle crocketed',3.4),Matrix.Translation((x,y,base+23.3)),'spire',[ashlar])

# Main doorway: three moulded orders, colonnettes, decorative capitals and a
# steep gabled porch. Wall is cut behind it, leaving a real recessed door leaf.
frame=tower_frames[0][1]@Matrix.Translation((tw/2,0,0))
porch=Mesh('Portal three moulded orders')
for i in range(3):
    arch_ring(porch,1.30+i*.17,.10,3.6,.10,.20+i*.17,.35,sill=False)
    for sign in (-1,1):
        x=sign*(1.38+i*.17)
        porch.tube([(x,.25,.32+i*.17),(x,3.6,.32+i*.17)],.09,sides=12)
        for z,r in [(.22,.16),(.36,.13),(3.46,.13),(3.60,.18)]:
            porch.box((x,z,.32+i*.17),(r*2,.12,r*2))
finish(porch,'tower',[ashlar],frame)
door=Mesh('Door main leaf');door.outline(pointed(1.24,.15,3.6),-.38,-.30)
finish(door,'tower',[wood],frame)
fine=Mesh('Fitting main door boarding')
for i in range(19):
    x=-1.15+i*2.3/18
    h=3.6+math.sqrt(max(0,(2*1.24)**2-(abs(x)+1.24)**2))-.18
    fine.box((x,(h+.2)/2,-.275),(.018,h-.2,.025))
for x in (-.12,.12):fine.tube([(x,1.65,-.23),(x,1.92,-.23)],.025,sides=8)
finish(fine,'tower',[lead],frame)
# Gable triangle starts above the arch, not through its opening.
porchpoly=[(-2.05,3.45),(0,8.30),(2.05,3.45)]
opening=pointed(1.85,.1,3.6)
finish(wall('Portal steep gable',porchpoly,[opening],.25),'tower',[ashlar],frame@Matrix.Translation((0,0,.65)))
for sign in (-1,1):
    m=Mesh('Portal gable coping');m.tube([(sign*2.1,3.45,.83),(0,8.35,.83)],.10,sides=8);finish(m,'tower',[ashlar],frame)
    m=Mesh('Ornament porch crockets')
    for i in range(8):
        t=(i+.4)/8;x=sign*2.1*(1-t);z=3.45+4.9*t
        m.ellipsoid((x+sign*.10,z,.83),(.12,.12,.11),segments=10,rings=6)
    finish(m,'tower',[plain],frame)
roundel=Mesh('Portal floral roundel');circle_band(roundel,0,6.65,.40,.11,.91,.15);foil(roundel,0,6.65,.35,6,.93,.05)
finish(roundel,'tower',[ashlar],frame)
fin=Mesh('Silhouette porch finial');fin.tube([(0,8.27,.83),(0,8.82,.83)],.06,sides=8);fin.tube([(-.20,8.61,.83),(.20,8.61,.83)],.05,sides=8);finish(fin,'tower',[ashlar],frame)
box('Portal threshold',(cx,tf+.35,base+.07),(2.60,.80,.14),'tower',ashlar)

# Octagonal broach spire. The four diagonal broach panels connect square tower
# to the octagonal shaft; the spire itself is one closed triangulated mesh.
cy=(tf+tb)/2
box('Roof tower weather deck',(cx,cy,base+22.65),(tw-.12,tf-tb-.12,.20),'spire',slate)
spire=Mesh('Roof broach spire closed')
rings=[(22.9,2.83),(24.7,2.66),(31.5,1.93),(38.5,1.13),(46.8,.12),(47.2,.025)]
verts=[]
for z,r in rings:
    for i in range(8):
        a=math.pi/8+i*math.tau/8;verts.append((cx+r*math.cos(a),cy+r*math.sin(a),base+z))
faces=[tuple(reversed(range(8)))]
for k in range(len(rings)-1):
    for i in range(8):faces.append((k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i))
faces.append(tuple((len(rings)-1)*8+i for i in range(8)))
spire.add(verts,faces);finish(spire,'spire',[stone])
# Small raised bands and geometric motifs divide the two visible spire tiers.
for z,r in ((31.55,1.95),(38.55,1.15)):
    m=Mesh('Course spire band')
    m.lathe((cx,cy),[(base+z-.15,r),(base+z-.08,r+.13),(base+z+.20,r+.13),(base+z+.28,r)],segments=8)
    # Rotate octagon to same azimuth as shaft, preserving exact ring direction.
    a=math.pi/8
    m.vertices=[(cx+(x-cx)*math.cos(a)-(y-cy)*math.sin(a),cy+(x-cx)*math.sin(a)+(y-cy)*math.cos(a),zz) for x,y,zz in m.vertices]
    finish(m,'spire',[ashlar])
# Two tiers of projecting pointed lucarnes: lower tall paired lights and upper
# smaller single louvres. Their backs stay inside the tapered shaft.
for tier,z,r,rad,spring in [(0,25.1,2.55,.58,2.65),(1,34.15,1.62,.34,1.25)]:
    for i,normal in enumerate(((1,0,0),(-1,0,0),(0,1,0),(0,-1,0))):
        frame=face_matrix((cx+normal[0]*r*.93,cy+normal[1]*r*.93,base+z),normal)
        m=Mesh('Lucarne gabled body '+str(tier))
        m.outline([(-rad-.24,0),(rad+.24,0),(rad+.24,spring),(0,spring+rad*2.1+.3),(-rad-.24,spring)],-.65,.12)
        finish(m,'spire',[ashlar],frame)
        m=Mesh('Lucarne dark opening '+str(tier));m.outline(pointed(rad,.12,spring),.125,.14);finish(m,'spire',[black],frame)
        surround=Mesh('Lucarne moulding '+str(tier));arch_ring(surround,rad,.12,spring,.09,.24,.18)
        if tier==0:surround.box((0,spring*.50,.21),(.09,spring,.19))
        for k in range(5):surround.box((0,.35+k*(spring-.3)/5,.22),(rad*1.8,.09,.11))
        finish(surround,'spire',[ashlar],frame)
        coping=Mesh('Lucarne coping '+str(tier));coping.tube([(-rad-.28,spring,.20),(0,spring+rad*2.1+.4,.20),(rad+.28,spring,.20)],.08,sides=6);finish(coping,'spire',[ashlar],frame)
        if tier==0:
            c=Mesh('Ornament lucarne finial');c.tube([(0,spring+rad*2.1+.35,.2),(0,spring+rad*2.1+.8,.2)],.05,sides=6);finish(c,'spire',[ashlar],frame)
for image in bpy.data.images:
    if image.source=='FILE':image.pack()
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.68,.75,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.5
ob=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(ob);ob.rotation_euler=(.5,-.5,-.7)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/st-georges-church.blend'))
