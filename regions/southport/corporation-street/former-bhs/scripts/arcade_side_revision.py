"""First Chapel-side run of Cambridge Arcade, from the 2025 Lead photo.

Positions are estimated on an oblique view. Dark grilles, two-light divisions,
piers, plain end panel and fascia are resolved; infill and hidden condition are
not. Temporary works and damaged finish are omitted.
"""

def build_arcade_chapel_side():
    plan = json.loads((ROOT/'research/elevation-schedule.json').read_text())['arcade_chapel']
    centres = plan['centres_m']
    width, sill, head = plan['width_m'], plan['sill_m'], plan['head_m']
    shop_bays = plan['shop_bays_m']
    windows = [rect(v-width/2, sill, v+width/2, head) for v in centres]
    shops = [rect(a, .12, b, 3.16) for a, b in shop_bays]
    holes = windows + shops

    # Cut real openings and returns: pale infill behind the upper grilles is
    # provisional, while dark display glazing stands behind the lower openings.
    m = Mesh('Shell Chapel arcade side')
    for q in cut(rect(0, 0, F, 12.8), holes):
        m.add([(0, v, z) for v,z in q], [tuple(reversed(range(len(q))))])
    for h in holes:
        for a,b in zip(h, h[1:]+h[:1]):
            m.add([(0,*a), (0,*b), (.14,*b), (.14,*a)], [(3,2,1,0)])
    finish(m, 'rear', pale)
    for h in windows:
        m = Mesh('Architecture arcade pale infill')
        m.add([(.14, v, z) for v,z in h], [tuple(reversed(range(len(h))))])
        finish(m, 'rear', pale)
    for h in shops:
        m = Mesh('Glazing chapel arcade display')
        m.add([(.14, v, z) for v,z in h], [tuple(reversed(range(len(h))))])
        finish(m, 'rear', glass)

    # Slim metal stiles and rails; the backing remains recessed behind them.
    half = .018
    for v in centres:
        a,b=v-width/2,v+width/2
        for y in (a,v,b):
            box('Architecture arcade window stile', -.105,y-half,sill, -.03,y+half,head, 'rear',dark)
        for z in [sill,*plan['transom_rails_m'],head]:
            for lo,hi in ((a+half,v-half),(v+half,b-half)):
                box('Architecture arcade window rail', -.105,lo,z-half, -.03,hi,z+half, 'rear',dark)
        box('Architecture arcade window sill', -.16,a-.05,4.04, -.025,b+.05,4.15, 'rear',cream)
        m = Mesh('Architecture arcade oval grille')
        for side in (-1,1):
            yy = v + side*width/4
            m.tube([(-.13, yy+.25*math.cos(math.tau*j/16), 5.76+.30*math.sin(math.tau*j/16))
                    for j in range(17)], .012, sides=5)
        finish(m, 'rear', dark)
    # Larger stone piers contrast with the thin ironwork. Capitals stop just
    # short of the separate roof-frame eave at 6.25 m.
    for v,pier_width in zip(plan['pier_centres_m'],plan['pier_widths_m']):
        pier_half=pier_width/2
        box('Architecture arcade stone pier', -.15,v-pier_half,4.06, -.025,v+pier_half,6.08, 'rear',cream)
        box('Architecture arcade pier capital', -.20,v-pier_half-.01,6.08, -.025,v+pier_half+.01,6.15, 'rear',cream)

    # One plain end panel and two unidentified relief panels. Outline only;
    # the obscured iconography is deliberately not invented.
    for a,b in plan['panels_m']:
        for y in (a,b):
            box('Architecture arcade panel stile', -.10,y-half,4.18, -.03,y+half,6.16, 'rear',dark)
        for z in (4.18,6.16):
            box('Architecture arcade panel rail', -.10,a+half,z-half, -.03,b-half,z+half, 'rear',dark)
    # Recessed display windows and their simple dark divisions. Door positions
    # inside the unobserved run are not inferred from the oblique photograph.
    for a,b in shop_bays:
        for y in (a,(a+b)/2,b):
            box('Architecture chapel arcade display stile', -.10,y-.035,.12, -.025,y+.035,3.16, 'rear',dark)
    box('Architecture chapel arcade fascia', -.13,0,3.20, -.025,F,3.94, 'rear',cream)
    box('Architecture chapel arcade fascia cornice', -.16,0,3.95, -.025,F,4.04, 'rear',cream)


def arcade_side_sign(font):
    # The 2025 photograph clearly retains a blue BHS sign above the displays.
    ob=text_object('Architecture sign arcade BHS','BHS',(X-.15,Y+2.2,Z+3.58),
                   (-1,0,0),.47,1.18,font,blue,extrude=.003,
                   collection=collections['rear'],fit_bounds=True)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.select_set(False)
    ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    for vert in ob.data.vertices:vert.co=world((vert.co.x-X,vert.co.y-Y,vert.co.z-Z))
    ob.data.update()
    if not ob.data.uv_layers:ob.data.uv_layers.new(name='metric')

build_arcade_chapel_side()
