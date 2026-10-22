"""Metric road-edge curves shared by neighbouring public-realm assets.

Positive offsets lie left of the directed kerb. At bends the offset lines meet
at a mitre, so setbacks are perpendicular distances rather than X/Y shifts.
"""
import math


def parallel(points, distance, closed=False):
    points = [tuple(p) for p in points]
    if closed and points[0] == points[-1]:
        points.pop()
    if len(points) < 2:
        raise ValueError('An edge needs two distinct points')
    normals = []
    ends = points[1:] + ([points[0]] if closed else [])
    for a, b in zip(points, ends):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1e-8:
            raise ValueError('Consecutive kerb points must differ')
        normals.append((-dy / length, dx / length))
    result = []
    for i, p in enumerate(points):
        before = normals[(i - 1) % len(normals)] if i or closed else normals[0]
        after = normals[i % len(normals)] if i < len(normals) else normals[-1]
        nx, ny = before[0] + after[0], before[1] + after[1]
        denominator = nx * before[0] + ny * before[1]
        if denominator < .08:
            raise ValueError('Kerb reversal needs an explicit rounded return')
        result.append((p[0] + distance * nx / denominator,
                       p[1] + distance * ny / denominator))
    return result + ([result[0]] if closed else [])


def clip_segment(a, b, bounds):
    """Clip a segment to (xmin, ymin, xmax, ymax), including exact seam points."""
    low, high = 0., 1.
    for axis in (0, 1):
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-12:
            if not bounds[axis] <= a[axis] <= bounds[axis + 2]:
                return None
            continue
        t0 = (bounds[axis] - a[axis]) / delta
        t1 = (bounds[axis + 2] - a[axis]) / delta
        low, high = max(low, min(t0, t1)), min(high, max(t0, t1))
        if high - low < 1e-9:
            return None
    return tuple(tuple(a[i] + t * (b[i] - a[i]) for i in (0, 1))
                 for t in (low, high))


def marking_segments(kerb, side, bounds=None, closed=False, offsets=(.18, .36)):
    """Yield the two paint centrelines; tile limits never become painted edges."""
    for offset in offsets:
        curve = parallel(kerb, side * offset, closed)
        for a, b in zip(curve, curve[1:]):
            segment = clip_segment(a, b, bounds) if bounds else (a, b)
            if segment:
                yield offset, segment
