"""Common dimensions for both flights, their intermediate landings and rails."""

def flight(stair, a, b, rise_right, z0=-.02, landing=2.8):
    n = stair['steps']
    assert n > 0 and n % 2 == 0
    mid = stair['middle_landing_m']
    run = (b - a - mid) / n
    assert run > 0
    rise = (landing - z0) / n
    half = n // 2
    def x(distance):
        return a + distance if rise_right else b - distance
    treads = []
    for i in range(n):
        d = i * run + (mid if i >= half else 0)
        treads.append((x(d), x(d + run), z0 + (i + 1) * rise))
    treads.append((x(half * run), x(half * run + mid), z0 + half * rise))
    points = [(x(0), z0), (x(half * run), z0 + half * rise),
              (x(half * run + mid), z0 + half * rise), (x(b - a), landing)]
    return treads, list(zip(points, points[1:]))

def baluster_points(stair, segments, seat_offset=.09):
    """A photographed 3/2/3 rhythm; seats follow the same stair profile."""
    counts = [stair['slope_balusters_per_segment'], stair['middle_balusters'],
              stair['slope_balusters_per_segment']]
    for ((x0, z0), (x1, z1)), count in zip(segments, counts):
        for i in range(count):
            t = (i + 1) / (count + 1)
            yield x0 + t * (x1 - x0), z0 + t * (z1 - z0) + seat_offset
