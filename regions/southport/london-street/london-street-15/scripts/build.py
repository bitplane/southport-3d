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
from mathutils import Matrix

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
glass = material('Exterior glass', (.10, .14, .16), roughness=.2)
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
pot = material('Terracotta chimney pot', (.50, .24, .14))

B = D['base_z']
FX, YN, YS, YA = D['front_x'], D['north_y'], D['south_y'], D['alley_south_y']
RX, RR = D['range_rear_x'], D['rear_x']
W = YN - YS                      # building width along the street
BAY = D['bay_width']
UC = D['gable_centre']            # gable centred on the whole frontage
ZL, ZR = D['jetty_left'], D['jetty_right']
CANT0, CANT1 = D['cant']
CENTRE0,CENTRE1=D['centre_panel'];ZC=D['jetty_centre']
LW, RW, CL, GP = D['left_window'], D['right_window'], D['cant_light'], D['gable_posts']
SHOP = D['shop_top']
TIE = D['tie_beam']
EAVE = TIE + .25                 # top of tie beam = main side eaves
RIDGE = D['ridge_height']
PITCH = (RIDGE - EAVE) / UC
HB = RIDGE - PITCH * (UC - BAY)  # main roof edge against the bay strip
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
        count = max(2, round(light / .15))
        for j in range(1, count):
            m.box((left + light * j / count, 0, -.08), (.012, hh - .1, .012), 1)
    rows = max(3, round((hh - .1) / .18))
    for j in range(1, rows):
        m.box((0, -hh / 2 + .05 + (hh - .1) * j / rows, -.08), (w - .1, .012, .012), 1)
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

frames = Group('Shop arched frames', FS, [sage, glass, tiles, door, shadow], 'shopfront')
for i, (a, b) in enumerate(arches):
    mid = (a + b) / 2
    outer = arc(a, b, spring, rise)
    inner = arc(a, b, spring, rise, .09)
    frames.poly(outer + inner[::-1], -.16, -.05)
    frames.poly([(a, spring)] + outer[1:-1] + [(b, spring)], -.14, -.12, 1)
    for u in (a, b - .08):
        frames.box(u, u + .08, .45, spring, -.16, -.05)
    frames.box(a, b, spring - .05, spring + .05, -.16, -.05)
    frames.box(a, b, .45, .53, -.17, -.04)
    if i == 1:
        # Central entrance: glazed door between narrow sidelights.
        for u in (mid - .52, mid + .44):
            frames.box(u, u + .08, 0, spring, -.24, -.05)
        frames.box(mid - .44, mid + .44, 0, .04, -.26, -.05, 2)
        frames.box(mid - .44, mid + .44, .05, spring - .05, -.24, -.22, 3)
        frames.box(mid - .34, mid + .34, .25, spring - .25, -.22, -.21, 1)
        frames.box(mid - .44, mid + .44, 0, spring, -.30, -.28, 4)
        for u0, u1 in ((a + .08, mid - .52), (mid + .52, b - .08)):
            frames.box(u0, u1, BURY, .45, -.36, -.10, 2)
            frames.box(u0, u1, .53, spring - .05, -.14, -.12, 1)
        frames.box(mid - .52, mid - .44, .45, .53, -.24, -.05)
    else:
        frames.box(a, b, BURY, .45, -.36, -.10, 2)
        frames.box(a + .08, b - .08, .53, spring - .05, -.14, -.12, 1)
        frames.box(mid - .03, mid + .03, .53, spring - .05, -.16, -.06)
frames.done()

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
wall('first floor left oriel',FG,BAY,CANT0,SHOP+.27,TIE,[(LW[0],LW[1],4.92,top)])
wall('first floor left return',FL,0,LL,SHOP+.27,TIE)
wall('first floor centre recess',FC,0,LC,SHOP+.27,TIE)
wall('first floor right return',FCR,0,LCR,SHOP+.27,TIE,[(CL[0],CL[1],4.92,top)])
wall('first floor right',FR,CANT1,W,SHOP+.27,TIE,[(RW[0],RW[1],4.92,top)])
leaded('first floor left',FG,LW[0],LW[1],4.92,top,LW[2])
leaded('first floor right return',FCR,CL[0],CL[1],4.92,top,1)
leaded('first floor right',FR,RW[0],RW[1],4.92,top,RW[2])
# Close the short step between the recessed entrance bay and left oriel.
step,stepwidth=plane((FX-.2,YN-BAY),(FX-ZL,YN-BAY))
wall('first floor oriel north cheek',step,0,stepwidth,SHOP+.27,TIE,depth=.05)


def frame_timbers(name, frame, u0, u1, posts):
    """Close-studded apron, sill beam, posts and head rail on one plane."""
    g = Group('Timber ' + name, frame, [timber])
    g.box(u0, u1, SHOP, SHOP + .30, -.05, .12)
    n = max(2, round((u1 - u0) / .42))
    for k in range(n + 1):
        u = min(max(u0 + (u1 - u0) * k / n, u0 + .055), u1 - .055)
        g.box(u - .055, u + .055, SHOP + .30, 4.76, 0, .06)
    g.box(u0, u1, 4.76, 4.92, -.02, .10)
    for u in posts:
        g.box(u - .06, u + .06, 4.92, top, 0, .06)
    g.box(u0, u1, top, TIE, -.01, .07)
    for z,h,out in [(SHOP+.03,.055,.16),(SHOP+.27,.055,.15),(4.78,.045,.14),(4.91,.045,.13),(top+.035,.045,.11)]:
        g.box(u0,u1,z,z+h,out-.045,out)
    return g


frame_timbers('first floor left oriel',FG,BAY,CANT0,[BAY+.03,CANT0-.06]).done()
left=frame_timbers('north entry bay',FB,0,BAY,[.06,BAY-.06])
pts=[(.12+(BAY-.24)*math.sin(t*math.pi/16),4.95+1.3*math.cos(t*math.pi/16)) for t in range(9)]
for a,b in zip(pts,pts[1:]):left.strut(a,b,.12,0,.06)
left.done()
frame_timbers('left oriel return',FL,0,LL,[.055,LL-.055]).done()
frame_timbers('recessed centre',FC,0,LC,[.055,LC/2,LC-.055]).done()
frame_timbers('right oriel return',FCR,0,LCR,[.055,LCR-.055]).done()
frame_timbers('first floor right',FR,CANT1,W,[RW[1]+.06,8.6,W-.06]).done()
# The arch spans the recess in the projecting head beam, rather than lying
# flat on an invented sloping wall. Its soffit leaves the return glazing clear.
centre=Group('Timber recessed centre arch',FG,[timber])
head=arc(CANT0+.05,CANT1-.05,5.95,.32)
centre.poly(head+[(CANT1-.05,top),(CANT0+.05,top)],0,.08)
centre.done()

# Tie beam across the whole front, solid gable floor and bay ledge behind it.
g = Group('Timber tie beam', FG, [timber])
g.box(0, W, TIE, EAVE, -.02, .13)
g.box(UC - .55, UC + .55, TIE - .04, EAVE + .02, .12, .16)
g.done()
m = Mesh('Envelope gable floor')
m.box(((FX - ZL + FX) / 2, (YN - BAY + YS) / 2, B + (TIE + EAVE) / 2), (ZL, W - BAY, EAVE - TIE))
finish(m, 'architecture', [timber])
m = Mesh('Fine carved tie-beam boss')
m.ellipsoid((0, 0, 0), (.36, .13, .07), 0, 16, 8)
for side in (-1, 1):
    m.ellipsoid((side * .30, -.02, -.01), (.14, .09, .05), 0, 10, 6)
finish(m, 'architecture', [timber], FG @ Matrix.Translation((UC, TIE + .13, .17)))

# Corner closures where the projecting storey meets NatWest and the alley.
north, _ = plane((FX, YN), (FX - .2, YN))
wall('first floor north return', north, 0, .2, SHOP + .27, TIE, depth=.05)
south, _ = plane((FX - ZR, YS), (FX, YS))
wall('first floor south return', south, 0, ZR, SHOP + .27, TIE, depth=.05)

# ------------------------------------------------------------- street gable
gable_top = RIDGE - .14
half = (gable_top - EAVE) / PITCH
# The north bay stays open; the bargeboard ends beside its attic window.
g = Group('Envelope street gable infill', FG, [plaster])
g.poly([(BAY, EAVE), (UC + half, EAVE), (UC, gable_top), (BAY, gable_top - PITCH * (UC - BAY))], -.25, 0)
g.done()
g = Group('Timber street gable framing', FG, [timber])


def under_roof(u, drop=0):
    return gable_top - drop - PITCH * abs(u - UC)


# Twin centre posts; four parallel braces each side rise outward to the
# bargeboards, the upper three from the post and the lowest from the tie beam.
SLOPE = .62
for side in (-1, 1):
    post = UC + side * GP
    g.box(post - .07, post + .07, EAVE, under_roof(post), 0, .07)
    for k in range(4):
        h0 = EAVE + .25 + (k - 1) * .85
        if h0 >= EAVE + .05:
            start = (post, h0)
        else:
            start = (post + side * (EAVE + .05 - h0) / SLOPE, EAVE + .05)
        run = (under_roof(start[0]) - .1 - start[1]) / (SLOPE + PITCH)
        g.strut(start, (start[0] + side * run, start[1] + SLOPE * run), .13, 0, .07)
# Small chevrons point up between the posts at the upper brace junctions.
for h in (EAVE + 1.1, EAVE + 1.95):
    for side in (-1, 1):
        g.strut((UC + side * (GP - .07), h), (UC, h + .22), .1, 0, .07)
g.done()

barge = Group('Roof bargeboards and finial', FG, [timber], 'roof')
for u0, u1 in ((BAY-.15, UC), (UC, W + .3)):
    t0, t1 = RIDGE + .1 - PITCH * abs(u0 - UC), RIDGE + .1 - PITCH * abs(u1 - UC)
    barge.poly([(u0,t0),(u1,t1),(u1,t1-.38),(u0,t0-.38)],.32,.40)
    for drop in (.04,.15,.30):
        barge.poly([(u0,t0-drop),(u1,t1-drop),(u1,t1-drop-.035),(u0,t0-drop-.035)],.40,.44)
barge.box(UC - .07, UC + .07, RIDGE - .5, RIDGE + .62, .30, .42)
barge.box(UC - .11, UC + .11, RIDGE + .55, RIDGE + .66, .29, .43)
# Shaped corner bracket under the southern barge foot (snag photograph).
barge.poly([(W - .12, EAVE - .35), (W + .2, EAVE - .35), (W + .2, EAVE - .55), (W - .02, EAVE - .85),
            (W - .12, EAVE - .85)], .05, .34)
barge.done()

# Main roof: front gable, ridge running back from the street, eaves over the alley.
def prism(name, section, x0, x1, materials, part='roof'):
    m = Mesh(name)
    n = len(section)
    verts = [(x0, y, z) for y, z in section] + [(x1, y, z) for y, z in section]
    faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    m.add(verts, faces)
    return finish(m, part, materials, roof_uv=True, recalc=True)


yr = YN - UC
ys_eave = YN - (W + .3)
section = [(YN - BAY, B + HB), (yr, B + RIDGE), (ys_eave, B + RIDGE - PITCH * (W + .3 - UC)),
           (ys_eave, B + RIDGE - PITCH * (W + .3 - UC) - .14), (yr, B + RIDGE - .14), (YN - BAY, B + HB - .14)]
prism('Roof main clay shell', section, FX - ZL - .35, RX + .3, [clay])
m = Mesh('Fine alley eaves gutter')
gz = B + RIDGE - PITCH * (W + .3 - UC) - .1
m.tube([(FX - ZL - .3, ys_eave - .06, gz), (RX + .3, ys_eave - .06, gz)], .06, 0, 8)
finish(m, 'roof', [iron])
m = Mesh('Roof main ridge tiles')
m.box(((FX - ZL - .35 + RX + .3) / 2, yr, B + RIDGE + .05), (RX + .3 - FX + ZL + .35, .26, .14))
finish(m, 'roof', [clay])

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
side, _ = plane((FX - .2, YN - BAY), (RX, YN - BAY))
wall('bay side above main roof', side, 0, RX - FX + .2, EAVE - .2, max(D['bay_eaves'], HB), mat=plaster, depth=.25)

be,br=D['bay_eaves'],D['bay_ridge'];north_h=be
yb=YN-BAY/2;xf=FX-.45
# Small hip entirely within the entrance strip; no roof sheet across the light.
frontx=xf;backx=RX+.3;y0=YN-BAY;y1=YN-.02
upper=[(frontx,y0,be),(backx,y0,be),(backx,y1,be),(frontx,y1,be),
       (frontx+.85,yb,br),(backx,yb,br)]
faces=[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)]
verts=[(x,y,z+B) for x,y,z in upper]+[(x,y,z+B-.12) for x,y,z in upper]
faces+= [tuple(i+6 for i in reversed(f)) for f in list(faces)]
for a,b in [(0,1),(1,2),(2,3),(3,0)]:faces.append((a,b,b+6,a+6))
m=Mesh('Roof north bay clay shell');m.add(verts,faces)
finish(m,'roof',[clay],roof_uv=True,recalc=True)
m = Mesh('Roof north bay ridge tiles')
m.box(((xf + .85 + RX + .3) / 2, yb, B + br + .04), (RX + .3 - xf - .85, .22, .12))
finish(m, 'roof', [clay])

# Tall brick stack on the ridge behind the gable: Nov2020 Street View shows it
# above the ridge, the May2011 frontal view hides it behind the apex.
cx = 14.0
m = Mesh('Roof brick chimney stack')
m.box((cx, yr, B + 10.55), (1.0, .62, 2.7))
m.box((cx, yr, B + 11.96), (1.12, .74, .12))
finish(m, 'roof', [brick])
m = Mesh('Fine chimney pots')
for dx in (-.25, .25):
    m.lathe((cx + dx, yr), [(B + 12.02, .13), (B + 12.37, .11), (B + 12.42, .13)], 12)
finish(m, 'roof', [pot])

# ------------------------------------------------- side, rear and party walls
alley, _ = plane((FX, YS), (RX, YS))
wall('alley side lower', alley, 0, RX - FX, BURY, SHOP, mat=render)
wall('alley side upper timbered', alley, 0, 2.6, SHOP, EAVE)
wall('alley side upper brick', alley, 2.6, RX - FX, SHOP, EAVE, mat=brick)
g = Group('Timber alley side return', alley, [timber])
g.box(0, 2.6, SHOP, SHOP + .22, 0, .06)
g.box(0, 2.6, 4.76, 4.92, 0, .07)
g.box(0, 2.6, TIE, EAVE, 0, .07)
for k in range(7):
    u = .06 + k * 2.48 / 6
    g.box(u - .055, u + .055, SHOP + .22, TIE, 0, .06)
g.done()

rearwall, _ = plane((RX, YS), (RX, YN))
main_w = W - BAY
g = Group('Envelope range rear gable', rearwall, [brick])
south_eave = RIDGE - PITCH * (W - UC)
g.poly([(0, BURY), (main_w, BURY), (main_w, HB - .14), (W - UC, RIDGE - .14), (0, south_eave - .14)],
       -.36, 0)
g.poly([(main_w, BURY), (W, BURY), (W, north_h - .12), (W - .85, br - .12), (main_w, north_h - .12)], -.36, 0)
g.done()
party, _ = plane((RR, YN), (FX, YN))
wall('NatWest party wall rear range', party, 0, RR - RX, BURY, D['rear_height'], mat=brick, depth=.2)
wall('NatWest party wall front range', party, RR - RX, RR - FX, BURY, north_h - .12, mat=brick, depth=.2)

# Low flat-roofed rear range along the alley, as seen in satellite imagery.
rh = D['rear_height']
rs, _ = plane((RX, YS), (RR, YS))
wall('rear range alley wall', rs, 0, RR - RX, BURY, rh, [(4.2, 5.1, 0, 2.1)], brick, 'rear')
g = Group('Rear range service door', rs, [door, metal], 'rear')
g.box(4.2, 5.1, 0, 2.1, -.12, -.08)
g.box(4.9, 4.95, .95, 1.1, -.08, -.04, 1)
g.done()
re, _ = plane((RR, YS), (RR, YN))
wall('rear range back wall', re, 0, W, BURY, rh, mat=brick, part='rear')
m = Mesh('Rear range flat roof')
m.box(((RX + RR) / 2, (YN + YS) / 2, B + rh - .08), (RR - RX, W, .16))
m.box(((RX + RR) / 2, YS + .15, B + rh + .12), (RR - RX, .3, .24), 1)
m.box((RR - .15, (YN + YS) / 2, B + rh + .12), (.3, W - .3, .24), 1)
finish(m, 'rear', [felt, coping])
for i, x in enumerate((21.2, 26.0)):
    m = Mesh('Rear range rooflight %d' % i)
    m.box((x, (YN + YS) / 2, B + rh + .1), (1.3, 1.8, .2), 0)
    m.add([(x - .6, (YN + YS) / 2 - .85, B + rh + .2), (x + .6, (YN + YS) / 2 - .85, B + rh + .2),
           (x + .6, (YN + YS) / 2 + .85, B + rh + .2), (x - .6, (YN + YS) / 2 + .85, B + rh + .2),
           (x, (YN + YS) / 2, B + rh + .55)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], 1)
    finish(m, 'rear', [metal, glass])

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
