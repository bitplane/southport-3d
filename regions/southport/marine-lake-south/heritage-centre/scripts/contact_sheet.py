from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1];names=['front','front-oblique','rear','entry'];canvas=Image.new('RGB',(1440,1000),'white');draw=ImageDraw.Draw(canvas)
for i,name in enumerate(names):
 im=ImageOps.contain(Image.open(root/'renders'/f'{name}.png').convert('RGB'),(720,470));x=(i%2)*720;y=(i//2)*500;canvas.paste(im,(x+(720-im.width)//2,y));draw.text((x+12,y+475),name,fill='black')
canvas.save(root/'renders/contact-sheet.png')
