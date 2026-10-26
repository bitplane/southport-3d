from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1]/'renders'
names=['chapel-oblique','corner-return','corporation','arcade','roof'];out=Image.new('RGB',(1500,900),(230,230,230))
for i,n in enumerate(names):
 im=Image.open(R/(n+'.png')).convert('RGB');im.thumbnail((500,420));x=(i%3)*500;y=(i//3)*450;out.paste(im,(x,y+25));ImageDraw.Draw(out).text((x+10,y+5),n,fill=(0,0,0))
out.save(R/'contact-sheet.jpg')
