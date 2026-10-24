"""Whole bay/frontage and mapped-wing envelopes, independent of detailed windows."""
import json,math
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());a=math.radians(d['local_rotation_degrees'])
    ox,oy=d['origin_site_xy'];nx,ny=d['north_basis'];base=d['base_z']
    def world(p):x,y,z=p;return (ox+math.cos(a)*x+nx*y,oy+math.sin(a)*x+ny*y,base+z)
    s=Surfaces(['frontage','roof','rear-wings'],world);w=d['width'];e=d['eaves'];r=d['ridge'];dep=d['main_depth'];bays=d['bay_centres'];flats=d['flat_centres']
    def front(name,x0,x1,y,z0,z1,weight=1):s.quad(name,[(x1,y,z0),(x0,y,z0),(x0,y,z1),(x1,y,z1)],weight=weight)
    # Flat strips between bays retain door recesses; windows become one atlas.
    ends=[(0,bays[0]-1.725)]+[(x+1.725,y-1.725) for x,y in zip(bays,bays[1:])]+[(bays[-1]+1.725,w)]
    for i,(l,h) in enumerate(ends):
        door=next((x for x in flats if l<x<h),None)
        if door is None:front('flat '+str(i),l,h,0,0,11)
        else:
            front('door left '+str(i),l,door-1.35,0,0,11)
            front('door right '+str(i),door+1.35,h,0,0,11)
            front('door head '+str(i),door-1.35,door+1.35,0,3.08,11)
            front('recessed door '+str(i),door-1.35,door+1.35,-1.18,.15,3.08)
            s.quad('portal left '+str(i),[(door-1.35,0,.12),(door-1.35,-1.18,.12),(door-1.35,-1.18,3.08),(door-1.35,0,3.08)])
            s.quad('portal right '+str(i),[(door+1.35,-1.18,.12),(door+1.35,0,.12),(door+1.35,0,3.08),(door+1.35,-1.18,3.08)])
            s.quad('portal soffit '+str(i),[(door-1.35,0,3.08),(door+1.35,0,3.08),(door+1.35,-1.18,3.08),(door-1.35,-1.18,3.08)])
            # Same two risers and continuous recessed landing as Detail.
            s.box('portal lower step '+str(i),(door-1.35,.35,-.30),(door+1.35,.70,.01),omit=('bottom','rear'))
            s.box('portal landing '+str(i),(door-1.35,-1.35,-.30),(door+1.35,.35,.15),omit=('bottom',))
    front('upper main wall',0,w,0,11,e)
    for i,x in enumerate(bays):
        path=[(x-1.725,0),(x-1.23,1.08),(x+1.23,1.08),(x+1.725,0)]
        for j,(p,q) in enumerate(zip(path,path[1:])):
            s.quad(f'whole bay {i} {j}',[(*q,0),(*p,0),(*p,11.0),(*q,11.0)],weight=1.5)
        tall=i not in (0,5);top=13.55 if tall else 11.15
        if tall:s.box('attic bay '+str(i),(x-1.725,0,11),(x+1.725,1.20,top),omit=('bottom','rear','top'))
        s.triangle('white gable '+str(i),[(x+1.725,1.245,top),(x-1.725,1.245,top),(x,1.245,top+1.65)],weight=1.5)
    # One fascia envelope replaces dozens of independent signage bakes.
    s.box('continuous fascia',(0,1.02,3.18),(w,1.335,3.80),omit=('bottom','rear'),weight=2)
    for l,h in [(bays[1],bays[2]),(bays[3],bays[4])]:
        s.box('paired attic bridge '+str(l),(l+1.725,0,11.025),(h-1.725,1.13,11.575),omit=('rear','left','right'))
    s.part='rear-wings'
    s.quad('west main',[(0,-dep,0),(0,0,0),(0,0,e),(0,-dep,e)][::-1])
    s.quad('east main',[(w,-dep,0),(w,0,0),(w,0,e),(w,-dep,e)])
    # Upper back wall and lower exposed intervals keep the actual courts open.
    s.quad('rear upper',[(0,-dep,10.9),(w,-dep,10.9),(w,-dep,e),(0,-dep,e)])
    wings=d['rear_wings']
    for l,h in zip([0]+[q[1] for q in wings],[q[0] for q in wings]+[w]):
        if h-l>.1:s.quad('rear court '+str(l),[(l,-dep,0),(h,-dep,0),(h,-dep,10.9),(l,-dep,10.9)])
    for i,(l,h,depth) in enumerate(wings):
        height=12.4 if i==0 else 11.45
        s.box('wing '+str(i),(l,-depth,0),(h,-dep,height),omit=('bottom','front','top'))
    s.part='roof'
    s.hip('main',-.06,w+.06,-dep-.08,-.10,e,r)
    for i,x in enumerate(bays):
        top=11.15 if i in (0,5) else 13.55;back=-.15 if i in (0,5) else -3.3
        p=(x-1.825,top+.05);q=(x,top+1.84);t=(x+1.825,top+.05)
        s.quad('gable left '+str(i),[(p[0],1.20,p[1]),(p[0],back,p[1]),(q[0],back,q[1]),(q[0],1.20,q[1])])
        s.quad('gable right '+str(i),[(q[0],1.20,q[1]),(q[0],back,q[1]),(t[0],back,t[1]),(t[0],1.20,t[1])])
        s.triangle('gable end '+str(i),[(t[0],1.20,t[1]),(p[0],1.20,p[1]),(q[0],1.20,q[1])])
    def chimney(name,x,y,z,bw,bd,h,potbase):
        s.box(name,(x-bw/2,y-bd/2,z),(x+bw/2,y+bd/2,z+h),omit=('bottom',))
        for j in range(4):
            px=x-.51+j*.34
            s.box(name+' pot '+str(j),(px-.085,y-.085,potbase),(px+.085,y+.085,potbase+.70),omit=('bottom',),cage=.08)
    for i,(l,h,depth) in enumerate(wings):
        height=12.4 if i==0 else 11.45
        s.hip('wing '+str(i),l-.08,h+.08,-depth-.08,-dep+.12,height,height+2.5,'y')
        chimney('rear chimney '+str(i),(l+h)/2,-depth+1.6,height+1.5,1.65,.82,2.5,height+4.0)
    for i,x in enumerate((5.,18.78,32.5)):chimney('main chimney '+str(i),x,-dep/2,r-.225,1.55,.94,1.675,r+1.45)
    return s.result
