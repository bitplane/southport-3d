from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[1]/'renders'
images=[Image.open(r/(n+'.png')).convert('RGB') for n in ['overview','underneath','detail']]
out=Image.new('RGB',(800,1500),'white')
for i,im in enumerate(images):im.thumbnail((800,500));out.paste(im,(0,i*500))
out.save(r/'contact-sheet.jpg')
