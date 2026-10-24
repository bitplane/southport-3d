"""Fixed envelope retaining nave/hall roofs, recessed belfry and octagonal spire."""
import json
import math
from blender_envelope import Surfaces
from southport3d.planar import subtract


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    registration_angle=math.atan2(.503,18.252);ox,oy=d['registration_source_xy'];tx,ty=d['registration_target_xy']
    def world(p):
        x,y,z=p;x-=ox;y-=oy
        return tx+math.cos(registration_angle)*x-math.sin(registration_angle)*y,ty+math.sin(registration_angle)*x+math.cos(registration_angle)*y,d['base_z']+z
    s=Surfaces(['nave','tower','spire'],world)
    cx=d['centre_x'];half=d['nave_width']/2;xl,xr=cx-half,cx+half
    front,rear=d['nave_front_y'],d['rear_y'];e,r=d['eaves'],d['ridge']
    tw,tf,tb=d['tower_width'],d['tower_front_y'],d['tower_back_y'];cy=(tf+tb)/2
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('west nave',(xl,front),(xl,rear),0,e);wall('east nave',(xr,rear),(xr,front),0,e)
    wall('rear nave',(xl,rear),(xr,rear),0,e)
    s.triangle('rear nave gable',[(xl,rear,e),(xr,rear,e),(cx,rear,r)])
    for name,left,right in [('west',xl,cx-tw/2),('east',cx+tw/2,xr)]:
        h=lambda x:e+(r-e)*(1-abs(x-cx)/half)
        s.quad('front nave '+name,[(right,front,0),(left,front,0),(left,front,h(left)),(right,front,h(right))])
    # Notch the front roof exactly at the tower so it never cuts the belfry.
    for sign in (-1,1):
        edge=cx+sign*(half+.15);inside=cx+sign*tw/2
        h=e+.12+(r-e)*(1-abs(inside-cx)/(half+.15))
        points=[(edge,rear-.12,e+.12),(cx,rear-.12,r+.12),(cx,tb+.03,r+.12),(edge,tb+.03,e+.12)]
        if sign==1:points.reverse()
        s.quad('nave main slope '+str(sign),points)
        points=[(edge,tb+.03,e+.12),(inside,tb+.03,h),(inside,front+.06,h),(edge,front+.06,e+.12)]
        if sign==1:points.reverse()
        s.quad('nave front slope '+str(sign),points)
    # A fixed seven-ring buttress profile retains the side silhouette without weathering strips.
    for side,x in [(-1,xl),(1,xr)]:
        for j in range(6):
            y=front-(front-rear)*j/5
            rings=[(0,.92,.95),(1.3,.92,.95),(1.42,.78,.78),(4.15,.78,.78),(4.70,.67,.57),(7.45,.67,.57),(8.85,.55,.08)]
            for k,((z,w,dep),(Z,W,DEP)) in enumerate(zip(rings,rings[1:])):
                p=[(x,y-w/2,z),(x+side*dep,y-w/2,z),(x+side*dep,y+w/2,z),(x,y+w/2,z)]
                q=[(x,y-W/2,Z),(x+side*DEP,y-W/2,Z),(x+side*DEP,y+W/2,Z),(x,y+W/2,Z)]
                for m in range(3):
                    pts=[p[m],p[m+1],q[m+1],q[m]]
                    if side<0:pts.reverse()
                    s.quad(f'buttress {side} {j} {k} {m}',pts)
    hx0,hx1,hy0,hy1=d['rear_hall']['bounds_xy'];he=d['rear_hall']['eaves'];hr=d['rear_hall']['ridge'];hy=(hy0+hy1)/2
    s.box('rear hall',(hx0,hy0,0),(hx1,hy1,he),omit=('bottom','top'))
    for x in (hx0,hx1):
        points=[(x,hy1,he),(x,hy0,he),(x,hy,hr)]
        s.triangle('hall end '+str(x),points if x==hx0 else points[::-1])
    s.quad('hall front roof',[(hx0-.12,hy,hr+.1),(hx1+.12,hy,hr+.1),(hx1+.12,hy1+.15,he+.1),(hx0-.12,hy1+.15,he+.1)])
    s.quad('hall rear roof',[(hx0-.12,hy0-.15,he+.1),(hx1+.12,hy0-.15,he+.1),(hx1+.12,hy,hr+.1),(hx0-.12,hy,hr+.1)])
    s.box('hall connector',(hx0,hy1,0),(hx1,rear,5.6),omit=('bottom','front','rear'))
    s.part='tower'
    # Frame local x follows each elevation, y points inward, z is height.
    frames=[('front',(cx+tw/2,tf),(-1,0),(0,1),tw),('west',(cx-tw/2,tf),(0,-1),(-1,0),tf-tb),('back',(cx-tw/2,tb),(1,0),(0,-1),tw),('east',(cx+tw/2,tb),(0,1),(1,0),tf-tb)]
    def T(origin,t,n,p):u,dep,z=p;return origin[0]+t[0]*u-n[0]*dep,origin[1]+t[1]*u-n[1]*dep,z
    for name,o,t,n,L in frames:
        def quad(label,pts):s.quad(name+' '+label,[T(o,t,n,p) for p in pts])
        def tri(label,pts):s.triangle(name+' '+label,[T(o,t,n,p) for p in pts])
        def panel(label,l,h,lo,hi,dep=0):quad(label,[(l,dep,lo),(h,dep,lo),(h,dep,hi),(l,dep,hi)])
        def pointed_recess(label,c,radius,bottom,spring,ceiling,depth):
            for j in range(8):
                x=-radius+2*radius*j/8;X=-radius+2*radius*(j+1)/8
                h=lambda u:spring+math.sqrt(max(0,4*radius*radius-(radius+abs(u))**2))
                z,Z=h(x),h(X)
                quad(label+' shoulder '+str(j),[(c+x,0,z),(c+X,0,Z),(c+X,0,ceiling),(c+x,0,ceiling)])
                quad(label+' backing '+str(j),[(c+x,depth,bottom),(c+X,depth,bottom),(c+X,depth,Z),(c+x,depth,z)])
                quad(label+' soffit '+str(j),[(c+x,0,z),(c+x,depth,z),(c+X,depth,Z),(c+X,0,Z)])
            for sign in (-1,1):
                u=c+sign*radius;pts=[(u,0,bottom),(u,depth,bottom),(u,depth,spring),(u,0,spring)]
                quad(label+' jamb '+str(sign),pts if sign<0 else pts[::-1])
        if name=='front':
            panel('door left',0,L/2-1.27,0,15.45);panel('door right',L/2+1.27,L,0,15.45)
            pointed_recess('door',L/2,1.27,.12,3.6,15.45,.30)
        else:panel('lower wall',0,L,0,15.45)
        if name=='back':panel('upper wall',0,L,15.45,22.2)
        else:
            centres=[L/2-1.14,L/2+1.14];radius=.89
            ends=[0]+[v for c in centres for v in (c-radius,c+radius)]+[L]
            for j in range(0,len(ends)-1,2):panel('belfry pier '+str(j),ends[j],ends[j+1],15.45,22.2)
            for j,c in enumerate(centres):pointed_recess('belfry '+str(j),c,radius,15.45,18.75,22.2,.26)
        # A separate narrow rail keeps negative space under the parapet coping.
        temp=Surfaces(['tower'],lambda p:T(o,t,n,p))
        temp.box(name+' parapet',(.13 if name in ('west','east') else 0,-.39,22.9),(L-.13 if name in ('west','east') else L,.13,23.1),omit=('bottom',))
        for j in range(5):temp.box(name+' parapet post '+str(j),(.195+j*(L-.56)/4,-.29,22.46),(.365+j*(L-.56)/4,.05,22.9),omit=('bottom','top'))
        for face in temp.result['tower']:s.quad(face['name'],face['vertices'])
    # Tower angle masses preserve the changing buttress width.
    for x in (cx-tw/2,cx+tw/2):
        for y in (tf,tb):
            for j,(z,Z,w,W) in enumerate([(0,9.55,.95,.57),(9.55,21.7,.57,.45),(21.7,23.3,.60,.60)]):
                p=[(x-w/2,y-w/2,z),(x+w/2,y-w/2,z),(x+w/2,y+w/2,z),(x-w/2,y+w/2,z)]
                q=[(x-W/2,y-W/2,Z),(x+W/2,y-W/2,Z),(x+W/2,y+W/2,Z),(x-W/2,y+W/2,Z)]
                for k in range(4):s.quad(f'tower buttress {x} {y} {j} {k}',[p[k],p[(k+1)%4],q[(k+1)%4],q[k]])
    # The broad porch gable is retained as a plate; fine moulded orders are baked.
    porch=[(-2.1,3.45),(2.1,3.45),(0,8.35)]
    aperture=[(-1.85,.1),(1.85,.1)]+[(x,3.6+math.sqrt(max(0,4*1.85**2-(1.85+abs(x))**2))) for x in [1.85-3.7*j/8 for j in range(9)]]
    for i,poly in enumerate(subtract(porch,aperture)):
        for j in range(1,len(poly)-1):
            s.triangle(f'porch gable {i} {j}',[(cx+x,tf+.83,z) for x,z in (poly[0],poly[j+1],poly[j])])
    s.part='spire';rings=[(22.9,2.83),(24.7,2.66),(31.5,1.93),(38.5,1.13),(46.8,.12),(47.2,.025)]
    for k,((z,r0),(Z,r1)) in enumerate(zip(rings,rings[1:])):
        for j in range(8):
            a=math.pi/8+j*math.tau/8;b=a+math.tau/8
            s.quad(f'spire {k} {j}',[(cx+r0*math.cos(a),cy+r0*math.sin(a),z),(cx+r0*math.cos(b),cy+r0*math.sin(b),z),(cx+r1*math.cos(b),cy+r1*math.sin(b),Z),(cx+r1*math.cos(a),cy+r1*math.sin(a),Z)])
    s.box('weather deck',(cx-(tw-.12)/2,tb+.06,22.55),(cx+(tw-.12)/2,tf-.06,22.75),omit=('bottom',))
    for tier,z,radius,rad,spring in [(0,25.1,2.55,.58,2.65),(1,34.15,1.62,.34,1.25)]:
        for j,n in enumerate(((1,0),(-1,0),(0,1),(0,-1))):
            t=(-n[1],n[0]);o=(cx+n[0]*radius*.93,cy+n[1]*radius*.93)
            temp=Surfaces(['spire'],lambda p:T(o,t,n,p));w=rad+.24;top=z+spring+rad*2.1+.4
            temp.box(f'lucarne {tier} {j}',(-w,-.24,z),(w,.65,z+spring),omit=('bottom','front','top'))
            temp.triangle(f'lucarne gable {tier} {j}',[(-w,-.24,z+spring),(w,-.24,z+spring),(0,-.24,top)])
            for side in (-1,1):temp.quad(f'lucarne slope {tier} {j} {side}',[(side*w,-.24,z+spring),(side*w,.65,z+spring),(0,.65,top),(0,-.24,top)] if side>0 else [(0,-.24,top),(0,.65,top),(side*w,.65,z+spring),(side*w,-.24,z+spring)])
            for face in temp.result['spire']:s.quad(face['name'],face['vertices'])
    for x in (cx-tw/2,cx+tw/2):
        for y in (tf,tb):
            profile=[(0,.48),(.40,.48),(.40,.40),(.90,.40),(1.,.53),(1.10,.42),(3.15,.02),(3.4,.02)]
            for k,((z,w),(Z,W)) in enumerate(zip(profile,profile[1:])):
                p=[(x-w/2,y-w/2,23.3+z),(x+w/2,y-w/2,23.3+z),(x+w/2,y+w/2,23.3+z),(x-w/2,y+w/2,23.3+z)]
                q=[(x-W/2,y-W/2,23.3+Z),(x+W/2,y-W/2,23.3+Z),(x+W/2,y+W/2,23.3+Z),(x-W/2,y+W/2,23.3+Z)]
                for j in range(4):s.quad(f'pinnacle {x} {y} {k} {j}',[p[j],p[(j+1)%4],q[(j+1)%4],q[j]])
    return s.result
