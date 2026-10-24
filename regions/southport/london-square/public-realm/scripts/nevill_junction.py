"""Traced Nevill/Lord Street mouth; Y41 is the sole ground ownership boundary."""
import json, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from southport3d.geometry import Mesh
from southport3d.planar import subtract
from southport3d.road import parallel
from furniture_lod import furniture


def rail_mesh(points, level, name):
    """Open three-rail panels, substantial posts and spherical finials.

    Pickets end at the middle rail, as seen in July 2026 imagery. District
    retains the silhouette and openings with fewer pickets and square profiles.
    """
    m=Mesh(name)
    sides={'detail':8,'walk':6,'district':4}[level]
    pitch={'detail':.14,'walk':.18,'district':.55}[level]
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b)
        for z in [.14,.88,1.13]:
            m.tube([(a[0],a[1],a[2]+z),(b[0],b[1],b[2]+z)],.023,0,sides)
        count=max(1,round(length/pitch))
        for j in range(1,count):
            p=[a[k]+(b[k]-a[k])*j/count for k in range(3)]
            m.tube([(p[0],p[1],p[2]+.165),(p[0],p[1],p[2]+.855)],.010,0,4)
    for x,y,z in points:
        m.lathe((x,y),[(z,.052),(z+1.18,.052),(z+1.21,.035)],sides,0)
        # Lathe avoids the degenerate pole faces of a UV sphere.
        m.lathe((x,y),[(z+1.21,.012),(z+1.225,.04),(z+1.26,.059),(z+1.295,.04),(z+1.31,.012)],sides,0)
    return m


def rail_points(d,key):
    side=-1 if key=='west_kerb' else 1
    cross=d['lord_crossings'][0 if side<0 else 1]
    full=[p for p in d[key] if abs(p[0])<20 and p[1]<44]
    offset=parallel(full,-side*d['rail_setback'])
    points=[]
    for a,b in zip(offset,offset[1:]):
        count=max(1,round(math.dist(a,b)/2))
        points.extend([(a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count) for j in range(count)])
    points.append(offset[-1])
    points.insert(0,(cross['x0']+3.9 if side<0 else cross['x1']-3.9,cross['edge_y']+.45))
    return [(x,y,-.0075-.022*min(36,y)+max(0,y-41)*.014485) for x,y in points]


def build_lod(name,settings,asset_dir):
    from pathlib import Path
    d=json.loads((Path(asset_dir)/'research/nevill-junction.json').read_text())
    return rail_mesh(rail_points(d,settings['key']),settings['level'],name).finish([])


def build_junction(ctx):
    root=ctx['ROOT'];d=json.loads((root/'research/nevill-junction.json').read_text())
    polygon,rect,grade=ctx['polygon'],ctx['rect'],ctx['grade']
    mixed,asphalt,kerb=ctx['mixed'],ctx['asphalt'],ctx['kerb']
    brick=ctx['mat']('Junction red paving border',(.33,.19,.14),'junction-brick')
    pad=ctx['mat']('Junction buff tactile',(.48,.45,.35),'junction-tactile')
    C=ctx['collections'];fm=ctx['fm']
    # Relief is authored procedurally, not copied from reference imagery.
    import bpy
    tex=pad.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(root/'textures/junction-tactile-normal.png'))
    tex.image.colorspace_settings.name='Non-Color'
    normal=pad.node_tree.nodes.new('ShaderNodeNormalMap')
    pad.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color'])
    pad.node_tree.links.new(normal.outputs['Normal'],pad.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
    pavement=[]
    # Curves run from Lord Street towards Nevill. Their Y41 points are shared
    # verbatim with Nevill's stations; there is no overlapping road neck.
    for side,key in [(-1,'west_kerb'),(1,'east_kerb')]:
        curve=[tuple(p) for p in d[key] if p[1]<=41]
        foot=curve+[(side*41,41)]
        pavement.append(foot)
        polygon('Surface junction footway',foot,mixed,'perimeter',0)
        inside=-side
        # Offset the full trace before clipping: ending an offset at Y41
        # shortens paint at the seam and leaves a triangular kerb-cap gap.
        full_curve=[tuple(p) for p in d[key]]
        inner=parallel(full_curve,inside*.30)
        outer=parallel(full_curve,inside*.58)
        for i in range(len(full_curve)-1):
            polygon('Surface junction red border',[inner[i],inner[i+1],outer[i+1],outer[i]],brick,'perimeter',.003)
        # Leave Lord Street crossing landings free of a vertical kerb.
        cross=d['lord_crossings'][0 if side<0 else 1]
        lo,hi=cross['x0'],cross['x1']
        for a,b in zip(full_curve,full_curve[1:]):
            ts=[0,1]
            if abs(b[0]-a[0])>1e-8:
                ts += [(x-a[0])/(b[0]-a[0]) for x in [lo,hi] if 0<(x-a[0])/(b[0]-a[0])<1]
            ts=sorted(ts)
            for t,u in zip(ts,ts[1:]):
                aa=tuple(a[k]+(b[k]-a[k])*t for k in [0,1]);bb=tuple(a[k]+(b[k]-a[k])*u for k in [0,1])
                if not lo<(aa[0]+bb[0])/2<hi:ctx['open_kerb']([aa,bb],inside,'perimeter')
        ctx['paint_edge']('Nevill corner '+key,full_curve,-inside,'roads',(-41,31,41,41))
        # Researched rail run stops before both crossing openings. Split long
        # runs into roughly 2m panels while retaining the traced bend vertices.
        xyz=rail_points(d,key)
        name='Junction railing '+key
        ob=rail_mesh(xyz,'detail',name).finish(fm,C['sw-furniture' if side<0 else 'ne-furniture'])
        ob['junction_rail_points']=json.dumps(xyz)
        # Adjacent signals face across Nevill. A bent mounting is represented
        # using the local variant of the existing signal family.
        for kind,x,y,yaw in [('offset-pedestrian',side*5.65,44.55,90 if side<0 else -90),
                              ('pedestrian',(lo+hi)/2+side*1.9,cross['edge_y']+.7,0)]:
            ob=furniture(kind,'detail','Furniture '+kind+' extension junction '+key).finish(fm,C['sw-furniture' if side<0 else 'ne-furniture'])
            ob.location=(x,y,grade(min(y,41))+max(0,y-41)*.014485);ob.rotation_euler.z=math.radians(yaw)
        y=cross['edge_y']
        ob=rect('Tactile junction '+key,lo,y-.025,hi,y+1.25,pad,'perimeter',.012)
        ob['junction_landing']=[lo,hi,y]
        # Corresponding dropped landing at the memorial-side forecourt.
        part='sw-ground' if side<0 else 'ne-ground'
        rect('Tactile junction south '+key,lo,19.75,hi,21,pad,part,.012)
        # Worn crossing studs, no invented zebra stripes. Two separate arms
        # connect the memorial forecourt and north pavement; exact current
        # paint wear cannot be reconstructed.
        for x in [lo,hi]:
            for j in range(12):
                yy=21.3+(y-21.6)*j/11
                rect('Marking junction crossing stud',x-.045,yy-.045,x+.045,yy+.045,ctx['white'],'roads',-.110)
    # Observed elongated central refuge east of the junction: raised tips
    # flank a flush crossing channel. Endpoints are traced, width estimated.
    refuge_y=26.25
    for left,right,round_left in [(15.35,23.1,True),(25.9,29.0,False)]:
        radius=.62
        if round_left:
            poly=[(right,refuge_y-radius),(right,refuge_y+radius),(left+radius,refuge_y+radius)]
            poly += [(left+radius+radius*math.cos(math.pi/2+j*math.pi/10),refuge_y+radius*math.sin(math.pi/2+j*math.pi/10)) for j in range(1,11)]
        else:
            poly=[(left,refuge_y-radius),(right-radius,refuge_y-radius)]
            poly += [(right-radius+radius*math.cos(-math.pi/2+j*math.pi/10),refuge_y+radius*math.sin(-math.pi/2+j*math.pi/10)) for j in range(1,11)]
            poly.append((left,refuge_y+radius))
        polygon('Surface junction refuge',poly,mixed,'roads',0)
        ctx['open_kerb'](poly+[poly[0]],1,'roads')
    rect('Tactile junction refuge',23.1,refuge_y-.62,25.9,refuge_y+.62,pad,'roads',-.105)
    for i,(kind,x,y,yaw) in enumerate([('signal',16.1,refuge_y,90),('pedestrian',22.65,refuge_y,180),('pedestrian',26.35,refuge_y,0)]):
        ob=furniture(kind,'detail','Furniture '+kind+' extension junction refuge '+str(i)).finish(fm,C['ne-furniture'])
        ob.location=(x,y,grade(y));ob.rotation_euler.z=math.radians(yaw)
    # The characteristic Lord Street lamp family, behind each railing run.
    for side,x,y in [(-1,-17.8,39.1),(1,17.1,36.8)]:
        ob=furniture('lord-street-lamp','detail','Furniture lord-street-lamp extension junction '+str(side)).finish(fm,C['sw-furniture' if side<0 else 'ne-furniture'])
        ob.location=(x,y,grade(y))
    # Explicitly subtract both footways from the new asphalt. This avoids a
    # second hidden floor at the new corner bulges and their shared tile edge.
    cutters=[]
    for poly in pavement:
        verts=[Vector((x,y,0)) for x,y in poly]
        for tri in tessellate_polygon([verts]):
            cutters.append([(verts[v].x,verts[v].y) if isinstance(v,int) else (v.x,v.y) for v in tri])
    pieces=[[(-41,31),(41,31),(41,41),(-41,41)]]
    for cutter in cutters:pieces=[p for old in pieces for p in subtract(old,cutter)]
    for piece in pieces:polygon('Surface junction asphalt',piece,asphalt,'roads',-.12)

    # Offset caps/bands would otherwise project a few centimetres over Y41.
    # Clip their 3D faces, preserving interpolated kerb heights and UV rebuild.
    for ob in list(C['perimeter'].objects):
        if not ob.name.startswith(('Surface junction','Tactile junction','Kerb aligned')):continue
        if max(v.co.y for v in ob.data.vertices)<=41:continue
        result=Mesh(ob.name)
        for face in ob.data.polygons:
            points=[tuple(ob.data.vertices[i].co) for i in face.vertices]
            clipped=[]
            for prev,cur in zip(points[-1:]+points[:-1],points):
                pin,cin=prev[1]<=41,cur[1]<=41
                if pin!=cin:
                    t=(41-prev[1])/(cur[1]-prev[1])
                    clipped.append(tuple(prev[k]+t*(cur[k]-prev[k]) for k in range(3)))
                if cin:clipped.append(cur)
            clipped=[p for i,p in enumerate(clipped) if math.dist(p,clipped[i-1])>1e-8]
            normal=Vector((0,0,0))
            for j in range(1,len(clipped)-1):normal+=(Vector(clipped[j])-Vector(clipped[0])).cross(Vector(clipped[j+1])-Vector(clipped[0]))
            if normal.length>1e-9:result.add(clipped,[tuple(range(len(clipped)))])
        if not result.faces:
            bpy.data.objects.remove(ob,do_unlink=True)
            continue
        ob.data.clear_geometry();ob.data.from_pydata(result.vertices,[],result.faces);ob.data.update()


def drop_landings(ctx):
    """Apply drops after priority clipping, including bordering material pieces."""
    d=json.loads((ctx['ROOT']/'research/nevill-junction.json').read_text())
    for ob in ctx['collections']['perimeter'].objects:
        if ob.type!='MESH':continue
        for v in ob.data.vertices:
            x,y=v.co.x,v.co.y
            if y<31:continue
            if ob.name.startswith(('Surface junction','Tactile junction')):
                v.co.z=ctx['grade'](y)
            for c in d['lord_crossings']:
                if c['x0']-.001<=x<=c['x1']+.001 and c['edge_y']-.04<=y<=c['edge_y']+1.251:
                    v.co.z=ctx['grade'](y)-.12*max(0,min(1,1-(y-c['edge_y'])/1.25))

    for part in ['ne-ground','sw-ground','roads']:
        for ob in ctx['collections'][part].objects:
            if ob.name.startswith('Tactile junction south'):
                for v in ob.data.vertices:v.co.z=ctx['grade'](v.co.y)-.12*max(0,min(1,(v.co.y-19.75)/1.25))
            elif ob.name.startswith('Tactile junction refuge'):
                for v in ob.data.vertices:v.co.z=ctx['grade'](v.co.y)-.12
