"""15 London Street: mock-Tudor cafe, north entrance bay and side alley.

Site frame: x runs back from the London Street frontage (x=7.5), y runs
along the street (negative towards Anchor Street), z is up. Street-facing
elevation frames put local u southward along the facade, local h up and
local z out towards the street. Widths and heights are visually calibrated
from dated Street View (see research/layout.json); hidden faces are estimates.
"""
import json
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(os.environ['SOUTHPORT_REPO_ROOT']) / 'lib'))
from southport3d.geometry import Mesh, face_matrix

D = json.loads((ROOT / 'research/layout.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
C = {}
for name in ['architecture', 'roof', 'shopfront', 'rear']:
    C[name] = bpy.data.collections.new(name)
    s.collection.children.link(C[name])


def material(name, colour, texture=None, roughness=.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = roughness
    if texture:
        node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = bpy.data.images.load(str(ROOT / 'textures' / (texture + '.png')))
        mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
    return mat


plaster = material('Lime-white plaster infill', (.80, .80, .77), roughness=.9)
timber = material('Black stained timber', (.028, .027, .03), roughness=.6)
render = material('Pale painted shop render', (.74, .75, .73), roughness=.85)
sage = material('Sage grey shop joinery', (.46, .49, .42), roughness=.55)
glass = material('Exterior glass', (.24, .28, .28), roughness=.38)
lead = material('Lead cames', (.09, .095, .10), roughness=.5)
shadow = material('Recess shadow', (.02, .022, .025))
tiles = material('Dark stall riser tiles', (.20, .21, .23), roughness=.35)
brick = material('Red common brick', (.45, .20, .13), 'brick')
clay = material('Red clay roof tile', (.55, .25, .17), 'tile')
iron = material('Black cast iron', (.035, .035, .038), roughness=.45)
door = material('Dark varnished door', (.17, .085, .045), roughness=.5)
flag = material('Grey concrete flags', (.47, .46, .43), 'flag')
felt = material('Grey roofing felt', (.27, .28, .28))
coping = material('Concrete coping', (.55, .54, .51))
metal = material('Rooflight metal', (.38, .40, .40), roughness=.5)

B = D['base_z']
FX, YN, YS, YA = D['front_x'], D['north_y'], D['south_y'], D['alley_south_y']
RX, RR = D['range_rear_x'], D['rear_x']
W = YN - YS                      # building width along the street
BAY = D['bay_width']
UC = D['gable_centre']            # midpoint of the main gable, excluding entrance bay
ZL, ZR = D['jetty_left'], D['jetty_right']
CANT0, CANT1 = D['cant']
CENTRE0,CENTRE1=D['centre_panel'];ZC=D['jetty_centre']
LW, RW, CL, GP = D['left_window'], D['right_window'], D['cant_light'], D['gable_posts']
SHOP = D['shop_top']
TIE = D['tie_beam']
EAVE = TIE + .25                 # top of tie beam = main side eaves
RIDGE = D['ridge_height']
PITCH = (RIDGE - EAVE) / ((W - BAY) / 2 + .3)
HB = RIDGE - PITCH * (UC - BAY)  # main roof edge against the bay strip
SILL = D['window_sill']
BURY = D['bury_z'] - B           # buried wall bottom, local height


def finish(mesh, part, materials, transform=None, roof_uv=False, recalc=False):
    obj = mesh.finish(materials, C[part])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    uv = obj.data.uv_layers.new(name='Authored metric repeat')
    for face in obj.data.polygons:
        axes = sorted(sorted(range(3), key=lambda i: abs(face.normal[i]))[:2])
        mat = obj.data.materials[face.material_index]
        for loop in face.loop_indices:
            v = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            if roof_uv:
                # Tile courses run parallel to each slope's eaves.
                if abs(face.normal.y) >= abs(face.normal.x):
                    u, h = v.x / 2.4, v.y / 2.2
                else:
                    u, h = v.y / 2.4, v.x / 2.2
            else:
                scale = {brick: (1.8, .6), clay: (2.4, 2.2), flag: (1.2, 1.2)}.get(mat, (1, 1))
                u, h = v[axes[0]] / scale[0], v[axes[1]] / scale[1]
            uv.data[loop].uv = (u, h)
    if transform is not None:
        obj.matrix_world = transform
    return obj


def plane(p1, p2, h0=0):
    """Frame on a vertical wall from p1 to p2; outward normal on the right."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    return face_matrix((p1[0], p1[1], B + h0), (dy / length, -dx / length, 0)), length


class Group:
    """One exported object built in a single wall frame (or world space)."""

    def __init__(self, name, frame, materials, part='architecture'):
        self.mesh = Mesh(name)
        self.frame, self.materials, self.part = frame, materials, part

    def box(self, u0, u1, h0, h1, z0, z1, m=0):
        self.mesh.box(((u0 + u1) / 2, (h0 + h1) / 2, (z0 + z1) / 2), (u1 - u0, h1 - h0, z1 - z0), m)

    def poly(self, points, z0, z1, m=0):
        self.mesh.outline(list(points), z0, z1, m)

    def strut(self, a, b, width, z0, z1, m=0):
        du, dh = b[0] - a[0], b[1] - a[1]
        length = math.hypot(du, dh)
        nu, nh = -dh / length * width / 2, du / length * width / 2
        self.poly([(a[0] + nu, a[1] + nh), (b[0] + nu, b[1] + nh),
                   (b[0] - nu, b[1] - nh), (a[0] - nu, a[1] - nh)], z0, z1, m)

    def done(self, **kw):
        return finish(self.mesh, self.part, self.materials, self.frame, **kw)


def wall(name, frame, u0, u1, h0, h1, openings=(), mat=plaster, part='architecture', depth=.36):
    """Wall split around real apertures; nothing is hidden inside solid walls."""
    xs = sorted({u0, u1, *(q for a, b, c, d in openings for q in (a, b))})
    zs = sorted({h0, h1, *(q for a, b, c, d in openings for q in (c, d))})
    g = Group('Envelope ' + name, frame, [mat], part)
    for a, b in zip(xs, xs[1:]):
        for lo, hi in zip(zs, zs[1:]):
            if any(c < (a + b) / 2 < d and e < (lo + hi) / 2 < f for c, d, e, f in openings):
                continue
            g.box(a, b, lo, hi, -depth, 0)
    return g.done()


def arc(a, b, spring, rise, inset=0, n=14):
    """Segmental arch intrados from left to right, optionally inset."""
    w = b - a
    radius = (w * w / 4 + rise * rise) / (2 * rise)
    cu, ch = (a + b) / 2, spring + rise - radius
    half = math.asin(w / 2 / radius)
    r = radius - inset
    return [(cu + r * math.cos(math.pi / 2 + half - 2 * half * i / n),
             ch + r * math.sin(math.pi / 2 + half - 2 * half * i / n)) for i in range(n + 1)]


window_meshes = {}


def leaded(name, frame, u0, u1, h0, h1, lights, part='architecture'):
    """Black timber window with mullions, transom and rectangular leaded quarries."""
    w, hh = u1 - u0, h1 - h0
    m = Mesh('Window ' + name)
    m.box((0, 0, -.17), (w, hh, .02), 3)
    m.box((0, 0, -.10), (w - .1, hh - .1, .02), 2)
    for x in (-w / 2 + .045, w / 2 - .045):
        m.box((x, 0, 0), (.09, hh, .12), 0)
    for y in (-hh / 2 + .045, hh / 2 - .045):
        m.box((0, y, 0), (w, .09, .12), 0)
    light = (w - .09) / lights
    for i in range(1, lights):
        m.box((-w / 2 + .045 + i * light, 0, -.01), (.07, hh - .09, .1), 0)
    transom = -hh / 2 + .045 + (hh - .09) * .66
    if hh > 1:
        m.box((0, transom, -.01), (w - .09, .07, .1), 0)
    for i in range(lights):
        left = -w / 2 + .045 + i * light
        count = max(2, round(light / .12))
        for j in range(1, count):
            m.box((left + light * j / count, 0, -.08), (.012, hh - .1, .012), 1)
    rows = max(3, round((hh - .1) / .14))
    for j in range(1, rows):
        m.box((0, -hh / 2 + .05 + (hh - .1) * j / rows, -.08), (w - .1, .012, .012), 1)
    if hh>1:
        # Repeated shallow ogee heads in the upper lights; keep this inside the
        # same Window object so distant receivers bake its actual silhouette.
        for i in range(lights):
            left=-w/2+.045+i*light
            count=max(3,round(light/.12))
            for j in range(count):
                x0=left+j*light/count;x1=left+(j+1)*light/count
                for drop in (.17,.25):
                    pts=[(x0+(x1-x0)*k/8,hh/2-drop+.035*math.sin(k*math.pi/8),-.065) for k in range(9)]
                    m.tube(pts,.007,1,sides=4)
    key = (round(w, 3), round(hh, 3), lights)
    obj = finish(m, part, [timber, lead, glass, shadow],
                 frame @ Matrix.Translation(((u0 + u1) / 2, (h0 + h1) / 2, 0)))
    if key in window_meshes:
        obj.data = window_meshes[key]
    else:
        window_meshes[key] = obj.data
    return obj


def projection(u):
    """Two oriels separated by a recessed flat and two canted returns."""
    if u < BAY:return .2
    if u <= CANT0:return ZL
    if u < CENTRE0:return ZL+(ZC-ZL)*(u-CANT0)/(CENTRE0-CANT0)
    if u <= CENTRE1:return ZC
    if u < CANT1:return ZC+(ZR-ZC)*(u-CENTRE1)/(CANT1-CENTRE1)
    return ZR


FS, _ = plane((FX, YN), (FX, YS))
FG, _ = plane((FX - ZL, YN), (FX - ZL, YS))
FR, _ = plane((FX - ZR, YN), (FX - ZR, YS))
FL, LL = plane((FX-ZL,YN-CANT0),(FX-ZC,YN-CENTRE0))
FC, LC = plane((FX-ZC,YN-CENTRE0),(FX-ZC,YN-CENTRE1))
FCR, LCR = plane((FX-ZC,YN-CENTRE1),(FX-ZR,YN-CANT1))
FB, _ = plane((FX-.2,YN),(FX-.2,YN-BAY))

# ---------------------------------------------------------------- shopfront
spring, rise = D['arch_spring'], D['arch_rise']
arches = D['arches']
shop = Group('Shop rendered arcade', FS, [render], 'shopfront')
edges = [BAY] + [q for a, b in arches for q in (a, b)] + [W]
for a, b in zip(edges[::2], edges[1::2]):
    shop.box(a, b, BURY, spring, -.36, 0)
outline = [(BAY, spring)]
for a, b in arches:
    outline += arc(a, b, spring, rise)
outline += [(W, spring), (W, SHOP), (BAY, SHOP)]
shop.poly(outline, -.36, 0)
shop.done()

frames=Group('Shop arched frames',FS,[sage,glass,tiles,shadow],'shopfront')
for i,(a,b) in enumerate(arches):
    mid=(a+b)/2
    outer=arc(a,b,spring,rise);inner=arc(a,b,spring,rise,.09)
    frames.poly(outer+inner[::-1],-.29,-.05)
    frames.poly(arc(a,b,spring,rise,.025)+arc(a,b,spring,rise,.045)[::-1],-.05,-.025)
    # One continuous arched glass receiver prevents slivers between the lower
    # rectangles and fanlight, including the zones over the entry jambs.
    bottom=0 if i==1 else .45
    frames.poly([(a+.08,bottom),(b-.08,bottom)]+arc(a,b,spring,rise,.075)[::-1],-.24,-.22,1)
    for u in (a,b-.08):
        for h0,h1 in ((.45,1.70),(1.80,spring)):
            frames.box(u,u+.08,h0,h1,-.29,-.05)
    frames.box(a,b,1.70,1.80,-.16,-.05)
    if i==1:
        left,right=mid-.44,mid+.44
        for u in (left-.08,right):frames.box(u,u+.08,0,1.70,-.16,-.05)
        frames.box(left,right,0,.12,-.16,-.05)
        frames.box(left,right,.12,1.70,-.13,-.11,1)
        frames.box(left-.08,right+.08,BURY,.04,-.40,.02,2)
        frames.box(right-.12,right-.095,.88,1.08,-.045,-.005)
        for u0,u1 in ((a,left-.08),(right+.08,b)):
            frames.box(u0,u1,BURY,.45,-.36,-.10,2)
            frames.box(u0,u1,.45,.53,-.17,-.04)
    else:
        frames.box(a,b,BURY,.45,-.36,-.10,2)
        frames.box(a,b,.45,.53,-.17,-.04)
        frames.box(mid-.03,mid+.03,.53,1.70,-.16,-.06)
frames.done()

# Documented Love To Eat frontage, matching the supplied 2020-era views.
from southport3d.geometry import text_object
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
lettering=material('Historic cafe lettering',(.055,.095,.16))
txt=text_object('Temporary cafe lettering','LOVE · TO · EAT',(0,0,0),(0,0,1),.10,1.25,font,lettering,extrude=.006)
bpy.ops.object.select_all(action='DESELECT');txt.select_set(True);bpy.context.view_layer.objects.active=txt
bpy.ops.object.convert(target='MESH')
m=Mesh('Fine historical cafe lettering')
m.add([tuple(txt.matrix_world@v.co) for v in txt.data.vertices],[tuple(f.vertices) for f in txt.data.polygons])
bpy.data.objects.remove(txt,do_unlink=True)
finish(m,'shopfront',[lettering],FS@Matrix.Translation(((BAY+W)/2,3.075,.012)))

# North entrance bay: gated porch with a panelled door at its back.
porch = Group('Shop entrance porch', FS, [render, tiles, door, glass, timber], 'shopfront')
porch.box(0, .10, BURY, SHOP, -1.5, 0)
porch.box(BAY - .10, BAY, BURY, SHOP, -1.5, 0)
porch.box(.10, BAY - .10, BURY, SHOP, -1.6, -1.4)
porch.box(.10, BAY - .10, 2.9, SHOP, -1.4, 0, 4)
porch.box(.10, BAY - .10, BURY, .05, -1.4, 0, 1)
porch.box(.38, 1.32, .05, 2.35, -1.40, -1.35, 2)
porch.box(.38, 1.32, 2.42, 2.82, -1.40, -1.37, 3)
for u in (.33, 1.32):
    porch.box(u, u + .05, .05, 2.85, -1.40, -1.32, 4)
porch.box(.33, 1.37, 2.35, 2.42, -1.40, -1.32, 4)
porch.done()

fine = Group('Fine porch ironwork and door furniture', FS, [iron, metal], 'shopfront')
for k in range(13):
    u = .16 + k * (BAY - .32) / 12
    fine.box(u - .012, u + .012, .05, 1.92, .015, .04)
for h in (.12, 1.05, 1.86):
    fine.box(.12, BAY - .12, h - .02, h + .02, .01, .045)
fine.box(.62, .66, 1.0, 1.25, -1.36, -1.30, 1)
fine.box(.48, .82, 1.30, 1.38, -1.36, -1.32, 1)
fine.done()

# Cast-iron bracket under the jetty corner beside NatWest (snag photograph).
m = Mesh('Fine cast-iron jetty bracket')
y = YN - .12
m.tube([(FX + .02, y, B + 2.35), (FX - ZL + .08, y, B + SHOP - .03)], .035)
m.tube([(FX + .02, y, B + SHOP - .05), (FX - ZL + .05, y, B + SHOP - .05)], .03)
m.tube([(FX - .12 - .18 * math.cos(t * math.pi / 6), y, B + 2.95 + .18 * math.sin(t * math.pi / 6))
        for t in range(13)], .018)
finish(m, 'shopfront', [iron])

# ------------------------------------------------------------- jetty storey
m = Mesh('Envelope jetty floor')
m.outline([(FX,YN),(FX-.2,YN),(FX-.2,YN-BAY),(FX-ZL,YN-BAY),
           (FX-ZL,YN-CANT0),(FX-ZC,YN-CENTRE0),(FX-ZC,YN-CENTRE1),
           (FX-ZR,YN-CANT1),(FX-ZR,YS),(FX,YS)],B+SHOP,B+SHOP+.27)
finish(m, 'architecture', [timber])

brackets = Group('Timber jetty brackets', FS, [timber])
for k in range(12):
    u = .25 + k * (W - .5) / 11
    p = projection(u) - .03
    brackets.box(u - .08, u + .08, SHOP - .30, SHOP, 0, p * .55)
    brackets.strut((u, SHOP - .30), (u, SHOP), .16, p * .55, p)
    brackets.box(u - .08, u + .08, SHOP - .12, SHOP, p * .55, p)
brackets.done()

top = 6.35
# Equal front-facing oriels; the right bay has one visible canted return light.
wall('first floor north bay',FB,0,BAY,SHOP+.27,TIE)
wall('first floor left oriel',FG,BAY,CANT0,SHOP+.27,TIE,[(LW[0],LW[1],SILL,top)])
wall('first floor left return',FL,0,LL,SHOP+.27,TIE,[(CL[0],CL[1],SILL,top)])
wall('first floor centre recess',FC,0,LC,SHOP+.27,TIE)
wall('first floor right return',FCR,0,LCR,SHOP+.27,TIE,[(CL[0],CL[1],SILL,top)])
wall('first floor right',FR,CANT1,W,SHOP+.27,TIE,[(RW[0],RW[1],SILL,top)])
leaded('first floor left',FG,LW[0],LW[1],SILL,top,LW[2])
leaded('first floor left return',FL,CL[0],CL[1],SILL,top,1)
leaded('first floor right return',FCR,CL[0],CL[1],SILL,top,1)
leaded('first floor right',FR,RW[0],RW[1],SILL,top,RW[2])
# Close the short step between the recessed entrance bay and left oriel.
step,stepwidth=plane((FX-.2,YN-BAY),(FX-ZL,YN-BAY))
wall('first floor oriel north cheek',step,0,stepwidth,SHOP+.27,TIE,depth=.05)


def frame_timbers(name, frame, u0, u1, posts):
    """Close-studded apron, sill beam, posts and head rail on one plane."""
    g = Group('Timber ' + name, frame, [timber])
    g.box(u0, u1, SHOP, SHOP + .30, -.05, .12)
    n = max(2, round((u1 - u0) / .72))
    for k in range(n + 1):
        u = min(max(u0 + (u1 - u0) * k / n, u0 + .055), u1 - .055)
        g.box(u - .055, u + .055, SHOP + .30, SILL-.16, 0, .06)
    g.box(u0, u1, SILL-.16, SILL, -.02, .10)
    for u in posts:
        g.box(u - .06, u + .06, SILL, top, 0, .06)
    g.box(u0, u1, top, TIE, -.01, .07)
    for z,h,out in [(SHOP+.03,.055,.16),(SHOP+.27,.055,.15),(SILL-.14,.045,.14),(SILL-.01,.045,.13),(top+.035,.045,.11)]:
        g.box(u0,u1,z,z+h,out-.045,out)
    for h in (SHOP+.065,SHOP+.20,SILL-.10):
        g.mesh.tube([(u0,h,.15),(u1,h,.15)],.025,sides=8)
    return g


frame_timbers('first floor left oriel',FG,BAY,CANT0,[BAY+.03,LW[0]-.06,CANT0-.06]).done()
left=frame_timbers('north entry bay',FB,0,BAY,[.06,BAY-.06])
left.strut((.12,top-.05),(BAY-.15,SILL+.08),.19,0,.08)
left.done()
frame_timbers('left oriel return',FL,0,LL,[.055,LL-.055]).done()
frame_timbers('recessed centre',FC,0,LC,[.055,LC/2,LC-.055]).done()
frame_timbers('right oriel return',FCR,0,LCR,[.055,LCR-.055]).done()
frame_timbers('first floor right',FR,CANT1,W,[CANT1+.03,RW[1]+.06,W-.06]).done()
# The arch spans the recess in the projecting head beam, rather than lying
# flat on an invented sloping wall. Its soffit leaves the return glazing clear.
centre=Group('Timber recessed centre arch',FG,[timber])
head=arc(CANT0+.05,CANT1-.05,5.95,.32)
centre.poly(head+[(CANT1-.05,top),(CANT0+.05,top)],0,.08)
centre.done()
orn=Group('Fine recessed arch spandrel carving',FG,[timber])
for sign in (-1,1):
    edge=CANT0+.05 if sign<0 else CANT1-.05
    pts=[(edge-sign*.07,top-.05),(edge-sign*.20,top-.07),(edge-sign*.36,top-.17),(edge-sign*.46,top-.30)]
    for a,b in zip(pts,pts[1:]):orn.strut(a,b,.022,.08,.105)
    for k in range(3):
        u=edge-sign*(.13+k*.09);h=top-.08-k*.045
        orn.strut((u,h),(u-sign*.07,h-.08),.018,.08,.105)
orn.done()

# Tie beam across the whole front, solid gable floor and bay ledge behind it.
g = Group('Timber tie beam', FG, [timber])
g.box(BAY, W, TIE, EAVE, -.02, .13)
for h,dep in [(TIE,.18),(TIE+.07,.16),(EAVE-.04,.19)]:g.box(BAY,W,h,h+.035,dep-.035,dep)
g.box(UC - .55, UC + .55, TIE - .04, EAVE + .02, .12, .16)
g.done()
m = Mesh('Envelope gable floor')
m.box(((FX - ZL - D['gable_projection'] + FX) / 2, (YN - BAY + YS) / 2, B + (TIE + EAVE) / 2), (ZL+D['gable_projection'], W - BAY, EAVE - TIE))
finish(m, 'architecture', [timber])
# Interpreted scrollwork, not an invented inscription: the close view resolves
# curled leaves and a central boss but not a reliably readable motif.
m = Mesh('Fine carved tie-beam boss')
m.ellipsoid((0,0,.035),(.14,.10,.055),0,16,8)
for sign in (-1,1):
    for offset,rad in [(.25,.11),(.49,.075)]:
        pts=[]
        for k in range(31):
            angle=k/30*math.pi*2.2;r=rad*(1-k/42)
            pts.append((sign*(offset+r*math.cos(angle)),r*math.sin(angle),.045))
        m.tube(pts,.018,sides=6)
    m.tube([(sign*.08,-.04,.025),(sign*.19,-.12,.025),(sign*.38,-.11,.025),(sign*.55,-.02,.025)],.018,sides=6)
finish(m,'architecture',[timber],FG@Matrix.Translation((UC,TIE+.13,.18)))

# Corner closures where the projecting storey meets NatWest and the alley.
north, _ = plane((FX, YN), (FX - .2, YN))
wall('first floor north return', north, 0, .2, SHOP + .27, TIE, depth=.05)
south, _ = plane((FX - ZR, YS), (FX, YS))
wall('first floor south return', south, 0, ZR, SHOP + .27, TIE, depth=.05)

FGA = FG @ Matrix.Translation((0, 0, D['gable_projection']))
# ------------------------------------------------------------- street gable
gable_top = RIDGE - .14
half = (gable_top - EAVE) / PITCH
# The north bay stays open; the bargeboard ends beside its attic window.
g = Group('Envelope street gable infill', FGA, [plaster])
g.poly([(UC-half, EAVE), (UC+half, EAVE), (UC, gable_top)], -.25-D['gable_projection'], 0)
g.done()
g = Group('Timber street gable framing', FGA, [timber])


def under_roof(u, drop=0):
    return gable_top - drop - PITCH * abs(u - UC)


# Single central king post with four straight outward-rising braces per side.
g.box(UC-.09,UC+.09,EAVE,gable_top,0,.09)
SLOPE=.62
for sign in (-1,1):
    for h0 in (EAVE-.6,EAVE+.25,EAVE+1.10,EAVE+1.95):
        run0=max(0,(EAVE+.04-h0)/SLOPE)
        start=(UC+sign*(.09+run0),max(EAVE+.04,h0))
        run=(under_roof(start[0])-.08-start[1])/(SLOPE+PITCH)
        if run>0:g.strut(start,(start[0]+sign*run,start[1]+SLOPE*run),.15,0,.07)
g.done()

barge = Group('Roof bargeboards and finial', FGA, [timber], 'roof')
for u0, u1 in ((BAY-.3, UC), (UC, W + .3)):
    t0, t1 = RIDGE + .1 - PITCH * abs(u0 - UC), RIDGE + .1 - PITCH * abs(u1 - UC)
    barge.poly([(u0,t0),(u1,t1),(u1,t1-.38),(u0,t0-.38)],.32,.40)
    for drop in (.04,.15,.30):
        barge.poly([(u0,t0-drop),(u1,t1-drop),(u1,t1-drop-.035),(u0,t0-drop-.035)],.40,.44)
barge.box(UC-.07,UC+.07,RIDGE-.40,RIDGE+.10,.30,.46)
barge.box(UC-.10,UC+.10,RIDGE+.06,RIDGE+.14,.29,.47)
# Shaped corner bracket under the southern barge foot (snag photograph).
barge.poly([(W - .12, EAVE - .35), (W + .2, EAVE - .35), (W + .2, EAVE - .55), (W - .02, EAVE - .85),
            (W - .12, EAVE - .85)], .05, .34)
barge.done()
for side,u in [(-1,BAY+.04),(1,W-.10)]:
    g=Group('Fine carved barge bracket '+str(side),FGA,[timber])
    htop=under_roof(u)+.03;bottom=htop-.76
    outline=[(u-.08,htop),(u+.16,htop)]+[(u-.035+.195*(1-t/10)**.5,htop-.76*t/10) for t in range(1,11)]+[(u-.08,bottom)]
    g.poly(outline,.08,.31)
    for k in range(3):g.box(u-.10,u+.08,bottom+.01+k*.055,bottom+.04+k*.055,.12,.34)
    g.done()


# Main roof: front gable, ridge running back from the street, eaves over the alley.
def prism(name, section, x0, x1, materials, part='roof'):
    m = Mesh(name)
    n = len(section)
    verts = [(x0, y, z) for y, z in section] + [(x1, y, z) for y, z in section]
    faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    m.add(verts, faces)
    return finish(m, part, materials, roof_uv=True, recalc=True)


def roof_shell(name, upper, faces, material=clay, part='roof', thickness=.14):
    """Closed slab from a connected roof surface, without internal seam walls."""
    n=len(upper)
    counts={}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1
    sides=[(a,b,b+n,a+n) for (a,b),count in counts.items() if count==1]
    vertices=upper+[(x,y,z-thickness) for x,y,z in upper]
    closed=faces+[tuple(i+n for i in reversed(f)) for f in faces]+sides
    m=Mesh(name);m.add(vertices,closed)
    return finish(m,part,[material],roof_uv=True,recalc=True)


yr=YN-UC;yn_eave=YN-BAY+.3;ys_eave=YS-.3
roof_front=FX-ZL-.35-D['gable_projection']
roof_back=roof_front+D['main_roof_depth']
RX=roof_back-.12
main_north_back=roof_back-D['main_rear_skew']
ridge_back=roof_back-D['main_hip_run']
roof_shell('Roof main clay shell',[
    (roof_front,yn_eave,B+EAVE),(roof_front,yr,B+RIDGE),
    (roof_front,ys_eave,B+EAVE),(roof_back,ys_eave,B+EAVE),
    (main_north_back,yn_eave,B+EAVE),(ridge_back,yr,B+RIDGE)],
    [(0,1,5,4),(1,2,3,5),(3,4,5)])
m=Mesh('Fine alley eaves gutter')
m.tube([(roof_front,ys_eave-.06,B+EAVE-.1),(roof_back,ys_eave-.06,B+EAVE-.1)],.06,0,8)
finish(m,'roof',[iron])
m=Mesh('Roof main ridge tiles')
m.box(((roof_front+ridge_back)/2,yr,B+RIDGE+.04),(ridge_back-roof_front,.20,.10))
finish(m,'roof',[clay])
for y in (yn_eave,ys_eave):
    m=Mesh('Roof rear hip tiles '+str(y))
    m.tube([(ridge_back,yr,B+RIDGE+.025),(main_north_back if y==yn_eave else roof_back,y,B+EAVE+.025)],.065,0,8)
    finish(m,'roof',[clay])

# Narrow north bay: small three-light attic window under its hipped clay roof,
# set back behind the tie beam and bargeboard (Nov2020 close, May2011 frontal).
m = Mesh('Envelope bay attic ledge')
m.box((FX - .425, YN - BAY / 2, B + TIE + .06), (.45, BAY, .12))
finish(m, 'architecture', [timber])
wall('bay top storey', FB, 0, BAY, TIE, D['bay_eaves'], [(.26,1.15,6.90,7.50)])
leaded('bay top storey', FB,.26,1.15,6.90,7.50,3)
g = Group('Timber bay top storey', FB, [timber])
for u in (.06, BAY - .06):
    g.box(u - .06, u + .06, TIE, D['bay_eaves'], 0, .06)
g.box(0, BAY, D['bay_eaves'] - .14, D['bay_eaves'], -.01, .08)
g.done()
north_back=FX-.45+D['north_roof_depth']
side, _ = plane((FX - .2, YN - BAY), (north_back, YN - BAY))
wall('bay side above main roof', side, 0, north_back - FX + .2, EAVE - .2, D['bay_eaves']-.12, mat=plaster, depth=.25)

be,br=D['bay_eaves'],D['bay_ridge'];north_h=br
xf=FX-.45;backx=north_back;y0=YN-BAY;y1=YN-.02
# Lean-to against NatWest: high edge stays against the wall. Only the front
# turns down into a hip; there is no ridge through the middle of this strip.
upper=[(xf,y0,be),(backx,y0,be),(backx,y1,br),(xf+.85,y1,br),(xf,y1,be)]
faces=[(0,1,2,3),(0,3,4)]
n=len(upper);verts=[(x,y,z+B) for x,y,z in upper]+[(x,y,z+B-.12) for x,y,z in upper]
faces += [tuple(i+n for i in reversed(f)) for f in list(faces)]
for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
m=Mesh('Roof north bay clay shell');m.add(verts,faces)
finish(m,'roof',[clay],roof_uv=True,recalc=True)
m=Mesh('Roof north wall flashing')
m.box(((xf+.85+backx)/2,y1-.025,B+br+.025),(backx-xf-.85,.05,.10))
finish(m,'roof',[iron])

# ------------------------------------------------- side, rear and party walls
alley, _ = plane((FX, YS), (RX, YS))
wall('alley side lower panelled',alley,0,2.6,BURY,SHOP,mat=sage)
wall('alley side lower',alley,2.6,RX-FX,BURY,SHOP,mat=render)
wall('alley side upper timbered',alley,0,RX-FX,SHOP,EAVE+.1)
g=Group('Timber alley side return',alley,[timber])
for lo,hi in [(SHOP,SHOP+.22),(SILL-.16,SILL),(TIE,EAVE)]:g.box(0,RX-FX,lo,hi,0,.07)
for k in range(16):
    u=.06+k*(RX-FX-.12)/15
    g.box(u-.055,u+.055,SHOP+.22,TIE,0,.06)
for h in (SHOP+.03,SHOP+.19,SILL-.13,SILL-.01):g.box(0,RX-FX,h,h+.035,.07,.095)
g.done()
# Panelled sage-painted return below the jetty, visible from William Hill.
g=Group('Shop alley panelled return',alley,[sage,tiles],'shopfront')
g.box(0,2.6,.04,.45,0,.06,1)
for lo,hi in [(.45,.52),(1.55,1.61),(2.03,2.09)]:g.box(0,2.6,lo,hi,.025,.09)
for u in (.04,.88,1.72,2.56):g.box(u-.03,u+.03,.52,2.03,.025,.07)
g.done()

# Rear hip closes at the eaves, not an invented tall rear gable.
rearwall,rear_width=plane((RX,YS),(main_north_back-.12,YN-BAY))
wall('main range rear wall',rearwall,.08,rear_width,BURY,EAVE+.05,mat=plaster)
g=Group('Timber main rear wall',rearwall,[timber])
for h in (SHOP,6.15,EAVE-.18):g.box(0,rear_width,h,h+.12,0,.06)
for u in (.08,1.6,3.1,4.6,6.1,W-BAY-.08):g.box(u-.05,u+.05,SHOP,EAVE-.14,0,.06)
g.done()

# The white middle deck wraps behind the short entrance roof and the main
# rear hip. The attached lower red wing occupies its alley-side edge.
mid_end=D['rear_flat_end_x'];mh=D['rear_flat_height']
wing_y=YS+D['rear_wing_width'];wh=D['rear_wing_eave']
def range_box(name,x0,x1,y0,y1,height,wallmat=brick,roofmat=felt,add_roof=True):
    m=Mesh('Rear '+name+' walls')
    m.box(((x0+x1)/2,(y0+y1)/2,B+(BURY+height-.16)/2),(x1-x0,y1-y0,height-.16-BURY))
    finish(m,'rear',[wallmat])
    if not add_roof:return
    m=Mesh('Rear '+name+' roof')
    m.box(((x0+x1)/2,(y0+y1)/2,B+height-.08),(x1-x0,y1-y0,.16))
    finish(m,'rear',[roofmat])

range_box('north middle deck',north_back,RX,YN-BAY,YN,mh,plaster,coping,add_roof=False)
range_box('middle deck',RX,mid_end,wing_y,YN,mh,plaster,coping,add_roof=False)
# A single L-shaped roof avoids coincident seams between the wraparound parts.
roof_shell('Rear continuous middle deck',[(north_back,YN,B+mh),
    (mid_end,YN,B+mh),(mid_end,wing_y,B+mh),(RX,wing_y,B+mh),
    (main_north_back-.12,YN-BAY,B+mh),(north_back,YN-BAY,B+mh)],
    [(0,1,2,3,4,5)],material=coping,part='rear',thickness=.16)
# Close the entrance lean-to's rear and party wall at its actual short depth.
r,_=plane((north_back,YN-BAY),(north_back,YN))
g=Group('Envelope north roof rear wall',r,[plaster])
g.poly([(0,BURY),(BAY,BURY),(BAY,br-.12),(0,be-.12)],-.20,0);g.done()
party,_=plane((north_back,YN),(FX,YN))
g=Group('Envelope short north party wall',party,[brick])
endheight=be+(br-be)*(FX-xf)/.85-.12
hipu=north_back-(xf+.85)
# The rendered porch jamb owns the front 1.5 m below the shop head.
# Notch the brick party wall around it instead of overlaying its outside face.
# Rear wall owns its .20 m corner thickness.
g.poly([(.20,BURY),(north_back-FX-1.5,BURY),(north_back-FX-1.5,SHOP),
        (north_back-FX,SHOP),(north_back-FX,endheight),(hipu,br-.12),(.20,br-.12)],-.2,0)
g.done()

# Lower single-slope wing with a hip at the rear, visible in both rear photos.
wing_tip=mid_end-.75
roof_shell('Rear red wing roof',[(RX,YS,B+wh),(RX,wing_y,B+mh),
    (wing_tip,wing_y,B+mh),(mid_end,YS,B+wh)],[(0,1,2),(0,2,3)],part='rear')
rs,_=plane((RX,YS),(mid_end,YS))
wall('red wing alley wall',rs,0,mid_end-RX,BURY,wh-.14,mat=plaster,part='rear')
g=Group('Timber rear wing framing',rs,[timber])
for h in (SHOP,wh-.28):g.box(0,mid_end-RX,h,h+.12,0,.055)
for k in range(5):
    u=.06+k*(mid_end-RX-.12)/4;g.box(u-.05,u+.05,SHOP,wh-.14,0,.055)
g.done()
re,_=plane((mid_end,YS),(mid_end,wing_y))
# Alley wall owns the corner; the rear return starts at its inner face.
wall('red wing rear wall',re,.36,D['rear_wing_width'],BURY,wh-.14,mat=plaster,part='rear')
# Grey roof is visibly stepped, with four lights on the broad section and
# one long light on its narrower, higher rear section. Plan offsets estimated.
step=D['rear_grey_step_x'];gh=D['rear_grey_height'];uh=D['rear_upper_height']
range_box('broad grey range',mid_end,step,YS,YN,gh)
range_box('upper grey range',step,RR,YS+1.0,YN-1.0,uh)
range_box('rear south shoulder',step,RR,YS,YS+1.0,gh)
range_box('rear north shoulder',step,RR,YN-1.0,YN,gh)

def skylight(name,x,y,z,sx,sy,slope=0):
    # Flush rectangular glass in a shallow raised curb; no invented pyramids.
    m=Mesh('Rear rooflight '+name)
    m.box((0,0,0),(sx,sy,.16),0)
    m.box((0,0,.09),(sx-.12,sy-.12,.025),1)
    m.box((0,0,.11),(.045,sy-.12,.035),0)
    transform=Matrix.Translation((x,y,B+z+.09)) @ Matrix.Rotation(slope,4,'X')
    finish(m,'rear',[metal,glass],transform)

skylight('middle north',11.25,YN-.73,mh,.85,.85)
skylight('middle central',15.25,YN-2.5,mh,1.25,1.25)
wx=15.05;wy=YS+1.25
# Dark rectangular light on the main rear hip, visible in the rear oblique.
a=Vector((ridge_back,yr,B+RIDGE));b=Vector((roof_back,ys_eave,B+EAVE));c=Vector((main_north_back,yn_eave,B+EAVE))
normal=(b-a).cross(c-a).normalized()
if normal.z<0:normal=-normal
m=Mesh('Rear rooflight main hip');m.box((0,0,0),(.62,.85,.12),0);m.box((0,0,.07),(.50,.73,.025),1)
transform=Matrix.Translation(a*.40+b*.40+c*.20+normal*.08) @ Vector((0,0,1)).rotation_difference(normal).to_matrix().to_4x4()
finish(m,'rear',[metal,glass],transform)
skylight('red wing',wx,wy,wh+(mh-wh)*.5,.68,.80,math.atan2(mh-wh,D['rear_wing_width']))
for i,(x,y) in enumerate(((19.2,YS+2.0),(21.4,YN-2.0),(24.2,YS+2.0),(24.0,YN-2.0))):
    skylight('grey '+str(i),x,y,gh,1.3,1.55)
skylight('upper long',28.2,(YN+YS)/2,uh,1.2,2.7)
m=Mesh('Rear grey access hatch')
m.box((22.3,(YN+YS)/2,B+gh+.08),(.85,.85,.16))
finish(m,'rear',[metal])

# The alley itself: paved floor along the whole depth, closed by an estimated
# rear wall and gate. Its southern side is William Hill's (placeholder) wall.
m = Mesh('Rear alley floor')
m.box(((FX + RR) / 2, (YS + YA) / 2, B - .083), (RR - FX, YS - YA, .16))
finish(m, 'rear', [flag])
ae, _ = plane((RR - .25, YS), (RR - .25, YA))
wall('alley rear end', ae, 0, YS - YA, BURY, 2.2, [(.15, 1.17, 0, 1.95)], brick, 'rear', .25)
g = Group('Rear alley timber gate', ae, [door], 'rear')
g.box(.15, 1.17, .05, 1.95, -.15, -.12)
for k in range(1, 6):
    u = .15 + k * 1.02 / 6
    g.box(u - .008, u + .008, .05, 1.95, -.12, -.11)
g.box(.15, 1.17, .3, .42, -.10, -.07)
g.box(.15, 1.17, 1.55, 1.67, -.10, -.07)
g.done()

m = Mesh('Fine downpipe')
m.tube([(FX - ZL - .09, YN - .1, B + TIE), (FX - ZL - .09, YN - .1, B + SHOP + .4),
        (FX - .09, YN - .1, B + SHOP - .1), (FX - .09, YN - .1, B + .05)], .045)
finish(m, 'architecture', [iron])

for image in bpy.data.images:
    if image.source == 'FILE':
        image.pack()
s.render.engine = 'CYCLES'
s.cycles.samples = 24
s.cycles.use_denoising = True
s.world = s.world or bpy.data.worlds.new('World')
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.65, .70, .76, 1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
sun.data.energy = 2.5
sun.rotation_euler = (.75, -.35, -1.9)
s.collection.objects.link(sun)
camera = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))
camera.data.type = 'ORTHO'
s.collection.objects.link(camera)
s.camera = camera
s.render.resolution_x = 1200
s.render.resolution_y = 900
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'models/london-street-15.blend'))
