"""Authored surface maps and readable signage; no source photograph pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(exist_ok=True)
rng=np.random.default_rng(15);y,x=np.mgrid[:512,:512];row=y//64;col=((x+(row%2)*32)//64)%8
for name,rgb in [('slate',[74,79,76]),('render',[219,216,195])]:
 a=np.array(rgb)+rng.normal(0,2,(512,512,1))
 if name=='slate':
  a=a+rng.normal(0,7,(8,8))[row,col,None];a[(y%64<3)|((x+(row%2)*32)%64<2)]*=.65
 else:a[(y%48<2)|((x+(y//48%2)*48)%96<2)]*=.94
 Image.fromarray(np.uint8(np.clip(a,0,255))).save(P/(name+'.png'))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
italic='/usr/share/fonts/truetype/liberation2/LiberationSerif-BoldItalic.ttf'
def sign(name,bg,lines):
 im=Image.new('RGB',(1024,256),bg);d=ImageDraw.Draw(im)
 for text,cy,color,size,style in lines:
  f=ImageFont.truetype(italic if style else font,size);box=d.textbbox((0,0),text,font=f);tw=box[2]-box[0]
  if tw>980:f=ImageFont.truetype(italic if style else font,int(size*980/tw))
  d.text((512,cy),text,fill=color,font=f,anchor='mm',stroke_width=1)
 im.save(P/(name+'.png'))
sign('salaars','#181a18',[("SALAARS",100,'#f4f0db',145,0),('PIZZAS  •  FRIED CHICKEN  •  PERI PERI',220,'#edd948',33,0)])
sign('antonios','#e4e3d5',[("Antonio’s",110,'#173a23',135,1),('ITALIAN GELATO  •  AWARD WINNING ICE CREAM',223,'#254832',30,0)])
sign('rock','#be3b6a',[('SOUTHPORT ROCK',93,'#f4d980',102,0),('SWEETS • FUDGE • CANDY FLOSS',215,'#fff5dc',40,0)])
# Counter decoration is intentionally illustrative, not guessed photographic detail.
for name in ['antonios','rock']:
 im=Image.open(P/(name+'.png'));im.save(P/(name+'-counter.png'))
