"""367 Lord Street: measured image ratios and separately authored stone details."""
import json, math, os, sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from southport3d.geometry import Mesh,text_object,face_matrix
from southport3d.conform import conform
from southport3d.planar import halfplane,area
from components import rect,cuts,ellipse_arch,arc,moulding,beam,column,balustrade,mask,tympanum,cartouche,leaf,scroll
D=json.loads((ROOT/'research/layout.json').read_text());DETAIL=D['phase']=='detail';W=D['width'];L=D['depth']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC'
C={}
for name in ('facades','roof','frontage'):
    C[name]=bpy.data.collections.new(name);s.collection.children.link(C[name])
def material(name,c,roughness=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    q=m.node_tree.nodes['Principled BSDF'];q.inputs['Base Color'].default_value=(*c,1);q.inputs['Roughness'].default_value=roughness
    return m
stone=material('Portland limestone',(.62,.60,.54));light=material('Clean stone arrises',(.68,.66,.60));shadow=material('Weathered stone recess',(.39,.38,.34))
stonevar=[material('Limestone block '+str(i),(.59+i*.013,.57+i*.013,.51+i*.012)) for i in range(6)]
white=material('Off-white painted glazing bars',(.83,.83,.76),.52);glass=material('Dark blue grey window glass',(.055,.082,.087),.23)
door=material('Burgundy timber',(.12,.033,.048),.5);black=material('Black painted iron',(.025,.030,.029),.45)
pink=material('Rose red sign sides',(.39,.16,.19));gold=material('Pale gold lettering face',(.72,.61,.38),.5)
roofmat=material('Pale flat roof membrane',(.43,.45,.43));lead=material('Rooflight and flashing lead',(.21,.24,.25));brick=material('Provisional concealed masonry',(.42,.39,.34))
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
serif=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
T=Matrix(((1,D['shear_x'],0,D['x']),(D['shear_y'],1,0,D['y']),(0,0,1,D['base_z']),(0,0,0,1)))
front=T@face_matrix((0,0,0),(0,-1,0));side=T@face_matrix((W,0,0),(1,0,0))
# Nevill face runs from Lord Street towards the red-brick neighbour.
def finish(m,part='facades',mat=None,frame=None):
    if (m.name.startswith('Wall ') or m.name=='Pediment main') and frame is not None:m=conform({'wall':m})[0]['wall']
    ob=m.finish(mat if isinstance(mat,list) else [mat or stone],C[part])
    transform=frame if frame is not None else T
    if m.name.startswith('Ashlar '):
        bevel=ob.modifiers.new('Dressed stone chamfers','BEVEL');bevel.width=.023;bevel.segments=1;bevel.limit_method='ANGLE'
        bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    uv=ob.data.uv_layers.new(name='Metric surface')
    for p in ob.data.polygons:
        axes=sorted(sorted(range(3),key=lambda i:abs(p.normal[i]))[:2])
        for li in p.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
    ob['face_frame']=[list(row) for row in transform]
    ob.data.transform(transform)
    return ob

def box(name,c,size,part='facades',mat=None,frame=None):
    m=Mesh(name);m.box(c,size);return finish(m,part,mat,frame)
def text(name,body,u,z,out,height,width,frame,mat=gold,font=font):
    ob=text_object('Sign '+name,body,(0,0,0),(0,0,1),height,width,font,mat,extrude=.004,collection=C['frontage'],fit_bounds=True)
    local=Matrix.Translation((u,z,out))@ob.matrix_world.copy()
    bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
    ob.data.transform(frame@local);ob.matrix_world=Matrix.Identity(4)
    # Font UVs for export and baking.
    if not ob.data.uv_layers:
        uv=ob.data.uv_layers.new(name='Lettering')
        for p in ob.data.polygons:
            for li in p.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
    return ob

def wall_skin(name,length,holes,depth=.42):
    m=Mesh('Wall '+name)
    for p in cuts(rect(0,0,length,17.25),holes):
        for out,reverse in [(-depth,True),(-.02,False)]:
            poly=halfplane(p,(length+out,0),(length+out,1)) if name=='Lord' else halfplane(p,(-out,1),(-out,0)) if name=='Nevill' else p
            if len(poly)<3 or area(poly)<1e-9:continue
            verts=[(u,z,out) for u,z in poly]
            m.add(verts,[tuple(reversed(range(len(poly)))) if reverse else tuple(range(len(poly)))])
    for hole in holes:
        for a,b in zip(hole,hole[1:]+hole[:1]):
            m.add([(*a,-.02),(*b,-.02),(*b,-depth),(*a,-depth)],[(0,1,2,3)])
    return m

def framed_window(name,u,bottom,top,width,frame,rows=4,cols=4):
    h=top-bottom;z=(top+bottom)/2
    m=Mesh('Window '+name);m.box((u,z,-.23),(width,h,.06),0)
    # Broad rails and slender individual glazing bars kept separate in scale.
    for x in (u-width/2+.035,u+width/2-.035):m.box((x,z,-.10),(.07,h-.14,.11),1)
    for y in (bottom+.035,top-.035):m.box((u,y,-.10),(width,.07,.11),1)
    for i in range(1,cols):m.box((u-width/2+i*width/cols,z,-.085),(.047 if i!=cols//2 else .075,h-.14,.10),1)
    for i in range(1,rows):m.box((u,bottom+i*h/rows,-.078),(width-.14,.046 if i!=rows//2 else .075,.10),1)
    finish(m,mat=[glass,white],frame=frame)
    trim=Mesh('Trim window '+name)
    for sign in (-1,1):
        trim.box((u+sign*(width/2+.11),z,.10),(.22,h+.02,.20))
        trim.box((u+sign*(width/2+.2475),z,.17),(.055,h+.02,.24))
    trim.box((u,bottom-.10,.225),(width+.57,.18,.45));trim.box((u,top+.095,.19),(width+.53,.17,.34))
    finish(trim,frame=frame)

# Street elevations: real openings through wall and masonry skins, not dark
# rectangles glued over a solid mass. The flat roof is built separately below.
for name,frame,length,bays,columns in [('Lord',front,W,D['front_bays'],D['front_columns']),('Nevill',side,L,D['side_bays'],D['side_columns'])]:
    holes=[]
    for i,u in enumerate(bays):
        central=name=='Lord' and i==1
        holes.append(ellipse_arch(u,0 if central else .76,5.55,1.48,1.65 if central else 1.12))
        if not central:holes.append(rect(u-.34,7.50,u+.34,7.94))
        holes += [rect(u-.86,9.55,u+.86,12.65),rect(u-.86,14.15,u+.86,15.30)]
    finish(wall_skin(name,length,holes),frame=frame)
    # Continuous cornice profiles: shadow grooves and proper stepped projection.
    trims=Mesh('Trim continuous '+name)
    for z,profile in [(0,[(0,.13),(.15,.13),(.15,.06),(.68,.06),(.68,.15),(.79,.15),(.85,.10)]),
                      (1.45,[(0,.07),(.09,.09),(.13,.22),(.24,.22),(.29,.09),(.36,.09)]),
                      (5.45,[(0,.06),(.07,.18),(.13,.19),(.18,.08),(.25,.08)]),
                      (8.05,[(0,.03),(.13,.13),(.18,.15),(.24,.55),(.32,.75),(.45,.75),(.45,.08)]),
                      (15.75,[(0,.0),(.10,.23),(.18,.23),(.18,.07),(.35,.07),(.42,.30),(.52,.30),(.52,.09),(.93,.09),(1.01,.37),(1.12,.46),(1.25,.60),(1.50,.60),(1.50,.03)])]:
        # Cut plinth/courses across entry and window/arch openings.
        if z<8:
            segments=[(0,length)]
            if z<7:
                for u in bays:
                    segments=[q for a,b in segments for q in ((a,min(b,u-1.49)),(max(a,u+1.49),b)) if q[1]>q[0]+.01]
            for a,b in segments:moulding(trims,a,b,z,profile)
        else:moulding(trims,0,length,z,profile)
    trims.box((length/2,8.72,.34),(length,.44,.82))
    # Mitre the projecting cornice/fascia around the street corner.
    joined=Mesh(trims.name)
    for face in trims.faces:
        pts=[trims.vertices[v] for v in face]
        if all(abs(p[0]-(length if name=='Lord' else 0))<1e-7 for p in pts):continue
        if all(abs(p[0]-(0 if name=='Lord' else length))<1e-7 for p in pts):
            cap=halfplane([(z,out) for u,z,out in pts],(0,0),(1,0))
            pts=[(pts[0][0],z,out) for z,out in cap]
        if len(pts)>=3:joined.add(pts,[tuple(range(len(pts)))])
    trims=joined
    trims.vertices=[((length+out if abs(u-length)<1e-7 else u),z,out) if name=='Lord' else ((-out if abs(u)<1e-7 else u),z,out) for u,z,out in trims.vertices]
    finish(trims,mat=light,frame=frame)
    if DETAIL:
        ashlar=Mesh('Ashlar '+name)
        ashlar_holes=list(holes)
        for i,u in enumerate(bays):
            if name=='Lord' and i==1:continue
            ashlar_holes.extend([rect(u-1.635,.63,u+1.635,5.48),rect(u-.605,7.32,u+.605,8.11)])
        for row in range(18):
            lo=.83+row*.40;hi=min(8.03,lo+.375)
            if hi<=lo:continue
            for j in range(-1,int(length/1.25)+2):
                a=max(0,j*1.25+(row%2)*.625+.01);b=min(length,j*1.25+(row%2)*.625+1.235)
                if b<=a:continue
                for p in cuts(rect(a,lo,b,hi),ashlar_holes):ashlar.outline(p,.005,.065,(row+j)%6)
        finish(ashlar,mat=stonevar,frame=frame)
    for i,u in enumerate(bays):
        central=name=='Lord' and i==1
        # Recessed tympanum and cut-stone voussoirs.
        arch=Mesh('Arch '+name+' '+str(i));rise=1.65 if central else 1.12
        for j in range(11):
            a=math.pi*j/11+.008;b=math.pi*(j+1)/11-.008
            poly=[(u+1.48*math.cos(a),5.55+rise*math.sin(a)),(u+2.00*math.cos(a),5.55+(rise+.67)*math.sin(a)),(u+2.00*math.cos(b),5.55+(rise+.67)*math.sin(b)),(u+1.48*math.cos(b),5.55+rise*math.sin(b))]
            arch.outline(poly,.04,.16 if j!=5 else .22)
        # Back plane under arch, above rectangular glazing; the carved relief sits forward.
        tym=ellipse_arch(u,5.32,5.55,1.48,rise)
        arch.outline(tym,-.30,-.13)
        finish(arch,frame=frame)
        if not central:
            framed_window(name+' ground '+str(i),u,.82,5.30,2.70,frame,rows=6,cols=4)
            framed_window(name+' vent '+str(i),u,7.51,7.93,.64,frame,rows=1,cols=2)
            if DETAIL:finish(tympanum(u,5.88,i+(1 if name=='Lord' else 0)),frame=frame)
        else:
            # Square deeply recessed entrance with enriched architrave and triangular hood.
            box('Trim entrance soffit',(u,4.76,-.11),(2.15,.04,.50),frame=frame)
            box('Door shadow', (u,2.37,-.36),(2.15,4.74,.08),'frontage',black,frame)
            for x in (-.94,.94):box('Door timber jamb',(u+x,1.8825,-.19),(.12,3.765,.16),'frontage',door,frame)
            box('Door timber transom',(u,3.83,-.19),(2,.13,.16),'frontage',door,frame)
            box('Door glazing',(u,3.39,-.23),(1.76,.75,.06),'frontage',glass,frame)
            for x in (-.46,.46):box('Door timber leaf',(u+x,1.49,-.23),(.84,2.98,.07),'frontage',door,frame)
            for x in (-.46,.46):box('Door glazed leaf',(u+x,1.86,-.18),(.72,2.08,.05),'frontage',glass,frame)
            for x in (-.10,.10):box('Door handle',(u+x,1.25,-.09),(.026,.34,.055),'frontage',gold,frame)
            trim=Mesh('Trim entrance architrave')
            for sign in (-1,1):
                for offset,width,depth in [(1.12,.18,.34),(1.28,.10,.42),(1.40,.08,.34)]:trim.box((u+sign*offset,2.40,depth/2),(width,4.80,depth))
            for z,w,h,out in [(4.88,2.9,.16,.38),(5.23,3.03,.18,.43),(5.48,3.22,.18,.50)]:trim.box((u,z,out/2),(w,h,out))
            trim.outline([(u-1.68,5.57),(u+1.68,5.57),(u,6.37)],.06,.23)
            beam(trim,(u-1.75,5.58,.37),(u,6.45,.37),.13,.24);beam(trim,(u,6.45,.37),(u+1.75,5.58,.37),.13,.24)
            finish(trim,frame=frame)
            box('Plaque established',(u,5.03,.43),(1.12,.48,.10),'frontage',light,frame)
            text('established','ESTABLISHED',u,5.13,.489,.10,.96,frame,black,serif);text('date','1833',u,4.95,.489,.13,.43,frame,black,serif)
            if DETAIL:
                finish(cartouche(u,7.04),frame=frame)
                carving=Mesh('Fine entrance beading')
                for sign in (-1,1):
                    for j in range(38):
                        z=.18+j*.12
                        leaf(carving,u+sign*1.26,z,.47,.14,sign*.32,.045)
                    scroll(carving,u+sign*1.40,5.31,.43,.12,.24,sign)
                for j in range(24):
                    if abs(-1.34+j*.116)<.67:continue
                    leaf(carving,u-1.34+j*.116,5.09,.43,.16,.55,.045)
                for sign in (-1,1):
                    for offset,outset in [(1.06,.35),(1.16,.37),(1.36,.38),(1.44,.35)]:
                        carving.box((u+sign*offset,2.46,outset),(.025,4.78,.024))
                for j in range(34):
                    carving.box((u-1.47+j*.089,5.44,.50),(.040,.095,.055))
                beam(carving,(u-1.43,5.66,.245),(u,6.24,.245),.035,.025)
                beam(carving,(u,6.24,.245),(u+1.43,5.66,.245),.035,.025)
                finish(carving,frame=frame)
        for j,(bottom,top) in enumerate([(9.55,12.65),(14.15,15.30)]):
            framed_window(name+' upper '+str(i)+' '+str(j),u,bottom,top,1.72,frame,rows=4 if j==0 else 2,cols=4)
            if j==0:
                hood=Mesh('Trim hood '+name+' '+str(i))
                moulding(hood,u-1.17,u+1.17,12.90,[(0,.02),(.12,.19),(.23,.22),(.28,.40),(.40,.40),(.40,.02)])
                for sign in (-1,1):
                    hood.outline([(u+sign*1.06-.11,12.48),(u+sign*1.06+.11,12.48),(u+sign*1.06+.14,13.12),(u+sign*1.06-.14,13.12)],.04,.31)
                if central:
                    hood.outline(ellipse_arch(u,12.96,12.96,1.10,.55),.06,.23)
                    arc(hood,u,12.96,1.10,.55,.12,out=.43)
                finish(hood,frame=frame)
            elif DETAIL:finish(mask(u,15.62,.92),frame=frame)
        finish(balustrade(u,8.90,2.25,DETAIL),frame=frame)
    for u in columns:finish(column(u,detail=DETAIL),frame=frame)
    if DETAIL:
        dentils=Mesh('Fine cornice '+name)
        for i in range(int(length/.22)):
            u=.10+i*.22;dentils.box((u,8.20,.56),(.11,.17,.24))
        for i in range(int(length/.43)):
            u=.23+i*.43;dentils.box((u,16.92,.32),(.25,.16,.46))
            # Mutule soffit drops (six stone guttae per block).
            for x in (-.065,.065):
                for out in (.22,.34,.46):dentils.box((u+x,16.825,out),(.035,.035,.035))
        # Triglyphs alternating with plain metopes in Doric frieze.
        for i in range(int(length/.90)):
            u=.30+i*.90
            for x in (-.12,0,.12):dentils.box((u+x,16.43,.13),(.055,.34,.08))
        finish(dentils,frame=frame)
        if name=='Lord':
            motif=Mesh('Fine frieze central palmette')
            for sign in (-1,1):
                scroll(motif,W/2+sign*.23,16.43,.20,.23,.16,sign)
                for j in range(4):leaf(motif,W/2+sign*.07,16.27,.18,.31,sign*(.25+j*.28),.045)
            finish(motif,frame=frame)
    # All lettering is authored geometry and fits the observed sill fascia.
    text(name+' rose','OCCULO    LOUNGE',length/2,8.67,.795,.40,min(8.6,length-3),frame,pink)
    text(name+' gold','OCCULO    LOUNGE',length/2,8.67,.812,.40,min(8.6,length-3),frame,gold)
    if name=='Lord':
        text('cafe','CAFÉ',1.90,8.66,.812,.20,1.0,frame,black);text('bar','BAR',W-1.72,8.66,.812,.20,.70,frame,black)

# Party/rear envelope. The narrow court face has three stacked windows in
# photogrammetry; exact mullions are estimates, unlike the street elevations.
plan=[(0,0),(W,0),(W,L),(4.5,L),(4.5,6),(0,6)]
for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
    if i<2:continue
    if i==3:
        f=T@face_matrix((4.5,L,0),(-1,0,0));length=L-6
        holes=[rect(length-3.8,lo,length-1.5,hi) for lo,hi in [(6.2,8.6),(10.4,12.5),(14.5,15.6)]]
        finish(wall_skin('rear court',length,holes,.30),mat=stone,frame=f)
        for j,(lo,hi) in enumerate([(6.2,8.6),(10.4,12.5),(14.5,15.6)]):framed_window('rear court '+str(j),length-2.65,lo,hi,2.3,f,rows=3 if j<2 else 2,cols=3)
    else:
        m=Mesh('Wall rear '+str(i));v=[(*a,0),(*b,0),(*b,17.20),(*a,17.20)]
        m.add(v,[(0,1,2,3)]);finish(m,mat=brick)
# Two visible vertical window stacks on the exposed party wall of the front strip.
party=T@face_matrix((0,6,0),(-1,0,0))
# Treat the otherwise hidden party face as restrained massing until better imagery.
# Roof uses the same L-shaped perimeter. No pitched roof behind the pediment.
m=Mesh('Roof flat deck');m.outline(plan,17.20,17.35);finish(m,'roof',roofmat)
for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
    if i in (0,1):continue
    x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
    dx=max(.22,abs(b[0]-a[0]));dy=max(.22,abs(b[1]-a[1]))
    if i==2:x+=.055;dx-=.11
    if i==4:dx-=.22
    box('Roof parapet '+str(i),(x,y,17.58),(dx,dy,.46),'roof',stone)
box('Roof street closure',(W+.04,L/2,17.30),(.24,L,.12),'roof',stone)
# Front attic wall behind the shallow pediment and urns, not a deep gabled roof.
box('Roof attic front',(W/2,.85,18.02),(W-.72,.38,1.34),'roof',stone)
box('Roof attic coping',(W/2,.85,18.73),(W-.58,.52,.12),'roof',light)
# Raised rear access volume visible in all aerials, details deliberately restrained.
box('Roof rear access',(6.55,14.50,18.05),(3.20,3.50,1.40),'roof',stone)
box('Roof rear access cap',(6.55,14.50,18.79),(3.40,3.70,.12),'roof',lead)
for j,y in enumerate((5.2,10.9)):
    box('Rooflight curb '+str(j),(W-6.2,y,17.56),(1.90,1.90,.42),'roof',stone)
    box('Rooflight glass '+str(j),(W-6.2,y,17.80),(1.55,1.55,.08),'roof',glass)
    for sign in (-1,1):
        box('Rooflight frame '+str(j),(W-6.2+sign*.85,y,17.83),(.08,1.80,.10),'roof',lead)
        box('Rooflight frame '+str(j),(W-6.2,y+sign*.85,17.83),(1.62,.08,.10),'roof',lead)
# Front pediment with a true round oculus through the tympanum.
ped=Mesh('Pediment main')
hole=[(W/2+.48*math.cos(math.tau*i/48),18.12+.48*math.sin(math.tau*i/48)) for i in range(48)]
triangle=[(0,17.25),(W,17.25),(W/2,19.70)]
for p in cuts(triangle,[hole]):
    for out,reverse in [(-.06,True),(.15,False)]:
        ped.add([(*v,out) for v in p],[tuple(reversed(range(len(p)))) if reverse else tuple(range(len(p)))])
for boundary,reverse in [(triangle,False),(hole,True)]:
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        ped.add([(*a,-.06),(*b,-.06),(*b,.15),(*a,.15)],[(3,2,1,0) if reverse else (0,1,2,3)])
finish(ped,frame=front)
ring=Mesh('Trim oculus');arc(ring,W/2,18.12,.48,.48,.075,out=.22,start=0,end=math.tau,steps=64);finish(ring,frame=front)
# One mitred raking cornice rather than two overlapping beams at the apex.
raking=Mesh('Trim pediment cornice');slope=2.45/(W/2);rise=.14*math.sqrt(1+slope*slope)
raking.outline(halfplane([(0,17.25-rise),(W/2,19.70-rise),(W,17.25-rise),(W,17.25+rise),(W/2,19.70+rise),(0,17.25+rise)],(0,17.25),(1,17.25)),.08,.56)
finish(raking,frame=front)
# Recessed dark oculus glazing, ring is carried by stone.
m=Mesh('Window oculus');m.outline([(W/2+.47*math.cos(math.tau*i/48),18.12+.47*math.sin(math.tau*i/48)) for i in range(48)],-.24,-.21);finish(m,mat=glass,frame=front)
if DETAIL:
    m=Mesh('Fine pediment mutules')
    for sign in (-1,1):
        for j in range(12):
            x=W/2+sign*(.42+j*.56);z=19.70-abs(x-W/2)*2.45/(W/2)-.20
            m.box((x,z,.26),(.30,.18,.38))
    finish(m,frame=front)
    for x in (.45,W-.45):
        m=Mesh('Urn front '+str(x));m.lathe((x,-.08),[(17.48,.20),(17.60,.22),(17.68,.13),(17.85,.16),(18.05,.27),(18.24,.21),(18.34,.12),(18.41,.14),(18.52,.03)],40);finish(m,'roof')
    # Projecting rectangular burgundy cafe signs, two readable faces.
    for name,u,frame in [('Lord',W-.55,front),('Nevill',.65,side)]:
        box('Sign bracket '+name,(u,7.43,.65),(.06,.07,1.15),'frontage',black,frame)
        box('Sign blade '+name,(u,6.93,1.00),(.07,.90,.76),'frontage',pink,frame)
        for direction in (-1,1):
            # Face coordinates remain upright: blade horizontal is facade normal.
            signframe=frame@Matrix(((0,0,direction,u+direction*.042),(0,1,0,6.93),(-direction,0,0,1.0),(0,0,0,1)))
            text(name+' blade occulo '+str(direction),'OCCULO',0,.12,.002,.105,.61,signframe,gold)
            text(name+' blade lounge '+str(direction),'LOUNGE',0,-.04,.002,.105,.61,signframe,gold)
            text(name+' blade cafe '+str(direction),'CAFÉ BAR',0,-.23,.002,.045,.39,signframe,gold)
if DETAIL:
    for y in (13.65,15.15):
        box('Roof access dark light',(4.94,y,18.13),(.025,.46,.46),'roof',glass)
# Scene for repeatable comparison renders.
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.world=s.world or bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.73,.79,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sun.data.energy=2.3;sun.rotation_euler=(.7,-.45,-.65);s.collection.objects.link(sun)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO'
s.render.resolution_x=1500;s.render.resolution_y=1400;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/occulo.blend'))
