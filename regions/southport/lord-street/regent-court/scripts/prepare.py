"""Procedural red brick for observed masonry, not photographic imagery."""
from pathlib import Path
from PIL import Image,ImageDraw
import random
root=Path(__file__).resolve().parents[1];(root/'textures').mkdir(exist_ok=True)
rng=random.Random(51826173);im=Image.new('RGB',(512,512),(91,69,62));d=ImageDraw.Draw(im)
for row in range(16):
 y=row*32;shift=32 if row%2 else 0
 for col in range(-1,9):
  x=col*64-shift;v=rng.randint(-13,13)
  d.rectangle((x+1,y+1,x+62,y+30),fill=(max(0,116+v),max(0,68+v//2),max(0,58+v//2)))
im.save(root/'textures/brick.png')
