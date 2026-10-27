"""Authored blockwork texture; no photograph pixels."""
from pathlib import Path
import random
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];out=root/'textures';out.mkdir(exist_ok=True)
rng=random.Random(52902208);size=512
im=Image.new('RGB',(size,size),(153,141,116));draw=ImageDraw.Draw(im)
# One 1.76 m × 0.88 m repeat: four stretcher blocks wide, four courses high.
for row in range(4):
 y=row*128;shift=(row%2)*64
 for col in range(-1,6):
  x=col*128-shift;v=rng.randrange(-7,8);color=(max(0,165+v),max(0,150+v),max(0,122+v))
  draw.rectangle((x+2,y+2,x+125,y+125),fill=color)
im.save(out/'blockwork.png')
