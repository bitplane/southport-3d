"""One column generator with explicit master and lower-detail settings."""
import json
import math
from pathlib import Path
from mathutils import Matrix
from geometry import Mesh

MASTER = dict(radial_segments=160, shaft_rings=65, moulding_segments=80,
              flutes=20, small_mouldings=True)


def build_mesh(name, shaft_top, radius_scale, settings=None):
    settings = MASTER if settings is None else settings
    radial = settings['radial_segments']
    rings = settings['shaft_rings']
    moulding = settings['moulding_segments']
    flutes = settings['flutes']
    if min(radial, moulding) < 8 or rings < 2:
        raise ValueError('Insufficient column samples')
    if flutes and (radial % flutes or radial < flutes * 4):
        raise ValueError('Fluted shafts require at least four samples per flute and an integral multiple')
    mesh = Mesh(name)
    mesh.lathe((0, 0), [(.32,.365),(.34,.382),(.37,.388),(.405,.379),(.432,.349),(.47,.331)], moulding)
    profile = []
    for j in range(rings):
        t = j/(rings-1)
        profile.append((.47+t*(shaft_top-.47), .33*(1-t)+.275*t+.010*math.sin(math.pi*t)))
    mesh.lathe((0, 0), profile, radial, 0, flutes, .024 if flutes else 0)
    if settings['small_mouldings']:
        mesh.lathe((0, 0), [(3.84,.282),(3.848,.292),(3.858,.298),(3.872,.293),(3.883,.280)], moulding)
    mesh.lathe((0, 0), [(3.883,.280),(3.975,.280),(3.985,.285)], moulding)
    mesh.lathe((0, 0), [(3.985,.285),(4.002,.301),(4.028,.342),(4.052,.391),(4.06,.397)], moulding)
    mesh.box((0,0,4.101),(.83,.83,.082))
    mesh.transform(Matrix.Diagonal((radius_scale,radius_scale,1,1)))
    return mesh


def build_lod(name, settings, asset_dir):
    spec = json.loads((Path(asset_dir)/'research/modelling_spec.json').read_text())
    return build_mesh(name, spec['colonnade_vertical_datums']['shaft_top'],
                      spec['dimensions']['column_shaft_diameter_lower']['value']/.66,
                      settings).finish([], smooth=True)
