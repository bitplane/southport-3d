"""Simple lamp envelopes retaining one/five globes and the open cross arms."""
import math
from geometry import Mesh


def build_lod(name, settings, asset_dir):
    m=Mesh(name);n=settings['segments'];rings=max(4,n//2)
    if settings['kind']=='single':
        m.box((0,0,.56),(.47,.47,.04),0)
        m.lathe((0,0),[(.56,.19),(.65,.155),(.92,.09),(1.02,.056),(2.42,.044),(2.55,.16),(2.77,.10)],n,1)
        m.ellipsoid((0,0,2.942),(.210,.210,.218),2,n,rings)
    else:
        m.box((0,0,.38),(.78,.78,.78),0)
        m.lathe((0,0),[(.77,.31),(1.05,.205),(1.3,.225),(1.62,.14),(4.10,.119),(4.43,.174),(5.235,.133)],n,1)
        m.ellipsoid((0,0,5.465),(.275,.275,.283),2,n,rings)
        for k in range(4):
            a=k*math.pi/2;cx=.66*math.cos(a);cy=.66*math.sin(a)
            m.tube([(.11*math.cos(a),.11*math.sin(a),4.65),(cx,cy,4.65)],.065,1,6)
            m.tube([(0,0,4.3),(.35*math.cos(a),.35*math.sin(a),4.5),(cx,cy,4.57)],.03,1,6)
            m.lathe((cx,cy),[(4.28,.115),(4.47,.046),(4.59,.043)],n,0)
            m.ellipsoid((cx,cy,4.075),(.275,.275,.283),2,n,rings)
    return m.finish([],smooth=True)
