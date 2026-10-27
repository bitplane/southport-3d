"""Bounded support at the BHS arcade wall, shared by its two ground owners."""

import math


def wall_x(spec, y):
    a, b = spec['wall_south'], spec['wall_station_edge']
    return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])


def outer_x(spec, y):
    return wall_x(spec, y) - spec['width_m']


def station_polygon(spec):
    south, north = spec['wall_south'], spec['wall_station_edge']
    return [spec['front_threshold_outer'],
            [outer_x(spec, south[1]), south[1]],
            [outer_x(spec, north[1]), north[1]], north, south]


def approach_polygon(spec):
    north = spec['wall_station_edge'][1]
    end = spec['approach_end_y']
    return [[outer_x(spec, north), north], [wall_x(spec, north), north],
            [wall_x(spec, end), end], [outer_x(spec, end), end]]


def station_mesh(mesh, surface, spec):
    """Add an outer-edge-conforming ramp and a fan to the Chapel threshold."""
    south, north = spec['wall_south'], spec['wall_station_edge']
    datum = spec['building_grade_m']
    inner = (south[0], south[1], datum)
    outer_south = (outer_x(spec, south[1]), south[1])
    outer_north = (outer_x(spec, north[1]), north[1])
    fan = list(surface.edge_points(spec['front_threshold_outer'], outer_south))
    for a, b in zip(fan, fan[1:]):
        mesh.add([inner, a, b], [(0, 2, 1)])
    # Short strips also bound the error from triangulating a ruled ramp whose
    # outer height changes along its length. Preserve every terrain break.
    count = math.ceil((north[1] - south[1]) / 2)
    stops = [south[1] + i * (north[1] - south[1]) / count for i in range(count + 1)]
    edge = []
    for y0, y1 in zip(stops, stops[1:]):
        points = list(surface.edge_points((outer_x(spec, y0), y0),
                                          (outer_x(spec, y1), y1)))
        edge.extend(points if not edge else points[1:])
    for a, b in zip(edge, edge[1:]):
        ia = (wall_x(spec, a[1]), a[1], datum)
        ib = (wall_x(spec, b[1]), b[1], datum)
        mesh.add([a, b, ib, ia], [(0, 2, 1), (0, 3, 2)])


def approach_mesh(mesh, surface, spec):
    """Continue the station ramp to level approach ground over two metres."""
    y0, y1 = spec['wall_station_edge'][1], spec['approach_end_y']
    z = spec['building_grade_m']
    x0, x1 = outer_x(spec, y0), outer_x(spec, y1)
    mesh.add([(x0, y0, surface.height(x0, y0)), (wall_x(spec, y0), y0, z),
              (wall_x(spec, y1), y1, z), (x1, y1, z)],
             [(0, 1, 2), (0, 2, 3)])
