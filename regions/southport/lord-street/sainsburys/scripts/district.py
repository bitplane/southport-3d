"""Fixed store envelope with skew registration and an open canopy skeleton."""
import json
import math
from blender_envelope import Surfaces
from southport3d.planar import subtract


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    W,DEP=d['width'],d['depth'];MW=d['main_front_width'];PH=d['front_parapet'];LH=d['church_wing_parapet'];RH=d['rear_parapet']
    corners=d['registration_corners']
    def world(p):
        x,y,z=p;u=x/W;v=-y/DEP
        return tuple((1-v)*((1-u)*corners[0][i]+u*corners[1][i])+v*((1-u)*corners[2][i]+u*corners[3][i]) for i in range(2))+(z+d['base_z'],)
    s=Surfaces(['frontage','canopy','roof-service'],world)
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    wall('main frontage',(MW,0),(0,0),0,PH)
    wall('wing frontage',(W,0),(MW,0),0,LH)
    s.part='roof-service';deck=RH-.23
    wall('west wall',(0,0),(0,-DEP),0,deck)
    wall('east wall',(W,-DEP),(W,0),0,deck)
    wall('loading wall',(0,-DEP),(W,-DEP),0,deck)
    # Inner parapet faces and caps remain above the deck, rather than a box lid.
    deck=RH-.23
    for name,x0,x1,y0,y1 in [('west',0,.225,-DEP,0),('east',W-.225,W,-DEP,0),('rear',.225,W-.225,-DEP,-DEP+.175)]:
        s.box(name+' parapet',(x0,y0,deck),(x1,y1,RH+.14),omit=('bottom','front') if name in ('west','east') else ('bottom',))
    ranges=[(.2,MW-.25,-12,-.38,PH-.45,PH+2.2),(MW+.2,W-.25,-10.8,-.38,LH-.28,LH+2.25)]
    pieces=[[(.225,-DEP+.175),(W-.225,-DEP+.175),(W-.225,-.60),(.225,-.60)]]
    for x0,x1,y0,y1,e,r in ranges:
        pieces=[q for p in pieces for q in subtract(p,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)])]
        h=min((x1-x0)*.24,(y1-y0)*.45);cy=(y0+y1)/2
        v=[(x0,y0,e),(x1,y0,e),(x1,y1,e),(x0,y1,e),(x0+h,cy,r),(x1-h,cy,r)]
        for j,ids in enumerate([(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]):
            p=[v[k] for k in ids];(s.quad if len(p)==4 else s.triangle)('hip '+str(x0)+' '+str(j),p)
        # Source contains support faces at both ends and both main-range sides.
        for y in (y0,y1):
            A,B=((x0,y),(x1,y)) if y==y0 else ((x1,y),(x0,y))
            wall('hip end support '+str((x0,y)),A,B,RH-.5,e)
        if x0<1:
            for x in (x0,x1):
                A,B=((x,y1),(x,y0)) if x==x0 else ((x,y0),(x,y1))
                wall('hip side support '+str(x),A,B,RH-.5,e)
    for j,p in enumerate(pieces):
        for k in range(1,len(p)-1):s.triangle('deck '+str(j)+' '+str(k),[(*q,deck) for q in (p[0],p[k],p[k+1])])
    s.box('rear access',(11.3,-DEP, RH-.3),(16.3,-DEP+1.445,RH+1.9),omit=('bottom','rear'))
    wall('access rear',(11.3,-DEP),(16.3,-DEP),RH+.14,RH+1.9)
    for i,(x,y,w,h,z) in enumerate([(8,-23,5,3,1.3),(20,-30,6,3.6,1.6),(31,-22,4,3,1),(28,-42,6,4,1.3),(8,-42,3,3,.8)]):
        s.box('plant '+str(i),(x-w/2,y-h/2,RH-.18),(x+w/2,y+h/2,RH-.18+z))
    s.part='canopy';projection=d['canopy_projection']
    # Six sides, fixed source profile. Deliberately omit glass and fine lattice;
    # neither becomes an opaque wall under the canopy.
    rings=[(0,.16),(.12,.17),(.18,.13),(.58,.13),(.68,.18),(.74,.15),(1,.10),(1.06,.12),(1.06,.09),(3.5,.067),(3.55,.12),(3.66,.13),(3.72,.20),(3.82,.20),(3.88,.12),(4.25,.095)]
    for col in range(8):
        x=.25+col*(W-.5)/7
        for j,((z,r),(Z,R)) in enumerate(zip(rings,rings[1:])):
            for k in range(6):
                a=math.tau*k/6;b=math.tau*(k+1)/6
                s.quad(f'column {col} {j} {k}',[(x+r*math.cos(a),projection+r*math.sin(a),z),(x+r*math.cos(b),projection+r*math.sin(b),z),(x+R*math.cos(b),projection+R*math.sin(b),Z),(x+R*math.cos(a),projection+R*math.sin(a),Z)],cage=.07)
        s.box('column head '+str(col),(x-.11,projection-.11,4.19),(x+.11,projection+.11,4.37),omit=('bottom',),cage=.04)
    # Identical painted columns share one metric prototype and one atlas set.
    # Bilinear footprint registration is for walls, not a reason to give each
    # iron column a microscopically different radial deformation.
    templates={};origin=world((.25,projection,0))
    for face in s.result['canopy']:
        tokens=face['name'].split();col=int(tokens[2] if tokens[1]=='head' else tokens[1])
        key='head '+tokens[-1] if tokens[1]=='head' else 'ring '+' '.join(tokens[2:])
        if col==0:
            templates[key]=[tuple(round(v*32768)/32768 for v in p) for p in face['vertices']]
            face['vertices']=templates[key]
        else:
            centre=world((.25+col*(W-.5)/7,projection,0));delta=[round((centre[j]-origin[j])*32768)/32768 for j in range(3)]
            face['vertices']=[tuple(p[j]+delta[j] for j in range(3)) for p in templates[key]]
        face['atlas_key']='column '+key
    for z in (4.34,4.79):s.box('front beam '+str(z),(0,projection-.0475,z-.04),(W,projection+.0475,z+.04),omit=('left','right'),cage=.04,weight=.08)
    # Keep eight real rafters, spaced by the original indices; coarse triangular
    # tubes project onto their source six-sided tubes without introducing a lid.
    from mathutils import Vector
    for idx in (0,7,14,21,28,35,42,48):
        x=idx*W/48;A=Vector((x,.05,5.36));B=Vector((x,projection+.05,4.84));t=(B-A).normalized();u=Vector((1,0,0));v=t.cross(u)
        for k in range(4):
            a=math.tau*k/4;b=math.tau*(k+1)/4
            P=(u*math.cos(a)+v*math.sin(a))*.025;Q=(u*math.cos(b)+v*math.sin(b))*.025
            s.quad('rafter '+str(idx)+' '+str(k),[A+P,A+Q,B+Q,B+P],cage=.02,weight=.2)
    return s.result
