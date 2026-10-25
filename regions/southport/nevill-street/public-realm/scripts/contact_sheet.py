from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]/'renders'
names=['corridor','monument-seam','middle-junctions','promenade','paving','crossing','stanley-corner']
names=[name for name in names if (root/(name+'.png')).exists()]
assert names, 'No review renders produced'
sheet=Image.new('RGB',(1200,1380),(32,35,34));draw=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
 im=Image.open(root/(name+'.png')).convert('RGB');im.thumbnail((600,430));x=(i%2)*600;y=(i//2)*460
 sheet.paste(im,(x+(600-im.width)//2,y+26));draw.text((x+12,y+7),name,fill=(235,235,225))
sheet.save(root/'contact-sheet.png')
