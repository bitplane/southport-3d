"""Build the London Square exterior study in Blender 5, using metres.

blender -b --factory-startup --python scripts/build_memorial.py -- --preview
The script is deterministic and does not require network access or an MCP.
"""
import bpy
import os
import sys
import json
import math
import random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from geometry import Mesh, face_matrix, text_object, TAU
import reliefs
import ornamental_lamps
import pedestal_joints
import obelisk_fixtures
import shaft_masonry
import obelisk_surfaces
import site_grade
import wwii_roundel
import column_geometry
from sculpt_surface import simplify_relief, trim_empty_relief_background

ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
PREVIEW='--preview' in ARGS
NO_RENDER='--no-render' in ARGS
NO_EXPORT='--no-export' in ARGS
SPEC=json.loads((ROOT/'research/modelling_spec.json').read_text())
COL=SPEC['colonnade_vertical_datums']
TROPHY=SPEC['dimensions']['horizontal_trophy_field']
SITE=json.loads((ROOT/'research/site_layout.json').read_text())
random.seed(1923)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['project']='Southport / London Square war memorial exterior study'
scene['origin_wgs84']=SITE['origin_wgs84_lat_lon']
scene['site_rotation_from_east_degrees']=SITE['site_rotation_from_east_degrees']
scene['status']='Research reconstruction; sculptural figures and site widths provisional; interiors deferred'
scene['source_manifest']='../research/reference_catalog.json'
scene['north_vector_site_xy']=SITE['north_vector_site_xy']
for sub in ('models','renders','textures'):(ROOT/sub).mkdir(exist_ok=True)

def coll(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c

CONTEXT=coll('00 Site registration and approximate paving')
OBELISK=coll('01 Obelisk exterior')
NE=coll('02 North-east colonnade exterior')
SW=coll('03 South-west colonnade exterior')
LAMPS=coll('04 Clustered lamp standards — placement provisional')
LIGHTS=coll('90 Lighting and cameras')
GUIDES=coll('99 Survey guides — hidden in renders')

def material(name,color,roughness=.75,stone=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree;bsdf=nt.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=roughness
    if stone:
        coord=nt.nodes.new('ShaderNodeTexCoord')
        noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=75
        noise.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
        bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.007
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
        broad=nt.nodes.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=2.7;broad.inputs['Detail'].default_value=3
        nt.links.new(coord.outputs['Object'],broad.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.17;ramp.color_ramp.elements[0].color=tuple(v*.86 for v in color)+(1,)
        ramp.color_ramp.elements[1].position=.84;ramp.color_ramp.elements[1].color=tuple(min(v*1.08,1) for v in color)+(1,)
        nt.links.new(broad.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    return m

STONE=[material('Portland limestone '+str(i+1),(.57+i*.014,.548+i*.013,.487+i*.012),stone=True) for i in range(6)]
STONE_DARK=material('Damp stone and sheltered cornices',(.33,.325,.295),stone=True)
GROOVE=material('Incised stone — exposed cut faces',(.48,.462,.410),stone=True)
PAVER=material('Grey granite paving',(.29,.315,.33),stone=True)
PALE_PAVER=material('Pale granite paving',(.49,.47,.415),stone=True)
ASPHALT=material('Asphalt — approximate road widths',(.12,.133,.14),stone=True)
JOINT=material('Narrow stone joints',(.31,.30,.27))
ROOF=material('Flat roof covering — provisional',(.24,.245,.235),.9)
WHITE_IRON=material('Ivory painted iron',(.64,.66,.61),.42)
BLACK_IRON=material('Black painted plinths',(.035,.045,.045),.38)
GLASS=material('Opaque ivory lamp globes',(.77,.78,.64),.31)
LIGHT_HOUSING=material('Pale metal obelisk light housings',(.56,.59,.58),.40)
LIGHT_HOUSING.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.45
GRILLE_METAL=material('Weathered obelisk grille metal',(.12,.14,.12),.65)
GRILLE_METAL.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.30
FONT=bpy.data.fonts.load(os.environ.get('SOUTHPORT_FONT', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'))
INSCRIPTION_LOG=[]
RELIEF_APPROXIMATION_LOG=[]
COLUMN_TEMPLATE=None
LAMP_TEMPLATES={}
RELIEF_TEMPLATES={}

def finish(m,c,bevel=.003,smooth=False):return m.finish(STONE+[STONE_DARK],c,bevel,smooth)

def block(name,centre,size,c,mat=None,bevel=.003):
    m=Mesh(name);m.box(centre,size)
    return m.finish([mat or STONE[2]],c,bevel)

def masonry(m,centre,width,depth,z0,z1,face='y',course=.40,block_width=.75):
    """Individual narrow-jointed ashlar courses; depth extends through wall."""
    rows=max(1,round((z1-z0)/course));h=(z1-z0)/rows
    for j in range(rows):
        a=-width/2;segments=[];step=block_width
        if j%2:segments.append((a,min(a+step*.5,width/2)));a+=step*.5
        while a<width/2-.001:
            b=min(a+step,width/2);segments.append((a,b));a=b
        for a,b in segments:
            x=centre[0];y=centre[1];z=z0+(j+.5)*h
            if face=='y':m.box((x+(a+b)/2,y,z),(b-a-.004,depth,h-.003),random.randrange(6))
            else:m.box((x,y+(a+b)/2,z),(depth,b-a-.004,h-.003),random.randrange(6))

def engrave(target,name,body,origin,normal,height,max_width,c,fit_bounds=False):
    """True recessed lettering, Boolean cut through the visible surface."""
    # Apply the edge bevel once, before cutting the first inscription.
    bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
    for existing in list(target.modifiers):
        if existing.type=='BEVEL':bpy.ops.object.modifier_apply(modifier=existing.name)
    n=Vector(normal);p=Vector(origin)-n*.001
    cutter=text_object(name+' cutter',body,p,normal,height,max_width,FONT,GROOVE,extrude=.005,collection=c,fit_bounds=fit_bounds)
    bpy.ops.object.select_all(action='DESELECT');cutter.select_set(True);bpy.context.view_layer.objects.active=cutter
    bpy.ops.object.convert(target='MESH')
    cutter=bpy.context.object
    # Transfer a slightly darker limestone material to newly cut faces.
    cutter.data.materials.clear();cutter.data.materials.append(target.data.materials[0]);cutter.data.materials.append(GROOVE)
    for p in cutter.data.polygons:p.material_index=1
    if GROOVE.name not in target.data.materials:target.data.materials.append(GROOVE)
    mod=target.modifiers.new(name+' recessed 6 mm','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=target;target.select_set(True);cutter.select_set(False)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    target['inscription']=body
    INSCRIPTION_LOG.append({'object':target.name,'name':name,'text':body,'origin_local':list(origin),'height_m':height,'width_m':max_width,'fit_glyph_bounds':fit_bounds,'method':'Boolean recessed glyphs; approximate Roman serif font'})

def mounted(m,origin,normal,c,scale=(1,1,1),smooth=False):
    mat=face_matrix(origin,normal) @ Matrix.Diagonal((*scale,1))
    # Preserve instances in glTF: geometry stays in panel coordinates, placement
    # lives on the object. Unique figure geometry is kept fully editable.
    key=(m.name,len(m.vertices),len(m.faces),tuple(m.vertices[:2]),tuple(m.vertices[-2:]),smooth)
    if key in RELIEF_TEMPLATES:
        template=RELIEF_TEMPLATES[key];o=template.copy();o.data=template.data;c.objects.link(o)
    else:
        o=finish(m,c,0,smooth)
        # Curved leaves and traced relief surfaces already supply their shape.
        # A bevel on every overlapping leaf produced excessive export geometry.
        RELIEF_TEMPLATES[key]=o
    o.matrix_world=mat;o['geometry_method']='Independently constructed from catalogued photographs; depths estimated'
    return o

def column(name,x,y,c):
    global COLUMN_TEMPLATE
    position=Vector((x,y,0))
    if COLUMN_TEMPLATE is not None:
        ob=COLUMN_TEMPLATE.copy();ob.data=COLUMN_TEMPLATE.data;c.objects.link(ob);ob.name=name
        ob.matrix_world=Matrix.Translation(position)
        return ob
    radius_scale=SPEC['dimensions']['column_shaft_diameter_lower']['value']/.66
    m=column_geometry.build_mesh(name,COL['shaft_top'],radius_scale)
    o=finish(m,c,.001,True);o['flutes']=20;o['flute_count_status']='provisional photographic count';o['shaft_taper_m']=[.48,.40]
    o['dimension_reference']='research/colonnade_vertical_proportion_study.json; conditional photographic estimate, not survey'
    o['capital_construction']='Lower annulus, plain cylindrical neck, spreading echinus, square abacus'
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    o.location=position;COLUMN_TEMPLATE=o
    return o


def mounted_flora(kind,origin,normal,c):
    m=reliefs.frieze_foliage() if kind=='frieze-foliage' else reliefs.architectural_rosette()
    o=mounted(m,origin,normal,c,smooth=True)
    if not o.data.get('surface_reduced'):
        check=simplify_relief(o,ROOT/'research/relief-data'/(kind+'.npz'),ratio=.30)
        radius=.087 if kind=='architectural-rosette' else None
        check['empty_background_faces_removed_after_check']=trim_empty_relief_background(o,radial_limit=radius)
        check['post_check_radial_limit_m']=radius
        RELIEF_APPROXIMATION_LOG.append(check);o.data['surface_reduced']=True
    o['floral_kind']=kind
    o['source_detail']='research/relief-data/'+kind+'-traces.json'
    o['status']='Photographic interpretation; absolute size, depth and individual surface variations estimated'
    if kind=='architectural-rosette':o['petals']=12
    return o

def window_frame(x,y,normal,c):
    # Exterior opening with two separately capped pilasters, not a lower lintel.
    # Width / aspect are photographic estimates; see window_calibration.json.
    n=Vector(normal)
    dims=SPEC['dimensions']['exterior_window']
    for dx in (-dims['jamb_centre_offset_m'],dims['jamb_centre_offset_m']):
        m=Mesh('Window stone jamb')
        masonry(m,(x+dx,y),dims['jamb_width_m'],.12,.35,3.011,course=.40,block_width=2)
        jamb=finish(m,c,.002);jamb['window_part']='jamb'
        cap=Mesh('Window individual jamb capital')
        cap.rect_profile((x+dx,y),[(3.011,.380,.12),(3.026,.395,.135),
            (3.050,.422,.158),(3.069,.434,.170),(3.078,.450,.186),(3.100,.450,.186)],2)
        capital=finish(cap,c,.0015);capital['window_part']='individual capital'
    for z,w,h,d in [(1.110,1.04,.04,.16),(1.165,1.08,.07,.18)]:
        block('Window sill moulding',(x,y-n.y*.015,z),(w,d,h),c)
    band=block('Window rosette lintel band',(x,y,3.21),(2.30,.12,.220),c)
    block('Window lintel upper moulding',(x,y+n.y*.015,3.340),(2.36,.17,.035),c)
    for xx in (-dims['jamb_centre_offset_m'],dims['jamb_centre_offset_m']):
        ro=mounted_flora('architectural-rosette',(x+xx,y+n.y*.058,3.21),normal,c)
        ro['support_object']=band.name;ro['setting_type']='window lintel'
    apron=Mesh('Window apron with recessed blank field')
    apron.box((x,y-n.y*.015,.725),(1.05,.075,.770),1)
    apron.cut_box_from_ashlar((x,y+n.y*.045,.725),(.88,.055,.530))
    finish(apron,c,.0015)

def end_panel(x,normal,c,kind):
    # One planar framed panel per end, with masonry retained to both sides.
    m=Mesh('End elevation pilasters and panel frame')
    for y in (-.73,.73):
        masonry(m,(x,y),.39,.15,.37,3.111,face='x',course=.40,block_width=2)
        for z,w,h in [(3.1285,.42,.035),(3.1685,.47,.045),(3.1945,.49,.011)]:
            m.box((x,y,z),(.20,w,h),2)
    for z,w,h in [(.66,2.30,.16),(1.13,1.16,.075),(1.19,1.19,.04),(3.4425,2.34,.045),(3.4825,2.38,.035)]:
        m.box((x,0,z),(.20,w,h),2)
    m.box((x,0,3.31),(.20,2.32,.22),2)
    frame=finish(m,c)
    n=Vector(normal)
    # Narrower photographic estimate, anchored to the source panel aspect.
    # Absolute size / ground datum remain uncertain; see modelling_spec.json.
    dims=SPEC['dimensions']['exterior_end_plaque']
    bottom=dims['bottom_z_m'];height=dims['height_m'];width=dims['width_m']
    sx=width/1.06;sz=height/2.15
    def panel_z(previous):return bottom+(previous-1.05)*sz
    panel=block(kind+' carved panel',(x+n.x*.022,0,bottom+height/2),(.09,width,height),c,STONE[3],.002)
    panel['dimension_confidence']=dims['confidence']
    face_x=x+n.x*.068
    # Sink the uncarved surface grid into its backing by 1 mm: the grid's
    # rectangular perimeter is a construction aid, not a joint in the stone.
    sculpt_x=face_x-n.x*.003
    for y in (-.73,.73):
        ro=mounted_flora('architectural-rosette',(x+n.x*.098,y,3.31),normal,c)
        ro['support_object']=frame.name;ro['setting_type']='end lintel'
    # Lower rectangular moulded panel, left blank as visible in references.
    block('End lower panel',(x,0,.79),(.09,1.09,.49),c,STONE[1])
    if kind in ('NE_SE','SW_SE'):
        o=mounted(reliefs.crossed_torches(),(sculpt_x,0,panel_z(2.745)),normal,c,scale=(sx,sz,1),smooth=True)
        if not o.data.get('surface_reduced'):
            RELIEF_APPROXIMATION_LOG.append(simplify_relief(o,ROOT/'research/relief-data/crossed-torches.npz',ratio=.32))
            o.data['surface_reduced']=True
        o['geometry_method']='Traced exterior torch relief; authored depths with bounded 3 mm fine shading detail'
        o['source_detail']='iwm-mont_8a.jpg; see research/relief-data/crossed-torches-traces.json'
        o['status']='Common carving design; NE surface erosion differs; all depths estimated'
        lines=SPEC['exterior_inscriptions'][kind+'_panel']
        top=2.258 if kind=='NE_SE' else 2.256
        spacing=.073 if kind=='NE_SE' else .076
        height=.055 if kind=='NE_SE' else .053
        # Match photographed line breaks; line width fitted only when necessary.
        for i,line in enumerate(lines):
            engrave(panel,kind+' line '+str(i+1),line,(face_x,0,panel_z(top-i*spacing)),normal,height*sz,.99*sx,c)
    elif kind=='NE_NW':
        o=mounted(reliefs.victory(),(sculpt_x,0,panel_z(1.075)),normal,c,scale=(.99/1.40*sx,2.10/2.75*sz,1),smooth=True)
        RELIEF_APPROXIMATION_LOG.append(simplify_relief(o,ROOT/'research/relief-data/victory.npz'))
        o['status']='Traced exterior sculpture; single-view depths estimated; outer left edge supplemented from IWM'
        o['source_detail']='centenary-03.jpg and iwm-mont_9.jpg; see research/relief-data/victory-traces.json'
        o['geometry_method']='Traced depth layers with bounded shading-gradient detail; all depths estimated'
    else:
        o=mounted(reliefs.mourning(),(sculpt_x,0,panel_z(1.075)),normal,c,scale=(.99/1.40*sx,2.10/2.75*sz,1),smooth=True)
        RELIEF_APPROXIMATION_LOG.append(simplify_relief(o,ROOT/'research/relief-data/mourning.npz'))
        o['status']='Traced exterior sculpture; single-view depths estimated; PATRIA incised into surface'
        o['source_detail']='centenary-03.jpg and iwm-mont_9a.jpg; see research/relief-data/mourning-traces.json'
        o['geometry_method']='Traced depth layers with bounded shading-gradient detail; all depths estimated'
        o['inscription']='PATRIA'

def lamp(x,y,c,kind='single'):
    if kind=='single':
        site_grade.lamp_plinth(globals(),x,y,c)
    if kind in LAMP_TEMPLATES:
        template=LAMP_TEMPLATES[kind];ob=template.copy();ob.data=template.data;c.objects.link(ob)
    else:
        m=ornamental_lamps.short_standard() if kind=='single' else ornamental_lamps.clustered_standard()
        ob=m.finish([BLACK_IRON,WHITE_IRON,GLASS],c,0,True)
        ob['lamp_type']=kind;ob['globe_count']=1 if kind=='single' else 5
        ob['reference']='Commons columns 1/2 and Flickr 7465683304; research/column_lamp_calibration.json'
        ob['status']='Authored cast-iron detail; dimensions and small acanthus forms estimated'
        LAMP_TEMPLATES[kind]=ob
    ob.matrix_world=Matrix.Translation(Vector((x,y,site_grade.LAMP_SHIFT if kind=='single' else 0)))
    return ob

def mounted_trophy(kind,origin,normal,c):
    o=mounted(reliefs.trophy(kind),origin,normal,c,
              scale=(TROPHY['width_m']/2.10,TROPHY['height_m']/.60,1),smooth=True)
    if not o.data.get('surface_reduced'):
        RELIEF_APPROXIMATION_LOG.append(simplify_relief(o,ROOT/('research/relief-data/trophy-'+kind+'.npz'),ratio=.32))
        o.data['surface_reduced']=True
    sources={'wreath':'iwm-mont_13a.jpg','pelta':'iwm-mont_13.jpg','victory':'iwm-mont_13b.jpg'}
    o['geometry_method']='Traced '+kind+' trophy with authored depth layers and bounded shading detail'
    o['source_detail']=sources[kind]+'; see research/relief-data/trophy-'+kind+'-traces.json'
    o['status']='Shared motif interpretation; individual weathering and damage not reconstructed; depth estimated'
    return o

def build_colonnade(code,c):
    import colonnade_assembly
    before=set(bpy.data.objects)
    colonnade_assembly.build(globals(),code,c,SPEC['colonnade_plan'])
    centre=SITE['colonnades'][code]['centre_site_xy_m']
    transform=Matrix.Translation(Vector((centre[0],centre[1],0))) @ Matrix.Rotation(math.pi/2,4,'Z')
    for ob in set(bpy.data.objects)-before:ob.matrix_world=transform @ ob.matrix_world;ob['assembly']=code
    print('ASSEMBLY',code,'objects',len(set(bpy.data.objects)-before),flush=True)

def build_obelisk():
    m=Mesh('Obelisk base mouldings')
    m.box((0,0,-.10),(4.70,4.70,.20),1)
    for z,w,h in [(.115,4.70,.23),(.275,4.22,.09),(.775,3.65,.91),(1.44,3.25,.40)]:m.box((0,0,z),(w,w,h),1)
    m.rect_profile((0,0),[(1.64,3.20,3.20),(1.72,3.20,3.20),(1.79,3.10,3.10),
                               (1.90,2.86,2.86),(2.05,2.66,2.66),(2.12,2.61,2.61)],2)
    finish(m,OBELISK,.006)
    body=block('Square obelisk pedestal',(0,0,3.08),(2.55,2.55,1.92),OBELISK,STONE[3],.003)
    caps=Mesh('Obelisk pedestal cornice')
    caps.rect_profile((0,0),[(4.04,2.56,2.56),(4.12,2.58,2.58),(4.16,2.69,2.69),
                                  (4.23,2.75,2.75),(4.27,2.91,2.91),(4.34,2.93,2.93),
                                  (4.51,2.86,2.86),(4.56,2.91,2.91)],3)
    caps.box((0,0,4.67),(2.12,2.12,.22),1);finish(caps,OBELISK,.004)
    shaft_masonry.build(OBELISK,STONE,obelisk_surfaces.shaft_palette())
    # Keep the existing colonnade palette reproducible while replacing the old
    # shaft. Its 38-row generator consumed 252 material draws; the registered
    # shaft uses its own RNG and does not alter other assemblies' materials.
    for _ in range(252):random.randrange(6)
    pyramid=obelisk_fixtures.build_pyramid(OBELISK,STONE[3],GRILLE_METAL,BLACK_IRON)
    obelisk_surfaces.apply_pyramid(pyramid)
    obelisk_fixtures.build_linear_lights(OBELISK,LIGHT_HOUSING,BLACK_IRON)
    # Actual exterior roundels. Front NW is +site Y; SE crest on -site Y.
    for face,normal in [('NW',(0,1,0)),('SE',(0,-1,0)),('SW',(-1,0,0))]:
        origin=Vector(normal)*1.278;origin.z=3.06
        m=Mesh('Obelisk '+face+' roundel border')
        m.closed_ring((0,0,.007),.647,.011)
        m.closed_ring((0,0,.009),.607,.008)
        border=mounted(m,origin,normal,OBELISK,smooth=True)
        pedestal_joints.cut_mesh_strips(border,face,cap=True)
        if face=='NW':
            wreath=mounted(reliefs.salute_wreath(),(0,1.273,3.06),normal,OBELISK,smooth=True)
            check=simplify_relief(wreath,ROOT/'research/relief-data/salute-wreath.npz',ratio=.28)
            check['trimmed_background_faces']=trim_empty_relief_background(wreath)
            RELIEF_APPROXIMATION_LOG.append(check)
            wreath['source_detail']='research/relief-data/salute-wreath-traces.json'
            wreath['leaf_count']=63
            wreath['status']='Photo-traced laurel branches; depth, veins and worn tips interpreted'
    for i,line in enumerate(SPEC['exterior_inscriptions']['obelisk_NW']):
        row=SPEC['salute_lettering_layout']['lines'][i]
        engrave(body,'Obelisk salute '+str(i),line,(-row['centre_u_m'],1.2751,row['centre_z_m']),(0,1,0),row['height_m'],row['width_m'],OBELISK,fit_bounds=True)
    pedestal_joints.cut_body_channels(body,OBELISK,GROOVE)
    body['salute_underline_width_height_m']=[.090,.006]
    date=block('Obelisk front date block',(0,1.626,1.44),(3.25,.015,.40),OBELISK,STONE[1])
    engrave(date,'Obelisk dates',SPEC['exterior_inscriptions']['obelisk_NW_date'],(0,1.634,1.46),(0,1,0),.22,3.02,OBELISK)
    arms=mounted(reliefs.southport_arms(),(0,-1.2725,3.06),(0,-1,0),OBELISK,smooth=True)
    RELIEF_APPROXIMATION_LOG.append(simplify_relief(arms,ROOT/'research/relief-data/southport-arms.npz',ratio=.26))
    arms['geometry_method']='Traced shield, crosslets, galley, naval crown and serpent; estimated depth layers'
    arms['source_detail']='iwm-mont_3a.jpg; research/relief-data/southport-arms-traces.json'
    arms['inscription']='SALVS POPVLI'
    arms['lettering_method']='Eleven Roman serif glyphs incised 3.5 mm into the numeric ribbon surface'
    arms['status']='Small worn forms and depth interpreted from a photograph; no measured relief survey'
    arms['masonry_joint_reference']='research/pedestal_joint_layout.json'
    wwii_roundel.build(globals())
    print('ASSEMBLY OBELISK',flush=True)

def capsule(m,width,length,z0,z1,segments=32):
    r=width/2;cy=length/2-r;pts=[]
    for i in range(segments+1):
        a=math.pi*i/segments;pts.append((r*math.cos(a),cy+r*math.sin(a)))
    for i in range(segments+1):
        a=math.pi+math.pi*i/segments;pts.append((r*math.cos(a),-cy+r*math.sin(a)))
    m.outline(pts,z0,z1)

def site_context():
    block('Working site ground',(0,0,-.19),(116,72,.24),CONTEXT,PAVER,0)
    # Road ribbons follow OSM centrelines. Width is a labelled placeholder.
    for road_index,road in enumerate(SITE['road_centrelines']):
        pts=road['points_site_xy_m'];m=Mesh(road['name']+' road placeholder')
        for segment_index,(a,b) in enumerate(zip(pts,pts[1:])):
            if min(abs(a[0]),abs(b[0]))>61 or min(abs(a[1]),abs(b[1]))>40:continue
            dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
            if length<.001:continue
            w=3.7;nx=-dy/length*w;ny=dx/length*w
            z=-.052+road_index*.0002+segment_index*.00001
            # Clip the placeholder strips to the working site rectangle.
            quad=[(a[0]+nx,a[1]+ny),(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny)]
            for axis,bound,sign in [(0,58,1),(0,-58,-1),(1,36,1),(1,-36,-1)]:
                clipped=[]
                for p,q in zip(quad,quad[1:]+quad[:1]):
                    pin=sign*p[axis]<=sign*bound;qin=sign*q[axis]<=sign*bound
                    if pin:clipped.append(p)
                    if pin!=qin:
                        t=(bound-p[axis])/(q[axis]-p[axis]);clipped.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
                quad=clipped
                if not quad:break
            if len(quad)>2:m.add([(x,y,z) for x,y in quad],[tuple(range(len(quad)))])
        o=m.finish([ASPHALT],CONTEXT);o['status']='OSM centreline; estimated 7.4 m width, no kerb survey'
    island=Mesh('Central monument island — outline provisional');capsule(island,15.2,34.2,-.07,.0)
    island.finish([PALE_PAVER],CONTEXT,.025)
    # Four tall standards stand on the flanking pavements, as visible in the
    # aerial and Commons street photographs. Exact current ground coordinates
    # remain provisional until the live survey is available.
    for sx in (-1,1):
        for sy in (-1,1):
            ob=lamp(sx*18,sy*9,LAMPS,kind='cluster')
            ob['placement_status']='Provisional pavement placement; uncertainty approximately 3 m; not surveyed'
    pavement_support=Mesh('Continuous paving beneath clustered lamps — provisional')
    for sx in (-1,1):
        for sy in (-1,1):pavement_support.box((sx*18,sy*9,-.04),(1.1,1.1,.06))
    pavement_support.finish([PAVER],CONTEXT)
    # Low-profile paving strips give useful scale without suggesting a surveyed pattern.
    paving=Mesh('Paving grid — provisional 600 mm modules')
    for side in (-1,1):
        for ix in range(26):
            for iy in range(50):
                x=side*(18+ix*.6);y=(iy-25)*.6
                paving.box((x,y,-.035),(.595,.595,.055),0)
    paving.finish([PAVER,PALE_PAVER],CONTEXT,0)
    # Monument bollards visible in reference; approximate count/layout, no chains yet.
    bollards=Mesh('Island bollards — placement provisional')
    for side in (-1,1):
        for y in range(-11,12,3):
            bollards.rect_profile((side*6.2,y),[(0,.22,.22),(.65,.18,.18),(.78,.17,.17)])
    bollards.finish([BLACK_IRON],CONTEXT,.008)
    # Survey legend is visible only in the overhead inspection render.
    guide=Mesh('North arrow and 10 metre scale')
    base=Vector((-48,22));north=Vector(SITE['north_vector_site_xy']);right=Vector((north.y,-north.x))
    arrow=[base-right*.16,base+right*.16,base+north*5+right*.16,
           base+north*5+right*.75,base+north*7,base+north*5-right*.75,base+north*5-right*.16]
    guide.outline([tuple(p) for p in arrow],.01,.04)
    guide.box((-43,19,.025),(10,.20,.04))
    for xx in (-48,-43,-38):guide.box((xx,19,.025),(.12,.7,.04))
    guide.finish([BLACK_IRON],GUIDES)
    text_object('North label','N',(*tuple(base+north*8),.05),(0,0,1),1.3,1.5,FONT,BLACK_IRON,collection=GUIDES)
    text_object('Scale label','10 m',(-43,17.5,.05),(0,0,1),1,4,FONT,BLACK_IRON,collection=GUIDES)
    GUIDES.hide_render=True
    site_grade.apply_to_site(CONTEXT,LAMPS,GUIDES)

def camera(name,position,target,scale,ortho=True):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);LIGHTS.objects.link(ob)
    ob.location=position;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO' if ortho else 'PERSP';data.ortho_scale=scale;data.lens=52;data.clip_end=1000
    return ob

def setup_render():
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24 if PREVIEW else 72
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.78,.87,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    scene.view_settings.view_transform='AgX'
    data=bpy.data.lights.new('Soft afternoon sun','SUN');ob=bpy.data.objects.new('Soft afternoon sun',data);LIGHTS.objects.link(ob)
    ob.rotation_euler=(math.radians(27),math.radians(-24),math.radians(-34));data.energy=2.4;data.angle=math.radians(12)
    data=bpy.data.lights.new('Large sky fill','AREA');ob=bpy.data.objects.new('Large sky fill',data);LIGHTS.objects.link(ob)
    ob.location=(0,4,45);data.energy=1900;data.shape='DISK';data.size=35

site_context()
build_obelisk()
build_colonnade('NE',NE)
build_colonnade('SW',SW)
setup_render()
ne=SITE['colonnades']['NE']['centre_site_xy_m'];sw=SITE['colonnades']['SW']['centre_site_xy_m']
cameras={
 '01_ensemble_northwest':camera('Ensemble from NW',(-49,69,43),(0,0,4),99),
 '02_ensemble_southeast':camera('Ensemble from SE',(57,-70,40),(0,0,4),99),
 '03_overhead':camera('Site plan',(0,0,130),(0,0,0),108),
 '04_ne_colonnade_inner':camera('NE inner façade',(ne[0]-81,ne[1]+4.5,7.2),(ne[0],ne[1],2.7),29),
 '05_sw_colonnade_inner':camera('SW inner façade',(sw[0]+81,sw[1]-4.5,7.2),(sw[0],sw[1],2.7),29),
 '06_obelisk_salute':camera('Obelisk salute',(5,12,6.3),(0,0,3),7),
 '07_ne_victory_end':camera('NE victory end',(ne[0]-6,ne[1]+23,5.2),(ne[0],ne[1]+10.3,2.8),9.8),
 '08_sw_mourning_end':camera('SW mourning end',(sw[0]+5,sw[1]+23,5.2),(sw[0],sw[1]+10.3,2.8),9.8),
 '09_ne_torches_text':camera('NE end torches and text',(ne[0]+2,ne[1]-24,3.4),(ne[0],ne[1]-12,2.4),4.8),
 '10_sw_remember_text':camera('SW end remember',(sw[0]+2,sw[1]-24,3.4),(sw[0],sw[1]-12,2.4),4.8),
 '11_column_pair':camera('Column pair detail',(ne[0]-10,ne[1]+4.45,2.8),(ne[0]-1.9,ne[1]+4.50,2.4),8.1),
 '12_obelisk_arms':camera('Obelisk coat of arms',(1,-9,3.9),(0,-1.28,3.06),2.4),
 '13_ne_outer':camera('NE outer façade',(ne[0]+84,ne[1],7.2),(ne[0],ne[1],2.7),29),
 '14_sw_outer':camera('SW outer façade',(sw[0]-84,sw[1],7.2),(sw[0],sw[1],2.7),29),
 '15_capital':camera('Doric capital',(ne[0]-6,ne[1]+5.9,4.30),(ne[0]-1.90,ne[1]+4.90,4.0),1.7),
 '16_mourning_close':camera('Mourning close view',(sw[0],sw[1]+18,2.7),(sw[0],sw[1]+12.3,2.3),4.8),
 '17_victory_close':camera('Victory close view',(ne[0],ne[1]+18,2.7),(ne[0],ne[1]+12.3,2.3),4.8)
}
scene.camera=cameras['01_ensemble_northwest']
# Set a useful opening viewport on saved file.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=92
            area.spaces.active.region_3d.view_location=(0,0,3)
            area.spaces.active.clip_end=1000
            area.spaces.active.shading.color_type='MATERIAL'
(ROOT/'research/inscriptions_built.json').write_text(json.dumps(INSCRIPTION_LOG,indent=2)+'\n')
(ROOT/'research/relief_approximation.json').write_text(json.dumps(RELIEF_APPROXIMATION_LOG,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
print('BLEND_SAVED',flush=True)
if not NO_EXPORT:
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:
        if ob.type in ('MESH','FONT') and not any(c==GUIDES for c in ob.users_collection):ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/london-square-exterior.glb'),export_format='GLB',
                             use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
    print('GLB_SAVED',flush=True)
if not NO_RENDER:
    selected=list(cameras) if '--all-views' in ARGS else ['01_ensemble_northwest','04_ne_colonnade_inner','09_ne_torches_text']
    for name in selected:
        scene.camera=cameras[name];scene.render.filepath=str(ROOT/'renders'/name)+'.png'
        if name=='03_overhead':scene.render.resolution_x=1800;scene.render.resolution_y=1000
        else:scene.render.resolution_x=1600;scene.render.resolution_y=1000
        bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
summary={'blender':bpy.app.version_string,'objects':len(scene.objects),
         'mesh_vertices':sum(len(ob.data.vertices) for ob in scene.objects if ob.type=='MESH'),
         'inscription_lines':len(INSCRIPTION_LOG),'column_count':len([o for o in scene.objects if 'fluted Doric column' in o.name]),
         'status':'Exterior research study; see source register and review for dimensional and sculptural uncertainty',
         'interiors':'Deferred by user; chambers contain structural shell only'}
(ROOT/'research/build_report.json').write_text(json.dumps(summary,indent=2)+'\n')
print('BUILD_COMPLETE',json.dumps(summary),flush=True)
