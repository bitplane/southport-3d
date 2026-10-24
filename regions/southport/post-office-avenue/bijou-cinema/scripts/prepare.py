"""Authored metric brick swatches; no photographic reference pixels."""
from pathlib import Path
import random
from PIL import Image,ImageDraw
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
for name,base in [('front-brick',(154,87,59)),('rear-brick',(113,83,61))]:
 rng=random.Random(1521);im=Image.new('RGB',(1024,512),(99,89,75));d=ImageDraw.Draw(im)
 # Ten bricks across 2.25m, eight courses across 0.60m.
 for row in range(8):
  for col in range(-1,11):
   x=round((col+.5*(row%2))*102.4);y=row*64
   delta=rng.uniform(-16,16);colour=tuple(max(0,min(255,round(c+delta))) for c in base)
   d.rectangle((x+2,y+4,x+100,y+61),fill=colour)
   for k in range(90):
    xx=x+rng.randrange(4,99);yy=y+rng.randrange(6,59)
    if 0<=xx<1024:d.point((xx,yy),fill=tuple(max(0,min(255,c+rng.randrange(-12,13))) for c in colour))
 im.save(out/(name+'.png'))

# Slate courses use a fixed metric swatch, independent of mesh detail.
rng=random.Random(88);im=Image.new("RGB",(1024,1024),(42,46,49));d=ImageDraw.Draw(im)
for row in range(8):
 for col in range(-1,9):
  x=col*128+(64 if row%2 else 0);y=row*128;c=rng.randrange(65,84)
  d.rectangle((x+2,y+3,x+126,y+125),fill=(c,c+5,c+8))
  d.line((x+2,y+125,x+126,y+125),fill=(51,57,60),width=3)
im.save(out/"slate.png")
