"""Authored stone cladding and mottled polished pier textures; no photo inputs."""
from pathlib import Path
import numpy as np
from PIL import Image
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
rng=np.random.default_rng(118122);n=512;y,x=np.mgrid[:n,:n]
noise=rng.normal(0,.9,(n,n))
colour=np.array([186,183,169])[None,None,:]+noise[:,:,None]
colour[(x%128<1)|(y%128<1)]*=.80
Image.fromarray(np.uint8(np.clip(colour,0,255))).save(out/'cladding.png')
# Authored brecciated green marble: angular mineral islands in pale veins.
# No image sampling. A toroidal Voronoi field gives a seamless metric tile.
points=rng.uniform(0,n,(150,2));best=np.full((n,n),np.inf);second=best.copy();ids=np.zeros((n,n),dtype=int)
for i,(px,py) in enumerate(points):
 dx=np.abs(x-px);dy=np.abs(y-py);dx=np.minimum(dx,n-dx);dy=np.minimum(dy,n-dy)
 distance=dx*dx+dy*dy;take=distance<best
 second=np.where(take,best,np.minimum(second,distance));best=np.minimum(best,distance);ids=np.where(take,i,ids)
colours=np.array([113,126,109])+rng.normal(0,29,(len(points),1))
colour=colours[ids]+rng.normal(0,4,(n,n,1))
vein=(np.sqrt(second)-np.sqrt(best))<1.4
colour[vein]=colour[vein]*.55+np.array([179,184,165])*.45+rng.normal(0,3,(vein.sum(),1))
# Fine diagonal pale fissures subdivide some larger fragments.
# Patches of paler mineral interrupt the cell boundaries; this is veined stone,
# not a uniform mosaic or mortar grid.
macro=np.asarray(Image.fromarray(np.uint8(rng.uniform(0,255,(24,24)))).resize((n,n),Image.Resampling.BICUBIC))/255
colour=colour*.70+(np.array([112,125,109])+((macro-.5)*70)[:,:,None])*.30
fissure=np.abs(np.sin(x*.17+y*.11+ids*1.7))<.045
colour[fissure]=colour[fissure]*.5+np.array([152,160,143])*.5
Image.fromarray(np.uint8(np.clip(colour,0,255))).save(out/'pier.png')

# Four brick courses in a .88 x .30 metre authored repeat.
brick=np.array([148,94,62])[None,None,:]+rng.normal(0,5,(n,n,1))
row=y//128;xx=(x+(row%2)*64)%128
brick[(xx<3)|(y%128<7)]=[124,117,100]
Image.fromarray(np.uint8(np.clip(brick,0,255))).save(out/'service-brick.png')
