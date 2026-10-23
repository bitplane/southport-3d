"""Author repeating masonry/roof colour maps; no reference-image pixels."""
from pathlib import Path
import random
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'textures').mkdir(exist_ok=True)
rng=random.Random(1121)
for name,base,cols,rows,mortar in [('brick',(163,108,70),5,13,(109,99,82)),('slate',(104,109,108),4,7,(60,64,63)),('tile',(124,101,84),5,7,(70,65,58))]:
    im=Image.new('RGB',(1024,1024),mortar);draw=ImageDraw.Draw(im)
    cw,ch=1024/cols,1024/rows
    for row in range(rows):
        for col in range(-1,cols+1):
            x=(col+(row%2)*.5)*cw;y=row*ch
            delta=rng.randint(-15,15);color=tuple(max(0,min(255,c+delta)) for c in base)
            draw.rectangle((round(x+3),round(y+3),round(x+cw-3),round(y+ch-3)),fill=color)
    im.save(ROOT/'textures'/f'{name}.png')
