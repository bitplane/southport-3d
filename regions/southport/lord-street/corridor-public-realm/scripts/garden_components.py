"""Town Hall Gardens furniture; site placements stay in build.py.

Reuses the metric bench family.  Stone profiles and column dimensions are
visual estimates from the 2017 and 2019 garden panoramas, not surveyed sections.
"""
import math
import bmesh
from southport3d.geometry import Mesh
from southport3d.street import furniture
from southport3d.landscape import tree

def make(kind,level,name):
 if kind=='bench' and level!='district':return furniture('bench',level,name)
 if kind=='bench':
  # Fixed coarse construction: boxes meet at edges without coincident caps.
  m=Mesh(name)
  for x in (-.72,.72):m.box((x,0,.215),(.065,.40,.43),0)
  m.box((0,0,.46),(1.9,.48,.06),7)
  m.box((0,.21,.69),(1.9,.06,.40),7)
  return m
 if kind=='tree':return tree(level,name)
 m=Mesh(name); n={'detail':16,'walk':10,'district':6}[level]
 if kind=='balustrade':
  m.box((2,0,.14),(3.54,.34,.28),0)
  m.box((2,0,.32),(3.54,.40,.08),0)
  m.box((2,0,1.02),(3.54,.42,.12),0)
  m.box((0,0,.52),(.46,.48,1.04),0)
  m.box((0,0,1.08),(.54,.55,.08),0)
  profile=[(.36,.10),(.40,.12),(.46,.10),(.53,.075),(.59,.10),(.67,.12),(.78,.085),(.89,.07),(.94,.11),(.96,.11)]
  if level=='district':profile=[(.36,.1),(.55,.08),(.68,.12),(.90,.07),(.96,.1)]
  for i in range(8):m.lathe((.42+.45*i,0),profile,n,0)
 elif kind=='globe':
  # Lamp and pier belong together; heights are estimated from 2017 imagery.
  m.rect_profile((0,0),[(0,.55,.55),(.08,.55,.55),(.12,.46,.46),(1.0,.46,.46),(1.05,.56,.56)])
  m.lathe((0,0),[(1.05,.16),(1.14,.16),(1.20,.095),(1.28,.075)],n,1)
  m.lathe((0,0),[(1.28,.07),(2.12,.055)],n,0)
  m.lathe((0,0),[(2.12,.08),(2.20,.11),(2.27,.10)],n,1)
  m.ellipsoid((0,0,2.52),(.24,.24,.24),2,n,max(4,n//2))
 elif kind=='column':
  # Both photographed entrances have three shafts on a broad masonry base,
  # carrying one layered entablature. Capitals are restrained at distance.
  m.rect_profile((0,0),[(0,2.05,.72),(.12,2.05,.72),(.18,1.95,.64),(.65,1.95,.64),(.72,2.02,.70)])
  for x in (-.66,0,.66):
   m.lathe((x,0),[(.72,.21),(.80,.21),(.88,.16),(3.03,.14),(3.10,.19),(3.18,.23)],n,0)
   if level!='district':
    # Shallow panel frames and the paired scrolls visible on the entrance
    # capitals. Coarse level keeps only the shaft and entablature silhouette.
    for y in (-.33,.33):
     m.tube([(x-.23,y,.23),(x+.23,y,.23),(x+.23,y,.58),(x-.23,y,.58),(x-.23,y,.23)],.012,0,4)
    for y in (-.25,.25):
     for side in (-1,1):
      centre=x+side*.18
      pts=[]
      for j in range(25):
       t=math.tau*1.4*j/24;r=.12-.08*j/24
       pts.append((centre+r*math.cos(t),y,3.10+r*math.sin(t)))
      m.tube(pts,.012,0,6)
  m.rect_profile((0,0),[(3.18,2.02,.66),(3.25,2.02,.66),(3.30,1.93,.62),(3.51,1.93,.62),(3.56,2.08,.72),(3.66,2.08,.72)])
 else:raise ValueError(kind)
 return m

def clean(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bad=[f for f in bm.faces if f.calc_area()<1e-10]
 bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 return ob

def build_lod(name,settings,asset_dir):
 return clean(make(settings['kind'],settings['level'],name).finish([]))
