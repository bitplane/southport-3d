"""Metric slab, brick, asphalt and tactile maps, authored without photo pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
n=512;rng=np.random.default_rng(20261022);y,x=np.mgrid[:n,:n]
for name,colour,cols,rows in [('paving',(166,162,147),4,6),('brick',(141,93,79),12,24),('asphalt',(63,65,64),1,1),('tactile',(166,128,89),4,4),('junction-tactile',(157,149,128),9,9)]:
 xx=x/n*cols;yy=y/n*rows;row=np.floor(yy).astype(int);col=np.floor(xx+(row%2)*.5).astype(int)
 variation=rng.uniform(-7,7,(rows+1,cols+1))[row,col];noise=rng.normal(0,1.6,(n,n))
 a=np.array(colour)[None,None,:]+(variation+noise)[:,:,None]
 joint=((xx+(row%2)*.5)%1<.018)|(yy%1<.018);height=np.where(joint,0,.0015)
 if name=='asphalt':a=np.array(colour)[None,None,:]+rng.normal(0,4,(n,n,1));height=rng.normal(0,.0002,(n,n))
 else:a[joint]*=.80
 if name=='tactile':
  radius=np.sqrt(((x/n*24)%1-.5)**2+((y/n*24)%1-.5)**2);height+=np.clip((.30-radius)/.30,0,1)*.004
 if name=='junction-tactile':
  u=(x/n*3.6+.03)%.06-.03;v=(y/n*3.6+.03)%.06-.03
  height+=.004*np.maximum(0,1-(u*u+v*v)/.012**2)
 dy,dx=np.gradient(height,3.6/n);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))
 Image.fromarray(np.uint8((normal+1)*127.5)).save(out/(name+'-normal.png'))
