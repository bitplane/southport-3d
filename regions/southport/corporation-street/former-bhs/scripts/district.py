"""Independent fixed-budget District silhouette for revised BHS composition.

It shares authored dimensions with the master but never derives topology from
ornament. Major open gallery recesses, curved bay projections, gable roofs and
cut dormers remain geometry; smaller window and stone detail is baked.
"""
import json,math,sys
from blender_envelope import Surfaces

def surfaces(asset):
 sys.path.insert(0,str(asset.parents[3]/'lib'))
 from components import cut,rect
 d=json.loads((asset/'research/layout.json').read_text());schedule=json.loads((asset/'research/elevation-schedule.json').read_text());X,Y,Z=d['origin'];W=d['width'];L=d['length'];F=d['front_depth'];A=d['arcade_wing_width'];B=W-d['corp_range_width'];E=d['wing_eave'];R=d['wing_ridge'];Q=d['range_eave'];S=d['range_ridge']
 def world(p):
  u,v,z=p;t=v/L;q=u/W
  return (X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q),Z+z)
 s=Surfaces(['frontage','rear','roof'],world)
 def quad(n,a,b,z0,z1):s.quad(n,[(*a,z0),(*b,z0),(*b,z1),(*a,z1)])
 def polygon(n,p,fn):
  p=list(p);changed=True
  while changed and len(p)>3:
   changed=False
   for i in range(len(p)):
    a,b,c=p[i-1],p[i],p[(i+1)%len(p)]
    if abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))<1e-7:
     del p[i];changed=True;break
  if len(p)==3:
   a,b,c=p
   if abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))<1e-7:return
   s.triangle(n,[fn(*x)for x in p])
  elif len(p)==4:s.quad(n,[fn(*x)for x in p])
  else:
   for i in range(1,len(p)-1):s.triangle(n+' '+str(i),[fn(*x)for x in (p[0],p[i],p[i+1])])
 def curved(n,cx,cy,r,t0,t1):
  N=8
  for i in range(N):
   a=t0+(t1-t0)*i/N;b=t0+(t1-t0)*(i+1)/N
   quad(n+' '+str(i),(cx+r*math.cos(a),cy+r*math.sin(a)),(cx+r*math.cos(b),cy+r*math.sin(b)),4.2,12.35)
 def repeated_boxes(name,boxes,key,cage):
  # Authored metric prototype copied by translation so repeated columns share
  # one atlas island per side; float32 congruence remains below 1 mm here.
  reference=None;anchor=None
  for lo,hi in boxes:
   centre=tuple(round(x*4096)/4096 for x in world(tuple((lo[i]+hi[i])/2 for i in range(3))))
   s.box(name,lo,hi,cage=cage);items=s.result[s.part][-5:]
   if reference is None:
    reference=[[tuple(round(x*4096)/4096 for x in p)for p in f['vertices']]for f in items];anchor=centre
    for f,points in zip(items,reference):f['vertices']=points
   else:
    delta=[centre[i]-anchor[i]for i in range(3)]
    for f,points in zip(items,reference):f['vertices']=[tuple(p[i]+delta[i]for i in range(3))for p in points]
   for j,f in enumerate(items):
    f['atlas_key']=key+'-'+str(j);f['weight']=3.0
 def arch_cut(u,bottom,spring,r):
  return [(u-r,bottom),(u+r,bottom)]+[(u+r*math.cos(math.pi*i/6),spring+r*math.sin(math.pi*i/6))for i in range(7)]
 s.part='frontage'
 # Explicit facade bands avoid inheriting the detailed mesh's fragmented
 # window triangulation. The same fixed 6-segment arch profile is used for
 # both the wall above each opening and the inset glazing.
 def panel(name,a,b,z0,z1,axis,fixed):
  if b-a<1e-6 or z1-z0<1e-6:return
  if axis=='x':quad(name,(a,fixed),(b,fixed),z0,z1)
  else:quad(name,(fixed,a),(fixed,b),z0,z1)
 def facade_bands(name,start,end,centres,r,axis,fixed):
  panel(name+' base',start,end,0,4.2,axis,fixed)
  edges=[(max(start,u-r),min(end,u+r),u)for u in centres if u+r>start and u-r<end]
  last=start
  for a,b,u in edges:
   panel(name+' lower pier',last,a,4.2,7,axis,fixed)
   panel(name+' upper pier',last,a,7,8.55,axis,fixed)
   # Six vertical segments trace the semicircular reveal. Wall and glass
   # are authored independently of source ornament but share the same profile.
   cuts=[a+(b-a)*i/6 for i in range(7)]
   def point(q,z):return (q,fixed,z) if axis=='x' else (fixed,q,z)
   def inset(q,z):return (q,fixed+.18,z) if axis=='x' else (fixed-.18,q,z)
   s.quad(name+' glass lower',[inset(a,4.2),inset(b,4.2),inset(b,7),inset(a,7)])
   for i in range(6):
    x0,x1=cuts[i:i+2];z0=7+math.sqrt(max(0,r*r-(x0-u)**2));z1=7+math.sqrt(max(0,r*r-(x1-u)**2))
    s.quad(name+' arch wall',[point(x0,z0),point(x1,z1),point(x1,8.55),point(x0,8.55)])
    poly=[inset(x0,7),inset(x1,7),inset(x1,z1),inset(x0,z0)]
    if abs(z0-7)<1e-6:s.triangle(name+' arch glass',[poly[0],poly[1],poly[2]])
    elif abs(z1-7)<1e-6:s.triangle(name+' arch glass',[poly[0],poly[1],poly[3]])
    else:s.quad(name+' arch glass',poly)
   last=b
  panel(name+' lower end',last,end,4.2,7,axis,fixed)
  panel(name+' upper end',last,end,7,8.55,axis,fixed)
 # Plain Chapel range, including the original paired window field, bakes on a
 # fixed wall. The two major arches and both projecting bays remain geometry.
 panel('Plain Chapel',0,14.05,0,12.8,'x',0)
 panel('Chapel base bay A',14.05,17.0,0,4.2,'x',0)
 facade_bands('Ornate Chapel',17.0,26.9,[19.1,22.8],1.2,'x',0)
 panel('Corner base',26.9,W,0,4.2,'x',0)
 panel('Chapel top',14.05,W,12.35,12.8,'x',0)
 facade_bands('Corporation',0,F,[3.4,6.8,10.2,13.6,17,20],1.05,'y',W)
 panel('Return top',0,F,12.35,12.8,'y',W)
 curved('inner curved bay',15.5,0,1.45,math.pi,math.tau)
 curved('corner curved bay',W-1.4,1.4,1.9,-math.pi/2,0)
 quad('Corner front return',(W-1.4,-.5),(W-1.4,0),4.2,12.35)
 quad('Corner side return',(W+.5,1.4),(W,1.4),4.2,12.35)
 quad('Gallery rear Chapel',(17,1.25),(26.9,1.25),8.55,12.35)
 s.quad('Gallery floor Chapel',[(17,.18,8.55),(26.9,.18,8.55),(26.9,1.25,8.55),(17,1.25,8.55)])
 s.quad('Gallery soffit Chapel',[(17,1.25,12.35),(26.9,1.25,12.35),(26.9,.18,12.35),(17,.18,12.35)])
 quad('Gallery rear return',(W-1.25,1.45),(W-1.25,F),8.55,12.35)
 s.quad('Gallery floor return',[(W-1.25,1.45,8.55),(W-.18,1.45,8.55),(W-.18,F,8.55),(W-1.25,F,8.55)])
 s.quad('Gallery soffit return',[(W-1.25,F,12.35),(W-.18,F,12.35),(W-.18,1.45,12.35),(W-1.25,1.45,12.35)])
 repeated_boxes('Gallery column',[((u-.13,-.11,8.55),(u+.13,.15,12.18))for u in [17.3,19.0,20.7,22.4,24.1,25.8]],'chapel-column',.5)
 repeated_boxes('Return gallery column',[((W-.15,v-.13,8.55),(W+.11,v+.13,12.18))for v in [1.7,4.9,8.1,11.3,14.5,17.7,20.4]],'return-column',.5)
 quad('Corporation low frontage',(W,F),(W,L),0,Q)
 s.quad('Canopy top',[(0,-3,3.93),(W,-3,3.93),(W,-.12,3.93),(0,-.12,3.93)])
 s.quad('Canopy underside',[(0,-.12,3.72),(W,-.12,3.72),(W,-3,3.72),(0,-3,3.72)])
 quad('Canopy fascia',(0,-3),(W,-3),3.72,3.93)
 repeated_boxes('Canopy post',[((u-.045,-2.75,0),(u+.045,-2.66,3.72))for u in [1,8,15,22,27.5]],'canopy-post',.25)
 s.part='rear'
 quad('Arcade wall',(0,F),(0,L),0,E);quad('Court wall',(A,L),(A,F),0,E);quad('Wing end',(0,L),(A,L),0,E);quad('Low court',(B,L),(B,F),0,Q);quad('Low end',(B,L),(W,L),0,Q);quad('Chapel rear',(0,F),(W,F),0,12.8);quad('Chapel arcade return',(0,F),(0,0),0,12.8)
 s.triangle('Wing gable',[(0,L,E),(A,L,E),(A/2,L,R)])
 cx,cy,r=A+2.1,F+1.5,1.8
 for i in range(8):
  t=math.tau*i/8;u=math.tau*(i+1)/8;quad('Tower '+str(i),(cx+r*math.cos(t),cy+r*math.sin(t)),(cx+r*math.cos(u),cy+r*math.sin(u)),0,16.4)
 s.part='roof'
 fronts=schedule['dormers']['chapel'];sides=schedule['dormers']['corporation']
 profile=[(0,0),(W,0),(W-2.3,3),(2.3,3)];openings=[rect(u-w/2,.7,u+w/2,2.95)for u,w,k in fronts]
 for i,p in enumerate(cut(profile,openings)):polygon('Chapel roof '+str(i),p,lambda u,v:(u,v,12.8+3.7*v/3))
 profile=[(0,0),(F,0),(F,2.3),(3,2.3)];openings=[rect(v-w/2,.65,v+w/2,2.25)for v,w,k in sides]
 for i,p in enumerate(cut(profile,openings)):polygon('Return roof '+str(i),p,lambda v,q:(W-q,v,12.8+3.7*q/2.3))
 s.quad('Arcade roof slope',[(0,F,12.8),(0,0,12.8),(2.3,3,16.5),(2.3,F,16.5)])
 s.quad('Chapel roof flat',[(2.3,3,16.5),(W-2.3,3,16.5),(W-2.3,F,16.5),(2.3,F,16.5)])
 for u,w,k in fronts:
  x0,x1=u-w/2,u+w/2;v0,v1=.7,2.95;z0=12.8+3.7*v0/3;z1=12.8+3.7*v1/3;top=16.75
  s.quad('Chapel dormer face',[(x0,v0,z0),(x1,v0,z0),(x1,v0,top),(x0,v0,top)],cage=.6)
  s.quad('Chapel dormer left',[(x0,v1,z1),(x0,v0,z0),(x0,v0,top),(x0,v1,top)],weight=2.5,cage=.6)
  s.quad('Chapel dormer right',[(x1,v0,z0),(x1,v1,z1),(x1,v1,top),(x1,v0,top)],weight=2.5,cage=.6)
  s.quad('Chapel dormer cap',[(x0,v0,top),(x1,v0,top),(x1,v1,top),(x0,v1,top)],cage=.6)
 for v,w,k in sides:
  y0,y1=v-w/2,v+w/2;d0,d1=.65,2.25;z0=12.8+3.7*d0/2.3;z1=12.8+3.7*d1/2.3;top=16.75
  s.quad('Return dormer face',[(W-d0,y0,z0),(W-d0,y1,z0),(W-d0,y1,top),(W-d0,y0,top)],cage=.6)
  s.quad('Return dormer left',[(W-d1,y0,z1),(W-d0,y0,z0),(W-d0,y0,top),(W-d1,y0,top)],weight=2.5,cage=.6)
  s.quad('Return dormer right',[(W-d0,y1,z0),(W-d1,y1,z1),(W-d1,y1,top),(W-d0,y1,top)],weight=2.5,cage=.6)
  s.quad('Return dormer cap',[(W-d1,y0,top),(W-d0,y0,top),(W-d0,y1,top),(W-d1,y1,top)],cage=.6)
 s.quad('Wing slope west',[(0,F,E),(A/2,F,R),(A/2,L,R),(0,L,E)]);s.quad('Wing slope east',[(A/2,F,R),(A,F,E),(A,L,E),(A/2,L,R)])
 for i in range(5):
  y0=F+(L-F)*i/5;y1=F+(L-F)*(i+1)/5;ym=(y0+y1)/2
  s.quad('Gable slope A '+str(i),[(B,y0,Q),(W,y0,Q),(W,ym,S),(B,ym,S)]);s.quad('Gable slope B '+str(i),[(B,ym,S),(W,ym,S),(W,y1,Q),(B,y1,Q)])
  s.part='frontage';s.triangle('Gable face '+str(i),[(W,y0,Q),(W,y1,Q),(W,ym,S)])
  s.part='rear';s.triangle('Court gable '+str(i),[(B,y1,Q),(B,y0,Q),(B,ym,S)])
  s.part='roof'
 return s.result
