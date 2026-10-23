"""Fixed-topology BHF envelope. Dimensions come from the reviewed layout, not meshes.

Faces at part interfaces intentionally have no hidden backing. No Boolean,
decimation or source-detail-dependent topology is used.
"""
import json


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    r=json.loads((asset/'research/roof-layout.json').read_text())
    result={p:[] for p in ('architecture','roof','shopfront')}
    x0,x1,y0,y1,z=[d[k] for k in ('x_far','x_near','rear_y','front_y','base_z')]
    deck=z+d['roof_level']+.10
    def face(part,label,points,weight=1):
        result[part].append({'name':label,'vertices':points,'weight':weight})
    def box(part,label,a,b,omit=(),weight=1):
        x,y,h=a;X,Y,H=b
        v=[(x,y,h),(X,y,h),(X,Y,h),(x,Y,h),(x,y,H),(X,y,H),(X,Y,H),(x,Y,H)]
        for name,ids in [('bottom',(0,3,2,1)),('rear',(0,1,5,4)),('right',(1,2,6,5)),('front',(2,3,7,6)),('left',(3,0,4,7)),('top',(4,5,6,7))]:
            if name not in omit:face(part,label+' '+name,[v[i] for i in ids],weight)
    # Front receives the entire thirteen-module grid, fascia lettering and cladding.
    # Lettering belongs to shopfront in the source but is projected onto this face.
    face('architecture','upper front',[(x1,y1,z+4.35),(x0,y1,z+4.35),(x0,y1,z+d['parapet_top']+.13),(x1,y1,z+d['parapet_top']+.13)],2)
    face('architecture','front coping',[(x0,y1,z+d['parapet_top']+.13),(x0,y1-.45,z+d['parapet_top']+.13),(x1,y1-.45,z+d['parapet_top']+.13),(x1,y1,z+d['parapet_top']+.13)])
    face('architecture','front back',[(x0,y1-.45,deck),(x1,y1-.45,deck),(x1,y1-.45,z+d['parapet_top']+.13),(x0,y1-.45,z+d['parapet_top']+.13)])
    # Exposed lateral/rear surfaces; narrow front returns close the cladding band.
    for x,rev in [(x0,False),(x1,True)]:
        v=[(x,y0,z),(x,y1,z),(x,y1,deck),(x,y0,deck)]
        face('architecture','side wall '+str(x),list(reversed(v)) if not rev else v)
        v=[(x,y1-.45,deck),(x,y1,deck),(x,y1,z+d['parapet_top']+.13),(x,y1-.45,z+d['parapet_top']+.13)]
        face('architecture','front return '+str(x),list(reversed(v)) if not rev else v)
    face('architecture','rear wall',[(x0,y0,z),(x1,y0,z),(x1,y0,deck),(x0,y0,deck)])
    # Utility enclosure projects into the court. Shafts above the roof remain masses.
    box('architecture','court utility',(x1,y0+4,z),(x1+1.5,y0+12.4,z+2.8),omit=('bottom','left'))
    # Roof deck retains its actual recess, rather than painting over the opening.
    cx,cy=r['walled_recess']['centre'];w,h=r['walled_recess']['size'];a,b=cx-w/2,cx+w/2;c,e=cy-h/2,cy+h/2
    for i,(xl,xr,ya,yb) in enumerate([(x0,a,y0,y1-.45),(b,x1,y0,y1-.45),(a,b,y0,c),(a,b,e,y1-.45)]):
        face('roof','deck '+str(i),[(xl,ya,deck),(xr,ya,deck),(xr,yb,deck),(xl,yb,deck)])
    floor=z+d['roof_level']+r['walled_recess']['floor_relative']
    face('roof','recess floor',[(a,c,floor),(b,c,floor),(b,e,floor),(a,e,floor)])
    for i,(xl,xr,ya,yb,top) in enumerate([(a,b,c,c+.22,deck+.85),(b-.22,b,c+.22,e,deck+.85),(a,a+.18,c+.22,e,deck+.02),(a+.18,b-.22,e-.18,e,deck+.02)]):
        box('roof','recess wall '+str(i),(xl,ya,floor),(xr,yb,top),omit=('bottom',))
    for i,wall in enumerate(r['parapets']):
        xa,ya=wall['a'];xb,yb=wall['b'];t=wall['thickness']/2
        box('roof','parapet '+str(i),(min(xa,xb)-(t if xa==xb else 0),min(ya,yb)-(t if ya==yb else 0),deck),(max(xa,xb)+(t if xa==xb else 0),max(ya,yb)+(t if ya==yb else 0),z+wall['top']+.09),omit=('bottom',))
    for i,housing in enumerate(r['edge_housings']):
        x,y=housing['centre'];w,h=housing['size']
        box('roof','housing '+str(i),(x-w/2,y-h/2,deck),(x+w/2,y+h/2,z+d['roof_level']+housing['height']+.12),omit=('bottom',))
    px,py=r['plant']['centre'];pw,pd=r['plant']['size'];base=z+d['roof_level']
    box('roof','plant platform',(px-pw/2,py-pd/2,deck),(px+pw/2,py+pd/2,base+.24),omit=('bottom',))
    box('roof','main cabinet',(px+1.85-.89,py-2.495,base+.24),(px+1.85+.89,py+2.495,base+1.68),omit=('bottom',))
    # Four separate condensers become one shallow bank; fans are texture detail.
    box('roof','condenser bank',(px-.675,py-2.85,base+.24),(px+.375,py+2.85,base+1.08),omit=('bottom',))
    lx,ly=r['low_rooflight']['centre'];lw,lh=r['low_rooflight']['size']
    box('roof','low rooflight',(lx-lw/2,ly-lh/2,deck),(lx+lw/2,ly+lh/2,base+.54),omit=('bottom',))
    # Frontage follows the major recesses/facets, not every frame or glazed pier.
    path=[(0,0),(.46,0),(.46,-.30),(5.65,-.30),(5.85,-.95),(7.60,-.95),(7.85,0),(8.45,0),(8.70,.25),(10.25,.25),(d['entry_left'],-d['entry_depth']),(d['entry_right'],-d['entry_depth']),(15,.25),(16,.25),(16.25,0),(16.85,0),(17.15,-.32),(x1-x0-.46,-.32),(x1-x0-.46,0),(x1-x0,0)]
    for i,((u,o),(v,p)) in enumerate(zip(path,path[1:])):
        face('shopfront','display '+str(i),[(x1-u,y1+o,z),(x1-v,y1+p,z),(x1-v,y1+p,z+4.35),(x1-u,y1+o,z+4.35)],2)
    # Main recessed ceilings close the soffits. Tiny triangular end returns
    # have no separate allocation; neighbouring faces meet at the facade line.
    for i,((u,o),(v,p)) in enumerate(zip(path,path[1:])):
        if u==v or o>=0 or p>=0:continue
        face('shopfront','soffit '+str(i),[(x1-u,y1,z+4.35),(x1-v,y1,z+4.35),(x1-v,y1+p,z+4.35),(x1-u,y1+o,z+4.35)])
    # Simplified access surfaces preserve silhouette; railings bake/omit at distance.
    def frontbox(label,u,v,o,p,b,t):
        box('shopfront',label,(x1-v,y1+o,z+b),(x1-u,y1+p,z+t),omit=('bottom','rear'),weight=1)
    frontbox('central step',10.25,15,.5,1,0,.18)
    frontbox('central landing',10.25,15,-1.35,.5,0,.36)
    frontbox('right apron',16.85,x1-x0-.46,.46,1,0,.18)
    frontbox('right landing',16.85,x1-x0-.46,-.43,.46,0,.36)
    frontbox('left landing',6.2,7.8,-.95,1.45,0,.36)
    u,v=.8,6.2;o,p=-.25,1.45
    face('shopfront','ramp',[(x1-u,y1+o,z+.045),(x1-u,y1+p,z+.045),(x1-v,y1+p,z+.36),(x1-v,y1+o,z+.36)])
    face('shopfront','ramp cheek',[(x1-v,y1+p,z),(x1-u,y1+p,z),(x1-u,y1+p,z+.225),(x1-v,y1+p,z+.54)])
    return result
