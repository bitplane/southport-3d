"""Generate small repeatable brick tiles; no photographic source pixels."""
from pathlib import Path
import random
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];dest=ROOT/'textures';dest.mkdir(exist_ok=True)
def srgb(x):return round(255*(12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055))
for name,rgb in [('brick',(.40,.22,.16)),('paintbrick',(.68,.68,.61))]:
 rng=random.Random(387);im=Image.new('RGB',(512,512),tuple(srgb(c*.70) for c in rgb));draw=ImageDraw.Draw(im)
 for row in range(12):
  y0=round(row*512/12);y1=round((row+1)*512/12)
  for col in range(-1,6):
   x0=round((col+(row%2)*.5)*512/5);x1=round((col+1+(row%2)*.5)*512/5)
   f=rng.uniform(.79,1.02);color=tuple(srgb(min(1,c*f)) for c in rgb)
   draw.rectangle((x0+1,y0+1,x1-2,y1-2),fill=color)
 im.save(dest/(name+'.png'))
