"""Two-view massing review sheet."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
canvas=Image.new('RGB',(1440,540),'white')
for i,name in enumerate(['street','roof']):
 im=ImageOps.contain(Image.open(root/'renders'/f'{name}.png').convert('RGB'),(720,500))
 canvas.paste(im,(i*720+(720-im.width)//2,0));ImageDraw.Draw(canvas).text((i*720+12,510),name,fill='black')
canvas.save(root/'renders/contact-sheet.png')
