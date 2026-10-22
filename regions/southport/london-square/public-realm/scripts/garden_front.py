"""Observed SW garden frontage; dimensions calibrated from Aug 2024 screenshot.

Local reusable shapes, with site placement kept in research/streets.json.
Keep balustrade openings at every level; no photo pixels are distributed.
"""
import math
from southport3d.geometry import Mesh


def globe_lamp(level='detail', name='Garden globe lamp'):
    m=Mesh(name)
    n={'detail':24,'walk':12,'district':6}[level]
    # Origin is the stone pier cap. Black moulded foot/collars, pale shaft/globe.
    profile=[(0,.16),(.055,.16),(.075,.12),(.11,.10),(.15,.085),(.19,.075)]
    if level=='district':profile=[(0,.15),(.16,.08)]
    m.lathe((0,0),profile,n,1)
    m.lathe((0,0),[(.16,.065),(.93,.045)],n,2)
    profile=[(.90,.07),(.95,.08),(1.0,.08),(1.03,.12),(1.08,.12),(1.10,.09)]
    if level=='district':profile=[(.90,.08),(1.10,.10)]
    m.lathe((0,0),profile,n,1)
    m.ellipsoid((0,0,1.32),(.25,.25,.25),2,n,max(4,n//2))
    return m


def balustrade(level='detail', name='Garden balustrade'):
    m=Mesh(name)
    m.box((2,0,.175),(4,.36,.35),0)
    m.box((2,0,.365),(4,.40,.08),0)
    m.box((2,0,.98),(4,.43,.14),0)
    m.box((0,0,.505),(.36,.46,1.01),0)
    m.box((0,0,1.045),(.46,.49,.07),0)
    profile=[(.40,.12),(.44,.12),(.47,.085),(.50,.075),(.54,.10),(.61,.115),(.69,.09),(.77,.065),(.86,.065),(.89,.105),(.91,.105)]
    if level=='walk':profile=[profile[i] for i in [0,1,3,5,7,8,10]]
    if level=='district':profile=[(.40,.10),(.61,.11),(.80,.065),(.91,.10)]
    n={'detail':16,'walk':8,'district':4}[level]
    for i in range(8):
        m.lathe((.42+i*.45,0),profile,n,0)
    return m


def build_lod(name, settings, asset_dir):
    ob={'lamp':globe_lamp,'balustrade':balustrade}[settings['kind']](settings['level'],name).finish([])
    if settings['kind']=='lamp':
        for face in ob.data.polygons:face.use_smooth=True
    return ob
