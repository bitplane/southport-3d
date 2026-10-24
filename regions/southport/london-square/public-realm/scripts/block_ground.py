"""Mapped St George's block ground; architectural placeholders remain explicit."""
import json
import math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from southport3d.geometry import Mesh
from southport3d.planar import subtract, halfplane
from southport3d.road import parallel


def build_block(ctx, existing_roads, anchor_outer):
    data=json.loads((ctx['ROOT']/'research/st-georges-block.json').read_text())
    ways=data['ways']; part='block-ground'; street='rear-streets-ground'
    polygon=ctx['polygon'];line=ctx['line'];grade=ctx['grade']
    def tris(poly):
        return [[(v.x,v.y) if not isinstance(v,int) else poly[v] for v in tri] for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])]
    def clipped(name,poly,material,cuts=(),z=0,dest=part):
        pieces=tris(poly)
        for cut in cuts:
            for cutter in tris(cut):
                if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(cutter,cutter[1:]+cutter[:1]))<0:cutter.reverse()
                pieces=[q for p in pieces for q in subtract(p,cutter)]
        for p in pieces:
            if len(p)>2:polygon(name,p,material,dest,z)
    hill=[(219.58,21),(219.961,-6.062),(222.111,-21.523),(224.285,-59.271),(223.91,-95.688),(224.15,-104)]
    left=parallel(hill,-3.5);right=parallel(hill,3.5)
    # Shared ownership with church gardens is X218, including the road surface.
    def east(poly):return halfplane(poly,(218,100),(218,-200),True)
    hillpoly=left+list(reversed(right));castle=[(224.285,-59.271),(236,-59.517)]
    castlepoly=parallel(castle,3.5)+list(reversed(parallel(castle,-3.5)))
    exit_apron=[(214.5,-63),(225,-62.5),(225,-56.5),(214.5,-57)]
    roads=existing_roads+[hillpoly,castlepoly,exit_apron]
    for name,poly in [('Hill Street',hillpoly),('Castle Street mouth',castlepoly),('Sainsburys Hill exit',exit_apron)]:
        clipped('Surface '+name,poly if name=='Sainsburys Hill exit' else east(poly),ctx['asphalt'],z=-.12,dest=street)
    # Lord Street east of X218 belongs to corridor-public-realm.
    # Footways are cut by every road and junction mouth, including existing Anchor.
    for edge,outer in [(left,parallel(hill,-5.5)),(right,parallel(hill,5.5))]:
        for i in range(len(edge)-1):
            poly=east([edge[i],edge[i+1],outer[i+1],outer[i]])
            if len(poly)>2:clipped('Surface Hill footway',poly,ctx['mixed'],roads,dest=street)
    # Kerbs stop at the Castle/Anchor junctions and mapped parking entrance.
    for edge,side in [(left,-1),(right,1)]:
        for a,b in zip(edge,edge[1:]):
            for lo,hi in [(-52,-31),(-86,-66),(-104,-101)]:
                if abs(b[1]-a[1])<1e-9:continue
                ts=sorted([max(0,min(1,(y-a[1])/(b[1]-a[1]))) for y in (lo,hi)])
                if ts[1]-ts[0]<1e-6:continue
                seg=[tuple(a[i]+(b[i]-a[i])*t for i in range(2)) for t in ts]
                if min(p[0] for p in seg)<218:continue
                ctx['open_kerb'](seg,side,street)
    parking=ways['42018443']['xy'][:-1]
    # Rear service courts terminate at the outer pavement, not at a guessed rectangle.
    ground=[(70.9,-27),(154,-27),(154,-23.6),(218,-23.6),(218,-100),(70.9,-100)]
    # The street asset owns the complete footway ribbon. Clip the block at its
    # outer edge, including the separate car-park entrance apron.
    # Consume the exact street-footway boundary, including widened stub ends.
    outer_anchor=anchor_outer
    street_reserve=outer_anchor+[(234,-120),(25,-120)]
    entrance=[(147.5,-86),(154.5,-86),(154.5,-96),(147.5,-96)]
    ramp=json.loads((ctx['ROOT']/'research/garage-ramp.json').read_text())['xy']
    reserve=[street_reserve,entrance,hillpoly,castlepoly,exit_apron,ramp]
    buildings=[ways[k]['xy'][:-1] for k in ('371203338','371742617','51826176','371742618','371742619','371742620')]
    # The OSM church outline includes its rear hall. Do not append a second
    # hall footprint into the parking/service aisle behind it.
    # Keep a continuous floor in the narrow access court behind NatWest and
    # the London Street plots. Stop exactly at Post Office Avenue's outer footway.
    avenue_outer=parallel([(68.154,-27),(68.0803,-36),(67.658,-87.563)],-3.8)
    west_court=[(25,-27)]+avenue_outer+[(25,-87)]
    # Anchor Street's gated lane is asphalt, not the decorative paving used
    # outside the shops. Its footprint is owned once, with a flush entrance.
    lane=[(27.3,-78.4),(36.7,-78.4),(36.7,-74),(34.6,-51),(33.2,-28),(27.3,-28)]
    clipped('Surface Posting House side court',west_court,ctx['mixed'],reserve+[lane])
    # Split at the grade clamp so triangulation cannot slope the level lane.
    for upper in [True,False]:
        piece=halfplane(lane,(0,-36),(100,-36),upper)
        clipped('Surface Posting House service lane',piece,ctx['asphalt'],reserve,z=-.12)
    # Two vehicle leaves and a narrow side gate are observed in August 2024.
    # Positions fit the mapped plot ends; widths are photographic estimates.
    iron=ctx['mat']('Posting lane painted gate',(.025,.028,.025))
    gatebrick=ctx['mat']('Posting lane brick piers',(.34,.14,.075))
    m=Mesh('Street Posting lane gate')
    for a,b in [(27.1,29.0),(29.3,32.7),(32.74,36.15)]:
        start_vertex=len(m.vertices)
        m.box(((a+b)/2,-78.25,1.08),(b-a,.08,1.98))
        for z in [.15,1.98]:m.box(((a+b)/2,-78.30,z),(b-a,.07,.07))
        for x in [a,b]:m.box((x,-78.30,1.08),(.07,.07,2.12))
        for j in range(1,max(2,int((b-a)/.3))):
            x=a+(b-a)*j/max(2,int((b-a)/.3));m.box((x,-78.31,1.08),(.028,.04,1.9))
        if a==27.1:
            # August 2024 shows the small gate attached directly to Myers'
            # rear brick wall, behind the vehicle-gate plane, with no outer pier.
            for i in range(start_vertex,len(m.vertices)):
                x,y,z=m.vertices[i]
                m.vertices[i]=(x,y+.65*(29.0-x)/1.9,z)
    ctx['finish'](m,iron,'block-furniture')
    m=Mesh('Wall Posting lane gate piers')
    for x in [29.15,36.4]:m.box((x,-78.23,1.15),(.30,.42,2.3))
    ctx['finish'](m,gatebrick,'block-furniture')
    # A short return joins the gate pier to the raised courtyard boundary.
    from southport3d.landscape import capped_wall
    # Meet the mapped rear facade with a mitred end, not a square end which
    # leaves a triangular daylight slot beside the oblique building wall.
    m=capped_wall([(36.4,-78.23,grade(-78.23)),(38.7,-76.5,grade(-76.5))],height=2.25,width=.28,name='Wall Posting lane gate return')
    wall_a=(36.69,-76.447);wall_b=(65.499,-76.96)
    slope=(wall_b[1]-wall_a[1])/(wall_b[0]-wall_a[0])
    # Reach past the modern range end at X38.40 in its coarse envelope.
    # The connection enters the closed building volume, rather than exposing
    # a slot when its shallow end-wall detail is baked away.
    # End-ring vertices in capped_wall are 1,2,5,6 in each eight-vertex band.
    for index in (1,2,5,6,9,10,13,14):
        x,y,z=m.vertices[index]
        m.vertices[index]=(x,wall_a[1]+slope*(x-wall_a[0]),z)
    m.finish([gatebrick,ctx['kerb']],ctx['collections']['block-furniture'])
    service_apron=[(106,-93),(121,-94),(122.452,-77.937),(122.229,-72.213),(110.248,-70.397),(105.364,-75.158)]
    cinema_path=[(70.9,-54.20),(89.16,-54.20),(89.16,-56.70),(79.4,-56.70),(79.4,-56.48),(70.9,-56.48)]
    clipped('Surface rear courts',ground,ctx['mixed'],[parking,cinema_path,service_apron]+reserve+buildings)
    clipped('Surface Anchor loading apron',service_apron,ctx['asphalt'],existing_roads[:2]+[parking]+buildings,z=-.12)
    clipped('Surface Bijou entrance passage',cinema_path,ctx['pale'],reserve+buildings)
    # South low boundary is visible along the approach; northern boundary is
    # the windowed access range owned by the cinema asset.
    m=capped_wall([(79.5,-56.6,grade(-56.6)),(88.9,-56.6,grade(-56.6))],height=1.65,width=.24,name='Wall Bijou passage south')
    passage_brick=ctx['mat']('Bijou passage brick courses',(.42,.23,.14),'junction-brick')
    ob=m.finish([passage_brick,ctx['kerb']],ctx['collections']['block-furniture'])
    uv=ob.data.uv_layers.new(name='Metric wall brick')
    for face in ob.data.polygons:
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv=(v.x/4.05,v.z/2.70)
    # Closed iron entrance leaves and spear finials are visible in August 2024.
    m=Mesh('Street Bijou entrance gate');gx=71.12;gy0=-56.43;gy1=-54.0;base=grade(-55)
    for z in (.35,1.25):m.box((gx,(gy0+gy1)/2,base+z),(.065,gy1-gy0,.055))
    for y in (gy0,(gy0+gy1)/2,gy1):m.box((gx,y,base+.77),(.075,.075,1.54))
    for i in range(13):
        y=gy0+.08+i*(gy1-gy0-.16)/12;m.box((gx,y,base+.76),(.025,.025,1.45))
        m.add([(gx-.05,y-.05,base+1.49),(gx+.05,y-.05,base+1.49),(gx+.05,y+.05,base+1.49),(gx-.05,y+.05,base+1.49),(gx,y,base+1.70)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)])
    m.finish([iron],ctx['collections']['block-furniture'])
    clipped('Surface Sainsburys parking',parking,ctx['asphalt'],reserve,z=-.12)
    # Open access apron joins parking to Anchor; no kerb or paint across its mouth.
    clipped('Surface car park Anchor access',entrance,ctx['asphalt'],z=-.12,dest=street)
    # The side court already owns the paved apron up to the exact footway edge.
    # Do not overlay a second coplanar apron on that surface.
    # Parking rows follow the aerial arrangement; stall count and sizes estimated.
    white=ctx['white']
    rows=[(131,-87,7,0),(161,-88,20,0),(190,-30,10,-90),(209,-30,10,-90)]
    for x,y,count,yaw in rows:
        a=math.radians(yaw);u=(math.cos(a),math.sin(a));v=(-u[1],u[0])
        for i in range(count+1):
            p=(x+i*2.5*u[0],y+i*2.5*u[1]);q=(p[0]+4.7*v[0],p[1]+4.7*v[1])
            # Clip stripes against parking boundary via triangle intersection.
            dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy);nx=-dy/length*.045;ny=dx/length*.045
            stripe=[(p[0]-nx,p[1]-ny),(q[0]-nx,q[1]-ny),(q[0]+nx,q[1]+ny),(p[0]+nx,p[1]+ny)]
            for triangle in tris(parking):
                if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(triangle,triangle[1:]+triangle[:1]))<0:triangle.reverse()
                piece=stripe
                for a,b in zip(triangle,triangle[1:]+triangle[:1]):piece=halfplane(piece,a,b,True)
                if len(piece)>2:clipped('Marking parking bay',piece,white,buildings+reserve,z=-.109)
    # Low-detail rear building volumes occupy mapped footprints, not guessed boxes.
    material=ctx['mat']('Provisional rear building volume',(.39,.37,.33))
    for key,height in [('51826175',6.5)]:
        points=ways[key]['xy'][:-1]
        if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))<0:points.reverse()
        m=Mesh('Placeholder OSM '+key+' estimated height')
        base=grade(-60)-.03;n=len(points)
        m.add([(x,y,z) for z in (base,base+height) for x,y in points],
              [tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
        ob=m.finish([material],ctx['collections']['block-furniture'])
        ob['status']='Mapped footprint placeholder; estimated height; replace on this footprint when researched'
    # Reuse existing furniture families; placements are photographic estimates.
    from furniture_lod import furniture
    for i,(kind,x,y,yaw) in enumerate([('bollard',180,-28,0),('bollard',183,-28,0),('bollard',186,-28,0),('bin',181,-31,0),('bench',183,-24,180)]):
        ob=furniture(kind,'detail','Block '+kind+' '+str(i)).finish(ctx['fm'],ctx['collections']['block-furniture'])
        ob.location=(x,y,grade(y));ob.rotation_euler.z=math.radians(yaw)

    # Low brick boundary behind the church-side building, with pedestrian gaps.
    from southport3d.landscape import capped_wall
    wallmat=ctx['mat']('Block red boundary brick',(.33,.15,.10))
    for i,points in enumerate([[(180,-26),(187,-26)],[(204,-26),(216,-26)]]):
        m=capped_wall([(x,y,grade(y)) for x,y in points],height=.55,width=.28,name='Wall block parking boundary '+str(i))
        m.finish([wallmat,ctx['kerb']],ctx['collections']['block-furniture'])
