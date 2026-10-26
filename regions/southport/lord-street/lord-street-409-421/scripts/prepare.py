"""Deterministic procedural brick colour; no reference image pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import random
root=Path(__file__).resolve().parents[1];(root/'textures').mkdir(exist_ok=True)
r=random.Random(393);im=Image.new('RGB',(512,512),(104,91,80));dr=ImageDraw.Draw(im)
for row in range(16):
 for col in range(-1,5):
  x=(col+.5*(row%2))*128;y=row*32;f=r.uniform(.86,1.08)
  dr.rectangle((int(x+2),y+2,int(x+125),y+29),fill=tuple(round(v*f) for v in (142,77,56)))
im.save(root/'textures/brick.png')

# Subtle staggered slate sizes: procedural appearance, not photographic weathering.
im=Image.new('RGB',(512,512),(75,83,90));dr=ImageDraw.Draw(im)
for row in range(8):
 for col in range(-1,5):
  x=(col+.5*(row%2))*128;y=row*64;f=r.uniform(.96,1.04)
  dr.rectangle((int(x+1),y+1,int(x+126),y+61),fill=tuple(round(v*f) for v in (104,112,118)))
im.save(root/'textures/slate.png')

# Subtle staggered ashlar joints, authored procedural stone colour.
im=Image.new('RGB',(512,512),(132,98,80));dr=ImageDraw.Draw(im)
for row in range(6):
 for col in range(-1,3):
  x=(col+.5*(row%2))*256;y=row*86;f=r.uniform(.97,1.03)
  dr.rectangle((int(x+1),y+1,int(x+254),y+84),fill=tuple(round(v*f)for v in (168,127,105)))
im.save(root/'textures/stone.png')
