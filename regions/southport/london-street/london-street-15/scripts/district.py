"""Fixed Tudor silhouette, corrected clay roofs and open alley/rear terraces."""
import json,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());FX,YN,YS,RR=(d[k] for k in ('front_x','north_y','south_y','rear_x'));W=YN-YS;bay=d['bay_width'];uc=d['gable_centre'];shop=d['shop_top'];e=d['tie_beam']+.25;r=d['ridge_height'];zl,zr=d['jetty_left'],d['jetty_right'];bottom=d['bury_z']-d['base_z']
    rf=FX-zl-.35-d['gable_projection'];rb=rf+d['main_roof_depth'];RX=rb-.12;nb=rb-d['main_rear_skew'];ridgeback=rb-d['main_hip_run'];northback=FX-.45+d['north_roof_depth'];yn,ys,yr=YN-bay+.3,YS-.3,YN-uc
    s=Surfaces(['architecture','roof','shopfront','rear'],lambda p:(p[0],p[1],p[2]+d['base_z']))
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    def polygon(name,points):
        v=list(map(Vector,points))
        for i,t in enumerate(tessellate_polygon([v])):s.triangle(name+' '+str(i),[v[k] if isinstance(k,int) else k for k in t])
    a,b=d['cant'];c,C=d['centre_panel'];zc=d['jetty_centre']
    path=[(FX-.2,YN),(FX-.2,YN-bay),(FX-zl,YN-bay),(FX-zl,YN-a),(FX-zc,YN-c),(FX-zc,YN-C),(FX-zr,YN-b),(FX-zr,YS),(FX,YS)]
    for i,(A,B) in enumerate(zip(path,path[1:])):wall('jettied facade '+str(i),A,B,shop,e)
    wall('north jetty return',(FX,YN),(FX-.2,YN),shop,e)
    wall('alley side',(FX,YS),(RX,YS),bottom,e+.1)
    pitch=(r-e)/((W-bay)/2+.3);half=(r-.14-e)/pitch
    s.triangle('gable',[(FX-zl-d['gable_projection'],YN-(uc-half),e),(FX-zl-d['gable_projection'],YN-(uc+half),e),(FX-zl-d['gable_projection'],YN-uc,r-.14)])
    wall('north attic front',(FX-.2,YN),(FX-.2,YN-bay),e,d['bay_eaves'])
    wall('north attic side',(FX-.2,YN-bay),(northback,YN-bay),e,d['bay_eaves']-.12)
    be,br=d['bay_eaves'],d['bay_ridge'];xf=FX-.45
    s.quad('short north rear',[(northback,YN-bay,bottom),(northback,YN,bottom),(northback,YN,br-.12),(northback,YN-bay,be-.12)])
    # Party wall steps around the deep entrance; no filled porch volume.
    endheight=be+(br-be)*(FX-xf)/.85-.12
    polygon('short north party',[(northback-.2,YN,bottom),(FX+1.5,YN,bottom),(FX+1.5,YN,shop),(FX,YN,shop),(FX,YN,endheight),(xf+.85,YN,br-.12),(northback-.2,YN,br-.12)])
    mh=d['rear_flat_height'];wh=d['rear_wing_eave'];mid=d['rear_flat_end_x'];wy=YS+d['rear_wing_width']
    # Match the skew rear hip end; lower panels are hidden by adjoining roofs.
    t=(wy-YS)/(YN-bay-YS);mx=RX+t*(nb-.12-RX)
    s.quad('rear hip lower exposed',[(RX,YS,wh),(mx,wy,mh),(mx,wy,e+.05),(RX,YS,e+.05)])
    wall('rear hip upper',(mx,wy),(nb-.12,YN-bay),mh,e+.05)
    s.part='roof'
    v=[(rf,yn,e),(rf,yr,r),(rf,ys,e),(rb,ys,e),(nb,yn,e),(ridgeback,yr,r)]
    for i,ids in enumerate([(0,1,5,4),(1,2,3,5),(3,4,5)]):
        p=[v[k] for k in ids];(s.quad if len(p)==4 else s.triangle)('main clay '+str(i),p)
    # The entrance range is a lean-to with a front hip, not a central ridge.
    v=[(xf,YN-bay,be),(northback,YN-bay,be),(northback,YN-.02,br),(xf+.85,YN-.02,br),(xf,YN-.02,be)]
    s.quad('north lean-to',[v[k] for k in (0,1,2,3)]);s.triangle('north front hip',[v[k] for k in (0,3,4)])
    s.part='shopfront'
    wall('arched shop',(FX,YN-bay),(FX,YS),bottom,shop)
    wall('entrance left pier',(FX,YN),(FX,YN-.1),bottom,shop)
    wall('entrance right pier',(FX,YN-bay+.1),(FX,YN-bay),bottom,shop)
    wall('entrance header',(FX,YN-.1),(FX,YN-bay+.1),2.9,shop)
    wall('entrance back',(FX+1.4,YN-.1),(FX+1.4,YN-bay+.1),bottom,2.9)
    for y in (YN-.1,YN-bay+.1):wall('porch jamb '+str(y),(FX,y),(FX+1.4,y),bottom,2.9)
    s.quad('porch soffit',[(FX,YN-.1,2.9),(FX,YN-bay+.1,2.9),(FX+1.4,YN-bay+.1,2.9),(FX+1.4,YN-.1,2.9)])
    s.quad('porch threshold',[(FX,YN-bay+.1,.05),(FX+1.4,YN-bay+.1,.05),(FX+1.4,YN-.1,.05),(FX,YN-.1,.05)])
    s.part='rear';step=d['rear_grey_step_x'];gh=d['rear_grey_height'];uh=d['rear_upper_height']
    wall('white north',(mid,YN),(northback,YN),bottom,mh)
    wall('white end',(mid,wy),(mid,YN),gh,mh)
    polygon('white deck',[(northback,YN,mh),(mid,YN,mh),(mid,wy,mh),(RX,wy,mh),(nb-.12,YN-bay,mh),(northback,YN-bay,mh)])
    s.quad('red wing roof',[(RX,YS,wh),(RX,wy,mh),(mid-.75,wy,mh),(mid,YS,wh)])
    wall('red wing alley',(RX,YS),(mid,YS),bottom,wh-.14)
    wall('grey front exposed',(mid,wy),(mid,YS),wh,gh)
    wall('grey south',(mid,YS),(RR,YS),bottom,gh)
    wall('grey north',(RR,YN),(mid,YN),bottom,gh)
    wall('rear south shoulder',(RR,YS),(RR,YS+1),bottom,gh)
    wall('rear centre',(RR,YS+1),(RR,YN-1),bottom,uh)
    wall('rear north shoulder',(RR,YN-1),(RR,YN),bottom,gh)
    wall('upper south',(step,YS+1),(RR,YS+1),gh,uh)
    wall('upper north',(RR,YN-1),(step,YN-1),gh,uh)
    wall('upper front',(step,YN-1),(step,YS+1),gh,uh)
    for name,x0,x1,y0,y1,h in [('broad',mid,step,YS,YN,gh),('high',step,RR,YS+1,YN-1,uh),('south',step,RR,YS,YS+1,gh),('north',step,RR,YN-1,YN,gh)]:
        s.quad('rear deck '+name,[(x0,y0,h),(x1,y0,h),(x1,y1,h),(x0,y1,h)])
    s.quad('alley floor',[(FX,d['alley_south_y'],-.003),(RR,d['alley_south_y'],-.003),(RR,YS,-.003),(FX,YS,-.003)])
    wall('alley gate',(RR-.25,YS),(RR-.25,d['alley_south_y']),bottom,2.2)
    return s.result
