"""Independent church envelope: battlements, Gothic wings and joined hall roofs."""
import json,math
import bpy,bmesh
from mathutils import Vector
from blender_envelope import Surfaces
from southport3d.geometry import face_matrix
from southport3d.planar import subtract,area
from components import pointed,roof
from cafe import PORCH


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text());base=d['base_z'];T=d['tower']
    cx,front,back,tw=T['centre_x'],T['front_y'],T['back_y'],T['width']
    s=Surfaces(['historic-front','modern-hall','roofs'],lambda p:(p[0],p[1],p[2]+base))
    def wall(name,A,B,lo,hi):s.quad(name,[(*A,lo),(*B,lo),(*B,hi),(*A,hi)])
    def face(name,poly,frame):
        # Ear triangulation also handles the concave stepped wall outlines.
        from mathutils.geometry import tessellate_polygon
        points=[Vector((x,y,0)) for x,y in poly]
        for i,tri in enumerate(tessellate_polygon([points])):
            s.triangle(name+' '+str(i),[frame@(points[p] if isinstance(p,int) else p) for p in tri])
    def doorway(name,poly,frame,c,r,bottom,spring,depth):
        hole=pointed(c,bottom,spring,r,steps=5)
        for i,p in enumerate(subtract(poly,hole)):face(name+' wall '+str(i),p,frame)
        for i in range(1,len(hole)-1):
            s.triangle(name+' inset '+str(i),[frame@Vector((x,y,-depth)) for x,y in (hole[0],hole[i],hole[i+1])])
        for i,(p,q) in enumerate(zip(hole,hole[1:]+hole[:1])):
            if abs(p[1]-bottom)<1e-8 and abs(q[1]-bottom)<1e-8:continue
            s.quad(name+' reveal '+str(i),[frame@Vector((p[0],p[1],0)),frame@Vector((q[0],q[1],0)),frame@Vector((q[0],q[1],-depth)),frame@Vector((p[0],p[1],-depth))])
    frames=[('front',(cx,front,0),(0,1,0),tw),('west',(cx-tw/2,(front+back)/2,0),(-1,0,0),front-back),('east',(cx+tw/2,(front+back)/2,0),(1,0,0),front-back),('back',(cx,back,0),(0,-1,0),tw)]
    for name,o,n,w in frames:
        frame=face_matrix(o,n)
        poly=[(-w/2,0),(w/2,0),(w/2,21.795),(-w/2,21.795)]
        if name=='front':doorway('main entrance',poly,frame,0,.95,0,2.2,.37)
        else:face('tower '+name,poly,frame)
        # Crenellations keep actual air gaps, with a recessed inner roof.
        temp=Surfaces(['historic-front'],lambda p:frame@Vector(p))
        inner_w=w if name in ('front','back') else w-.48
        temp.quad(name+' parapet inside',[(-inner_w/2,21.1,-.24),(-inner_w/2,21.795,-.24),(inner_w/2,21.795,-.24),(inner_w/2,21.1,-.24)])
        temp.quad(name+' parapet cap',[(-inner_w/2,21.795,0),(inner_w/2,21.795,0),(inner_w/2,21.795,-.24),(-inner_w/2,21.795,-.24)])
        spacing=tw if name in ('front','back') else front-back-.96
        for j in (range(5) if name in ('front','back') else range(1,4)):
            u=-spacing/2+j*spacing/4;top=22.96 if j in (0,4) else 22.36
            temp.box(name+' merlon '+str(j),(u-.26,21.795,-.24),(u+.26,top,.24),omit=('rear',))
        for f in temp.result['historic-front']:s.quad(f['name'],f['vertices'])
    for x in (cx-tw/2-.2,cx+tw/2+.2):
        for j,(lo,hi,w,depth) in enumerate([(0,1.2,.95,1),(1.2,6.8,.68,.8),(6.8,13.9,.52,.64),(13.9,19.9,.4,.5)]):
            s.box('tower buttress '+str(x)+' '+str(j),(x-w/2,front+.1-depth/2,lo),(x+w/2,front+.1+depth/2,hi),omit=('bottom','rear'))
    for x in (cx-tw/2-.1,cx+tw/2+.1):s.box('rear buttress '+str(x),(x-.24,back-.11,0),(x+.24,back+.61,19.4),omit=('bottom',))
    tx,ty=cx+tw/2+.42,back+1.35
    for k in range(8):
        a,b=math.tau*k/8,math.tau*(k+1)/8
        s.quad('stair turret '+str(k),[(tx+.64*math.cos(a),ty+.64*math.sin(a),0),(tx+.64*math.cos(b),ty+.64*math.sin(b),0),(tx+.64*math.cos(b),ty+.64*math.sin(b),18.2),(tx+.64*math.cos(a),ty+.64*math.sin(a),18.2)])
    frame=face_matrix((cx,back,0),(0,1,0))
    for sign in (-1,1):
        knots=[(tw/2,9.9),(5.85,8.5),(7.65,10.35),(9.57,8.4)]
        for j,((a,h),(b,H)) in enumerate(zip(knots,knots[1:])):
            poly=[(sign*a,0),(sign*b,0),(sign*b,H),(sign*a,h)]
            if sign<0:poly.reverse()
            # The wing door straddles the outer gable peak: clip its recess
            # across each strip rather than adding a filled rectangular bay.
            hole=pointed(sign*7.65,0,1.85,.68,steps=5)
            for i,p in enumerate(subtract(poly,hole)):face(f'wing {sign} {j} {i}',p,frame)
        hole=pointed(sign*7.65,0,1.85,.68,steps=5)
        for i in range(1,len(hole)-1):s.triangle(f'wing door {sign} {i}',[frame@Vector((x,y,-.28)) for x,y in (hole[0],hole[i],hole[i+1])])
        for x in (sign*5.8,sign*9.57):
            temp=Surfaces(['historic-front'],lambda p:frame@Vector(p))
            for j,(lo,hi,w,dep) in enumerate([(0,.55,.9,.7),(.55,3.2,.62,.5),(3.2,7.9,.44,.34),(7.9,10,.38,.3)]):temp.box(f'wing buttress {x} {j}',(x-w/2,lo,0),(x+w/2,hi,dep),omit=('bottom','rear'))
            for f in temp.result['historic-front']:s.quad(f['name'],f['vertices'])
        temp=Surfaces(['historic-front'],lambda p:frame@Vector(p))
        for j,(u,h) in enumerate([(tw/2+(5.85-tw/2)*t,9.9-1.4*t+.18) for t in (.15,.45,.75)]+[(u+(U-u)*t,h+(H-h)*t+.22) for u,h,U,H in [(5.85,8.5,7.65,10.35),(7.65,10.35,9.57,8.4)] for t in (.25,.65)]+[(7.65,10.55)]):
            temp.box(f'wing merlon {sign} {j}',(sign*u-.21,h-.22,-.215),(sign*u+.21,h+.25,.215),omit=('rear',))
        for f in temp.result['historic-front']:s.quad(f['name'],f['vertices'])
    s.part='modern-hall'
    wall('west hall',(-112,-30),(-112,-52),0,6.65)
    wall('hall shoulder',(-113.9,-52.26),(-111.1,-52.26),0,6.6)
    wall('rear long',(-113.8,-61.2),(-89.55,-61.2),0,6.7)
    # Transverse end gables and the rising long cafe-side return.
    face('cross west',[(0,0),(9.1,0),(9.1,6.7),(4.55,10.2),(0,6.7)],face_matrix((-113.8,-52.1,0),(-1,0,0)))
    face('east return',[(0,0),(31.3,0),(31.3,6.54),(9.22,6.54),(4.55,10.04),(0,6.63)],face_matrix((-89.55,-61.2,0),(1,0,0)))
    face('front shoulder',[(0,0),(3.57,0),(3.57,6.54+3.5*3.57/11.3),(0,6.54)],face_matrix((-89.55,-29.6,0),(0,1,0)))
    for ya,yb,h in [(-35,-26,4.15),(-54,-35,5.4),(-71.4,-54,3.9)]:wall('annex east '+str(ya),(-76.54,ya),(-76.54,yb),0,h)
    wall('annex rear',(-89.7,-71.56),(-76.7,-71.56),0,3.9)
    wall('annex west',(-89.55,-61.25),(-89.55,-71.55),0,3.9)
    wall('middle step',(-89.5,-34.9),(-76.7,-34.9),4.24,5.4)
    wall('rear step',(-76.7,-54.1),(-89.5,-54.1),3.99,5.4)
    wall('porch backing',(-84.4,-29.55),(-89.55,-29.6),0,4.15)
    porch=PORCH
    for x in (porch['x0']+.30,porch['x1']-.30):
        s.box('porch pier '+str(x),(x-.20,porch['pier_y']-.20,0),(x+.20,porch['pier_y']+.20,2.72))
        s.box('porch capital '+str(x),(x-.24,porch['pier_y']-.24,2.72),(x+.24,porch['pier_y']+.24,2.84),omit=('bottom','top'))
    s.box('porch cross beam',(-88.375,porch['pier_y']-.12,2.84),(-85.675,porch['pier_y']+.12,3.02),omit=('top',))
    wall('cafe front',(-76.68,-25.9),(-82.4,-25.9),-.12,4.35)
    arc=[(-82.4+2*math.cos(math.pi/2+i*math.pi/12),-27.9+2*math.sin(math.pi/2+i*math.pi/12)) for i in range(7)]
    for i,(a,b) in enumerate(zip(arc,arc[1:])):wall('cafe round '+str(i),a,b,-.12,4.35)
    wall('cafe return',(-84.4,-27.9),(-84.4,-29.55),-.12,4.35)
    s.part='roofs'
    s.quad('tower deck',[(cx-tw/2+.4,back+.4,21.24),(cx+tw/2-.4,back+.4,21.24),(cx+tw/2-.4,front-.4,21.24),(cx-tw/2+.4,front-.4,21.24)])
    for k in range(8):
        a,b=math.tau*k/8,math.tau*(k+1)/8
        s.quad('turret cap '+str(k),[(tx+.75*math.cos(a),ty+.75*math.sin(a),18.28),(tx+.75*math.cos(b),ty+.75*math.sin(b),18.28),(tx+.04*math.cos(b),ty+.04*math.sin(b),19.45),(tx+.04*math.cos(a),ty+.04*math.sin(a),19.45)])
    # Only two constant-size roof operands. No detailed mesh/ornament is read.
    main=roof('coarse main',-112.15,-89.55,-56.65,-29.6,6.7,10.2,0).finish([])
    crossmesh=roof('coarse cross',-61.32,-51.98,-113.96,-89.55,6.7,10.2,0)
    crossmesh.vertices=[(y,x,z) for x,y,z in crossmesh.vertices];crossmesh.faces=[tuple(reversed(f)) for f in crossmesh.faces];cross=crossmesh.finish([])
    bpy.context.view_layer.objects.active=main;mod=main.modifiers.new('coarse valleys','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=cross;bpy.ops.object.modifier_apply(modifier=mod.name)
    main.data.update()
    for i,p in enumerate(main.data.polygons):
        if p.normal.z>.1:
            v=[main.data.vertices[j].co for j in p.vertices]
            for j in range(1,len(v)-1):
                # Boolean ridge collinearity can leave float32 numerical slivers.
                if (v[j]-v[0]).cross(v[j+1]-v[0]).length>1e-4:
                    s.triangle('hall slope '+str(i)+' '+str(j),[v[0],v[j],v[j+1]])
    bpy.data.objects.remove(main,do_unlink=True);bpy.data.objects.remove(cross,do_unlink=True)
    for ya,yb,h in [(-35,-29.55,4.15),(-54,-35,5.4),(-71.5,-54,3.9)]:
        s.quad('annex deck '+str(ya),[(-89.55,ya,h+.09),(-76.55,ya,h+.09),(-76.55,yb,h+.09),(-89.55,yb,h+.09)])
    plan=[(-76.55,-29.55),(-76.55,-25.78),(-82.4,-25.78)]+[(-82.4+2.12*math.cos(math.pi/2+i*math.pi/12),-27.9+2.12*math.sin(math.pi/2+i*math.pi/12)) for i in range(1,7)]+[(-84.52,-29.55)]
    for i in range(1,len(plan)-1):s.triangle('cafe cap '+str(i),[(*p,4.30) for p in (plan[0],plan[i],plan[i+1])])
    m=roof('porch roof',porch['x0'],porch['x1'],porch['y0'],porch['y1'],porch['eaves'],porch['ridge'],0)
    for i,ids in enumerate(m.faces):
        v=[m.vertices[j] for j in ids];(s.quad if len(v)==4 else s.triangle)('porch roof '+str(i),v)
    # Repeated small rooflights become roof-atlas appearance, not 15 extra boxes.
    return s.result
