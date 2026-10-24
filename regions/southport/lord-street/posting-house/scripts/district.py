"""Fixed coarse volumes from the registered plan, not detailed mesh reduction.

Retains the accepted source dimensions and their documented uncertainty. Fine
window/stonework relief is projected; the open courtyard is never filled in.
"""
import json
import math
import bpy
import bmesh
from mathutils import Vector
from blender_envelope import Surfaces


def surfaces(asset):
    d=json.loads((asset/'research/layout.json').read_text())
    ox,oy=d['front_east'];ex,ey=d['front_west'];width=math.hypot(ex-ox,ey-oy)
    ux,uy=(ex-ox)/width,(ey-oy)/width
    depth=d['main_depth'];start=d['historic_start'];eave=d['eave_z'];ridge=d['ridge_z']
    def world(p):
        x,y,z=p
        X,Y=ox+ux*x+uy*y,oy+uy*x-ux*y
        t=max(0,(-y-depth)/(d['rear_depth']-depth))
        u=x/width;east,west=d['rear_boundary']
        tx=(1-u)*east[0]+u*west[0];ty=(1-u)*east[1]+u*west[1]
        X+=(tx-(ox+ux*x-uy*d['rear_depth']))*t
        Y+=(ty-(oy+uy*x+ux*d['rear_depth']))*t
        return X,Y,d['base_z']+z
    s=Surfaces(['historic-front','roof','rear-range','shopfronts','courtyard-ground'],world)
    def panel(name,a,b,y,lo,hi):
        s.quad(name,[(b,y,lo),(a,y,lo),(a,y,hi),(b,y,hi)])
    def polygon(name,points):
        # Convex authored face fan, each triangle uses nondegenerate atlas quads.
        for j in range(1,len(points)-1):s.triangle(name+' '+str(j),[points[0],points[j],points[j+1]])
    edges=d['historic_bay_edges'];bays=[(a+b)/2 for a,b in zip(edges,edges[1:])]
    for i,(a,b,c) in enumerate(zip(edges,edges[1:],bays)):
        y=.42 if i in (1,3) else 0
        panel('historic upper '+str(i),a,b,y,5.65,eave)
        if y:
            for x in (a,b):s.quad('bay return '+str(x),[(x,0,0),(x,y,0),(x,y,eave),(x,0,eave)])
    # Principal gable outline retains the shoulders and curved pediment silhouette.
    for i in (1,3):
        a,b,c=edges[i],edges[i+1],bays[i];w=(b-a)/2-.12
        outline=[(-w,16.18),(w,16.18),(w-.15,17),(1.7,18.05),(1.65,19.75),(1.15,20.65),(-1.15,20.65),(-1.65,19.75),(-1.7,18.05),(-w+.15,17)]
        # Horizontal trapezoids avoid a concave polygon fan.
        rows=[(16.18,w),(17,w-.15),(18.05,1.7),(19.75,1.65),(20.65,1.15)]
        for j,((z0,w0),(z1,w1)) in enumerate(zip(rows,rows[1:])):
            s.quad(f'principal gable {i} {j}',[(c+w0,.54,z0),(c-w0,.54,z0),(c-w1,.54,z1),(c+w1,.54,z1)])
            s.quad(f'principal gable rear {i} {j}',[(c-w0,-.06,z0),(c+w0,-.06,z0),(c+w1,-.06,z1),(c-w1,-.06,z1)])
        # Pediment is a shallow semicircular plate; rear and edge close it.
        arc=[(c+1.55*math.cos(math.pi*j/8),20.12+1.2*math.sin(math.pi*j/8)) for j in range(9)]
        polygon('pediment '+str(i),[(x,.79,z) for x,z in reversed(arc)])
        for j,((x,z),(X,Z)) in enumerate(zip(arc,arc[1:])):
            s.quad(f'pediment edge {i} {j}',[(x,.54,z),(x,.79,z),(X,.79,Z),(X,.54,Z)])
        # Main gable owns the lower backing; only expose the arc above it.
        from southport3d.planar import halfplane
        upper=halfplane(arc,(c+3,20.65),(c-3,20.65),inside=False)
        polygon('pediment back '+str(i),[(x,.54,z) for x,z in upper])
        for j in range(len(outline)):
            x,z=outline[j];X,Z=outline[(j+1)%len(outline)]
            s.quad(f'gable edge {i} {j}',[(c+x,-.06,z),(c+x,.54,z),(c+X,.54,Z),(c+X,-.06,Z)])
        # Narrow octagonal tourelles retain the vertical skyline accents.
        for x in (a+.04,b-.04):
            for j in range(8):
                t=2*math.pi*j/8;T=2*math.pi*(j+1)/8
                p=(x+.28*math.cos(t),.63+.28*math.sin(t));q=(x+.28*math.cos(T),.63+.28*math.sin(T))
                s.quad(f'turret {i} {x} {j}',[(*p,5.65),(*q,5.65),(*q,17.28),(*p,17.28)])
    # 132's three whole canted bays; adjoining wall strips own the other plane.
    centres=[start*(j+.5)/3 for j in range(3)]
    panel('132 ground structure',0,start,0,4.8,5.0)
    panel('132 upper plain',0,start,0,12.80,16.35)
    limits=[0]+[v for c in centres for v in (c-1.27,c+1.27)]+[start]
    for j in range(0,len(limits)-1,2):panel('132 flat '+str(j),limits[j],limits[j+1],0,5,12.8)
    for i,c in enumerate(centres):
        path=[(c-1.27,0),(c-.97,.74),(c+.97,.74),(c+1.27,0)]
        for j,(p,q) in enumerate(zip(path,path[1:])):s.quad(f'132 canted {i} {j}',[(*q,5),(*p,5),(*p,12.8),(*q,12.8)])
        s.triangle('132 white gable '+str(i),[(c+1.4,.07,16.35),(c-1.4,.07,16.35),(c,.07,18.05)])
    # Side returns and gable end walls retain alley profile.
    for x,E,R in [(0,16.3,19.1),(width,eave,ridge)]:
        points=[(x,-depth,0),(x,0,0),(x,0,E),(x,-depth,E)]
        s.quad('end wall '+str(x),points[::-1] if x==0 else points)
        points=[(x,0,E),(x,-depth,E),(x,-depth/2,R)]
        s.triangle('end gable '+str(x),points[::-1] if x==0 else points)
    s.part='shopfronts'
    for i,(a,b,c) in enumerate(zip(edges,edges[1:],bays)):
        y=.42 if i in (1,3) else 0
        if i in (0,4):
            panel('door jamb left '+str(i),a,c-1.05,y,0,5.65)
            panel('door jamb right '+str(i),c+1.05,b,y,0,5.65)
            panel('door head '+str(i),c-1.05,c+1.05,y,4.8,5.65)
            panel('recessed portal '+str(i),c-1.05,c+1.05,y-.22,.08,4.8)
            for x in (c-1.05,c+1.05):s.quad('door reveal '+str(x),[(x,y-.22,.08),(x,y,.08),(x,y,4.8),(x,y-.22,4.8)])
        else:panel('arched shop bay '+str(i),a,b,y,0,5.65)
    panel('132 shop arcade',0,start,.13,0,4.8)
    s.part='roof'
    # Low-complexity solid unions remove hidden/coplanar roof intersections.
    # These operands depend only on measured massing, never source mesh detail.
    def volume(name,x0,x1,y0,y1,E,R,along_x=True):
        v=[(x0,y0,E-.18),(x1,y0,E-.18),(x1,y1,E-.18),(x0,y1,E-.18),
           (x0,y0,E),(x1,y0,E),(x1,y1,E),(x0,y1,E)]
        v+=([(x0,(y0+y1)/2,R),(x1,(y0+y1)/2,R)] if along_x else [((x0+x1)/2,y0,R),((x0+x1)/2,y1,R)])
        f=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        f+=([(4,5,9,8),(5,6,9),(6,7,8,9),(7,4,8)] if along_x else [(4,5,8),(5,6,9,8),(6,7,9),(7,4,8,9)])
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
        ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob)
        return ob
    def joined(name,operands):
        target=operands[0]
        for operand in operands[1:]:
            bpy.context.view_layer.objects.active=target
            mod=target.modifiers.new('Coarse union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand
            bpy.ops.object.modifier_apply(modifier=mod.name)
            mesh=operand.data;bpy.data.objects.remove(operand,do_unlink=True);bpy.data.meshes.remove(mesh)
        bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.dissolve_limit(bm,angle_limit=.00001,verts=list(bm.verts),edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free()
        target.data.update()
        for j,face in enumerate(target.data.polygons):
            if face.normal.z<-.5:continue  # Hidden underside is not a baked surface.
            coords=[target.data.vertices[k].co for k in face.vertices]
            # Architecture owns these exact gable-end planes. Duplicating the
            # roof volume's end triangle here would create coplanar fighting.
            boundary=width if name.startswith('historic') else 0
            if abs(face.normal.x)>.99 and all(abs(v.x-boundary)<1e-5 for v in coords):continue
            if name.startswith('historic') and abs(face.normal.y)>.99 and all(abs(v.y+depth)<1e-5 for v in coords) and max(v.z for v in coords)<=eave+1e-5:continue
            if name.startswith('132') and abs(face.normal.y)>.99 and all(abs(v.y)<1e-5 for v in coords) and max(v.z for v in coords)<=16.35+1e-5:continue
            s.triangle(name+' '+str(j),[tuple(target.data.vertices[k].co) for k in face.vertices])
        mesh=target.data;bpy.data.objects.remove(target,do_unlink=True);bpy.data.meshes.remove(mesh)
    ops=[volume('historic main',start,width,-depth+.06,-.06,eave,ridge)]
    for c,w,top in [(start+3.1,5.7,ridge-.65),((start+width)/2,6.2,ridge-.15),(width-3,5.7,ridge-.65)]:ops.append(volume('rear cross',c-w/2,c+w/2,-depth,-depth/2,eave,top,False))
    for i in (0,2,4):
        c=bays[i];z=eave+(ridge-eave)*1.1/(depth/2)+.08
        # A closed coarse dormer united with the roof removes the slope behind
        # the dormer front, rather than leaving two intersecting visible skins.
        v=[(c-1.03,-4,z-.12),(c+1.03,-4,z-.12),(c+1.03,-.92,z-.12),(c-1.03,-.92,z-.12),
           (c-1.03,-4,z+1.91),(c+1.03,-4,z+1.91),(c+1.03,-.92,z+1.91),(c-1.03,-.92,z+1.91),(c,-2.2,z+3.6)]
        f=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,8),(5,6,8),(6,7,8),(7,4,8)]
        mesh=bpy.data.meshes.new('coarse dormer');mesh.from_pydata(v,[],f);mesh.update()
        ob=bpy.data.objects.new('coarse dormer',mesh);bpy.context.scene.collection.objects.link(ob);ops.append(ob)
    joined('historic joined roof',ops)
    ops=[volume('132 main',0,start,-depth,0,16.3,19.1)]
    for c in centres:ops.append(volume('132 cross',c-1.48,c+1.48,-6,.08,16.32,18.12,False))
    joined('132 joined roof',ops)
    for j,(u,dep,w,hdepth,h) in enumerate([(start+.6,8.7,.72,1.10,23.3),(start+2.4,8.7,.72,1.10,23.4),(width-2,8.7,.76,1.05,23.7),(width-.5,8.7,.76,1.05,23.1),(start+7,14.8,1.10,.72,22.2),(width-7,14.8,1.10,.72,22.2)]):
        s.box('chimney '+str(j),(u-w/2,-dep-hdepth/2,15),(u+w/2,-dep+hdepth/2,h+.08))
    s.box('warehouse flat roof',(0,-44.4,13.7),(11,-17.9,13.9),omit=('bottom',))
    s.quad('warehouse pitched attic',[(10.8,-44.4,13.9),(16.1,-44.4,12.6),(16.1,-17.9,12.6),(10.8,-17.9,13.9)])
    corners=[(10.6,-17.5,14.75),(16.7,-17.5,14.75),(16.7,-24.1,14.75),(10.6,-24.1,14.75)]
    for j in range(4):s.triangle('tower hip '+str(j),[corners[(j+1)%4],corners[j],(13.65,-20.8,15.35)])
    s.box('modern roof',(4.85,-54.7,12.6),(29.65,-44,12.8),omit=('bottom',))
    s.box('modern tower roof',(-.4,-54.7,15.25),(5.4,-44,15.45),omit=('bottom',))
    s.box('stair cap',(16.425,-20.975,14.72),(17.575,-17.825,14.88),omit=('bottom',))
    s.part='rear-range'
    s.quad('historic rear',[(start,-depth,0),(width,-depth,0),(width,-depth,eave),(start,-depth,eave)])
    for c,w,top in [(start+3.1,5.7,ridge-.65),((start+width)/2,6.2,ridge-.15),(width-3,5.7,ridge-.65)]:s.triangle('rear gable '+str(c),[(c-w/2,-depth-.035,eave),(c+w/2,-depth-.035,eave),(c,-depth-.035,top)])
    s.box('warehouse',(0,-44.4,0),(15.5,-17.9,12.6),omit=('bottom','top','front','rear','right'))
    s.quad('warehouse courtyard',[(15.5,-44.4,2.7),(15.5,-17.9,2.7),(15.5,-17.9,12.6),(15.5,-44.4,12.6)])
    s.quad('warehouse upper street',[(0,-44.4,12.6),(0,-17.9,12.6),(0,-17.9,13.7),(0,-44.4,13.7)])
    s.box('access tower',(11,-23.7,2.7),(16.3,-17.9,14.7),omit=('bottom','top','front','left'))
    s.box('stair enclosure',(16.5,-20.9,2.9),(17.5,-17.9,14.7),omit=('bottom','top','front','left'))
    s.box('modern range',(0,-54.3,0),(29.3,-44.4,12.6),omit=('bottom','top','front','rear'))
    panel('modern courtyard',15.5,29.3,-44.4,2.7,12.6)
    for label,l,h,lo,hi in [('left',0,14.4,0,12.6),('right',17.3,29.3,0,12.6),('head',14.4,17.3,4.87,12.6),('recess',14.4,17.3,-1.35,4.87)]:
        y=-51.5 if label=='recess' else -54.3
        s.quad('garage '+label,[(l,y,lo),(h,y,lo),(h,y,hi),(l,y,hi)])
    for x in (14.4,17.3):s.quad('garage jamb '+str(x),[(x,-54.3,-1.35),(x,-51.5,-1.35),(x,-51.5,4.87),(x,-54.3,4.87)])
    s.box('modern raised tower',(0,-54.3,12.6),(5,-44.4,15.2),omit=('bottom','top'))
    s.box('retaining wall',(28.8,-44.4,0),(29.3,-17.9,4.02),omit=('bottom','front','rear'))
    s.box('historic extension',(17,-23,2.7),(29,-17.9,5.01),omit=('bottom','top','front'))
    s.part='courtyard-ground'
    s.quad('raised garden',[(15.5,-44.4,2.7),(28.8,-44.4,2.7),(28.8,-17.9,2.7),(15.5,-17.9,2.7)])
    s.box('rear terrace',(17,-23,5.01),(29,-17.9,5.19),omit=('bottom','front'))
    # Fine spiral treads and rails are omitted at District distance.
    s.quad('garage ramp',[(14.4,-54.35,.2045),(17.3,-54.35,.2045),(17.3,-51.55,-1.35),(14.4,-51.55,-1.35)])
    # Frontage coordinates are left handed (x runs west, y faces the street).
    # Preserve outward normals after the reflected geographic transform.
    for faces in s.result.values():
        for face in faces:face['vertices'].reverse()
    return s.result
