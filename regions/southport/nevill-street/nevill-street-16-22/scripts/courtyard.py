"""Street-observed rear projection and gated boundary; local Nevill metres.

The main rear wall owns the buried attachment face. No ground is authored here.
District has a bounded set of structural surfaces independent of slat sampling.
"""
PROJECTION=(3.3,6.4,11.35,12.8,5.7)
GATE=(-.12,11.35,12.9,2.2)
WALL=(-.12,12.9,14.7,2.5)

def build(api):
 Mesh,finish,box,T,brick,wood,iron,stone,lead=api
 u0,u1,v0,v1,h=PROJECTION
 m=Mesh('Architecture courtyard projection')
 # Attached face v0 belongs to the main rear wall; front end has a real door recess.
 for p in [[(u1,v1,0),(u1,v0,0),(u1,v0,h+.16),(u1,v1,h)],[(u0,v1,0),(u1,v1,0),(u1,v1,h),(u0,v1,h)]]:m.add(p,[(0,1,2,3)])
 # Front end opening, boarded as in July2026, with masonry above and alongside.
 for a,b,lo in [(v0,v0+.12,0),(v1-.12,v1,0),(v0+.12,v1-.12,2.45)]:
  top=lambda v:h+.16*(v1-v)/(v1-v0)
  m.add([(u0,a,lo),(u0,b,lo),(u0,b,top(b)),(u0,a,top(a))],[(0,1,2,3)])
 m.faces=[tuple(reversed(f)) for f in m.faces]
 finish(m,'rear',brick,T)
 m=Mesh('Architecture courtyard projection roof');m.add([(u1,v0,h+.16),(u1,v1,h),(u0,v1,h),(u0,v0,h+.16)],[(0,1,2,3)]);finish(m,'rear',lead,T)
 box('Architecture courtyard boarded door',(u0+.035,(v0+v1)/2,1.20),(.07,v1-v0-.24,2.4),wood,'rear',T)
 for v in (v0+.16,v1-.16):box('Architecture courtyard door jamb',(u0-.02,v,1.2),(.08,.07,2.4),iron,'rear',T)
 box('Architecture courtyard door lintel',(u0-.02,(v0+v1)/2,2.49),(.08,v1-v0,.08),iron,'rear',T)
 u,a,b,h=WALL
 box('Architecture courtyard boundary', (u,(a+b)/2,h/2),(.28,b-a,h),brick,'rear',T)
 box('Architecture courtyard coping',(u,(a+b)/2,h+.045),(.36,b-a,.09),stone,'rear',T)
 u,a,b,h=GATE
 # Closed reed-screened gate retains its modest gaps and independent frame.
 for v in (a+.05,b-.05):box('Architecture courtyard gate upright',(u,v,h/2),(.09,.10,h),iron,'rear',T)
 for z in (.12,h-.06):box('Architecture courtyard gate rail',(u,(a+b)/2,z),(.09,b-a-.2,.08),iron,'rear',T)
 for j in range(22):
  v=a+.12+(b-a-.24)*(j+.5)/22
  box('Architecture courtyard gate reed',(u+.035,v,h/2),(.04,(b-a-.24)/22*.86,h-.24),wood,'rear',T)
 # The stone lintel bridges only the gate; it does not fill the open delivery lane.
 box('Architecture courtyard gate lintel',(u,(a+b)/2,h+.11),(.32,b-a,.16),stone,'rear',T)

def district(s):
 s.part='rear';u0,u1,v0,v1,h=PROJECTION
 for name,points in [('near',[(u0,v0,0),(u0,v0,h+.16),(u0,v1,h),(u0,v1,0)]),('far',[(u1,v1,0),(u1,v1,h),(u1,v0,h+.16),(u1,v0,0)]),('outer',[(u0,v1,0),(u0,v1,h),(u1,v1,h),(u1,v1,0)])]:s.quad('courtyard projection '+name,points,cage=.20)
 s.quad('courtyard projection roof',[(u1,v0,h+.16),(u1,v1,h),(u0,v1,h),(u0,v0,h+.16)],cage=.20)
 for name,settings,thickness in [('boundary',WALL,.28),('screened gate',GATE,.09)]:
  u,a,b,h=settings;s.box('courtyard '+name,(u-thickness/2,a,0),(u+thickness/2,b,h),cage=.20)
