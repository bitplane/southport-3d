"""Photographic joint layout for the obelisk pedestal, in face-local metres.

Panel X increases to the viewer's right, Y is world height minus 3.06 m.
The SE coordinates follow IWM mont_3a and the arms' existing trace mapping.
NW vertical bonds are estimated independently from mont_1a. These are not
surveyed dimensions; the shared course heights are registered through the SE
carving so that a joint cannot stop at the edge of its relief mesh.
"""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CENTRE_Z=3.06
BODY_BOTTOM,BODY_TOP=2.12,4.04
GAP=.004
def se_x(px):return (px-434.5)*1.30/515
def se_z(py):return CENTRE_Z+.65-(py-275)*1.30/484
COURSES=sorted([se_z(y) for y in (203,413,631)])


def face_segments(face):
    """Return joint centre segments (u, local-up) on a chosen pedestal face."""
    segments=[((-1.30,z-CENTRE_Z),(1.30,z-CENTRE_Z)) for z in COURSES]
    if face=='SE':
        for x,top,bottom in [(280,203,413),(588,203,413),(128,413,631),
                              (739,413,631),(269,631,867),(600,631,867),
                              (141,152,203),(735,152,203)]:
            segments.append(((se_x(x),max(BODY_BOTTOM,se_z(bottom))-CENTRE_Z),
                             (se_x(x),min(BODY_TOP,se_z(top))-CENTRE_Z)))
    elif face=='NW':
        # Approximate circumference registration: photographed outer ring
        # spans 273 px horizontally, centred at x=459 in IWM mont_1a.
        for xs,zlo,zhi in [((365,555),BODY_BOTTOM,COURSES[0]),
                            ((290,627),COURSES[0],COURSES[1]),
                            ((373,548),COURSES[1],COURSES[2])]:
            for x in xs:
                u=(x-459)*1.294/273
                segments.append(((u,zlo-CENTRE_Z),(u,zhi-CENTRE_Z)))
    return segments


def cut_numeric_surface(surface,face='SE'):
    """A narrow mortar joint through the entire carving, with a softened arris.

The groove is filled by the recessed pedestal face underneath. Its measured
width and depth are unknown; the 4 mm authored gap is a visual approximation.
"""
    xx=(surface.x-surface.bounds[0])/(surface.bounds[2]-surface.bounds[0])*surface.width-surface.width/2
    yy=(1-(surface.y-surface.bounds[1])/(surface.bounds[3]-surface.bounds[1]))*surface.height+surface.origin_y
    weight=np.zeros(surface.z.shape)
    for a,b in face_segments(face):
        a,b=np.asarray(a),np.asarray(b);v=b-a
        t=np.clip(((xx-a[0])*v[0]+(yy-a[1])*v[1])/(v@v),0,1)
        distance=np.hypot(xx-a[0]-t*v[0],yy-a[1]-t*v[1])
        edge=.00065
        w=np.clip((GAP/2+edge-distance)/edge,0,1)
        weight=np.maximum(weight,w)
    surface.z=surface.z*(1-weight)+.001*weight
    return {'face':face,'width_m':GAP,'floor_depth_in_relief_coordinates_m':.001,
            'method':'Mortar joints cut through the numeric carving; positions registered to pedestal channels',
            'segments_face_local_m':face_segments(face)}


def cut_mesh_strips(obj,face,cap=False):
    """Bisect and remove joint bands, including across open foliate surfaces.

Closed border tori receive stone cut faces. Open leaf meshes keep their
existing surface representation and are seated against the pedestal.
"""
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    removed=0
    for a,b in face_segments(face):
        axis=1 if abs(a[1]-b[1])<1e-7 else 0
        centre=a[axis];other=1-axis
        lo,hi=sorted([a[other],b[other]])
        # Split both sides of the narrow band, and both segment end planes.
        for ax,value in [(axis,centre-GAP/2),(axis,centre+GAP/2),(other,lo),(other,hi)]:
            p=[0,0,0];n=[0,0,0];p[ax]=value;n[ax]=1
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                                  plane_co=p,plane_no=n,dist=1e-7,
                                  clear_inner=False,clear_outer=False)
        faces=[]
        for f in bm.faces:
            c=f.calc_center_median()
            if abs(c[axis]-centre)<GAP/2-1e-7 and lo-1e-7<c[other]<hi+1e-7:faces.append(f)
        removed+=len(faces)
        bmesh.ops.delete(bm,geom=faces,context='FACES')
    if cap:
        boundary=[e for e in bm.edges if e.is_boundary]
        filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0)['faces']
        for f in filled:f.smooth=False
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    obj['masonry_joint_reference']='research/pedestal_joint_layout.json'
    obj['authored_joint_gap_m']=GAP
    return removed


def cut_body_channels(body,collection,cut_material):
    """Carve shallow continuous mortar beds into the solid pedestal."""
    import bpy
    from geometry import Mesh,face_matrix
    normals={'NW':(0,1,0),'SE':(0,-1,0),'NE':(1,0,0),'SW':(-1,0,0)}
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True);bpy.context.view_layer.objects.active=body
    for mod in list(body.modifiers):
        if mod.type=='BEVEL':bpy.ops.object.modifier_apply(modifier=mod.name)
    if cut_material.name not in body.data.materials:body.data.materials.append(cut_material)
    cut_index=list(body.data.materials).index(cut_material)
    count=0
    for face,normal in normals.items():
        origin=(normal[0]*1.275,normal[1]*1.275,CENTRE_Z)
        for i,(a,b) in enumerate(face_segments(face)):
            horizontal=abs(a[1]-b[1])<1e-7
            length=abs(b[0]-a[0]) if horizontal else abs(b[1]-a[1])
            size=(length,GAP,.004) if horizontal else (GAP,length,.004)
            m=Mesh('Pedestal mortar channel cutter')
            m.box(((a[0]+b[0])/2,(a[1]+b[1])/2,-.001),size,cut_index)
            cutter=m.finish(list(body.data.materials),collection)
            cutter.matrix_world=face_matrix(origin,normal)
            mod=body.modifiers.new(f'{face} masonry joint {i+1}','BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.context.view_layer.objects.active=body
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(cutter,do_unlink=True);count+=1
    body['masonry_joint_reference']='research/pedestal_joint_layout.json'
    body['masonry_channel_count']=count
    body['authored_joint_width_depth_m']=[GAP,.003]
    return count


def save_layout():
    d={'source_pages':['https://memorials.iwm.org.uk/memorial/1228'],
       'source_images':['iwm-mont_3a','iwm-mont_1a'],
       'SE_mapping':'Existing 1.30 m square arms trace: image bounds 177,275 to 692,759; centre world z=3.06 m',
       'SE_horizontal_source_y_px':[203,413,631],
       'horizontal_world_z_m':COURSES,'joint_width_m':GAP,'pedestal_channel_depth_m':.003,
       'segments_by_face':{f:face_segments(f) for f in ('NW','SE','NE','SW')},
       'confidence':'Photographic registration, not surveyed; source perspective and model roundel scale affect absolute positions',
       'limits':['NW vertical bonds use an approximate frontal-circle scale',
                 'NE and SW vertical bonds are unresolved and are not invented',
                 '4 mm gap and 3 mm face-channel depth are authored estimates',
                 'Individual erosion and irregular mortar are not reconstructed']}
    (ROOT/'research/pedestal_joint_layout.json').write_text(json.dumps(d,indent=2)+'\n')
    return d


if __name__=='__main__':
    print(json.dumps(save_layout(),indent=2))
