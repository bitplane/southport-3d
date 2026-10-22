"""Post Office Avenue / Anchor Street continuation, registered to retained OSM."""
from southport3d.planar import subtract
from southport3d.road import parallel

PARTS={'rear-streets-ground':'Post Office Avenue and Anchor Street surfaces'}

def build_rear_streets(ctx):
    polygon=ctx['polygon'];part='rear-streets-ground'
    # Ownership starts at the existing Anchor stub X25 and front strip Y-27.
    # Anchor widens to the nine-metre stub, then follows mapped centreline bends.
    anchor=[(25,-83.5),(26,-83.5),(49.817,-85.631),(67.658,-87.563),(150.579,-95.244),(160,-97.0)]
    avenue=[(68.154,-27),(68.0803,-36),(67.658,-87.563)]
    an=parallel(anchor,4);aso=parallel(anchor,-4)
    an[0]=(25,-79);aso[0]=(25,-88)
    an[1]=(26,-79);aso[1]=(26,-88)
    aw=parallel(avenue,-2);ae=parallel(avenue,2)
    roads=[an+list(reversed(aso)),aw+list(reversed(ae))]
    for name,pts in zip(['Anchor Street','Post Office Avenue'],roads):
        polygon('Surface '+name,pts,ctx['asphalt'],part,-.12)
    # Footways are genuinely cut out at the T-junction, not layered over roads.
    for name,edge,outer in [
        ('Anchor north',an,parallel(anchor,6.5)),('Anchor south',aso,parallel(anchor,-6.5)),
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
        ctx['open_kerb'](curve,side,part)
        ctx['paint_edge'](name,curve,-side,part)
