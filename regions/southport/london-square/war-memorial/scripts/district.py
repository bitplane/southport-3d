"""Independent, fixed-topology distant memorial: preserve volumes and open spaces.

No original mesh topology is consumed. Repeated column/lamp surfaces explicitly
share atlas islands, baked once per part at the representative instance.
"""
import json
import math


def surfaces(asset):
    spec=json.loads((asset/'research/modelling_spec.json').read_text())
    site=json.loads((asset/'research/site_layout.json').read_text())
    shaft=json.loads((asset/'research/shaft_masonry_calibration.json').read_text())['metric_envelope']
    result={p:[] for p in ('obelisk','north-east','south-west','lamps')}
    part='obelisk';transform=lambda p:p
    def face(label,vertices,key=None,weight=1):
        row={'name':label,'vertices':[transform(p) for p in vertices],'weight':weight}
        if key is not None:row['atlas_key']=key
        result[part].append(row)
    def box(label,a,b,key=None,omit=('bottom',),weight=1):
        x,y,z=a;X,Y,Z=b
        points=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
        for side,indices in [('bottom',(0,3,2,1)),('rear',(0,1,5,4)),('right',(1,2,6,5)),('front',(2,3,7,6)),('left',(3,0,4,7)),('top',(4,5,6,7))]:
            if side not in omit:face(label+' '+side,[points[i] for i in indices],key+' '+side if key else None,weight)
    def rect_profile(label,rings):
        for i,((z,w,d),(Z,W,D)) in enumerate(zip(rings,rings[1:])):
            lo=[(-w/2,-d/2,z),(w/2,-d/2,z),(w/2,d/2,z),(-w/2,d/2,z)]
            hi=[(-W/2,-D/2,Z),(W/2,-D/2,Z),(W/2,D/2,Z),(-W/2,D/2,Z)]
            for j in range(4):face(label+f' {i} {j}',[lo[j],lo[(j+1)%4],hi[(j+1)%4],hi[j]])
    def lathe(label,x,y,rings,key,n=8):
        for i,((z,r),(Z,R)) in enumerate(zip(rings,rings[1:])):
            for j in range(n):
                a=math.tau*j/n;b=math.tau*(j+1)/n
                face(label+f' {i} {j}',[(x+r*math.cos(a),y+r*math.sin(a),z),(x+r*math.cos(b),y+r*math.sin(b),z),(x+R*math.cos(b),y+R*math.sin(b),Z),(x+R*math.cos(a),y+R*math.sin(a),Z)],key+f' {i} {j}')
    # Profile steps describe the major pedestal, cornice and tapered shaft only.
    rect_profile('obelisk base',[(-.2,4.70,4.70),(.23,4.70,4.70),(.23,4.22,4.22),(.32,4.22,4.22),(.32,3.65,3.65),(1.23,3.65,3.65),(1.23,3.25,3.25),(1.64,3.25,3.25),(2.12,2.61,2.61),(2.12,2.55,2.55),(4.04,2.55,2.55),(4.04,2.56,2.56),(4.27,2.91,2.91),(4.56,2.91,2.91),(4.56,2.12,2.12),(4.78,2.12,2.12),(4.78,shaft['base_width_m'],shaft['base_width_m']),(shaft['top_z_m'],shaft['top_width_m'],shaft['top_width_m']),(spec['dimensions']['obelisk_height']['value'],.002,.002)])
    # Single-globe lamps retained as narrow poles with eight-sided globes.
    def single(x,y,label):
        box(label+' plinth',(x-.71,y-.53,-.6),(x+.71,y+.53,.35),'single plinth')
        lathe(label+' stem',x,y,[(.43,.19),(.89,.056),(2.42,.044),(2.64,.1)],'single stem')
        lathe(label+' globe',x,y,[(2.594,.004),(2.66,.15),(2.812,.21),(2.966,.15),(3.03,.004)],'single globe')
    for code,part in [('NE','north-east'),('SW','south-west')]:
        cx,cy=site['colonnades'][code]['centre_site_xy_m'];transform=lambda p:(cx-p[1],cy+p[0],p[2])
        plan=spec['colonnade_plan'];dims=spec['dimensions']['exterior_window']
        # Broad level portico steps, without per-stone cuts or bevels.
        for i,(bottom,top,depth) in enumerate([(-.6,-.04,5.90),(-.04,.14,5.38),(.14,.32,4.90)]):
            box('portico step '+str(i),(-6.85,-depth/2,bottom),(6.85,depth/2,top))
        for sign in (-1,1):
            centre=sign*9.5
            box('chamber base '+str(sign),(centre-2.68,-2.39,-.6),(centre+2.68,2.39,.58))
            lo,hi=sorted((sign*plan['side_wall_inner_tip_x'],sign*plan['chamber_outer_x']))
            wc=sign*abs(plan['window_centres'][0]);wl,wr=wc-dims['width_m']/2,wc+dims['width_m']/2
            # Preserve actual window openings, inside wall faces and reveals.
            for sy in (-1,1):
                yi,yo=sorted((sy*1.84,sy*2.20))
                for i,(a,b,z,Z) in enumerate([(lo,wl,.58,4.142),(wr,hi,.58,4.142),(wl,wr,.58,dims['bottom_z_m']),(wl,wr,dims['top_z_m'],4.142)]):
                    box(f'chamber wall {sign} {sy} {i}',(a,yi,z),(b,yo,Z),omit=('bottom','top'))
                # Projecting anta ends remain distinct in silhouette.
                px=sign*7.5
                box(f'anta {sign} {sy}',(px-.65,min(sy*2.20,sy*2.32),.58),(px+.65,max(sy*2.20,sy*2.32),4.142),omit=('bottom','top'))
            outer=sign*plan['end_wall_centre_x']
            box('chamber end '+str(sign),(outer-.18,-1.84,.58),(outer+.18,1.84,4.142),omit=('bottom','top'),weight=1.5)
            inner=sign*plan['entrance_wall_centre_x']
            for sy in (-1,1):
                box(f'entrance pier {sign} {sy}',(inner-.18,sy*1.41-.43,.58),(inner+.18,sy*1.41+.43,4.142),omit=('bottom','top'))
        # Sixteen distinct shafts, tapered octagons; all share one baked prototype.
        for y in (-1.9,1.9):
            for x in [a+d for a in plan['column_pair_centres'] for d in (-.4,.4)]:
                label=f'column {x} {y}'
                lathe(label,x,y,[(.32,.282),(.47,.24),(3.84,.20),(4.06,.289)],'column')
                box(label+' abacus',(x-.302,y-.302,4.06),(x+.302,y+.302,4.142),'abacus',omit=('bottom','top'))
        # Stepped continuous roof outline and recessed roof field, all open below.
        b=plan['central_roof_break_x'];setback=plan['central_to_chamber_setback']
        def outline(length,depth,br=b):
            x,y=length/2,depth/2;c=y-setback
            return [(-x,-c),(-br,-c),(-br,-y),(br,-y),(br,-c),(x,-c),(x,c),(br,c),(br,y),(-br,y),(-br,c),(-x,c)]
        rings=[(4.142,24.22,4.64),(4.42,24.36,4.8),(4.90,24.36,4.8),(5.10,24.60,4.9),(5.13,24.40,4.78),(5.54,24.40,4.78)]
        for i,((z,w,d),(Z,W,D)) in enumerate(zip(rings,rings[1:])):
            low,high=outline(w,d),outline(W,D)
            for j in range(12):
                k=(j+1)%12;face(f'roof band {i} {j}',[(*low[j],z),(*low[k],z),(*high[k],Z),(*high[j],Z)],weight=1.5 if i==1 else 1)
        outer,inside=outline(24.4,4.78),outline(23.84,4.22,b-.28)
        for j in range(12):
            k=(j+1)%12
            face('parapet cap '+str(j),[(*outer[j],5.54),(*outer[k],5.54),(*inside[k],5.54),(*inside[j],5.54)])
            face('parapet inside '+str(j),[(*inside[k],5.305),(*inside[j],5.305),(*inside[j],5.54),(*inside[k],5.54)])
        # Three rectangles cover the stepped roof; a matching underside closes it.
        for i,(a,z,depth) in enumerate([(-11.92,-(b-.28),3.98),(-(b-.28),b-.28,4.22),(b-.28,11.92,3.98)]):
            quad=[(a,-depth/2,5.305),(z,-depth/2,5.305),(z,depth/2,5.305),(a,depth/2,5.305)]
            face('roof field '+str(i),quad)
        for i,(a,z,depth) in enumerate([(-12.11,-b,4.40),(-b,b,4.64),(b,12.11,4.40)]):
            face('roof underside '+str(i),[(a,depth/2,4.142),(z,depth/2,4.142),(z,-depth/2,4.142),(a,-depth/2,4.142)])
        for x in plan['pier_centres']:
            for y in (-plan['lamp_y'],plan['lamp_y']):single(x,y,f'single {x} {y}')
    part='lamps';transform=lambda p:p
    for x in (-18,18):
        for y in (-9,9):
            shift=-.022*y;label=f'cluster {x} {y}'
            box(label+' foot',(x-.39,y-.39,shift-.01),(x+.39,y+.39,shift+.77),'cluster foot')
            lathe(label+' stem',x,y,[(shift+.77,.31),(shift+1.62,.14),(shift+4.43,.174),(shift+5.235,.133)],'cluster stem')
            def globe(gx,gy,gz,key):lathe(label+key,gx,gy,[(gz-.283,.003),(gz-.2,.195),(gz,.275),(gz+.2,.195),(gz+.283,.003)],key)
            globe(x,y,shift+5.465,'top globe')
            for j in range(4):
                a=math.tau*j/4;gx=x+.66*math.cos(a);gy=y+.66*math.sin(a)
                globe(gx,gy,shift+4.075,'side globe '+str(j))
                # Arms remain open; a narrow rectangular beam represents each.
                if j%2==0:box(label+' arm '+str(j),(min(x,gx)-.04,y-.055,shift+4.59),(max(x,gx)+.04,y+.055,shift+4.71),'arm '+str(j))
                else:box(label+' arm '+str(j),(x-.055,min(y,gy)-.04,shift+4.59),(x+.055,max(y,gy)+.04,shift+4.71),'arm '+str(j))
                lathe(label+' pendant '+str(j),gx,gy,[(shift+4.34,.08),(shift+4.65,.05)],'pendant '+str(j))
    return result
