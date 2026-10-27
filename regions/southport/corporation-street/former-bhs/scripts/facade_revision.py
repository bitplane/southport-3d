"""Measured facade and roof composition, revision 01; shared build namespace.

The assembly follows elevation-schedule.json. Ornament and measured shopfronts
are developed after the main volumes have been compared to the source photos.
"""
# Older left range and the ornate corner have separate opening schedules.
chapel_holes=[]
chapel_doors=[(6.5,1.05),(16.9,1.0),(24.4,1.4)]
chapel_door_holes=[]
for a,b in [(.5,5.1),(5.3,9.2),(9.4,13.2),(13.4,17.5),(17.7,22.3),(22.5,27.9)]:
 doors=[(u-w/2,u+w/2) for u,w in chapel_doors if a<u<b]
 if not doors:chapel_holes.append(rect(a,.12,b,3.6));continue
 lo,hi=doors[0]
 chapel_holes.extend([rect(a,.12,lo,3.6),rect(hi,.12,b,3.6),rect(lo,2.95,hi,3.6)])
 chapel_door_holes.append(rect(lo,.12,hi,2.95))
chapel_holes += chapel_door_holes
for u in [2.1,4.1,7.3,9.2]:
 chapel_holes += [rect(u-.5,4.7,u+.5,7.4),arch(u,8.7,10.4,.5,.5)]
for u in [11.0,13.0]:chapel_holes.append(rect(u-.55,8.9,u+.55,11.25))
# Two principal round-headed arches, tall enough to occupy the lower storey.
for u in [19.1,22.8]:chapel_holes.append(arch(u,4.2,7.0,1.2,1.2))
chapel_open=[rect(14.05,4.2,16.95,12.35),rect(17.0,8.55,26.9,12.35),rect(27.0,4.2,W,12.35)]
chapel_holes += chapel_open
wall('Chapel revised face',W,12.8,chapel_holes,'x',0,'frontage',pale,chapel_open+chapel_door_holes)
exec(compile((ROOT/'scripts'/'arcade_side_revision.py').read_text(),str(ROOT/'scripts'/'arcade_side_revision.py'),'exec'),globals())
# The corner return has a second recessed gallery and tall lower arches.
corp_open=[rect(.2,.15,F-.2,3.5),rect(0,4.2,1.45,12.35),rect(1.45,8.55,F,12.35)]
corp_holes=list(corp_open)
for u in [3.4,6.8,10.2,13.6,17.0,20.0]:corp_holes.append(arch(u,4.2,7.0,1.05,1.05))
wall('Corporation revised face',F,12.8,corp_holes,'y',W,'frontage',pale,corp_open)
face('Corporation display glazing',[(W-.18,.2,.15),(W-.18,F-6.0,.15),(W-.18,F-6.0,2.75),(W-.18,.2,2.75)],'frontage',glass)
face('Chapel rear',[(0,F,0),(W,F,0),(W,F,12.8),(0,F,12.8)],'rear',pale)
# Close the exposed court-side end between the rear wall and the flat roof.
# Its plain finish is provisional; the round circulation tower masks part of
# the junction and the concealed construction is not visible in the references.
face('Chapel rear roof closure',[(A,F,12.8),(W,F,12.8),(W-2.3,F,16.5),(A,F,16.5)],'rear',pale)

def gallery_wall(name,a,b,z0,z1,openings,axis,fixed):
 def point(u,z,depth=0):return (u,fixed+depth,z) if axis=='x' else (fixed-depth,u,z)
 m=Mesh('Shell '+name)
 for q in cut(rect(a,z0,b,z1),openings):m.add([point(*v) for v in q],[tuple(range(len(q)))])
 for h in openings:
  for x,y in zip(h,h[1:]+h[:1]):m.add([point(*x),point(*y),point(*y,.14),point(*x,.14)],[(0,1,2,3)])
 finish(m,'frontage',pale)
 for p in openings:
  m=Mesh('Glazing '+name);m.add([point(*v,.14) for v in p],[tuple(range(len(p)))]);finish(m,'frontage',glass)
# Rear wall is 1.25 m behind the actual column line, with broad rear windows.
gallery_wall('Chapel gallery back',17.0,26.9,8.55,12.35,[rect(18.0,9.2,20.8,11.55),rect(22.3,9.2,25.1,11.55)],'x',1.25)
face('Chapel gallery floor',[(17,.18,8.55),(26.9,.18,8.55),(26.9,1.25,8.55),(17,1.25,8.55)],'frontage',cream)
face('Chapel gallery soffit',[(17,1.25,12.35),(26.9,1.25,12.35),(26.9,.18,12.35),(17,.18,12.35)],'frontage',cream)
gallery_wall('Corporation gallery back',1.45,F,8.55,12.35,[rect(a,9.2,b,11.55) for a,b in [(2.1,4.7),(5.5,8.1),(8.9,11.5),(12.3,14.9),(15.7,18.3)]],'y',W-1.25)
face('Corporation gallery floor',[(W-1.25,1.45,8.55),(W-.18,1.45,8.55),(W-.18,F,8.55),(W-1.25,F,8.55)],'frontage',cream)
face('Corporation gallery soffit',[(W-1.25,F,12.35),(W-.18,F,12.35),(W-.18,1.45,12.35),(W-1.25,1.45,12.35)],'frontage',cream)
# Massing includes actual projecting cylindrical assemblies; bands follow the arc.
def curved_bay(name,cx,cy,r,t0,t1,segments,connect=False):
 arc=[(cx+r*math.cos(t0+(t1-t0)*i/segments),cy+r*math.sin(t0+(t1-t0)*i/segments)) for i in range(segments+1)]
 for z0,z1,material,label in [(4.2,4.72,pale,'base'),(4.72,7.86,glass,'lower glazing'),(7.86,8.55,pale,'intermediate spandrel'),(8.55,9.02,pale,'upper sill'),(9.02,11.83,glass,'upper glazing'),(11.83,12.35,pale,'upper cornice')]:
  m=Mesh(('Glazing ' if material==glass else 'Architecture ')+name+' '+label)
  for (x0,y0),(x1,y1) in zip(arc,arc[1:]):m.add([(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)],[(0,1,2,3)])
  finish(m,'frontage',material)
  if connect:
   m=Mesh(('Glazing ' if material==glass else 'Architecture ')+name+' return '+label)
   for (x0,y0),(x1,y1) in [(arc[0],(arc[0][0],0)),(arc[-1],(W,arc[-1][1]))]:
    m.add([(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)],[(0,1,2,3)])
   finish(m,'frontage',material)
 for x,y in arc[::4]+([arc[-1]] if segments%4 else []):
  for z0,z1 in [(4.72,7.86),(9.02,11.83)]:box('Architecture '+name+' mullion',x-.045,y-.045,z0,x+.045,y+.045,z1,'frontage',cream)
 for z in [4.72,7.86,8.55,9.02,11.83,12.35]:
  m=Mesh('Architecture '+name+' curved band');m.tube([(x,y,z)for x,y in arc],.10,sides=8);finish(m,'frontage',cream)
curved_bay('inner round bay',15.5,0,1.45,math.pi,math.tau,16)
curved_bay('corner round bay',W-1.4,1.4,1.9,-math.pi/2,0,12,True)
# Structural columns stand on the front line rather than on the rear gallery wall.
for u in [17.3,19.0,20.7,22.4,24.1,25.8]:
 m=Mesh('Architecture gallery column');m.lathe((u,.02),[(8.55,.16),(8.68,.16),(11.95,.12),(12.18,.17)],segments=12);finish(m,'frontage',columnstone)
for v in [1.7,4.9,8.1,11.3,14.5,17.7,20.4]:
 m=Mesh('Architecture return gallery column');m.lathe((W-.02,v),[(8.55,.16),(8.68,.16),(11.95,.12),(12.18,.17)],segments=12);finish(m,'frontage',columnstone)
# Principal horizontal cornices, structural canopy and framing are retained.
for z,h in [(4.0,.2),(8.25,.22),(12.4,.28)]:box('Architecture front cornice',0,-.23,z,W,-.02,z+h,'frontage',cream)
for z in [4.0,8.25,12.4]:box('Architecture return cornice',W+.02,0,z,W+.22,F,z+.2,'frontage',cream)
box('Architecture canopy',0,-3.0,3.72,W,-.12,3.93,'frontage',timber)
box('Architecture canopy fascia',0,-3.05,3.75,W,-3.0,3.96,'frontage',dark)
for u in [1.0,8.0,15.0,22.0,27.5]:box('Architecture canopy post',u-.045,-2.75,0,u+.045,-2.66,3.72,'frontage',dark)
# Upper shopfront framing is provisional at this massing stage.
for a,b in [(.5,5.1),(5.3,9.2),(9.4,13.2),(13.4,17.5),(17.7,22.3),(22.5,27.9)]:
 for u in [a,(a+b)/2,b]:box('Architecture shop mullion',u-.045,-.10,.12,u+.045,.04,3.6,'frontage',dark)
# Roof slopes are cut in their own plane. The recessed holes are replaced by
# dormer fronts and cheeks; none of the glazing is buried behind the host plane.
schedule=json.loads((ROOT/'research/elevation-schedule.json').read_text())
chapel_dormers=schedule['dormers']['chapel'];side_dormers=schedule['dormers']['corporation']
front_profile=[(0,0),(W,0),(W-2.3,3),(2.3,3)]
front_open=[rect(u-w/2,.70,u+w/2,2.95) for u,w,k in chapel_dormers]
for i,q in enumerate(cut(front_profile,front_open)):
 face('Chapel roof plane %d'%i,[(u,v,12.8+3.7*v/3)for u,v in q],'roof',tile)
face('Arcade mansard return',[(0,F,12.8),(0,0,12.8),(2.3,3,16.5),(2.3,F,16.5)],'roof',slate)
side_profile=[(0,0),(F,0),(F,2.3),(3,2.3)]
side_open=[rect(v-w/2,.65,v+w/2,2.25)for v,w,k in side_dormers]
for i,q in enumerate(cut(side_profile,side_open)):
 face('Corporation roof plane %d'%i,[(W-d,v,12.8+3.7*d/2.3)for v,d in q],'roof',tile)
face('Chapel flat roof',[(2.3,3,16.5),(W-2.3,3,16.5),(W-2.3,F,16.5),(2.3,F,16.5)],'roof',flat)
for u,w,k in chapel_dormers:
 x0,x1=u-w/2,u+w/2;v0,v1=.70,2.95;z0=12.8+3.7*v0/3;top=16.75;frame=cream if k=='light' else dark
 # Cheeks meet the sloped roof at their lower edge; front glazing starts above it.
 for x in [x0,x1]:face('Dormer front cheek',[(x,v0,z0),(x,v1,12.8+3.7*v1/3),(x,v1,top),(x,v0,top)],'roof',frame)
 face('Dormer glazing',[(x0+.12,v0-.025,z0+.12),(x1-.12,v0-.025,z0+.12),(x1-.12,v0-.025,top-.16),(x0+.12,v0-.025,top-.16)],'roof',glass)
 for x in [x0,x1,(x0+x1)/2]:box('Architecture dormer frame',x-.065,v0-.10,z0,x+.065,v0+.10,top,'roof',frame)
 box('Architecture dormer transom',x0,v0-.10,top-.8,x1,v0+.10,top-.70,'roof',frame)
 box('Architecture dormer cap',x0-.12,v0-.12,top-.14,x1+.12,v1+.05,top+.04,'roof',frame)
for v,w,k in side_dormers:
 y0,y1=v-w/2,v+w/2;d0,d1=.65,2.25;z0=12.8+3.7*d0/2.3;top=16.75;frame=cream if k=='light' else dark
 for y in [y0,y1]:face('Return dormer cheek',[(W-d0,y,z0),(W-d1,y,12.8+3.7*d1/2.3),(W-d1,y,top),(W-d0,y,top)],'roof',frame)
 face('Return dormer glazing',[(W-d0+.025,y0+.12,z0+.12),(W-d0+.025,y1-.12,z0+.12),(W-d0+.025,y1-.12,top-.16),(W-d0+.025,y0+.12,top-.16)],'roof',glass)
 for y in [y0,y1,(y0+y1)/2]:box('Architecture return dormer frame',W-d0-.1,y-.065,z0,W-d0+.1,y+.065,top,'roof',frame)
 box('Architecture return dormer transom',W-d0-.10,y0,top-.80,W-d0+.10,y1,top-.70,'roof',frame)
 box('Architecture return dormer cap',W-d1-.05,y0-.12,top-.14,W-d0+.12,y1+.12,top+.04,'roof',frame)
