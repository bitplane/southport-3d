"""Shared bridge registration and bounded profile controls."""
import json,math,os
from pathlib import Path
from southport3d.elevation import Elevations
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'research/layout.json').read_text())
U=D['axis'];q=math.hypot(*U);U=[v/q for v in U];N=[-U[1],U[0]]
E=Elevations(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/elevation/marine-drive.json');GRADE=E.surface('marine-bridge-measured-reference')
def xy(s,t):return (D['origin'][0]+s*U[0]+t*N[0],D['origin'][1]+s*U[1]+t*N[1])
def transform(p):return (*xy(p[0],p[1]),p[2])
def grade(s,t=0):return GRADE.height(*xy(s,t))
def width(s):
 knots=[(0,8),(122,8),(128,9.4),(134,12.3),(139,13.3),(143,13.3),(147,11),(150,8)]
 for (a,w),(b,W) in zip(knots,knots[1:]):
  if s<=b:return w+(W-w)*(s-a)/(b-a)
 return 8
# Break deck surfaces at every shared geographic profile knot. Crossfall is zero;
# transverse points still use the evaluator rather than copied height arithmetic.
def stations():
 ss={0.,23.8,31.8,43.8,55.8,67.8,79.8,91.8,103.8,122.,128.,134.,139.,143.,147.,150.}
 # Measured profile uses the bridge axis, so every station is a transverse
 # break shared by road, soffit and fascia. No copied geographic Y knots.
 ss.update(s for s in GRADE.stations if 0<s<150)
 return sorted(ss)

def ground(s,t):return E.surface('marine-mainland').height(*xy(s,t))
