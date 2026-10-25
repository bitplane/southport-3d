"""Bounded shop terrace envelope, recessed doors and the stepped service rear."""
import json
import math
from mathutils import Matrix,Vector
from blender_envelope import Surfaces
from southport3d.geometry import face_matrix


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());z=d['base_z']
    x0,x1=d['x_far'],d['x_near'];yf,yb=d['front_y'],d['rear_y'];h=d['parapet_top'];rl=d['roof_level'];w=x1-x0
    s=Surfaces(['architecture','roof','shopfront'],lambda p:(p[0],p[1],p[2]+z))
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('upper front',(x1,yf),(x0,yf),5.2,h)
    wall('west party',(x0,yf),(x0,yb),0,h)
    wall('east party',(x1,yb),(x1,yf),0,h)
    wall('upper rear',(x0,yb),(x1,yb),7.09,h)
    wall('annex rear',(x0,-49),(x1,-49),0,7)
    wall('annex west',(x0,yb),(x0,-49),0,7)
    wall('annex east',(x1,-49),(x1,yb),0,7)
    s.part='roof'
    s.quad('main flat roof',[(x0+.3,yb+.31,rl+.11),(x1-.3,yb+.31,rl+.11),(x1-.3,yf-.4,rl+.11),(x0+.3,yf-.4,rl+.11)])
    s.quad('annex roof',[(x0,-49,7.09),(x1,-49,7.09),(x1,yb,7.09),(x0,yb,7.09)])
    for name,A,B in [('front',(x0+.3,yf-.4),(x1-.3,yf-.4)),('west',(x0+.3,yb+.31),(x0+.3,yf-.4)),('east',(x1-.3,yf-.4),(x1-.3,yb+.31)),('rear',(x1-.3,yb+.31),(x0+.3,yb+.31))]:wall('parapet inner '+name,A,B,rl+.11,h+.11)
    # Caps meet at butt joints; front/rear own the corners.
    for name,a,b in [('front',(x0,yf-.4,h),(x1,yf,h+.11)),('rear',(x0,yb,h),(x1,yb+.31,h+.11)),('west',(x0,yb+.31,h),(x0+.3,yf-.4,h+.11)),('east',(x1-.3,yb+.31,h),(x1,yf-.4,h+.11))]:
        s.quad(name+' coping',[(a[0],a[1],b[2]),(b[0],a[1],b[2]),(b[0],b[1],b[2]),(a[0],b[1],b[2])])
    # Rooflights and the single vent are distinct broad skyline features.
    for x in (-35.4,-41.4,-47.1):s.box('rooflight '+str(x),(x-.75,-36.125,rl+.05),(x+.75,-34.875,rl+.38))
    s.box('vent',(-46.2,-39.2,rl+.1),(-45.8,-38.8,rl+.8))
    s.part='shopfront'
    def panel(name,a,b,lo,hi,depth=0):wall(name,(x1-a,yf-depth),(x1-b,yf-depth),lo,hi)
    last=0
    for shop in d['shops']:
        a,b=shop['u0'],shop['u1'];name=shop['id'];u=b-.61 if name!='bugle-tap' else a+(b-a)*.67;l,r=u-.53,u+.53
        panel('front '+name,last,l,0,5.2)
        panel('door head '+name,l,r,3.1,5.2)
        panel('door '+name,l,r,0,3.1,.45 if name=='mamma-mia' else .4)
        s.quad('door soffit '+name,[(x1-l,yf,3.1),(x1-l,yf-.42,3.1),(x1-r,yf-.42,3.1),(x1-r,yf,3.1)])
        for side in (l,r):s.quad('door jamb '+name+str(side),[(x1-side,yf,0),(x1-side,yf-.42,0),(x1-side,yf-.42,3.1),(x1-side,yf,3.1)])
        panel('front return '+name,r,b,0,5.2);last=b
        if name=='mamma-mia':
            s.quad('awning top',[(x1-b,yf,3.62),(x1-a,yf,3.62),(x1-a,yf+.85,3.28),(x1-b,yf+.85,3.28)])
            panel('awning valance',a,b,3.12,3.28,-.85)
    panel('last pier',last,w,0,5.2)
    s.part='architecture'
    # Fixed 19-tread escapes retain the source rise/run; rails and fittings are
    # omitted. They do not inherit subdivision from detailed ornament meshes.
    rear_frame=face_matrix((x0,-49,0),(0,-1,0))
    for name,u,landing,width,run,frame in [('west',0,0,.85,3.6,rear_frame@Matrix.Translation((.65,0,.75))@Matrix.Rotation(math.pi/2,4,'Y')),('central',9.4,.9,.95,4.2,rear_frame)]:
        temp=Surfaces(['architecture'],lambda p:frame@Vector(p))
        for i in range(19):
            X=u-run+(i+.5)*run/19;Y=(i+1)*3.6/19
            temp.box(name+' tread '+str(i),(X-run/38,Y-.0325,landing-width/2),(X+run/38,Y+.0325,landing+width/2),omit=())
        temp.box(name+' landing',(u,3.55,landing-width/2),(u+.7,3.65,landing+width/2),omit=())
        for face in temp.result['architecture']:s.quad(face['name'],face['vertices'],cage=.08)
    return s.result
