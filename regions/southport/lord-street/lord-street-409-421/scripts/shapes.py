"""Measured main surfaces. Decoration never controls receiver topology."""
import math
from southport3d.planar import subtract

def rect(a,b,c,d):return [(a,b),(c,b),(c,d),(a,d)]
def cuts(p,holes):
 out=[p]
 for h in holes:out=[q for poly in out for q in subtract(poly,h)]
 return out

def transform(d,p):
 x,y,z=p
 return(d['front_origin'][0]+x+d['side_shear']*y,d['front_origin'][1]+y+d['front_shear']*x,d['floor_z']+z)

def roof_probes():
    """Independent physical bounds above local floor; None requires an open gap."""
    return [
        ('long valley', 5.40, 8.30, (11.0, 11.3)),
        ('hip valley', 14.50, 7.50, (12.4, 12.7)),
        ('rear hip', 14.10, 12.60, (10.8, 11.1)),
        ('transverse return', 9.50, 19.00, (10.7, 11.0)),
        ('court rooflight', 8.15, 11.00, (5.15, 5.4)),
        ('service rooflight', 15.00, 17.20, (4.9, 5.2)),
        ('open behind court', 9.00, 16.80, None),
        ('open rear service gap', 12.80, 19.40, None),
    ]

def canopy_profile(d,n=12):
 c=d['canopy'];P=c['projection']
 return [(P*i/n,c['wall_z']+(c['spring_z']-c['wall_z'])*i/n+c['arch_rise']*math.sin(math.pi*i/n)) for i in range(n+1)]

def _front_join(d, height):
    """Intersection of a cross-ridge and the descending street-roof pitch."""
    return d['ridge_y'] + (d['front_ridge'] - height) * (d['main_depth'] - d['ridge_y']) / (d['front_ridge'] - d['rear_eaves'])


def roofs(d):
    """Independent high ranges, clipped valleys, and two lower lightwells.

    All roof polygons are exterior skins. The two triangular holes in the
    street roof are precisely the footprints of the incoming roof slopes.
    """
    w, b, r = d['front_width'], d['main_depth'], d['ridge_y']
    e, h, back_e = d['front_eaves'], d['front_ridge'], d['rear_eaves']
    ranges = d['rear_ranges']
    strip, ret, hip = ranges['long_range'], ranges['return'], ranges['hip']
    out = []
    # Cafe gable intersects the front roof; never retain the skin beneath it.
    cafe = d['cafe']; cw = cafe['width']
    cafe_join = (cafe['gable_top'] - e) * r / (h - e)
    for i, p in enumerate(cuts(rect(0, 0, w, r), [[(0, 0), (cw, 0), (cw / 2, cafe_join)]])):
        out.append(('main front ' + str(i), [(x, y, e + (h - e) * y / r) for x, y in p]))
    out += [
        ('cafe front gable left', [(0, 0, e), (cw / 2, 0, cafe['gable_top']), (cw / 2, cafe_join, cafe['gable_top'])]),
        ('cafe front gable right', [(cw / 2, 0, cafe['gable_top']), (cw, 0, e), (cw / 2, cafe_join, cafe['gable_top'])]),
    ]
    a, c = strip['x0'], strip['x1']; m = (a + c) / 2
    hs, join_s = strip['ridge'], _front_join(d, strip['ridge'])
    ha, hc = hip['x0'], hip['x1']; hm = (ha + hc) / 2
    hh, join_h = hip['ridge'], _front_join(d, hip['ridge'])
    holes = [[(a, b), (m, join_s), (c, b)], [(ha, b), (hm, join_h), (hc, b)]]
    for i, p in enumerate(cuts(rect(0, r, w, b), holes)):
        out.append(('main rear ' + str(i), [(x, y, h + (back_e - h) * (y - r) / (b - r)) for x, y in p]))

    # Long west range joins a lower transverse return at their mitred valley.
    ys, ye, xmax = ret['y0'], ret['y1'], ret['x1']
    ym = (ys + ye) / 2; xr = xmax - (ym - ys)
    out += [
        ('long range west', [(a, b, back_e), (m, join_s, hs), (m, ym, hs), (a, ys, back_e)]),
        ('long range east', [(m, join_s, hs), (c, b, back_e), (c, ys, back_e), (m, ym, hs)]),
    ]
    # Front return plane is trimmed by the arriving long-range roof.
    p = [(a, ys), (xmax, ys), (xr, ym), (m, ym)]
    for i, q in enumerate(cuts(p, [[(a, ys), (c, ys), (m, ym)]])):
        out.append(('return front ' + str(i), [(x, y, back_e + (hs - back_e) * (y - ys) / (ym - ys)) for x, y in q]))
    out += [
        ('return back', [(m, ym, hs), (xr, ym, hs), (xmax, ye, back_e), (a, ye, back_e)]),
        ('return west hip', [(a, ys, back_e), (m, ym, hs), (a, ye, back_e)]),
        ('return east hip', [(xmax, ys, back_e), (xmax, ye, back_e), (xr, ym, hs)]),
    ]
    # Compact cross range: a rear hip, no gable, and an exact front valley.
    end, ridge_end = hip['y1'], hip['ridge_end']
    out += [
        ('middle hip west', [(ha, b, back_e), (hm, join_h, hh), (hm, ridge_end, hh), (ha, end, back_e)]),
        ('middle hip east', [(hm, join_h, hh), (hc, b, back_e), (hc, end, back_e), (hm, ridge_end, hh)]),
        ('middle hip rear', [(ha, end, back_e), (hm, ridge_end, hh), (hc, end, back_e)]),
    ]
    # Pitched low roofs are opaque proxies for glazing whose transparency and
    # ground-level structure are not resolved by the photogrammetric mesh.
    for cover in ranges['covers']:
        a, c, y0, y1, z, top = [cover[k] for k in ('x0', 'x1', 'y0', 'y1', 'eaves', 'ridge')]
        m = (a + c) / 2
        out += [
            (cover['id'] + ' glass west', [(a, y0, z), (m, y0, top), (m, y1, top), (a, y1, z)]),
            (cover['id'] + ' glass east', [(m, y0, top), (c, y0, z), (c, y1, z), (m, y1, top)]),
        ]
    return out


def exterior(d):
    """Single wall ownership for street block, wings, hip and low covers."""
    w, b, r = d['front_width'], d['main_depth'], d['ridge_y']
    e, h, back_e = d['front_eaves'], d['front_ridge'], d['rear_eaves']
    lo = d['foundation_z'] - d['floor_z']; ranges = d['rear_ranges']
    strip, ret, hip = ranges['long_range'], ranges['return'], ranges['hip']
    a, c = strip['x0'], strip['x1']; ys, ye, xmax = ret['y0'], ret['y1'], ret['x1']
    ha, hc, end = hip['x0'], hip['x1'], hip['y1']
    out = [
        ('southwest party', [(0, b, lo), (0, r, lo), (0, 0, lo), (0, 0, e), (0, r, h), (0, b, back_e)]),
        ('northeast party', [(w, 0, lo), (w, r, lo), (w, b, lo), (w, b, back_e), (w, r, h), (w, 0, e)]),
    ]
    last = 0
    for left, right in [(a, c), (ha, hc), (w, w)]:
        if left > last:
            out.append(('rear front range', [(left, b, lo), (last, b, lo), (last, b, back_e), (left, b, back_e)]))
        last = right
    out += [
        ('long range west wall', [(a, ys, lo), (a, b, lo), (a, b, back_e), (a, ys, back_e)]),
        ('long range east wall', [(c, b, lo), (c, ys, lo), (c, ys, back_e), (c, b, back_e)]),
        ('return front wall', [(c, ys, lo), (xmax, ys, lo), (xmax, ys, back_e), (c, ys, back_e)]),
        ('return back wall', [(xmax, ye, lo), (a, ye, lo), (a, ye, back_e), (xmax, ye, back_e)]),
        ('return west wall', [(a, ye, lo), (a, ys, lo), (a, ys, back_e), (a, ye, back_e)]),
        ('return east wall', [(xmax, ys, lo), (xmax, ye, lo), (xmax, ye, back_e), (xmax, ys, back_e)]),
        ('middle hip west wall', [(ha, end, lo), (ha, b, lo), (ha, b, back_e), (ha, end, back_e)]),
        ('middle hip east wall', [(hc, b, lo), (hc, end, lo), (hc, end, back_e), (hc, b, back_e)]),
        ('middle hip rear wall', [(hc, end, lo), (ha, end, lo), (ha, end, back_e), (hc, end, back_e)]),
    ]
    for cover in ranges['covers']:
        a, c, y0, y1, z, top = [cover[k] for k in ('x0', 'x1', 'y0', 'y1', 'eaves', 'ridge')]
        m = (a + c) / 2
        # C1 lies between the high walls and the street-range rear wall;
        # it owns only its low end wall. C2 is a separate low volume.
        out.append((cover['id'] + ' rear wall', [(c, y1, lo), (a, y1, lo), (a, y1, z), (m, y1, top), (c, y1, z)]))
        if cover['id'] == 'court cover':
            # The high hip wall ends before this low roof's rear edge.
            out.append(('court cover exposed east wall', [(c, hip['y1'], lo), (c, y1, lo), (c, y1, z), (c, hip['y1'], z)]))
        else:
            out += [
                (cover['id'] + ' front wall', [(a, y0, lo), (c, y0, lo), (c, y0, z), (m, y0, top), (a, y0, z)]),
                (cover['id'] + ' west wall', [(a, y1, lo), (a, y0, lo), (a, y0, z), (a, y1, z)]),
                (cover['id'] + ' east wall', [(c, y0, lo), (c, y1, lo), (c, y1, z), (c, y0, z)]),
            ]
    return out

def bays(d):
 if d['kind']=='red':return [(d['bay_centres'][i],3.05,4.7,11.5,.56)for i in (0,3)]
 return [(d['bay_centres'][0],2.6,7.2,10.0,.65)]+[(x,3.2,4.55,7.1,.64)for x in d['bay_centres'][1:]]


def box_bays(d):
 for cx in d['bay_centres'][1:3]:
  a,b=cx-1.6,cx+1.6
  yield cx, [
   ('front',[(a,-.65,4.8),(b,-.65,4.8),(b,-.65,7.4),(a,-.65,7.4)]),
   ('skirt',[(a,-.43,4.4),(b,-.43,4.4),(b,-.65,4.8),(a,-.65,4.8)]),
   ('left',[(a,0,4.4),(a,-.43,4.4),(a,-.65,4.8),(a,-.65,7.4),(a,0,8.0)]),
   ('right',[(b,-.43,4.4),(b,0,4.4),(b,0,8.0),(b,-.65,7.4),(b,-.65,4.8)]),
   ('roof',[(a,-.65,7.4),(b,-.65,7.4),(b,0,8.0),(a,0,8.0)]),
   ('bottom',[(a,0,4.4),(b,0,4.4),(b,-.43,4.4),(a,-.43,4.4)])]


def facade_x(d,x):
 c=d.get('cafe',{}).get('width',0)
 return c+x*(d['front_width']-c)/d['front_width']

def cafe_front_envelope(d):
 c=d['cafe'];w=c['width'];a=(w-c['bay_width'])/2;b=w-a;p=c['projection'];lo=4.45;hi=11.65
 out=[]
 for poly in cuts(rect(0,0,w,d['front_eaves']),[rect(a,lo,b,hi)]):out.append(('wall',[(x,0,z)for x,z in poly]))
 out += [('bay front',[(a,-p,lo),(b,-p,lo),(b,-p,hi),(a,-p,hi)]),('bay left',[(a,0,lo),(a,-p,lo),(a,-p,hi),(a,0,hi)]),('bay right',[(b,-p,lo),(b,0,lo),(b,0,hi),(b,-p,hi)]),('bay top',[(a,-p,hi),(b,-p,hi),(b,0,hi),(a,0,hi)]),('bay bottom',[(a,0,lo),(b,0,lo),(b,-p,lo),(a,-p,lo)]),('gable',[(0,0,d['front_eaves']),(w,0,d['front_eaves']),(w/2,0,c['gable_top'])])]
 return out
