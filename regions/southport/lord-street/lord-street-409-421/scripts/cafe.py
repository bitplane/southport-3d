"""409–411 Lord Street: gabled cafe frontage, not part of Masonic's four axes."""
import math
from mathutils import Matrix
from southport3d.geometry import face_matrix, text_object, Mesh
from shapes import rect

def build_cafe(g):
 bpy=g['bpy'];D=g['D'];c=D['cafe'];w=c['width'];cx=w/2
 wall,plane,box,tube,window,mat,finish=[g[n]for n in ['wall','plane','box','tube','window','mat','finish']]
 brick,white,lead,glass,iron=[g[n]for n in ['brick','white','lead','glass','iron']]
 trim=mat('Cafe weathered stone',(.27,.29,.22));panel=mat('Cafe pale bay panels',(.72,.73,.68));shop=mat('Cafe charcoal joinery',(.045,.055,.05))
 a=(w-c['bay_width'])/2;b=w-a;p=c['projection'];lo,hi=4.45,11.65
 wall('cafe front',rect(0,4.34,w,D['front_eaves']),[rect(a,lo,b,hi)],brick)
 wall('cafe gable parapet',[(0,12),(w,12),(w,12.35),(w/2,14.4),(0,12.35)],[],brick)
 # The solid gable skirt closes the space between its coping and pitched roof.
 tube('Cafe gable coping',[(0,-.08,12.35),(cx,-.08,14.48),(w,-.08,12.35)],.075,trim,'front',None,n=8)
 M=face_matrix((0,-p,0),(0,-1,0));holes=[rect(a+.08,z,b-.08,z+h)for z,h in [(4.75,2.55),(9.0,2.43)]]
 wall('cafe bay face',rect(a,lo,b,hi),holes,panel,'front',M)
 for i,(z,h)in enumerate([(4.75,2.55),(9.0,2.43)]):window('shop first cafe '+str(i),cx,z,b-a-.16,h,M,'front',out=.205,divide=3)
 for x,rev in [(a,True),(b,False)]:
  pp=[(x,0,lo),(x,-p,lo),(x,-p,hi),(x,0,hi)];plane('Cafe bay return',pp[::-1]if rev else pp,panel,'front',None)
 plane('Cafe bay soffit',[(a,0,lo),(b,0,lo),(b,-p,lo),(a,-p,lo)],panel,'front',None)
 plane('Cafe bay cap',[(a,-p,hi),(b,-p,hi),(b,0,hi),(a,0,hi)],lead,'front',None)
 # Narrow moulded top and bottom lips; a large pale spandrel separates floors.
 for z in [4.56,7.45,8.87,11.60]:box('Cafe bay lip',(cx,-p-.04,z),(b-a+.12,.10,.09),white,'front',None)
 box('Cafe bay roof cornice',(cx,-p/2,11.78),(b-a+.30,p+.24,.16),trim,'front',None)
 for x in [.14,w-.14]:
  box('Trim cafe brick pier',(x,8.17,.055),(.28,7.66,.11),brick)
  for z in [4.52,8.15,11.9]:box('Trim cafe pier stone tie',(x,z,.10),(.29,.14,.20),trim)
 for z in [8.15,11.95]:
  for left,right in [(.30,a-.01),(b+.01,w-.30)]:box('Trim cafe short course',((left+right)/2,z,.08),(right-left,.10,.16),trim)
 # Arc and round boss visible in the small gable. Fine carving remains unresolved.
 pts=[(cx+.48*math.cos(t),-.07,12.95+.48*math.sin(t))for t in [i*math.pi/24 for i in range(25)]]
 tube('Cafe gable blind arch',pts,.045,trim,'front',None,n=8)
 m=Mesh('Cafe gable boss');m.lathe((0,0),[(0,.15),(.045,.17),(.075,.12)],20)
 finish(m,'front',trim,face_matrix((cx,-.06,13.0),(0,-1,0)))
 # Ground shop: tall display to the left, recessed glazed entrance to the right.
 box('Cafe fascia',(cx,3.37,.03),(w-.18,.50,.24),shop)
 wall('cafe shop top',rect(.12,3.62,w-.12,4.34),[],brick)
 for left,right in [(.13,2.55),(3.75,w-.13)]:
  box('Cafe plinth',((left+right)/2,.20,-.02),(right-left,.40,.20),shop)
  window('shop cafe display',(left+right)/2,.40,right-left,2.72,out=-.10,material=shop,divide=max(1,round((right-left)/.9)))
 window('door cafe',3.15,0,1.2,3.12,out=-.38,material=shop,divide=2)
 for x,rev in [(2.55,False),(3.75,True)]:
  pp=[(x,0,0),(x,3.12,0),(x,3.12,-.42),(x,0,-.42)]
  plane('Cafe door return',pp[::-1] if rev else pp,shop)
 for x in [.06,w-.06]:box('Trim cafe shop pier',(x,2.12,.01),(.12,4.24,.2),brick)
 plane('Cafe threshold',[(2.55,0,0),(3.75,0,0),(3.75,.55,0),(2.55,.55,0)],g['stone'],'front',None)
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
 ob=text_object('Cafe shop lettering','CAFFE DOLCE',(cx,3.36,.16),(0,0,1),.23,w-.45,font,g['cream'],collection=g['C']['front'])
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.data.transform(g['T']@g['F']@ob.matrix_world);ob.matrix_world=Matrix.Identity(4);ob.select_set(False)
 for x in [.06,w-.06]:tube('Cafe rainwater pipe',[(x,-.18,4.35),(x,-.18,12.05)],.032,iron,'front',None,n=8)
