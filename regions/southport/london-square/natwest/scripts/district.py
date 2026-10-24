"""Fixed bank envelope with shaped Dutch gables and the five-volume roof plan."""
import json
import math
import bpy
from mathutils import Vector
from blender_envelope import Surfaces
from roof import joined_roof


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());base=d['base_z']
    xn,xf,yf,yb=(d[k] for k in ('x_min','x_max','front_y','rear_y'))
    s=Surfaces(['architecture','roof','bank-frontage'],lambda p:(p[0],p[1],p[2]+base))
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('rear',(xn,yb),(xf,yb),0,12.3);wall('party',(xf,yb),(xf,yf),0,12.3)
    frames=[('Lord',(xf,yf),(-1,0),(0,1),xf-xn,[3,xf-xn-3],1),('London',(xn,yf),(0,-1),(-1,0),yf-yb,[6.83],.79)]
    def T(o,t,n,p):u,depth,z=p;return o[0]+t[0]*u-n[0]*depth,o[1]+t[1]*u-n[1]*depth,z
    for name,o,t,n,L,gables,spread in frames:
        def quad(label,pts):s.quad(name+' '+label,[T(o,t,n,p) for p in pts])
        def panel(label,l,r,lo,hi,depth=0):quad(label,[(l,depth,lo),(r,depth,lo),(r,depth,hi),(l,depth,hi)])
        s.part='architecture';panel('upper',0,L,6.2,12.6)
        for u in [0.25,L-.25]+([5.55,17.35] if name=='Lord' else [4.76,8.76]):
            temp=Surfaces(['architecture'],lambda p:T(o,t,n,p))
            temp.box(name+' turret '+str(u),(u-.31,-.46,5.5),(u+.31,.04,12.4),omit=('bottom','front','top'))
            temp.box(name+' turret head '+str(u),(u-.41,-.56,12.4),(u+.41,.18,13.35),omit=('bottom',))
            for face in temp.result['architecture']:
                if name=='London' and u==.25 and face['name'].endswith('top'):
                    from southport3d.planar import subtract
                    polygon=[p[:2] for p in face['vertices']]
                    cutter=[(xn-.16,yf-.18),(xn+.66,yf-.18),(xn+.66,yf+.56),(xn-.16,yf+.56)]
                    for j,piece in enumerate(subtract(polygon,cutter)):
                        for k in range(1,len(piece)-1):s.triangle('corner turret top '+str(j)+' '+str(k),[(*p,13.35) for p in (piece[0],piece[k],piece[k+1])])
                else:s.quad(face['name'],face['vertices'])
        for u in gables:
            rows=[(12.6,2.80*spread),(13.35,2.55*spread),(14.1,2.15*spread),(14.85,1.70*spread),(15.65,1.25*spread),(16.35,.92),(17.05,.76),(18.18,.72)]
            for i,((z,w),(Z,W)) in enumerate(zip(rows,rows[1:])):
                quad(f'gable {u} {i}',[(u-w,-.18,z),(u+w,-.18,z),(u+W,-.18,Z),(u-W,-.18,Z)])
                quad(f'gable back {u} {i}',[(u+w,.22,z),(u-w,.22,z),(u-W,.22,Z),(u+W,.22,Z)])
                for sign in (-1,1):quad(f'gable edge {u} {i} {sign}',[(u+sign*w,-.18,z),(u+sign*w,.22,z),(u+sign*W,.22,Z),(u+sign*W,-.18,Z)])
            # Coarse rounded pediment cap, separated from the shoulder envelope.
            for j in range(6):
                a=math.pi*j/6;b=math.pi*(j+1)/6
                p=(u+.78*math.cos(a),18.30+.78*math.sin(a));q=(u+.78*math.cos(b),18.30+.78*math.sin(b))
                s.triangle(f'{name} pediment {u} {j}',[T(o,t,n,(u,-.35,18.18)),T(o,t,n,(q[0],-.35,q[1])),T(o,t,n,(p[0],-.35,p[1]))])
                quad(f'pediment edge {u} {j}',[(p[0],-.35,p[1]),(q[0],-.35,q[1]),(q[0],.02,q[1]),(p[0],.02,p[1])])
            # Heraldic finial keeps a small silhouette mass without sculptural tessellation.
            temp=Surfaces(['architecture'],lambda p:T(o,t,n,p));temp.box(f'{name} finial {u}',(u-.18,-.35,19.08),(u+.18,.03,19.8),omit=('bottom',))
            for face in temp.result['architecture']:s.quad(face['name'],face['vertices'])
        spans=[(5.8,17.1)] if name=='Lord' else [(.7,4.36),(9.16,L-.65)]
        for j,(l,r) in enumerate(spans):
            temp=Surfaces(['architecture'],lambda p:T(o,t,n,p))
            units=3 if r-l>7 else 1;unit=(r-l)/units
            for k in range(units):
                width=unit-.24;centre=l+(k+.5)*unit
                for z in (12.62,13.15):temp.box(f'{name} parapet rail {j} {k} {z}',(centre-width/2,-.26,z-.05),(centre+width/2,-.04,z+.05),omit=('bottom',))
                # Keep one actual V brace per broad parapet bay. Scrolls and
                # the other repeated braces disappear, leaving genuine air.
                count=max(1,round(width/.95));cell=(count-1)//2
                c=centre-width/2+(cell+.5)*width/count
                for leg,(p,q) in enumerate([((c-.36,-.15,12.69),(c,-.15,13.09)),((c,-.15,13.09),(c+.36,-.15,12.69))]):
                    A,B=Vector(p),Vector(q);direction=(B-A).normalized()
                    across=Vector((direction.z,0,-direction.x))*.03;depth=Vector((0,.03,0))
                    v=[tuple(point+i*across+h*depth) for point in (A,B) for i,h in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                    # Miter both legs at the apex, sharing only their edge.
                    for index in (range(4,8) if leg==0 else range(4)):
                        point=Vector(v[index]);point+=direction*((c-point.x)/direction.x);v[index]=tuple(point)
                    for f,ids in enumerate([(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]):
                        if f==(1 if leg==0 else 0):continue
                        temp.quad(f'{name} parapet brace {j} {k} {leg} {f}',[v[n] for n in ids])
            for face in temp.result['architecture']:s.quad(face['name'],face['vertices'])
        s.part='bank-frontage'
        if name=='London':panel('lower',0,L,0,6.2)
        else:
            doors=[(8.1,1.14),(19.9,1.48)];last=0
            for j,(u,radius) in enumerate(doors):
                panel('lower strip '+str(j),last,u-radius,0,6.2)
                panel('door head '+str(j),u-radius,u+radius,5.35,6.2)
                panel('recessed door '+str(j),u-radius,u+radius,0,5.35,.17)
                for x in (u-radius,u+radius):quad('door return '+str(x),[(x,0,0),(x,.17,0),(x,.17,5.35),(x,0,5.35)])
                last=u+radius
            panel('last lower strip',last,L,0,6.2)
    s.part='roof';R=d['roof_ranges'];xi=xn+R['side_width'];back=yf-R['front_depth'];xr=xn+R['side_width']/2;yr=yf-R['front_depth']/2
    # This shared generator is five simple dimensioned roof volumes, with no
    # window, slate-tile or ornament meshes. Keep its explicit triangle cap.
    def finish(mesh):
        ob=mesh.finish([]);ob.data.uv_layers.new(name='coarse shape UV');return ob
    roof=joined_roof(xn,xf,yf,yb,0,finish,R)
    for j,face in enumerate(roof.data.polygons):
        if face.normal.z<-.5:continue
        s.triangle('joined roof '+str(j),[tuple(roof.data.vertices[k].co) for k in face.vertices])
    mesh=roof.data;bpy.data.objects.remove(roof,do_unlink=True);bpy.data.meshes.remove(mesh)
    s.box('lower flat deck',(xi+.1,yb+.36,10.125),(xf-.36,back,10.375),omit=('bottom',))
    wall('inner west',(xi+.1,back),(xi+.1,yb+.36),10.375,12.35)
    wall('inner north',(xf-.36,back),(xi+.1,back),10.375,12.35)
    s.box('rear parapet',(xn+.42,yb-.02,12.3),(xf,yb+.26,12.8),omit=('bottom',))
    for i,(x,y,w,dep,h,pots) in enumerate([(20.5,yf-3.8,.95,.85,18.,1),(29,yr,1.25,.8,17.3,2),(xr,yb+1,2.25,.9,16.8,4),(13,yf-8,1.9,.85,17.5,3)]):
        s.box('chimney '+str(i),(x-w/2,y-dep/2,12),(x+w/2,y+dep/2,h),omit=('bottom',))
        s.box('chimney cap '+str(i),(x-w/2-.12,y-dep/2-.11,h),(x+w/2+.12,y+dep/2+.11,h+.09),omit=('bottom',))
        for j in range(pots):
            u=x+(j-(pots-1)/2)*.38
            s.box(f'pot {i} {j}',(u-.13,y-.13,h+.09),(u+.13,y+.13,h+.59),omit=('bottom',),cage=.10)
    for x,y in [(24,-39),(26,-35.5)]:s.box('service upstand '+str(x),(x-.6,y-.9,10.375),(x+.6,y+.9,10.775),omit=('bottom',))
    s.part='architecture';L=math.hypot(30.4-33.12,-23.16+22.8);t=((30.4-33.12)/L,(-23.16+22.8)/L);n=(t[1],-t[0]);o=(33.12,-22.8)
    s.quad('boundary wall',[T(o,t,n,p) for p in [(0,0,0),(L,0,0),(L,0,2.71),(0,0,2.71)]])
    for j in range(6):
        a=math.pi*j/6;b=math.pi*(j+1)/6
        s.triangle('boundary pediment '+str(j),[T(o,t,n,p) for p in [(1.465,-.1,2.71),(1.465+.70*math.cos(b),-.1,2.71+.70*math.sin(b)),(1.465+.70*math.cos(a),-.1,2.71+.70*math.sin(a))]])
    s.part='bank-frontage';temp=Surfaces(['bank-frontage'],lambda p:T(o,t,n,(p[0]+.43,p[1]-.58,p[2])))
    temp.box('telephone kiosk',(-.455,-.455,0),(.455,.455,2.38),omit=('bottom','top'))
    for j in range(4):
        points=[(-.46,-.46,2.38),(.46,-.46,2.38),(.46,.46,2.38),(-.46,.46,2.38)]
        temp.triangle('telephone roof '+str(j),[points[j],points[(j+1)%4],(0,0,2.54)])
    for face in temp.result['bank-frontage']:s.quad(face['name'],face['vertices'])
    return s.result
