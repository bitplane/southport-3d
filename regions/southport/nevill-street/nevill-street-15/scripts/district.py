"""Fixed envelope: budgets do not depend on shop ornament or slate detail."""
import json,math
from blender_envelope import Surfaces
from plan import world,roofs

def surfaces(asset):
 d=json.loads((asset/'research/layout.json').read_text());w=d['width'];l=d['depth'];m=d['main_depth'];e=d['eave'];r=d['ridge_v'];a=d['wing_width'];b=d['wing_depth'];s=Surfaces(['frontage','rear','roof'],lambda p:world(d,p))
 s.part='frontage';s.quad('whole front',[(0,0,-.25),(w,0,-.25),(w,0,e),(0,0,e)],weight=2)
 for aa,bb in [(4.65,8.9),(8.94,w)]:
  s.quad('canopy',[(aa,-1.13,2.57),(bb,-1.13,2.57),(bb,-.22,2.84),(aa,-.22,2.84)])
  s.quad('valance',[(aa,-1.13,2.39),(bb,-1.13,2.39),(bb,-1.13,2.57),(aa,-1.13,2.57)])
 for i in range(3):
  aa=-math.pi/2+i*math.pi/6;bb=aa+math.pi/6;A=(w+1.13*math.cos(aa),1.13*math.sin(aa));B=(w+1.13*math.cos(bb),1.13*math.sin(bb))
  s.quad('corner canopy',[(*A,2.57),(*B,2.57),(w+.22*math.cos(bb),.22*math.sin(bb),2.84),(w+.22*math.cos(aa),.22*math.sin(aa),2.84)])
  s.quad('corner valance',[(*A,2.39),(*B,2.39),(*B,2.57),(*A,2.57)])
 s.part='rear';s.quad('Cable main',[(w,0,-.25),(w,m,-.25),(w,m,e),(w,0,e)],weight=2);s.triangle('Cable gable',[(w,0,e),(w,m,e),(w,r,d['ridge'])])
 s.quad('Cable lean-to',[(w,m,-.25),(w,l,-.25),(w,l,4.02),(w,m,4.77)])
 s.quad('Cable canopy',[(w+1.13,0,2.57),(w+1.13,m,2.57),(w+.22,m,2.84),(w+.22,0,2.84)])
 s.quad('Cable valance',[(w+1.13,0,2.39),(w+1.13,m,2.39),(w+1.13,m,2.57),(w+1.13,0,2.57)])
 s.quad('south main',[(0,m,-.25),(0,0,-.25),(0,0,e),(0,m,e)])
 s.quad('south wing',[(0,b,-.25),(0,m,-.25),(0,m,4.77),(0,b,4.17)])
 s.triangle('south gable',[(0,m,e),(0,0,e),(0,r,d['ridge'])])
 for name,A,B,h0,h1 in [('rear',(w,l),(a,l),4.02,4.02),('wing return',(a,l),(a,b),4.77-.6*(l-m)/(b-m),4.17),('wing end',(a,b),(0,b),4.17,4.17)]:s.quad(name,[(*A,-.25),(*B,-.25),(*B,h1),(*A,h0)])
 s.quad('rear main top',[(w,m,4.85),(0,m,4.85),(0,m,e-.08),(w,m,e-.08)])
 s.part='roof'
 for name,p in roofs(d):s.quad(name,p)
 return s.result
