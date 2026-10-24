"""Bounded London Street corridor and Lord Street gardens.

OSM fixes road/path registration; widths, grades, planting, walls and furniture
orientations are estimates documented in research/streets.json. Keep these site
choices here, with reusable canopy/edge construction in southport3d.landscape.
"""
import json,math
from southport3d.geometry import Mesh
from furniture_lod import furniture
from southport3d.landscape import capped_wall
from landscape_lod import tree
from rear_streets import PARTS as REAR_PARTS, build_rear_streets

PARTS={
 **REAR_PARTS,
 'ne-garden-ground':'North-east gardens, Lord Street and St George’s Place',
 'ne-garden-furniture':'North-east garden planting and furnishings',
 'sw-garden-ground':'South-west memorial garden and Lord Street',
 'sw-garden-furniture':'South-west garden planting and furnishings',
 **{f'london-{i}-{kind}':f'London Street section {i} '+('surfaces' if kind=='ground' else 'furnishings') for i in range(1,4) for kind in ['ground','furniture']}}


def build_extensions(ctx):
    rect,polygon,line,mat,grade,finish=[ctx[k] for k in ['rect','polygon','line','mat','grade','finish']]
    paint_edge=ctx['paint_edge']
    C=ctx['collections'];root=ctx['ROOT'];fm=ctx['fm']
    mixed,asphalt,kerb,white,yellow,tactile=[ctx[k] for k in ['mixed','asphalt','kerb','white','yellow','tactile']]
    roadpavers=ctx['roadpavers']
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

    def curb(points,part,inside=-1):
        # Road-facing boundary is the actual kerb line, not a centred wall.
        return ctx['open_kerb'](points,inside,part)

    def dashed(points,part,width=.10,length=2,gap=4,material=None):
        a,b=points;d=math.dist(a,b)
        for j in range(int(d/(length+gap))):
            t=j*(length+gap)/d;u=min(1,t+length/d)
            line('Marking lane dash',[(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v) for v in [t,u]],width,material or white,part,-.112)

    front=[(41,-19.9),(42,-19.9),(64,-19.6),(71,-19.65),(108,-18.2),(151,-16.45),(154,-16.45)]
    garden=[(41,-14.8),(42,-14.8),(64,-13.6),(108,-12.2),(143,-10.7),(147,-8),(147,21)]
    def ordinate(curve,x):
        for a,b in zip(curve,curve[1:]):
            if a[0]<=x<=b[0] and b[0]>a[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
        raise ValueError(x)
    def span(curve,a,b):return [(a,ordinate(curve,a))]+[v for v in curve if a<v[0]<b]+[(b,ordinate(curve,b))]
    # Rounded Post Office Avenue returns observed in November 2020 Street View.
    # One curve owns paving, kerb and paint; radius is a visual estimate.
    def corner_curve(x,west,r=1.4):
        y=ordinate(front,x)
        p0=(x-r,ordinate(front,x-r)) if west else (x,y-r)
        p1=(x,y)
        p2=(x,y-r) if west else (x+r,ordinate(front,x+r))
        return [tuple((1-t)**2*p0[k]+2*(1-t)*t*p1[k]+t*t*p2[k] for k in (0,1)) for t in [j/8 for j in range(9)]]
    west_return=span(front,41,66.154-1.4)[:-1]+corner_curve(66.154,True)+[(66.154,-27)]
    east_return=[(70.154,-27)]+corner_curve(70.154,False)+span(front,70.154+1.4,154)[1:]
    # The old square ends exactly at x=+/-41. Shared coordinates avoid doubled floors.
    # North-side footway is widened to include the mapped bench and bus-stop line.
    for a,b in [(-41,-6),(6,41)]:rect('Surface north footway continuation',a,36,b,41,mixed,'perimeter')
    for side,x0,x1,label in [(1,41,154,'ne'),(-1,-73,-41,'sw')]:
        part=label+'-garden-ground';fp=label+'-garden-furniture'
        rect('Surface extended carriageways',x0,-27,x1,41,asphalt,part,-.12)
        if side<0:rect('Surface service road blocks',x0,-23.6,x1,-14.8,roadpavers,part,-.117)
        rect('Surface Lord Street north footway',x0,31,x1,41,mixed,part)
        if side<0:rect('Surface rear frontage footway',x0,-27,x1,-23.6,mixed,part)
        if side==1:
            # Leave the mapped Post Office Avenue mouth open, including the
            # 1.8/1.1m footways on either side of its four-metre carriageway.
            polygon('Surface registered frontage west',[(41,-27)]+list(reversed(west_return)),mixed,part)
            polygon('Surface registered frontage east',east_return+[(154,-27)],mixed,part)
            polygon('Surface St Georges service blocks',front+list(reversed(garden[:-2]+[(154,-10.7)])),roadpavers,part,-.117)
        if side==-1:
            # Continue the Prezzo approach along the registered terrace and BHF frontage.
            # Keep pavement ownership here; taper beyond BHF at the church edge.
            polygon('Surface 116-122 frontage approach',[(-73,-23.6),(-73,-21.1),(-41,-21.1),(-41,-23.6)],mixed,part)
        # Garden envelope with continuous footways beside main/rear carriageways.
        end=147 if side==1 else -73
        lo,hi=sorted([side*41,end])
        if side==1:polygon('Surface garden paved envelope',garden+[(41,21)],mixed,part)
        else:rect('Surface garden paved envelope',lo,-14.8,hi,21,mixed,part)
        gx0,gx1=(42,143.7) if side==1 else (-63.25,-42)
        if side>0:rect('Surface lawn',gx0,-8,gx1,17.8,grass,part,.006)
        else:
            # Lawn follows the inside of the rounded wall, never the old square
            # corner which would spill turf across the new pedestrian pavement.
            arc=[(-60.5+2.75*math.cos(a),-9.3+2.75*math.sin(a)) for a in [math.pi+i*math.pi/2/16 for i in range(17)]]
            polygon('Surface lawn',arc+[(gx1,-12.05),(gx1,17.8),(gx0,17.8)],grass,part,.006)
        # SW rear service lane wraps round the small memorial garden, not through it.
        if side==-1:
            rect('Surface rear service return',-72,-21.1,-66,21,roadpavers,part,.026)
        else:
            rect('Surface St Georges Place end return',147,-23.6,154,31,asphalt,part,-.12)
        # Garden paths use the mapped coordinates; long NE path and fountain circle.
        paths=recipe['garden_paths'][label] if side==1 else []
        for path in paths:
            line('Surface garden path',path['xy'],path['width'],pathmat,part,.018)
            # Round segment joins fill the outside wedges at bends. Coplanar
            # clipping in the assembler removes overlaps before export.
            for px,py in path['xy']:
                radius=path['width']/2
                polygon('Surface garden path join',[(px+radius*math.cos(j*math.tau/16),py+radius*math.sin(j*math.tau/16)) for j in range(16)],pathmat,part,.018)
        for x in ([68,116.5] if side==1 else []):
            polygon('Surface garden entrance path',[(x-1.3,ordinate(garden,x-1.3)),(x+1.3,ordinate(garden,x+1.3)),(x+1.3,20.5),(x-1.3,20.5)],pathmat,part,.019)
        # Rectangular reflecting pool is behind each colonnade. Coping follows the
        # site slope; water is deliberately a flat plane, with a shallow basin.
        a,b=sorted([side*44,side*61]);rect('Surface pool bed',a,-2.5,b,2.5,water,part,.025)
        wall([(a,-2.7),(b,-2.7),(b,2.7),(a,2.7),(a,-2.7)],fp,.18,.28,'reflecting pool coping')
        # Low garden retaining edges, broken at every cross-path entrance.
        cuts=[(lo,hi)]
        gates=[68,116.5] if side==1 else [-99,-69]
        for gate in gates:
            opening=3 if side==-1 else 1.8
            cuts=[piece for a,b in cuts for piece in ([(a,min(b,gate-opening))] if a<gate-opening else [])+([(max(a,gate+opening),b)] if b>gate+opening else [])]
        for a,b in cuts:
            if b-a<.2 or (side==-1 and b<=-66):continue
            for y in [(-8.3 if side>0 else -12.3),18]:
                if side==-1 and y==-12.3:
                    # The observed balustrade replaces this portion of the provisional edge.
                    for start,end in [(a,min(b,-66)),(max(a,-42),b)]:
                        if end>start:wall([(start,y),(end,y)],fp,.3,.25)
                else:wall([(max(a,-63.5) if side==-1 else a,y),(b,y)],fp,.3,.25)
        # Front/back pavements, with cross-path kerb openings, no kerb across scene ends.
        for a,b in cuts:
            if b>a:curb([(a,21),(b,21)],part)
        curb([(x0,31),(x1,31)],part,1)
        if side==-1:curb([(x1,-21.1),(-72,-21.1),(-72,21)],part,1)
        else:
            curb(west_return,part)
            curb([p for p in east_return if p[0]<116.8]+[(116.8,ordinate(front,116.8))],part)
            curb(span(front,119.2,154),part)
        # One phase and one kerb setback across all Lord Street ownership seams.
        for x in range(math.floor(x0/6)*6,math.ceil(x1/6)*6,6):
            start,end=max(x0,x),min(x1,x+2)
            if end>start:line('Marking lane dash',[(start,25.6),(end,25.6)],.10,white,part,-.111)
        bounds=(x0,-27,x1,41)
        for a,b in cuts:
            if b>a:paint_edge('Lord Street garden edge',[(a,21),(b,21)],1,part,bounds)
        if side==-1:
            paint_edge('terrace approach double yellow',[(x1,-21.1),(-72,-21.1),(-72,21)],-1,part,bounds)
            from rounded_garden import kerb_curve
            curve=kerb_curve()
            # Road extends up to the curved kerb; the pale footway owns its inside.
            arc=curve[1:-1]
            polygon('Surface rounded corner road',arc+[(-66,-14.8)],roadpavers,part,.027)
            curb(curve,part,-1)
            paint_edge('garden service edge',curve,1,part,bounds)
            # Observed taxi bay: dashed inner edge and closed ends beside the church.
            dashed([(-69.4,-12),(-69.4,15)],part,.10,1.1,1.8,yellow)
            for y in [-12,15]:line('Marking Christ taxi bay end',[(-71.5,y),(-69.4,y)],.10,yellow,part,-.109)
            from rounded_garden import taxi_letters
            for cy in [-5,8]:
                for poly in taxi_letters(-70.4,cy):polygon('Marking TAXIS',poly,yellow,part,-.108)
        else:
            curb(span(garden,41,116.8),part,1)
            curb(span(garden,119.2,147)+[(147,21)],part,1)
            # Derive paint from each continuous kerb return before clipping.
            # Separate perpendicular strokes leave conspicuous open corners.
            paint_edge('St Georges frontage west return',west_return,1,part,bounds)
            paint_edge('St Georges frontage east return',east_return,1,part,bounds)
            paint_edge('St Georges garden edge',garden,-1,part,bounds)
            curb([(154,-10.8),(154,21)],part)
            for y in range(-8,19,3):line('Marking St Georges taxi bay',[(151.8,y),(151.8,min(y+1.2,19))],.10,yellow,part,-.109)
            for y in [-8,19]:line('Marking St Georges taxi bay end',[(151.8,y),(153.9,y)],.10,yellow,part,-.109)
        # OSM benches/bins outside the old core. Orient benches toward road or paths.
        for node_id,node in osm['nodes'].items():
            x,y=node['xy'];kind={'bench':'bench','waste_basket':'bin'}.get(node['tags'].get('amenity'))
            if kind and x0<x<x1 and -23<y<41:
                furnishing(kind,x,y,180 if 0<y<25 else 0,fp,'OSM node '+node_id+'; orientation estimated')
        for x in ([48,78,105,137] if side==1 else [-53]):
            furnishing('lord-street-lamp',x,32.1,0,fp)
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
    # White parking-bay edges follow the shop kerb; the garden row stays clear.
    for start,end,y in [(-64,-18,-19.1)]:
        for x in range(start,end,3):
            a,b=x,min(x+1.2,end)
            split=[(a,min(b,-41),'sw-garden-ground'),(max(a,-41),b,'roads')] if x<0 else [(a,b,'ne-garden-ground')]
            for aa,bb,part in split:
                if bb>aa:line('Marking service parking bay',[(aa,y),(bb,y)],.10,white,part,-.109)
        for x in [start,end]:
            part=('sw-garden-ground' if x<-41 else 'roads') if x<0 else 'ne-garden-ground'
            line('Marking service parking bay end',[(x,y),(x,y-1.8)],.10,white,part,-.109)
    part='ne-garden-ground'
    for side,edge,back in [('south',ordinate(front,118),ordinate(front,118)-1),('north',ordinate(garden,118),ordinate(garden,118)+1)]:
        rect('Surface Sainsbury ramp '+side,116.8,min(edge,back),119.2,max(edge,back),mixed,part,.023)
        rect('Tactile Sainsbury '+side,116.8,min(edge,back),119.2,max(edge,back),tactile,part,.024)
    for x in [116.8,119.2]:
        for y in range(math.ceil(ordinate(front,118)),math.floor(ordinate(garden,118))+1):rect('Marking Sainsbury crossing stud',x-.05,y-.05,x+.05,y+.05,white,part,-.109)
    # Screenshot-supported shop-facing garden edge, added without duplicating core posts.
    from garden_front import globe_lamp,balustrade
    frontage=recipe['sw_frontage_2024'];fp='sw-garden-furniture'
    for x in frontage['garden_bollards_x']:
        furnishing('bollard',x,frontage['garden_bollards_y'],0,
                   'sw-furniture' if x>-41 else fp,'user-street-2024; spacing estimated')
    for x in frontage['shop_bollards_x']:
        furnishing('bollard',x,frontage['shop_bollards_y'],0,fp,
                   'user-street-2024; spacing estimated')
    garden_materials=[mat('Pale weathered balustrade stone',(.48,.46,.39)),fm[0],
                      mat('Globe lamp pale shaft and opal glass',(.79,.79,.70))]
    y=frontage['balustrade_y'];start=-58;end=frontage['balustrade_end_x']
    template=None
    for x in range(start,end,4):
        if template is None:
            ob=balustrade(name='Garden balustrade segment').finish(garden_materials,C[fp]);template=ob
        else:
            ob=template.copy();ob.data=template.data;C[fp].objects.link(ob)
        ob.location=(x,y,grade(y));ob['source']='user-street-2024; calibrated repeat spacing'
    m=Mesh('Wall balustrade end pier');m.box((end,y,grade(y)+.505),(.36,.46,1.01));m.box((end,y,grade(y)+1.045),(.46,.49,.07));m.finish([garden_materials[0]],C[fp])
    template=None
    for x in [-58,-46]:
        if template is None:
            ob=globe_lamp().finish(garden_materials,C[fp]);template=ob
            for face in ob.data.polygons:face.use_smooth=True
        else:
            ob=template.copy();ob.data=template.data;C[fp].objects.link(ob)
        ob.location=(x,y,grade(y)+1.08);ob['source']='user-street-2024; pier placement estimated'
    from rounded_garden import build_corner
    build_corner(ctx,garden_materials)
    # Photographed return opposite St George's: open stone balusters, globe
    # lamps and shallow planter bowls. The remaining NE boundary is provisional.
    fp='ne-garden-furniture'
    for y in range(-10,18,4):
        ob=balustrade(name='Garden balustrade St Georges return').finish(garden_materials,C[fp])
        ob.location=(144.8,y,grade(y));ob.rotation_euler.z=math.pi/2
    for y in [-10,18]:
        ob=globe_lamp(name='Garden globe lamp St Georges').finish(garden_materials,C[fp])
        ob.location=(144.8,y,grade(y)+1.08)
        bowl=Mesh('Street garden planter bowl')
        bowl.lathe((142.8,y),[(grade(y),.20),(grade(y)+.25,.24),(grade(y)+.37,.55),(grade(y)+.62,.68),(grade(y)+.68,.64),(grade(y)+.61,.57),(grade(y)+.46,.42)],16)
        bowl.finish([garden_materials[0]],C[fp])
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
        if i==1:
            # Detailed Glebe asset owns the western throat, including its ramp.
            rect('Surface London Street carriageway',-10,south,8.5,-69.4,asphalt,part,-.12)
            rect('Surface London Street carriageway',-4.3,-69.4,8.5,-63.4,asphalt,part,-.12)
            rect('Surface London Street carriageway',-10,-63.4,8.5,north,asphalt,part,-.12)
        else:rect('Surface London Street carriageway',-10,south,8.5,north,asphalt,part,-.12)
        for side in [-1,1]:
            # split at side roads and final crossroads, preserving contiguous road mouths
            gaps=([(-69.4,-63.4)] if side==-1 else [(-88,-79)])+[(-150,-138)]
            ranges=[(south,north)]
            for ga,gb in gaps:
                ranges=[p for a,b in ranges for p in ([(a,min(b,ga))] if a<ga else [])+([(max(a,gb),b)] if b>gb else [])]
            if i==3:
                ranges=[(a,min(b,-134.5)) for a,b in ranges if a<-134.5]+[(max(a,-132),b) for a,b in ranges if b>-132]
                a,b=-134.5,-132
                polygon('Surface crossing ramp',[(side*4.3,a),(side*5.4,a),(side*5.4,b),(side*4.3,b)],mixed,part)
                polygon('Surface crossing back landing',[(side*5.4,a),(side*(12.5 if side<0 else 11.5),a),(side*(12.5 if side<0 else 11.5),b),(side*5.4,b)],mixed,part)
            ranges=[(lo,hi) for a,b in ranges for lo,hi in zip(sorted({a,b,*[y for y in [-46] if a<y<b]})[:-1],sorted({a,b,*[y for y in [-46] if a<y<b]})[1:])]
            for a,b in ranges:
                if b<=a:continue
                def inner(y):return 4.3+(max(0,min(1,(y+46)/10))*1.9 if side<0 else 0)
                points=[(side*inner(a),a),(side*(12.5 if side<0 else 11.5),a),(side*(12.5 if side<0 else 11.5),b),(side*inner(b),b)]
                polygon('Surface London Street footway',points,mixed,part)
                curb([(side*inner(a),a),(side*inner(b),b)],part,-side)
                paint_edge('London yellow edge',ctx['london_kerb'](side),side,part,(-10,a,8.5,b))
        if i==1:
            # The Glebe asset clips these same bends at X=-4.3. Keep the
            # carriageway-side fragments here so both yellow pairs join.
            north_curve=[(-4.3,-63.4),(-4.3,-63.65),(-4.5,-63.9),(-4.9,-64.05),(-5.5,-64.1),(-9.8,-64.05),(-29.9,-64.1)]
            south_curve=[(-4.3,-69.4),(-4.3,-69.15),(-4.5,-68.9),(-4.9,-68.75),(-5.5,-68.7),(-9.8,-68.75),(-26.85,-68.92)]
            for curve,side in [(north_curve,1),(south_curve,-1)]:
                paint_edge('Glebe mouth return',curve,side,part,(-4.3,-69.4,8.5,-63.4))
        dashed([(0,south),(0,north)],part)
        for side in [-1,1]:
            furnishing('london-led' if i==1 and side==-1 else 'streetlight',side*4.65,(north+south)/2,-90*side,fp,'User kerb/orientation correction; Halifax LED observed, other fittings provisional')
        # The later Halifax photograph explicitly disproves the old (-5.4,-56) bin.
        for yy,side in [(-74,1),(-94,-1),(-113,1),(-130,-1),(-153,1)]:
            if south<=yy<north:furnishing('stainless-bin' if int(abs(yy))%2==0 else 'bollard',side*5.4,yy,0,fp)
        # Short junction stubs establish future road/building ownership boundaries.
        for cy,side,width in [(-83.5,1,9),(-144,-1,12),(-144,1,12)]:
            if south<cy<north:
                a,b=sorted([side*(10 if side<0 else 8.5),side*25]);rect('Surface side road mouth',a,cy-width/2,b,cy+width/2,asphalt,part,-.12)
                for yy in [cy-width/2,cy+width/2]:
                    rect('Surface side road footway',a,yy-(3 if yy<cy else 0),b,yy+(3 if yy>cy else 0),mixed,part)
                    ka,kb=sorted([side*4.3,side*25])
                    curve=[(ka,yy),(kb,yy)];inside=1 if yy>cy else -1
                    curb(curve,part,inside)
                    paint_edge('Side road throat',curve,-inside,part)
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
            furnishing(kind,x,y,0,'ne-furniture' if x>0 else 'sw-furniture','OSM node '+node_id)
    build_rear_streets(ctx)
    ctx['extension_furniture_count']=count
