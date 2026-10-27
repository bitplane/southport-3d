"""Measured working plan for the Diana Gardens paving.

Coordinates are the corridor's site metres. The aerial references are not a
survey; tree cover hides portions of the terminal cross paths and the exact
level transition at the fountain remains estimated.
"""
import math

CENTRE = (-185.7, -2.5)
END_STATIONS = (-221.0, -160.9)
CELL = .85
HALF_WIDTH = 2.4
RING_INNER = 6.4
RING_OUTER = 9.4
POOL_RADIUS = 2.4


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle(radius, segments=96):
    x, y = CENTRE
    return [(x + radius * math.cos(i * math.tau / segments),
             y + radius * math.sin(i * math.tau / segments))
            for i in range(segments)]


def path_rectangles():
    """Long axis, two end cross paths, and the centre's two approaches."""
    cx, cy = CENTRE
    w = HALF_WIDTH
    return [rect(-224.2, -155.7, cy-w, cy+w),
            *(rect(x-w, x+w, -23.3, 17.5) for x in END_STATIONS),
            rect(cx-w, cx+w, -23.0, 10.4)]


def surfaces(plan):
    """Return disjoint dark/light paving as GEOS geometries.

    Checkers and framing are real cut-ins in the ground mesh. A long strip has
    precedence at crossings, so adjacent surfaces never double-own a junction.
    Four framed arc panels reproduce the central ornament seen in the overhead
    and the May 2017 photosphere, with a broad opening towards the Atkinson.
    """
    cx, cy = CENTRE
    w = HALF_WIDTH
    def run(along_x, fixed, begin, end):
        dark_polys = []
        # Four near-square cells and two framing lines on each side.
        for i in range(math.floor(begin / CELL), math.ceil(end / CELL)):
            a, b = max(begin, i*CELL), min(end, (i+1)*CELL)
            if b-a < 1e-5:
                continue
            for j in range(4):
                if (i+j) % 2:
                    continue
                lo, hi = fixed-2*CELL+j*CELL, fixed-2*CELL+(j+1)*CELL
                dark_polys.append(rect(a, b, lo, hi) if along_x else rect(lo, hi, a, b))
        for lo in (-w, -w+.40, w-.62, w-.22):
            dark_polys.append(rect(begin, end, fixed+lo, fixed+lo+.22)
                              if along_x else rect(fixed+lo, fixed+lo+.22, begin, end))
        return plan.polygons(dark_polys)

    # The long strip owns the intersection; branch stripes stop at its edge
    # rather than cutting across its checkers.
    routes=[(True,cy,-224.2,-155.7),
            *((False,x,-23.3,17.5) for x in END_STATIONS),
            (False,cx,-23.0,10.4)]
    body=plan.polygons([]); dark_parts=[]
    for along_x,fixed,begin,end in routes:
        rectangle=rect(begin,end,fixed-w,fixed+w) if along_x else rect(fixed-w,fixed+w,begin,end)
        segment=plan.polygons([rectangle])
        unoccupied=plan.difference(segment,body)
        dark_parts.extend(plan.triangles(plan.intersection(unoccupied,run(along_x,fixed,begin,end))))
        body=plan.polygons([*plan.triangles(body),*plan.triangles(segment)])
    outer = plan.polygons([circle(RING_OUTER)])
    axis = plan.difference(body, outer)
    axis_dark = plan.intersection(axis, plan.polygons(dark_parts))
    axis_light = plan.difference(axis, axis_dark)

    def disc(r):
        return plan.polygons([circle(r)])
    def annulus(a, b):
        return plan.difference(disc(b), disc(a))
    ring = annulus(RING_INNER, RING_OUTER)
    def panel(ri,ro,a,b):
        """Curved rectangular panel with short rounded corner transitions."""
        corner=min(.16,(ro-ri)/4,(b-a)*ri/8)
        def pt(r,t):return (cx+r*math.cos(t),cy+r*math.sin(t))
        def quadratic(start,control,end):
            return [((1-t)**2*start[0]+2*(1-t)*t*control[0]+t*t*end[0],
                     (1-t)**2*start[1]+2*(1-t)*t*control[1]+t*t*end[1])
                    for t in (0.25,0.5,0.75,1)]
        outer_a,outer_b=a+corner/ro,b-corner/ro
        inner_a,inner_b=a+corner/ri,b-corner/ri
        count=max(4,math.ceil((b-a)*48/math.tau))
        points=[pt(ro,outer_a+(outer_b-outer_a)*i/count) for i in range(count+1)]
        points+=quadratic(points[-1],pt(ro,b),pt(ro-corner,b))
        points.append(pt(ri+corner,b))
        points+=quadratic(points[-1],pt(ri,b),pt(ri,inner_b))
        points += [pt(ri,inner_b+(inner_a-inner_b)*i/count) for i in range(1,count+1)]
        points+=quadratic(points[-1],pt(ri,a),pt(ri+corner,a))
        points.append(pt(ro-corner,a))
        points+=quadratic(points[-1],pt(ro,a),pt(ro,outer_a))
        return points[:-1]

    linework=[]
    # Each quadrant has one broad arc panel and two shorter end panels. Each
    # panel owns two closed outlines, separated by pale stone and separated
    # from its neighbours, rather than continuous circular stripes.
    for k in range(4):
        for first,last in ((13,24),(27,63),(66,77)):
            a,b=math.radians(k*90+first),math.radians(k*90+last)
            ri,ro=6.48,9.32;mean=(ri+ro)/2
            def inset(d):return plan.polygons([panel(ri+d,ro-d,a+d/mean,b-d/mean)])
            for outer_inset,inner_inset in ((0,.17),(.34,.51)):
                linework.extend(plan.triangles(plan.difference(inset(outer_inset),inset(inner_inset))))
    # Taper the paired path borders through each mouth without crossing the
    # individually framed end panels.
    for k in range(4):
        for offset in (-11.2,-9.2,9.2,11.2):
            t=math.radians(k*90+offset);u=(math.cos(t),math.sin(t));v=(-u[1],u[0])
            linework.append([(cx+r*u[0]+side*v[0],cy+r*u[1]+side*v[1])
                             for r,side in ((6.4,-.08),(9.4,-.08),(9.4,.08),(6.4,.08))])
    ring_dark = plan.intersection(ring, plan.polygons(linework))
    ring_light = plan.difference(ring, ring_dark)
    dark = plan.polygons([*plan.triangles(axis_dark), *plan.triangles(ring_dark)])
    light = plan.polygons([*plan.triangles(axis_light), *plan.triangles(ring_light)])
    return dark, light
