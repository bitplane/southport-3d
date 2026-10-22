"""Bounded London Street corridor and Lord Street gardens.

OSM fixes road/path registration; widths, grades, planting, walls and furniture
orientations are estimates documented in research/streets.json. Keep these site
choices here, with reusable canopy/edge construction in southport3d.landscape.
"""
import json,math
from southport3d.geometry import Mesh
from southport3d.street import furniture
from southport3d.landscape import tree,capped_wall

PARTS={
 'ne-garden-ground':'North-east gardens, Lord Street and St George’s Place',
 'ne-garden-furniture':'North-east garden planting and furnishings',
 'sw-garden-ground':'South-west memorial garden and Lord Street',
 'sw-garden-furniture':'South-west garden planting and furnishings',
 **{f'london-{i}-{kind}':f'London Street section {i} '+('surfaces' if kind=='ground' else 'furnishings') for i in range(1,4) for kind in ['ground','furniture']}}


def build_extensions(ctx):
    rect,polygon,line,mat,grade,finish=[ctx[k] for k in ['rect','polygon','line','mat','grade','finish']]
    C=ctx['collections'];root=ctx['ROOT'];fm=ctx['fm']
    mixed,asphalt,kerb,white,yellow,tactile=[ctx[k] for k in ['mixed','asphalt','kerb','white','yellow','tactile']]
    grass=mat('Authored lawn',(.15,.235,.075),'grass');pathmat=mat('Garden asphalt path',(.17,.16,.14),'asphalt')
    stone=mat('Weathered garden coping',(.30,.29,.25));water=mat('Still dark pool water',(.035,.075,.065));water.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.24
    tm=[mat('Tree bark',(.14,.11,.075)),mat('Canopy shade',(.075,.145,.045)),mat('Canopy green',(.12,.22,.065)),mat('Canopy light',(.18,.27,.085))]
    osm=json.loads((root/'research/streets-osm.json').read_text())
    recipe=json.loads((root/'research/streets.json').read_text())
    count=0
    prototypes={}
    tree_prototype=None

    def furnishing(kind,x,y,yaw,part,source='Photographic estimate'):
        nonlocal count
        count+=1
        name=f'Furniture {kind} extension {count:03d}'
        if kind not in prototypes:
            ob=furniture(kind,'detail',name).finish(fm,C[part]);prototypes[kind]=ob
        else:
            ob=prototypes[kind].copy();ob.data=prototypes[kind].data;ob.name=name;C[part].objects.link(ob)
        ob.location=(x,y,grade(y));ob.rotation_euler.z=math.radians(yaw);ob['source']=source
        return ob

    def wall(points,part,height=.35,width=.28,name='garden edging'):
        m=capped_wall([(x,y,grade(y)) for x,y in points],height,width,'Wall '+name)
        return m.finish([stone],C[part])

    def curb(points,part):
        # Physical edge reaches carriageway. Open polylines leave junctions unblocked.
        m=capped_wall([(x,y,grade(y)-.12) for x,y in points],.125,.18,'Kerb street extension')
        m.finish([kerb],C[part])

    def dashed(points,part,width=.10,length=2,gap=4,material=None):
        a,b=points;d=math.dist(a,b)
        for j in range(int(d/(length+gap))):
            t=j*(length+gap)/d;u=min(1,t+length/d)
            line('Marking lane dash',[(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v) for v in [t,u]],width,material or white,part,-.112)

    # The old square ends exactly at x=+/-41. Shared coordinates avoid doubled floors.
    # North-side footway is widened to include the mapped bench and bus-stop line.
    for a,b in [(-41,-6),(6,41)]:rect('Surface north footway continuation',a,36,b,41,mixed,'perimeter')
    for side,x0,x1,label in [(1,41,154,'ne'),(-1,-104,-41,'sw')]:
        part=label+'-garden-ground';fp=label+'-garden-furniture'
        rect('Surface extended carriageways',x0,-27,x1,41,asphalt,part,-.12)
        rect('Surface Lord Street north footway',x0,31,x1,41,mixed,part)
        rect('Surface rear frontage footway',x0,-27,x1,-23.6,mixed,part)
        # Garden envelope with continuous footways beside main/rear carriageways.
        end=149 if side==1 else -100
        lo,hi=sorted([side*41,end]);rect('Surface garden paved envelope',lo,-14.8,hi,20.5,mixed,part)
        gx0,gx1=(42,146.5) if side==1 else (-66,-42)
        rect('Surface lawn',gx0,-12,gx1,17.8,grass,part,.006)
        # SW rear service lane wraps round the small memorial garden, not through it.
        if side==-1:
            rect('Surface western lawn continuation',-100,-13.5,-73,17.8,grass,part,.006)
            rect('Surface rear service return',-72,-19,-66,20.5,asphalt,part,.012)
            for x in [-72,-66]:curb([(x,-13),(x,17)],part)
        else:
            rect('Surface St Georges Place end return',149,-23.6,154,31,asphalt,part,-.112)
            curb([(149,-12),(149,19)],part)
        # Garden paths use the mapped coordinates; long NE path and fountain circle.
        paths=recipe['garden_paths'][label]
        for path in paths:
            line('Surface garden path',path['xy'],path['width'],pathmat,part,.018)
            # Round segment joins fill the outside wedges at bends. Coplanar
            # clipping in the assembler removes overlaps before export.
            for px,py in path['xy']:
                radius=path['width']/2
                polygon('Surface garden path join',[(px+radius*math.cos(j*math.tau/16),py+radius*math.sin(j*math.tau/16)) for j in range(16)],pathmat,part,.018)
        for x in ([68,116.5] if side==1 else [-99]):
            line('Surface garden entrance path',[(x,-14.8),(x,20.5)],2.6,pathmat,part,.019)
        # Rectangular reflecting pool is behind each colonnade. Coping follows the
        # site slope; water is deliberately a flat plane, with a shallow basin.
        a,b=sorted([side*44,side*61]);rect('Surface pool bed',a,-2.5,b,2.5,water,part,.025)
        wall([(a,-2.7),(b,-2.7),(b,2.7),(a,2.7),(a,-2.7)],fp,.18,.28,'reflecting pool coping')
        # Low garden retaining edges, broken at every cross-path entrance.
        cuts=[(lo,hi)]
        gates=[68,116.5] if side==1 else [-99,-69]
        for gate in gates:
            cuts=[piece for a,b in cuts for piece in ([(a,min(b,gate-1.8))] if a<gate-1.8 else [])+([(max(a,gate+1.8),b)] if b>gate+1.8 else [])]
        for a,b in cuts:
            if b-a<.2:continue
            for y in [-12.3,18]:wall([(a,y),(b,y)],fp,.3,.25)
        # Front/back pavements, with cross-path kerb openings, no kerb across scene ends.
        for a,b in cuts:
            if b>a:curb([(a,20.5),(b,20.5)],part)
        curb([(x0,31),(x1,31)],part);curb([(x0,-23.6),(x1,-23.6)],part)
        dashed([(x0,25.6),(x1,25.6)],part)
        for y in [21,21.2,-22.9,-23.1]:line('Marking double yellow',[(x0,y),(x1,y)],.075,yellow,part,-.111)
        # OSM benches/bins outside the old core. Orient benches toward road or paths.
        for node_id,node in osm['nodes'].items():
            x,y=node['xy'];kind={'bench':'bench','waste_basket':'bin'}.get(node['tags'].get('amenity'))
            if kind and x0<x<x1 and -23<y<41:
                furnishing(kind,x,y,180 if y>25 else 0,fp,'OSM node '+node_id+'; orientation estimated')
        for x in ([48,78,105,137] if side==1 else [-53,-88]):
            furnishing('streetlight',x,32.1,0,fp)
        # Bus stop poles only where mapped; shelter geometry awaits close evidence.
        for node_id,node in osm['nodes'].items():
            x,y=node['xy']
            if node['tags'].get('highway')=='bus_stop' and x0<x<x1 and 18<y<36:
                m=Mesh('Street bus stop pole '+node_id);m.lathe((x,y),[(grade(y),.035),(grade(y)+2.7,.035)],10)
                m.box((x,y,grade(y)+2.4),(.34,.06,.48));m.finish([kerb],C[fp])
        for i,record in enumerate(recipe['trees'][label]):
            x,y,scale=record;name=f'Tree {label} {i:02d}'
            if tree_prototype is None:
                ob=tree('detail',name).finish(tm,C[fp]);tree_prototype=ob
            else:
                ob=tree_prototype.copy();ob.data=tree_prototype.data;ob.name=name;C[fp].objects.link(ob)
            ob.location=(x,y,grade(y));ob.scale=(scale,scale,scale);ob.rotation_euler.z=i*1.73
            ob['source']='Canopy grouping estimated from Google satellite; generic species/shape'
    # Round fountain site: retain pool and surrounding path; sculpture deferred.
    part='ne-garden-ground';fp='ne-garden-furniture';x,y=117.87,2.02
    pts=[(x+4.0*math.cos(i*math.tau/48),y+4.0*math.sin(i*math.tau/48)) for i in range(48)]
    polygon('Surface fountain apron',pts,pathmat,part,.024)
    pts=[(x+3.3*math.cos(i*math.tau/48),y+3.3*math.sin(i*math.tau/48)) for i in range(49)]
    polygon('Surface fountain basin',pts[:-1],water,part,.030);wall(pts,fp,.32,.28,'round fountain basin')

    # London Street is divided at fixed seam stations; side-road mouths remain open.
    # The northern carriageway narrows from the existing square to an estimated 8.6m.
    for i,(north,south) in enumerate([(-36,-76),(-76,-116),(-116,-154)],1):
        part=f'london-{i}-ground';fp=f'london-{i}-furniture'
        rect('Surface London Street carriageway',-8.5,south,8.5,north,asphalt,part,-.12)
        for side in [-1,1]:
            # split at side roads and final crossroads, preserving contiguous road mouths
            gaps=([(-70,-62)] if side==-1 else [(-88,-79)])+[(-150,-138)]
            ranges=[(south,north)]
            for ga,gb in gaps:
                ranges=[p for a,b in ranges for p in ([(a,min(b,ga))] if a<ga else [])+([(max(a,gb),b)] if b>gb else [])]
            if i==3:
                ranges=[(a,min(b,-134.5)) for a,b in ranges if a<-134.5]+[(max(a,-132),b) for a,b in ranges if b>-132]
                a,b=-134.5,-132
                polygon('Surface crossing ramp',[(side*4.3,a),(side*5.4,a),(side*5.4,b),(side*4.3,b)],mixed,part)
                polygon('Surface crossing back landing',[(side*5.4,a),(side*8.5,a),(side*8.5,b),(side*5.4,b)],mixed,part)
            for a,b in ranges:
                if b<=a:continue
                def inner(y):return 4.3+max(0,min(1,(y+46)/10))*1.9
                points=[(side*inner(a),a),(side*8.5,a),(side*8.5,b),(side*inner(b),b)]
                polygon('Surface London Street footway',points,mixed,part)
                curb([(side*inner(a),a),(side*inner(b),b)],part)
                for delta in [.25,.45]:line('Marking London yellow edge',[(side*(inner(a)-delta),a),(side*(inner(b)-delta),b)],.075,yellow,part,-.111)
        dashed([(0,south),(0,north)],part)
        for side in [-1,1]:
            furnishing('streetlight',side*7.3,(north+south)/2,90*side,fp)
        for yy,side in [(-56,-1),(-74,1),(-94,-1),(-113,1),(-130,-1),(-153,1)]:
            if south<=yy<north:furnishing('bin' if int(abs(yy))%2==0 else 'bollard',side*5.4,yy,0,fp)
        # Short junction stubs establish future road/building ownership boundaries.
        for cy,side,width in [(-66,-1,8),(-83.5,1,9),(-144,-1,12),(-144,1,12)]:
            if south<cy<north:
                a,b=sorted([side*8.5,side*25]);rect('Surface side road mouth',a,cy-width/2,b,cy+width/2,asphalt,part,-.12)
                for yy in [cy-width/2,cy+width/2]:
                    rect('Surface side road footway',a,yy-(3 if yy<cy else 0),b,yy+(3 if yy>cy else 0),mixed,part)
                    curb([(a,yy),(b,yy)],part)
        # Pedestrian crossing near Chapel/Hoghton: estimated studs and landing pads.
        if i==3:
            for yy in [-134.5,-132]:
                for k in range(18):rect('Marking London crossing stud',-4.25+k*.5,yy-.05,-4.15+k*.5,yy+.05,white,part,-.109)
            for side in [-1,1]:
                rect('Tactile London crossing landing',side*4.8-.45,-134.5,side*4.8+.45,-132,tactile,part,.02)
                furnishing('pedestrian',side*5.25,-131.3,90*side,fp)
                furnishing('signal',side*5.25,-135.8,180 if side==1 else 0,fp)
    # Mapped benches on the north pavement opposite the monument.
    for node_id,node in osm['nodes'].items():
        x,y=node['xy'];kind={'bench':'bench','waste_basket':'bin'}.get(node['tags'].get('amenity'))
        if kind and -41<x<41 and 31<y<41:
            furnishing(kind,x,y,180,'ne-furniture' if x>0 else 'sw-furniture','OSM node '+node_id)
    ctx['extension_furniture_count']=count
