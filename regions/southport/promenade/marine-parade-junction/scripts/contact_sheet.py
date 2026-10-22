from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
p=Path(__file__).resolve().parents[1]/'renders';out=Image.new('RGB',(1200,920),(35,38,38));d=ImageDraw.Draw(out)
for i,n in enumerate(['overview','plan','marine-crossing','promenade-crossing']):
 im=Image.open(p/(n+'.png'));im.thumbnail((590,430));x=(i%2)*600;y=(i//2)*460;out.paste(im,(x,y+24));d.text((x+5,y+4),n,fill='white')
out.save(p/'contact-sheet.png')
