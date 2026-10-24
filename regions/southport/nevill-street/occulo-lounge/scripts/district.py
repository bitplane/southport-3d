"""Fixed District topology; nine low-sided columns preserve the giant order."""
import json,math
from blender_envelope import Surfaces

def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());W=d['width'];L=d['depth']
    def T(p):x,y,z=p;return d['x']+x+d['shear_x']*y,d['y']+y+d['shear_y']*x,d['base_z']+z
    s=Surfaces(['facades','roof','frontage'],T)
    for name,length,bays,cols in [('Lord',W,d['front_bays'],d['front_columns']),('Nevill',L,d['side_bays'],d['side_columns'])]:
        def F(p):u,z,out=p;return (u,-out,z) if name=='Lord' else (W+out,u,z)
        def q(label,pts,**kw):
            if label in ('fascia','fascia top','cornice top','entablature'):
                pts=[((length+out if abs(u-length)<1e-7 else u),z,out) if name=='Lord' else ((-out if abs(u)<1e-7 else u),z,out) for u,z,out in pts]
            s.quad(name+' '+label,[F(p) for p in pts],**kw)
        def panel(label,a,b,lo,hi,out=0):q(label,[(a,lo,out),(b,lo,out),(b,hi,out),(a,hi,out)])
        s.part='facades'
        if name=='Lord':
            u=W/2;panel('lower left',0,u-1.075,0,8.95,.06);panel('lower right',u+1.075,W,0,8.95,.06);panel('entrance head',u-1.075,u+1.075,4.74,8.95,.06)
            q('door jamb left',[(u-1.075,0,.06),(u-1.075,0,-.32),(u-1.075,4.74,-.32),(u-1.075,4.74,.06)])
            q('door jamb right',[(u+1.075,0,-.32),(u+1.075,0,.06),(u+1.075,4.74,.06),(u+1.075,4.74,-.32)])
            q('door threshold',[(u-1.075,0,.06),(u+1.075,0,.06),(u+1.075,0,-.32),(u-1.075,0,-.32)])
            q('door soffit',[(u-1.075,4.74,-.32),(u+1.075,4.74,-.32),(u+1.075,4.74,.06),(u-1.075,4.74,.06)])
        else:panel('lower',0,length,0,8.95,.06)
        panel('upper wall',0,length,8.95,15.75,-.02)
        panel('entablature',0,length,15.75,17.25,.28)
        q('cornice top',[(0,17.25,.60),(length,17.25,.60),(length,17.25,-.02),(0,17.25,-.02)])
        # Narrow sign fascia is baked from both facade and lettering source groups.
        panel('fascia',0,length,8.50,8.94,.75)
        q('fascia top',[(0,8.94,.75),(length,8.94,.75),(length,8.94,-.02),(0,8.94,-.02)])
        # Eight-sided shafts with coarse base and capital profiles. No dependence
        # on high-detail flutes, foliage, baluster count or window subdivision.
        for j,u in enumerate(cols):
            profile=[(8.95,.57),(9.30,.45),(15.37,.39),(15.75,.55)]
            for k,((z,r),(Z,R)) in enumerate(zip(profile,profile[1:])):
                for i in range(8):
                    a=math.tau*i/8;b=math.tau*(i+1)/8
                    q(f'column {j} {k} {i}',[(u+r*math.cos(a),z,.24-r*math.sin(a)),(u+r*math.cos(b),z,.24-r*math.sin(b)),(u+R*math.cos(b),Z,.24-R*math.sin(b)),(u+R*math.cos(a),Z,.24-R*math.sin(a))],cage=.20)
        # Balcony projection retained as one solid sill mass per window; open
        # balusters become a baked panel at district viewing distances.
        for j,u in enumerate(bays):
            q(f'balcony {j}',[(u-1.20,8.90,.73),(u+1.20,8.90,.73),(u+1.20,9.76,.73),(u-1.20,9.76,.73)])
    # Rear L-shaped wall perimeter, same registration as the detailed shell.
    plan=[(0,0),(W,0),(W,L),(4.5,L),(4.5,6),(0,6)]
    for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
        if i>=2:s.quad('rear wall '+str(i),[(*a,0),(*b,0),(*b,17.25),(*a,17.25)])
    # Pediment remains geometric; the small dark oculus is baked into its face.
    for name,y,reverse in [('front',-.16,False),('back',.06,True)]:
        pts=[(0,y,17.25),(W,y,17.25),(W/2,y,19.70)]
        s.triangle('pediment '+name,list(reversed(pts)) if reverse else pts)
    for a,b in [((0,17.25),(W/2,19.70)),((W/2,19.70),(W,17.25))]:s.quad('pediment edge '+str(a),[(a[0],-.30,a[1]),(b[0],-.30,b[1]),(b[0],.06,b[1]),(a[0],.06,a[1])])
    s.part='frontage';u=W/2
    s.quad('recessed door',[(u-1.075,.32,0),(u+1.075,.32,0),(u+1.075,.32,4.74),(u-1.075,.32,4.74)])
    s.part='roof'
    s.quad('front deck',[(0,0,17.35),(W,0,17.35),(W,6,17.35),(0,6,17.35)])
    s.quad('rear deck',[(4.5,6,17.35),(W,6,17.35),(W,L,17.35),(4.5,L,17.35)])
    for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
        if i<2:continue
        x=(a[0]+b[0])/2;y=(a[1]+b[1])/2;dx=max(.22,abs(b[0]-a[0]))/2;dy=max(.22,abs(b[1]-a[1]))/2
        s.box('parapet '+str(i),(x-dx,y-dy,17.35),(x+dx,y+dy,17.81))
    s.box('front attic',(.36,.66,17.35),(W-.36,1.04,18.79))
    s.box('rear access',(4.85,12.65,17.35),(8.25,16.35,18.85))
    for i,y in enumerate((5.2,10.9)):s.box('rooflight '+str(i),(W-7.15,y-.95,17.35),(W-5.25,y+.95,17.85))
    # Coarse urn silhouettes, with shared baked appearance remaining fixed.
    for j,x in enumerate((.45,W-.45)):
        for k,((z,r),(Z,R)) in enumerate(zip([(17.48,.20),(17.85,.16),(18.08,.27),(18.52,.03)],[(17.85,.16),(18.08,.27),(18.52,.03)])):
            for i in range(6):
                a=math.tau*i/6;b=math.tau*(i+1)/6
                s.quad(f'urn {j} {k} {i}',[(x+r*math.cos(a),-.08+r*math.sin(a),z),(x+r*math.cos(b),-.08+r*math.sin(b),z),(x+R*math.cos(b),-.08+R*math.sin(b),Z),(x+R*math.cos(a),-.08+R*math.sin(a),Z)],cage=.12)
    return s.result
