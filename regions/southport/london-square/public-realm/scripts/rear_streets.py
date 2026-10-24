"""Post Office Avenue / Anchor Street continuation, registered to retained OSM."""
from southport3d.planar import subtract
from southport3d.road import parallel

PARTS={'rear-streets-ground':'Post Office Avenue and Anchor Street surfaces', 'block-ground':'St Georges block courts and parking', 'block-furniture':'St Georges block furniture and mapped placeholders'}

def build_rear_streets(ctx):
    polygon=ctx['polygon'];part='rear-streets-ground'
    # Ownership starts at the existing Anchor stub X25 and front strip Y-27.
    # Anchor widens to the nine-metre stub, then follows mapped centreline bends.
    anchor=[(25,-83.5),(26,-83.5),(49.817,-85.631),(67.658,-87.563),(83,-88.984),(104,-90.929),(116,-92.041),(150.579,-95.244),(159.105,-96.894),(223.91,-95.688),(234,-95.5)]
    avenue=[(68.154,-27),(68.0803,-36),(67.658,-87.563)]
    an=parallel(anchor,4);aso=parallel(anchor,-4)
    # Calibrated Anchor shopfront section: the mapped road line lies only
    # about 3.4m from the shop bays. A symmetric 8m ribbon cut into 15–21.
    # Keep south ownership fixed; trace the north kerb about 1.3m off the bays.
    for i,width in ((4,2.9),(5,1.75),(6,3.0)):
        an[i]=parallel(anchor,width)[i]
    an[0]=(25,-79);aso[0]=(25,-88)
    an[1]=(26,-79);aso[1]=(26,-88)
    aw=parallel(avenue,-2);ae=parallel(avenue,2)
    roads=[an+list(reversed(aso)),aw+list(reversed(ae))]
    for name,pts in zip(['Anchor Street','Post Office Avenue'],roads):
        polygon('Surface '+name,pts,ctx['asphalt'],part,-.12)
    # Include the adjoining junctions and car-park mouth when cutting Anchor's
    # footways, otherwise a higher pavement slab would bridge the new road.
    hill=[(219.58,21),(219.961,-6.062),(222.111,-21.523),(224.285,-59.271),(223.91,-95.688),(224.15,-104)]
    roads.append(parallel(hill,-3.5)+list(reversed(parallel(hill,3.5))))
    roads.append([(147.5,-86),(154.5,-86),(154.5,-96),(147.5,-96)])
    roads.append([(106,-70),(121,-70),(121,-96),(106,-96)])
    anchor_outer=parallel(anchor,6.5)
    for i,width in ((4,4.2),(5,3.05),(6,4.6)):
        anchor_outer[i]=parallel(anchor,width)[i]
    anchor_outer[0]=(25,-76)
    # Footways are genuinely cut out at the T-junction, not layered over roads.
    for name,edge,outer in [
        ('Anchor north',an,anchor_outer),('Anchor south',aso,parallel(anchor,-6.5)),
        ('Avenue west',aw,parallel(avenue,-3.8)),('Avenue east',ae,parallel(avenue,3.1))]:
        if name.startswith('Anchor'):
            outer[0]=(25,-76 if name.endswith('north') else -91)
        pieces=[[edge[i],edge[i+1],outer[i+1],outer[i]] for i in range(len(edge)-1)]
        for road in roads:
            # Road ribbons have bends; use per-segment convex cutters.
            n=len(road)//2
            for i in range(n-1):
                cutter=[road[i],road[i+1],road[-i-2],road[-i-1]]
                area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(cutter,cutter[1:]+cutter[:1]))
                if area<0:cutter.reverse()
                pieces=[q for p in pieces for q in subtract(p,cutter)]
        for p in pieces:
            if len(p)>2:polygon('Surface '+name+' footway',p,ctx['mixed'],part)
    # Split kerbs and paint at the junction: no transverse edge across either road.
    curves=[('Anchor north into Avenue west',an[:3]+[(65.69,-83.3),aw[1],aw[0]],1),
            ('Avenue east into Anchor north',[ae[0],ae[1],(69.69,-83.7)]+an[4:],1),
            ('Anchor south',aso,-1)]
    for name,curve,side in curves:
        # This pass ends the Anchor kerb at the Hill Street junction mouth.
        from southport3d.planar import halfplane
        for a,b in zip(curve,curve[1:]):
            cuts=[(a,b)]
            # Open vehicular access to Sainsbury's from Anchor, and Hill junction.
            for lo,hi in ([(106,121),(147.5,154.5),(219.8,228)] if name!='Anchor south' else [(219.8,228)]):
                trimmed=[]
                for p,q in cuts:
                    if abs(q[0]-p[0])<1e-9:
                        if not lo<p[0]<hi:trimmed.append((p,q))
                        continue
                    ts=sorted(set([0.,1.]+[max(0,min(1,(x-p[0])/(q[0]-p[0]))) for x in (lo,hi)]))
                    for ta,tb in zip(ts,ts[1:]):
                        mid=p[0]+(q[0]-p[0])*(ta+tb)/2
                        if lo<mid<hi:continue
                        trimmed.append((tuple(p[i]+(q[i]-p[i])*ta for i in range(2)),tuple(p[i]+(q[i]-p[i])*tb for i in range(2))))
                cuts=trimmed
            for segment in cuts:
                ctx['open_kerb'](list(segment),side,part)
                ctx['paint_edge'](name,list(segment),-side,part)
    from block_ground import build_block
    build_block(ctx,roads,anchor_outer)
