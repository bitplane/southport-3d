"""Fixed silhouette envelope, retaining the accepted plan and stepped rear."""
import json
import math
from mathutils import Vector
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());base=d['base_z']
    s=Surfaces(['architecture','roof','shopfront'],lambda p:(p[0],p[1],p[2]+base))
    def wall(name,a,b,lo,hi):
        s.quad(name,[(*a,lo),(*b,lo),(*b,hi),(*a,hi)])
    lord=((-12.8,-23.4),(-30.4,-23.4));london=((-9.6,-39),(-9.6,-26.1));corner=(london[1],lord[0])
    for name,(a,b) in [('Lord',lord),('London',london),('corner',corner)]:wall('upper '+name,a,b,5.3,15.6)
    wall('party',(-30.4,-23.4),(-30.4,-37.1),0,15.6)
    # Terminal bays remain distinct narrow masses beyond the main cornice.
    wall('Lord terminal upper',(-30.4,-23.75),(-32.2,-23.75),5.3,15)
    wall('Lord terminal return',(-32.2,-23.75),(-32.2,-37.1),0,15)
    wall('London terminal upper',(-9.92,-41.2),(-9.92,-39),5.3,15)
    wall('London terminal join',(-9.92,-39),(-9.6,-39),0,15)
    # Each rear wing retains its three exposed faces and its actual roof level.
    for wing in d['rear_review']['wings']:
        l,r=wing['x_limits'];y=wing['rear_y'];h=wing['height_m']
        s.box('rear '+wing['id'],(l,y,0),(r,-37.1,h),omit=('bottom','top','front','right') if wing['id']=='east' else ('bottom','top','front'))
        if wing['id']=='east':wall('rear east exposed return',(r,-39),(r,-37.1),0,h)
        if h>18.3:wall('headhouse front',(r,-37.1),(l,-37.1),18.3,h)
    for i,rec in enumerate(d['rear_review']['recesses']):
        l,r=rec['x_limits'];y=rec['rear_y'];h=18.45 if i==0 else 15
        wall('recess '+str(i),(l,y),(r,y),0,h)
        # Coarse landings and diagonal flights retain open wells; no solid
        # stairwell box. Slender railings/pipes/aerials disappear at District.
        width=r-l;u0=width-2.05;outer=width-.15;divider=u0+.94
        levels=[0,rec['landing_heights_m'][0]/2,*rec['landing_heights_m']]
        for j,z in enumerate(levels[1:]):
            for k,(x0,x1,d0,d1) in enumerate([(.18,outer,.02,.95),(divider,outer,.95,4.25),(u0-.08,outer,4.25,5.10)]):
                s.box(f'landing {i} {j} {k}',(l+x0,y-d1,z-.07),(l+x1,y-d0,z),omit=('bottom',))
        for j,(lo,hi) in enumerate(zip(levels,levels[1:])):
            for k in range(6):
                near=.95+3.3*k/6;far=.95+3.3*(k+1)/6;z=lo+(hi-lo)*(k+1)/6-.025
                s.quad(f'flight {i} {j} {k}',[(l+u0,y-near,z),(l+u0,y-far,z),(l+u0+.85,y-far,z),(l+u0+.85,y-near,z)])
    s.part='shopfront'
    for name,(a,b) in [('Lord',lord),('London',london)]:wall('shop '+name,a,b,0,5.3)
    def framed(origin,tangent,normal):
        def transform(p):u,depth,z=p;return (origin[0]+tangent[0]*u-normal[0]*depth,origin[1]+tangent[1]*u-normal[1]*depth,z)
        return transform
    def local_quad(name,points,transform,**kw):s.quad(name,[transform(p) for p in points],**kw)
    def portal(name,a,b,width,head,arch=False):
        L=math.dist(a,b);t=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(t[1],-t[0]);T=framed(a,t,n);c=L/2
        def panel(label,l,r,lo,hi,depth=0):local_quad(name+label,[(l,depth,lo),(r,depth,lo),(r,depth,hi),(l,depth,hi)],T)
        panel(' left',0,c-width/2,0,5.3);panel(' right',c+width/2,L,0,5.3)
        segments=8 if arch else 1
        for j in range(segments):
            x=-width/2+width*j/segments;X=-width/2+width*(j+1)/segments
            z=head+(math.sqrt(max(0,(width/2)**2-x*x)) if arch else 0)
            Z=head+(math.sqrt(max(0,(width/2)**2-X*X)) if arch else 0)
            local_quad(name+' head '+str(j),[(c+x,0,z),(c+X,0,Z),(c+X,0,5.3),(c+x,0,5.3)],T)
            local_quad(name+' door '+str(j),[(c+x,.22,0),(c+X,.22,0),(c+X,.22,Z),(c+x,.22,z)],T)
            if not arch:local_quad(name+' soffit '+str(j),[(c+x,.22,z),(c+X,.22,Z),(c+X,0,Z),(c+x,0,z)],T)
        for x in (c-width/2,c+width/2):local_quad(name+' jamb '+str(x),[(x,0,0),(x,.22,0),(x,.22,head),(x,0,head)],T)
    portal('corner',*corner,1.65,3.35,True)
    portal('Lord flats',(-30.4,-23.75),(-32.2,-23.75),1.05,3.1)
    portal('London inset',(-9.92,-41.2),(-9.92,-39),1.05,3.1)
    s.part='roof';poly=d['footprint'];inner=[]
    for i,p in enumerate(poly):
        before,here,after=Vector(poly[i-1]),Vector(p),Vector(poly[(i+1)%len(poly)])
        t0=(here-before).normalized();t1=(after-here).normalized();n0=Vector((-t0.y,t0.x));n1=Vector((-t1.y,t1.x))
        inner.append(tuple(here+(n0+n1)*(1.8/(1+n0.dot(n1)))))
    inner[0]=(-30.4,-39);inner[1]=(inner[1][0],-39);inner[4]=(-30.4,inner[4][1])
    for i in (1,2,3):
        j=(i+1)%len(poly)
        s.quad('mansard '+str(i),[(*poly[i],15.7),(*poly[j],15.7),(*inner[j],18.3),(*inner[i],18.3)])
    for i in range(1,len(inner)-1):s.triangle('flat deck '+str(i),[(*inner[0],18.3),(*inner[i],18.3),(*inner[i+1],18.3)])
    s.quad('party gable',[(-30.4,-39,15.6),(-30.4,-23.4,15.6),(-30.4,-25.2,18.3),(-30.4,-39,18.3)][::-1])
    s.quad('east rear upper',[(-19.3,-39,15),(-9.6,-39,15),(-11.4,-39,18.3),(-19.3,-39,18.3)])
    # Individual coarse dormers retain nine projections, not window frame meshes.
    for name,(a,b),centres,scale in [('Lord',lord,[2.05,5.8,9.55,13.3,17.05],17.6/19.2),('London',london,[2.35,6.45,10.55],1),('corner',corner,[math.dist(*corner)/2],1)]:
        L=math.dist(a,b);t=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(t[1],-t[0])
        for j,u in enumerate(centres):
            origin=(a[0]+t[0]*u*scale,a[1]+t[1]*u*scale);T=framed(origin,t,n)
            temp=Surfaces(['roof'],lambda p:T((p[0]*scale,p[1],p[2])))
            temp.quad(f'dormer front {name} {j}',[(-.825,.20,16.2),(.825,.20,16.2),(.825,.20,17.8),(-.825,.20,17.8)])
            for sign in (-1,1):
                x=sign*.825;points=[(x,.20,16.2),(x,.346,16.2),(x,1.46,17.8),(x,.20,17.8)]
                temp.quad(f'dormer cheek {name} {j} {sign}',points if sign>0 else points[::-1])
            temp.box(f'dormer cap {name} {j}',(-.96,.075,17.80),(.96,1.585,17.96),omit=('bottom',))
            for face in temp.result['roof']:s.quad(face['name'],face['vertices'])
    for c in d['chimneys']:
        angle=math.radians(c['yaw_degrees']);x,y=c['centre'];length=c['length'];w=c['width']
        T=lambda p:(x+math.cos(angle)*p[0]-math.sin(angle)*p[1],y+math.sin(angle)*p[0]+math.cos(angle)*p[1],p[2])
        temp=Surfaces(['roof'],T)
        temp.box('stack '+c['id'],(-length/2,-w/2,17.2),(length/2,w/2,19.9))
        temp.box('coping '+c['id'],(-length/2-.11,-w/2-.11,19.9),(length/2+.11,w/2+.11,20.04),omit=('bottom',))
        for j in range(c['pots']):
            u=(j-(c['pots']-1)/2)*(length-.30)/(c['pots']-1)
            temp.box(f'pot {c["id"]} {j}',(u-.095,-.095,20.04),(u+.095,.095,21.22),cage=.07)
        for face in temp.result['roof']:s.quad(face['name'],face['vertices'],cage=face.get('cage_m'))
    for wing in d['rear_review']['wings']:
        l,r=wing['x_limits'];y=wing['rear_y'];h=wing['height_m']
        s.quad('rear roof '+wing['id'],[(l,y,h),(r,y,h),(r,-37.1,h),(l,-37.1,h)])
    s.box('Lord terminal roof',(-32.25,-39.04,15),(-30.35,-23.71,15.10),omit=('bottom',))
    return s.result
