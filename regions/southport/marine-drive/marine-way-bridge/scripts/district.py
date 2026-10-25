"""Independent fixed receiver envelope; fine mesh counts never determine topology."""
from blender_envelope import Surfaces
from shapes import Faces,transform

def surfaces(asset):
 f=Faces();f.pylons(coarse=True);f.deck(coarse=True);f.stays(coarse=True);f.rails(coarse=True)
 s=Surfaces(['pylons','deck','fittings'],transform)
 # The District silhouette deliberately omits all lanterns, horns, tension wires,
 # pickets, sleeves, collars and underside ribs. This list is fixed, not a source
 # mesh traversal; detailed additions cannot grow receivers or atlases.
 for row in f.items:
  s.part=row['part'];p=row['vertices'];kw={'weight':(8 if row['name'].startswith('post ') else .05 if row['name'].startswith('rail ') else row['weight']),'cage':row['cage_m']}
  if len(p)==4:s.quad(row['name'],p,**kw)
  else:
   for i in range(1,len(p)-1):s.triangle(row['name']+' cap '+str(i),[p[0],p[i],p[i+1]],**kw)
 return s.result
