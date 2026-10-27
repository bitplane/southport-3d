"""Authored lettering and material patterns, without reference photograph pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(exist_ok=True)
script='/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf';serif='/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(path,size):return ImageFont.truetype(path,size)
def centered(d,xy,text,f,fill='#161616'):d.text(xy,text,font=f,fill=fill,anchor='mm')
im=Image.new('RGB',(2048,256),'#f0eee8');d=ImageDraw.Draw(im);d.text((28,25),'Jacksons',font=font(script,172),fill='#181818');d.text((650,48),'Traditional Fish And Chips',font=font(script,115),fill='#181818');centered(d,(340,202),'Restaurant',font(serif,35));centered(d,(1250,202),'Takeaway',font(serif,35));im.save(P/'fascia.png')
im=Image.new('RGB',(1024,256),'#f0eee8');d=ImageDraw.Draw(im);centered(d,(512,88),'Jacksons',font(script,160));centered(d,(512,205),'Traditional Fish And Chips  Restaurant',font(serif,43));im.save(P/'side-fascia.png')
im=Image.new('RGB',(512,640),'#f0eee8');d=ImageDraw.Draw(im);centered(d,(256,78),'Jacksons',font(script,116));
for y,t in [(220,'Award Winning'),(290,'Traditional'),(360,'Fish & Chips'),(430,'5 Star Rated')]:centered(d,(256,y),t,font(bold,38))
centered(d,(256,532),'★ ★ ★ ★ ★',font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',48));im.save(P/'award.png')
im=Image.new('RGB',(512,512),'#f3f2ea');d=ImageDraw.Draw(im)
for y,t in [(98,'FISH'),(250,'&'),(402,'CHIPS')]:centered(d,(256,y),t,font(bold,126))
im.save(P/'fish-sign.png')
rng=random.Random(21)
for name in ('brick','tile','slate'):
 im=Image.new('RGB',(512,512));d=ImageDraw.Draw(im)
 if name=='brick':
  d.rectangle((0,0,511,511),fill='#80665a')
  for row in range(13):
   y=row*40;shift=(row%2)*64
   for col in range(-1,5):
    x=col*128+shift;n=rng.randrange(-11,12);c=(max(0,125+n),max(0,59+n),max(0,43+n));d.rectangle((x+2,y+2,x+126,y+37),fill=c)
 elif name=='tile':
  d.rectangle((0,0,511,511),fill='#78594a')
  for row in range(4):
   for col in range(4):
    x=col*128;y=row*128;n=rng.randrange(-12,13);d.rectangle((x+2,y+2,x+125,y+125),fill=(155+n,102+n,76+n))
 elif name=='slate':
  d.rectangle((0,0,511,511),fill='#353a3a')
  for row in range(10):
   y=row*52;shift=(row%2)*32
   for col in range(-1,9):
    x=col*64+shift;n=rng.randrange(-8,9);d.rectangle((x+1,y+1,x+63,y+50),fill=(74+n,79+n,78+n))
 im.save(P/(name+'.png'))
