from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
r=Path(__file__).resolve().parents[1]/'renders';names=['overview','north','west','pylon-head','deck-detail','underside'];out=Image.new('RGB',(1200,1200),'white');d=ImageDraw.Draw(out)
for i,n in enumerate(names):
 im=Image.open(r/(n+'.png'));im=ImageOps.contain(im,(600,370));x=(i%2)*600;y=(i//2)*400;out.paste(im,(x,y+25));d.text((x+8,y+5),n,fill='black')
out.save(r/'contact-sheet.jpg')
