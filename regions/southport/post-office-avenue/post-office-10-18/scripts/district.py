"""Bounded facade atlas and the same three cross-gable roof silhouette."""
import json,math,os,sys
from pathlib import Path
from blender_envelope import Surfaces
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from components import roof_shapes,profile,clip_values
from southport3d.planar import subtract,area


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    angle=math.radians(d['local_rotation_degrees']);co=math.cos(angle);si=math.sin(angle)
    ox,oy=d['origin_site_xy'];base=d['base_z'];w=d['width'];dep=max(d['depth_start'],d['depth_end'])
    def world(p):x,y,z=p;return (ox+co*x-si*y,oy+si*x+co*y,base+z)
    s=Surfaces(['street-facade','roof','rear-and-ends'],world)
    plan=[(co*(x-ox)+si*(y-oy),-si*(x-ox)+co*(y-oy)) for x,y in d['footprint_site_xy']]
    boundary=[plan[1],plan[2],plan[3],plan[0]]
    shapes=roof_shapes(w,dep,d['eaves'],d['ridge'])
    for index,a in enumerate(boundary):
        b=boundary[(index+1)%4];s.part='street-facade' if index==0 else 'rear-and-ends'
        outline=profile(shapes,a,b)
        for j,((t,z),(u,Z)) in enumerate(zip(outline,outline[1:])):
            x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            X=a[0]+(b[0]-a[0])*u;Y=a[1]+(b[1]-a[1])*u
            s.quad(f'wall {index} {j}',[(x,y,-.06),(X,Y,-.06),(X,Y,Z),(x,y,z)],weight=1.5 if index==0 else 1)
    s.part='roof'
    # The maximum of four analytic height fields supplies actual valleys,
    # independent of window, sign and timber mesh complexity.
    for index,(domain,planes) in enumerate(shapes):
        for k,(a,b,c) in enumerate(planes):
            region=domain
            for p,q,r in planes:
                if region:region=clip_values(region,lambda v:p*v[0]+q*v[1]+r-(a*v[0]+b*v[1]+c))
            regions=[region] if len(region)>2 else []
            for other,(od,op) in enumerate(shapes):
                if other==index:continue
                cover=od
                for p,q,r in op:
                    if cover:cover=clip_values(cover,lambda v:p*v[0]+q*v[1]+r-(a*v[0]+b*v[1]+c)-1e-10)
                if len(cover)>2:regions=[piece for poly in regions for piece in subtract(poly,cover)]
            for j,poly in enumerate(regions):
                # Remove duplicate/collinear clipping points before atlas islands.
                clean=[]
                for point in poly:
                    if not clean or math.dist(point,clean[-1])>1e-6:clean.append(point)
                if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-6:clean.pop()
                for v in range(1,len(clean)-1):
                    tri=[clean[0],clean[v],clean[v+1]]
                    if area(tri)<1e-6:continue
                    s.triangle(f'roof {index} {k} {j} {v}',[(x,y,a*x+b*y+c) for x,y in tri])
    for i,u in enumerate((w/5*.8,w/5*2.35,w/5*3.8)):
        v=dep*.52;r=d['ridge']
        s.box(f'chimney {i}',(u-.29,v-.44,r-.2),(u+.29,v+.44,r+1.2))
        for j,y in enumerate((v-.23,v+.23)):
            s.box(f'pot {i} {j}',(u-.10,y-.10,r+1.29),(u+.10,y+.10,r+1.77),cage=.08)
    return s.result
