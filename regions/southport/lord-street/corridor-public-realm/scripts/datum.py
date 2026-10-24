def grade(x,y):
 z=-.0075-.022*max(-36,min(36,y))
 # Blend the known rising Nevill datum into its immediate corner neighbours.
 near=max(0,1-max(-81.84-x,x-34.19,0)/16)
 return z+max(0,min(207.07,y-41))*((2.2+.7995)/207.07)*near
