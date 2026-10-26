"""Named, bounded elevation profiles in metres; no implicit town-wide ground.

Profiles are piecewise linear along a declared straight metric axis. Curved
roads use bounded segments with shared control heights. Split input triangles
at breaklines before lifting them, otherwise a long face can erase a crest.
Only explicitly included geographic files are opened (and traced by builds).
"""
import bisect
import json
import math
from pathlib import Path
from .planar import area, halfplane


class Elevations:
    def __init__(self, path):
        self.controls, self.surfaces, self.files = {}, {}, []
        self.surface_paths, self._instances = {}, {}
        self.datum = None
        self._load(Path(path).resolve(), set())
        for name, spec in self.surfaces.items():
            self.surface(name)  # fail early, including unused bad profiles

    def _load(self, path, active):
        if path in active:
            raise ValueError('Cyclic elevation include: ' + str(path))
        if path in self.files:
            return
        data = json.loads(path.read_text())
        if data.get('schema_version') != 1:
            raise ValueError('Unsupported elevation schema')
        if self.datum is not None and self.datum != data['datum']:
            raise ValueError('Elevation datum mismatch')
        self.datum = data['datum']
        for relative in data.get('includes', []):
            self._load((path.parent / relative).resolve(), active | {path})
        for field in ('controls', 'surfaces'):
            target = getattr(self, field)
            for key, value in data.get(field, {}).items():
                if key in target:
                    raise ValueError('Duplicate elevation identifier: ' + key)
                target[key] = value
                if field == 'surfaces':
                    self.surface_paths[key] = path.parent
        self.files.append(path)

    def surface(self, name):
        if name not in self._instances:
            spec = self.surfaces[name]
            if spec.get('type') in ('survey', 'control_grid'):
                from .survey_surface import SurveySurface
                self._instances[name] = SurveySurface(
                    self.surface_paths[name]/spec['terrain'], name, spec['bounds'],
                    spec.get('grid_m', 5.), spec.get('offset_m', 0.), spec.get('refinements', []),
                    controlled=spec.get('type') == 'control_grid')
                if 'offset_profile' in spec:
                    profile=Surface(self,name+' offset',dict(spec['offset_profile'],bounds=spec['bounds']))
                    self._instances[name]=OffsetSurface(self._instances[name],profile)
            elif spec.get('type', 'profile') == 'profile':
                self._instances[name] = Surface(self, name, spec)
            else:
                raise ValueError('Unknown elevation surface type: '+name)
        return self._instances[name]

    def control_height(self, name):
        record = self.controls[name]
        if not record.get('evidence') or not record.get('status'):
            raise ValueError('Height control needs evidence and status: ' + name)
        h = record['height_m']
        if not isinstance(h, (float, int)) or not math.isfinite(h):
            raise ValueError('Invalid control height: ' + name)
        if not math.isfinite(record['uncertainty_m']) or record['uncertainty_m'] < 0:
            raise ValueError('Invalid height uncertainty: ' + name)
        return h


class Surface:
    def __init__(self, plan, name, spec):
        self.name, self.spec = name, spec
        self.bounds = spec['bounds']  # xmin, xmax, ymin, ymax; ownership clips refine this
        if len(self.bounds) != 4 or not all(math.isfinite(v) for v in self.bounds):
            raise ValueError('Invalid surface bounds: ' + name)
        if self.bounds[0] >= self.bounds[1] or self.bounds[2] >= self.bounds[3]:
            raise ValueError('Empty surface bounds: ' + name)
        self.origin = spec['axis_origin']
        direction = spec['axis_direction']
        length = math.hypot(*direction)
        if not length:
            raise ValueError('Empty profile axis')
        self.axis = tuple(v / length for v in direction)
        self.stations = [p['distance_m'] for p in spec['profile']]
        self.heights = [plan.control_height(p['control']) for p in spec['profile']]
        if not self.stations or any(not math.isfinite(s) for s in self.stations):
            raise ValueError('Profile needs finite stations')
        if any(b <= a for a, b in zip(self.stations, self.stations[1:])):
            raise ValueError('Profile stations must increase')
        self.offset = spec.get('offset_m', 0)
        self.crossfall = spec.get('crossfall', 0)
        if not all(math.isfinite(v) for v in (*self.origin, *self.axis, self.offset, self.crossfall)):
            raise ValueError('Nonfinite profile')

    def contains(self, x, y, tolerance=1e-7):
        a,b,c,d = self.bounds
        return a-tolerance <= x <= b+tolerance and c-tolerance <= y <= d+tolerance

    def height(self, x, y):
        if not self.contains(x, y):
            raise ValueError(f'{self.name}: outside declared bounds at {(x,y)}')
        dx,dy = x-self.origin[0], y-self.origin[1]
        ux,uy = self.axis
        station, lateral = dx*ux+dy*uy, -dx*uy+dy*ux
        i = bisect.bisect_right(self.stations, station)
        if i == 0:
            h = self.heights[0]
        elif i == len(self.stations):
            h = self.heights[-1]
        else:
            t = (station-self.stations[i-1])/(self.stations[i]-self.stations[i-1])
            h = self.heights[i-1]*(1-t)+self.heights[i]*t
        return h+self.offset+self.crossfall*lateral

    def breaklines(self):
        """Every profile knot, including transitions to clamped end plateaus."""
        ux,uy = self.axis
        for station in self.stations:
            x,y = self.origin[0]+station*ux, self.origin[1]+station*uy
            yield ((x-uy,y+ux),(x+uy,y-ux))

    def edge_points(self, a, b):
        """Ordered XYZ points for a wall/kerb edge, including every grade break."""
        ux,uy = self.axis
        start = (a[0]-self.origin[0])*ux+(a[1]-self.origin[1])*uy
        end = (b[0]-self.origin[0])*ux+(b[1]-self.origin[1])*uy
        fractions = [0.,1.]
        if abs(end-start) > 1e-12:
            fractions += [(s-start)/(end-start) for s in self.stations
                          if 0 < (s-start)/(end-start) < 1]
        for t in sorted(set(fractions)):
            x,y = a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])
            yield (x,y,self.height(x,y))

    def lift_triangle(self, triangle):
        """Split a planar triangle at profile breaks, then lift to exact planes."""
        pieces = [list(triangle)]
        for a,b in self.breaklines():
            divided = []
            for polygon in pieces:
                distances = [(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]) for p in polygon]
                if min(distances) < -1e-9 and max(distances) > 1e-9:
                    divided.extend(p for side in (True,False)
                                   if len(p := halfplane(polygon,a,b,side)) >= 3 and area(p) > 1e-10)
                else:
                    divided.append(polygon)
            pieces = divided
        for polygon in pieces:
            for i in range(1,len(polygon)-1):
                tri = [polygon[0],polygon[i],polygon[i+1]]
                if area(tri) > 1e-10:
                    yield [(x,y,self.height(x,y)) for x,y in tri]


class OffsetSurface:
    """An authored ramp/offset above survey terrain, split at both sets of breaks."""
    def __init__(self,base,profile):
        self.base,self.profile=base,profile
        self.name,self.bounds=base.name,base.bounds
        self.terrain=base.terrain

    def contains(self,x,y,tolerance=1e-7):
        return self.base.contains(x,y,tolerance)

    def height(self,x,y):
        return self.base.height(x,y)+self.profile.height(x,y)

    def lift_triangle(self,triangle):
        for tri in self.base.lift_triangle(triangle):
            for piece in self.profile.lift_triangle([p[:2]for p in tri]):
                yield [(x,y,self.height(x,y))for x,y,z in piece]

    def edge_points(self,a,b):
        points={tuple(p[:2])for surface in [self.base,self.profile]for p in surface.edge_points(a,b)}
        for x,y in sorted(points,key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2):
            yield x,y,self.height(x,y)
