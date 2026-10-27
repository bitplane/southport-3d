"""Create a restrained metric ashlar map without photographic pixels."""
from pathlib import Path
from PIL import Image
import random
random.seed(23)
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
n=256;im=Image.new('RGB',(n,n));p=im.load()
# One metre repeat: two horizontal courses, alternating half-block joints.
for y in range(n):
 row=y//128
 for x in range(n):
  xx=(x+(128 if row%2 else 0))%256
  joint=(y%128<2 or xx%256<2)
  grain=random.randint(-4,4);v=(157 if joint else 185)+grain
  p[x,y]=(v,min(255,v+1),max(0,v-7))
im.save(out/'stone.png')
