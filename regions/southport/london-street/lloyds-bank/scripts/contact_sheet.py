from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
canvas=Image.new('RGB',(1440,480),'white')
for i,name in enumerate(['street','anchor','roof']):
 im=ImageOps.contain(Image.open(root/'renders'/f'{name}.png').convert('RGB'),(480,440))
 canvas.paste(im,(i*480+(480-im.width)//2,0));ImageDraw.Draw(canvas).text((i*480+10,450),name,fill='black')
canvas.save(root/'renders/contact-sheet.png')
