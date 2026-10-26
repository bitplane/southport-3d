import json,math
from pathlib import Path
D=json.loads((Path(__file__).resolve().parents[1]/'research/layout.json').read_text());W=D['width'];L=D['depth']
def world(p):
 x,y,z=p;u,v=D['u_axis'],D['v_axis'];o=D['origin_site'];return(o[0]+u[0]*x+v[0]*y,o[1]+u[1]*x+v[1]*y,z+D['base'])
def top(x,y):
 if y<5.6:return D['front_eave']
 if 0<=x<5.6 and 5.6<=y<18:return 3.7
 if 0<=x<1.1 and 29<=y:return 3.8
 if 0<=x<5.6 and 18<=y<29:return 9.
 if 1.1<=x<14 and 29<=y<58.8:return 8.15
 return D['roof']
XS=[0,1.1,5.6,14,W];YS=[0,5.6,18,29,58.8,L]
def at(side):
 if side=='front':return lambda x,z,o=0:(x,-o,z)
 if side=='north':return lambda y,z,o=0:(W+o,y,z)
 if side=='rear':return lambda x,z,o=0:(W-x,L+o,z)
 return lambda y,z,o=0:(-o,L-y,z)
def canopy_ring(radius,z,n=16):
 cx,cy=D['carousel']['centre'];return[(cx+radius*math.cos(2*math.pi*i/n),cy+radius*math.sin(2*math.pi*i/n),z)for i in range(n)]
