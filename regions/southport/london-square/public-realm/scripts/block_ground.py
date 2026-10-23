"""Mapped St George's block ground; architectural placeholders remain explicit."""
import json
import math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from southport3d.geometry import Mesh
from southport3d.planar import subtract, halfplane
from southport3d.road import parallel


def build_block(ctx, existing_roads, anchor_north, anchor_south):
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
    polygon('Surface Lord Street Hill junction',[(218,21),(236,21),(236,31),(218,31)],ctx['asphalt'],street,-.12)
    polygon('Surface Lord north continuation',[(218,31),(236,31),(236,41),(218,41)],ctx['mixed'],street)
    clipped('Surface Lord south continuation',[(218,19),(236,19),(236,21),(218,21)],ctx['mixed'],roads,dest=street)
    for x in range(216,236,6):
        if min(x+2,236)>max(x,218):line('Marking Lord continuation',[(max(x,218),25.6),(min(x+2,236),25.6)],.1,ctx['white'],street,-.109)
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
    outer_anchor=parallel(anchor_north,2.5)
    street_reserve=outer_anchor+[(234,-120),(25,-120)]
    entrance=[(147.5,-86),(154.5,-86),(154.5,-96),(147.5,-96)]
    reserve=[street_reserve,entrance,hillpoly,castlepoly,exit_apron]
    buildings=[ways[k]['xy'][:-1] for k in ('371203338','371742617','51826176','371742618','371742619','371742620')]
    hall=[(159.55,-53.1),(178.2,-53.1),(178.2,-68.6),(159.55,-68.6)]
    # Keep a continuous floor in the narrow access court behind NatWest and
    # the London Street plots. Stop exactly at Post Office Avenue's outer footway.
    avenue_outer=parallel([(68.154,-27),(68.0803,-36),(67.658,-87.563)],-3.8)
    west_court=[(25,-27)]+avenue_outer+[(25,-87)]
    clipped('Surface Posting House side court',west_court,ctx['mixed'],reserve)
    clipped('Surface rear courts',ground,ctx['mixed'],[parking]+reserve)
    clipped('Surface Sainsburys parking',parking,ctx['asphalt'],reserve,z=-.12)
    # Open access apron joins parking to Anchor; no kerb or paint across its mouth.
    clipped('Surface car park Anchor access',entrance,ctx['asphalt'],z=-.12,dest=street)
    # Current photo shows a landscaped margin at the modern Posting House front.
    apron=[(36.5,-76.5),(65.5,-77),(65.65,-81),(49.8,-79.1),(36.5,-78)]
    clipped('Surface Posting House rear apron',apron,ctx['mixed'],reserve)
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
                if len(piece)>2:clipped('Marking parking bay',piece,white,[hall]+buildings+reserve,z=-.109)
    # Low-detail rear building volumes occupy mapped footprints, not guessed boxes.
    material=ctx['mat']('Provisional rear building volume',(.39,.37,.33))
    for key,height in [('371742618',7.5),('371742619',11),('371742620',8.5),('51826175',6.5)]:
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
