"""July 2026 Stanley corner furniture, separate from the walkable floor."""
import math
from mathutils import Matrix
from southport3d.geometry import Mesh

def build(scene,materials,grade):
 import bpy
 c=bpy.data.collections.new('stanley-furniture');scene.collection.children.link(c)
 palette=[]
 for name,col in [('grey metal',(.31,.34,.34)),('black timber',(.055,.045,.035)),('cream sign',(.73,.71,.63)),('parking blue',(.05,.20,.38)),('tourist brown',(.31,.16,.07))]:
  m=bpy.data.materials.new('Stanley '+name);m.use_nodes=True;m.diffuse_color=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);palette.append(m)
 # Metric picnic-table family, two observed tables outside the bar.
 # Position/orientation visually estimated from street-front-road.png.
 for x,y,angle in [(6.65,92.6,0),(6.65,88.0,0)]:
  m=Mesh('Furniture picnic table');m.box((0,0,.74),(1.65,.70,.065),1)
  for side in (-1,1):m.box((0,side*.57,.43),(1.65,.25,.06),1)
  for u in (-.57,.57):
   m.tube([(u,-.62,.04),(u,-.18,.72)],.045,1,4);m.tube([(u,.62,.04),(u,.18,.72)],.045,1,4)
   m.box((u,0,.38),(.08,1.45,.075),1)
  m.transform(Matrix.Translation((x,y,grade(y,x)))@Matrix.Rotation(angle,4,'Z'));o=m.finish(palette,c)
  o.data.uv_layers.new(name='Untextured furniture')
 # Two-pole direction panel seen at the rounded corner. Abstract bands retain
 # the photographed white/blue/brown hierarchy; tiny text not invented.
 m=Mesh('Furniture direction board');m.box((0,0,3.05),(1.55,.10,1.55),2)
 for u in (-.56,.56):m.tube([(u,0,0),(u,0,3.80)],.045,0,8)
 m.box((0,-.061,2.52),(1.48,.02,.42),4)
 for zz in (2.95,3.37):m.box((-.47,-.061,zz),(.19,.02,.20),3)
 # Street View places the board on the kerb side of the glazed canopy.
 # The canopy ends at site X=5.84; the former X=6 placement cut its roof.
 m.transform(Matrix.Translation((4.9,95.4,grade(95.4,4.9)))@Matrix.Rotation(math.pi/2,4,'Z'));o=m.finish(palette,c);o.data.uv_layers.new(name='Untextured furniture')
 return c
