from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
canvas=Image.new('RGB',(1440,900),'white')
for i,name in enumerate(['front','overview','rear','roof','chapel']):
 im=Image.open(root/'renders'/f'{name}.png').convert('RGB');im=ImageOps.contain(im,(480,420));x=(i%3)*480;y=(i//3)*450;canvas.paste(im,(x+(480-im.width)//2,y));ImageDraw.Draw(canvas).text((x+12,y+424),name,fill='black')
canvas.save(root/'renders/contact-sheet.png')
