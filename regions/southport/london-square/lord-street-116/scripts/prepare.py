"""Deterministic authored cladding, aggregate spandrels and red tiles; no photos."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(116);n=512;y,x=np.mgrid[:n,:n]
for name,base,noise in [('cladding',[214,212,201],1.2),('spandrel',[145,163,157],11),('red-tile',[173,21,28],2)]:
 a=np.array(base)[None,None,:]+rng.normal(0,noise,(n,n,1))
 if name=='cladding':
  # Larger rectangular sheets; restrained mottling, not invented cracks.
  weather=np.asarray(Image.fromarray(rng.integers(0,255,(32,32),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),dtype=float)/255
  a-=weather[:,:,None]*9
  a[(x%128<1)|(y%256<1)]*=.85
 elif name=='red-tile':
  # Four columns/four rows mapped onto .32 x 1.2 m: 8 x 30 cm tiles.
  a[(x%128<3)|(y%128<1)]*=.65
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/(name+'.png'))

# Authored felt lap pattern and weathering, never a sampled aerial photograph.
coarse=np.asarray(Image.fromarray(rng.integers(0,255,(8,8),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),dtype=float)/255
felt=np.array([87,91,90])[None,None,:]+(coarse[:,:,None]-.5)*10+rng.normal(0,2,(n,n,1))
for row in range(0,n,48):felt[row:row+1]*=.78
for col in range(0,n,192):felt[:,col:col+1]*=.90
Image.fromarray(np.uint8(np.clip(felt,0,255))).save(out/'roof-felt.png')
brick=np.array([138,99,78])[None,None,:]+rng.normal(0,4,(n,n,1))
rows=y//128;xx=(x+(rows%2)*64)%128
brick[(xx<3)|(y%128<7)]=[112,109,99]
Image.fromarray(np.uint8(np.clip(brick,0,255))).save(out/'roof-brick.png')
