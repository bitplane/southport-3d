"""Prototype dimensions for the Venetian Bridge fittings, in metres.

The 2023 Geograph photograph is the visual reference.  This module describes a
single representative panel and column; it is intentionally not yet repeated
or connected to the publication recipe.  Placement, panel count, gate openings
and current lamp heads require independent main-shape and image review.
"""
import math
from southport3d.geometry import Mesh

# Relative heights above deck. The exact dimensions are visual estimates.
BALUSTER = [(0,.072),(.018,.075),(.04,.064),(.07,.053),(.10,.047),
            (.13,.052),(.16,.063),(.19,.071),(.22,.073),(.25,.070),
            (.28,.062),(.31,.050),(.34,.040),(.37,.037),(.40,.040),
            (.43,.050),(.46,.062),(.49,.071),(.52,.074),(.55,.071),
            (.58,.062),(.61,.051),(.64,.044),(.67,.044),(.70,.055),
            (.73,.068),(.76,.073),(.79,.068),(.82,.062)]
COLUMN = [(0,.16),(.035,.19),(.075,.19),(.10,.16),(.13,.13),(.17,.18),
          (.21,.19),(.25,.15),(.29,.10),(.34,.074),(1.28,.066),
          (1.32,.082),(1.35,.084),(1.39,.12),(1.43,.13),(1.46,.10),
          (1.50,.09),(1.53,.12),(1.56,.11),(1.58,.05)]

def panel_prototype(length=3.0, count=17):
    """One x-axis panel, z=0 deck, plus a separate end pier and lamp column.

    The detached meshes make physical inspection and later LoD substitutions
    possible.  No photographic pixels are used.  Dimensions are estimates.
    """
    assert length > .5 and count >= 2
    rails=Mesh('Venetian prototype rails')
    # Separate bands touch at edges rather than occupying the same volume.
    rails.box((length/2,0,.045),(length,.17,.09))
    rails.box((length/2,0,.125),(length,.13,.07))
    rails.box((length/2,0,.965),(length,.15,.09))
    rails.box((length/2,0,1.03),(length,.22,.04))
    turned=Mesh('Venetian prototype turned balusters')
    for i in range(count):
        x=(i+.5)*length/count
        turned.rect_profile((x,0),[(.16,.13,.13),(.22,.13,.13)])
        turned.lathe((x,0),[(.22+z*(.70/.82),r) for z,r in BALUSTER],segments=24)
    pier=Mesh('Venetian prototype pier')
    # Two quads per cap add a station break at the centre. Bottom vertices
    # can then follow a profile knot without a raised corner or buried base.
    rings=[(0,.43,.43),(.06,.43,.43),(.08,.38,.38)]
    verts=[]
    for z,w,d in rings:
        verts.extend([(-w/2,-d/2,z),(0,-d/2,z),(w/2,-d/2,z),
                      (w/2,d/2,z),(0,d/2,z),(-w/2,d/2,z)])
    faces=[(5,4,1,0),(4,3,2,1)]
    for j in range(len(rings)-1):
        for i in range(6):
            a=j*6+i;b=j*6+(i+1)%6;faces.append((a,b,b+6,a+6))
    faces.extend([(12,13,16,17),(13,14,15,16)])
    pier.add(verts,faces)
    # Four recessed faces and their borders are one surface each: no flat
    # duplicate wall lies behind the shallow inset panel.
    half=.19;inside=.135;lo=.13;hi=.90;z0=.08;z1=.95;depth=.008
    for n in range(4):
        angle=n*math.pi/2
        normal=(math.cos(angle),math.sin(angle));tangent=(-normal[1],normal[0])
        def vertex(u,z,d=0):return (normal[0]*(half-d)+tangent[0]*u,normal[1]*(half-d)+tangent[1]*u,z)
        outer=[vertex(-half,z0),vertex(half,z0),vertex(half,z1),vertex(-half,z1)]
        ring=[vertex(-inside,lo),vertex(inside,lo),vertex(inside,hi),vertex(-inside,hi)]
        inset=[vertex(-inside,lo,depth),vertex(inside,lo,depth),vertex(inside,hi,depth),vertex(-inside,hi,depth)]
        verts=outer+ring+inset
        faces=[]
        for j in range(4):
            k=(j+1)%4;faces.extend([(j,k,4+k,4+j),(4+j,4+k,8+k,8+j)])
        faces.append((8,9,10,11));pier.add(verts,faces)
    pier.rect_profile((0,0),[(.95,.38,.38),(.98,.45,.45),(1.04,.45,.45),(1.07,.36,.36)])
    column=Mesh('Venetian prototype column')
    column.lathe((0,0),[(z+1.07,r) for z,r in COLUMN],segments=24,
                 flutes=20,flute_depth=.004)
    return {'rails':rails,'balusters':turned,'pier':pier,'column':column}

# Fixed, source-independent District topology: half of the spindles are shown
# as narrow open posts. Walk uses a smaller turned profile. No solid wall bake.
def make_balusters(level, bridge):
    from venetian_ground import at,L,RAIL_OFFSET,PIERS,RAIL_START,RAIL_END,assert_frame,green_at
    assert_frame(bridge)
    m=Mesh('Fitting Venetian balusters')
    piers=PIERS
    profile=[(.16,.065),(.22,.052),(.28,.068),(.34,.07),(.40,.048),
             (.45,.038),(.50,.048),(.56,.071),(.62,.070),(.68,.049),(.74,.044),(.81,.06),(.92,.065)]
    for side in (-1,1):
        for i in range(1,math.ceil(L/.19)):
            t=i*.19
            if not RAIL_START<t<RAIL_END or green_at(t) or any(abs(t-p)<.29 for p in piers):continue
            if side==-1 and 150.24<t<151.76:continue
            if level=='district' and i%2:continue
            x,y=at(t,side*RAIL_OFFSET);z=bridge.height(x,y)
            if level=='district':m.box((x,y,z+.54),(.075,.075,.76))
            else:
                chosen=profile if level=='detail' else profile[::2]+[profile[-1]]
                chosen=sorted(set(chosen))
                m.lathe((x,y),[(z+h,r)for h,r in chosen],segments=10 if level=='detail' else 8)
    return m

def build_lod(name,settings,asset_dir):
    import os
    from pathlib import Path
    from southport3d.elevation import Elevations
    bridge=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/marine-lake-south.json').surface('south-venetian')
    level=settings['level']
    if settings.get('kind')=='lamps':
        from venetian_ground import at,RAIL_OFFSET,PIERS,GREEN_STANDARDS
        mesh=Mesh(name)
        for side in (-1,1):
            for t in PIERS:
                x,y=at(t,side*RAIL_OFFSET);z=bridge.height(x,y)+1.07
                profile=[(z,.16),(z+.08,.18),(z+.22,.14),(z+.34,.074),(z+1.28,.066),(z+1.4,.12),(z+1.50,.09),(z+1.58,.05)]
                mesh.lathe((x,y),profile,segments=8)
            for t in GREEN_STANDARDS:
                x,y=at(t,side*RAIL_OFFSET);z=bridge.height(x,y)
                scale=2.65/1.58
                profile=[(z+h*scale,r) for h,r in [(0,.16),(.08,.18),(.22,.14),(.34,.074),(1.28,.066),(1.4,.12),(1.50,.09),(1.58,.05)]]
                mesh.lathe((x,y),profile,segments=8)
    else:mesh=make_balusters(level,bridge);mesh.name=name
    return mesh.finish([])
