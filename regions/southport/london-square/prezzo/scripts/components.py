"""Prezzo's local XY elevation components; positive Z points out of the facade."""
import math,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))/'lib'))
from southport3d.geometry import Mesh


def window(width,height,level='detail',name='Window'):
    m=Mesh(name);w=width/2;h=height/2
    m.box((0,-.06,-.16),(width+.27,height+.12,.02),0)
    # Complete receiving glass plane and thick outer frame, with recessed sash.
    m.box((0,0,-.10),(width,height,.025),2)
    for x in [-w+.065,w-.065]:m.box((x,0,.015),(.13,height,.17),1)
    for y in [-h+.065,h-.065]:m.box((0,y,.015),(width,.13,.17),1)
    m.box((0,-h-.06,.05),(width+.27,.13,.10),0)
    for x in [-w+.15,w-.15]:m.box((x,0,-.035),(.045,height-.2,.07),1)
    if width>2.2 and height>3:
        # Tall restaurant panes, narrow side lights and a high transom.
        m.box((0,h-.65,-.005),(width-.22,.07,.10),1)
        for x in [-width*.32,width*.32]:m.box((x,0,-.005),(.055,height-.22,.10),1)
    else:
        m.box((0,0,-.005),(width-.22,.07,.10),1)
        m.box((0,0,-.005),(.055,height-.22,.10),1)
        if level=='detail':
            for x in [-width/6,width/6]:m.box((x,0,-.025),(.025,height-.23,.05),1)
            for y in [-height/4,height/4]:m.box((0,y,-.025),(width-.23,.025,.05),1)
    return m


def pilaster(level='detail',name='Pilaster'):
    m=Mesh(name);fine=level=='detail';n=20 if fine else 10 if level=='walk' else 6
    m.box((0,1.95,.10),(.40,3.65,.24),0)
    for y,w,h,d in [(.10,.65,.20,.38),(.24,.55,.08,.32),(3.73,.53,.12,.34),(3.95,.74,.15,.38),(4.08,.78,.09,.42)]:m.box((0,y,d/2),(w,h,d),0)
    if level!='district':
        for side in [-1,1]:
            pts=[]
            for i in range(n+1):
                a=i*math.tau*1.4/n;r=.11*(1-i/(n+1))
                pts.append((side*.25+r*math.cos(a),3.88+r*math.sin(a),.29))
            m.tube(pts,.021,0,6 if fine else 4)
    if fine:
        for x in [-.15,-.075,0,.075,.15]:m.box((x,1.93,.235),(.023,3.35,.025),0)
    return m


def build_lod(name,settings,asset_dir):
    if settings['kind']=='window':return window(settings['width'],settings['height'],settings['level'],name).finish([])
    return pilaster(settings['level'],name).finish([])
