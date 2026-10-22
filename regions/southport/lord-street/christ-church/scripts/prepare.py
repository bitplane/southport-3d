"""Authored coursed materials, never copied photographic pixels."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(1821)
for name,colour,courses,width in [('stone',(165,155,126),24,75),('brick',(139,82,61),32,90),('buff-brick',(153,129,96),16,50),('slate',(86,91,90),64,96)]:
    im=Image.fromarray(np.clip(np.array(colour)[None,None,:]+rng.normal(0,3,(512,512,1)),0,255).astype('uint8'))
    d=ImageDraw.Draw(im)
    for j,y in enumerate(range(0,512,courses)):
        mortar=tuple(max(0,c-22) for c in colour)
        d.line((0,y,512,y),fill=mortar,width=2)
        for x in range(-(j%2)*width//2,512,width):d.line((x,y,x,y+courses),fill=mortar,width=2)
    im.save(ROOT/'textures'/f'{name}.png')

# Vertically streaked metal cladding: authored weathering, not sampled imagery.
a=np.empty((512,512,3),dtype=float)
for x in range(512):
    shade=rng.normal(0,12)+(-22 if x%85<3 else 0)
    for y in range(512):a[y,x]=np.array([164,166,156])+shade*(.3+.7*y/512)+rng.normal(0,3)
Image.fromarray(np.clip(a,0,255).astype('uint8')).save(ROOT/'textures/cafe-metal.png')
