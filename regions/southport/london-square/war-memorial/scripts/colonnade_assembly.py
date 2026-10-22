"""Complete exterior colonnade assembly with the photographically fitted plan.

The caller supplies existing shared columns, reliefs, lettering and materials.
This keeps the NE/SW-specific carvings separate from the common architecture.
"""
import bpy
import colonnade_envelope as envelope
import site_grade


def build(ns,code,c,plan):
    ROOT=ns['ROOT'];Mesh=ns['Mesh'];spec=ns['SPEC']
    finish=ns['finish'];block=ns['block'];masonry=ns['masonry'];engrave=ns['engrave']
    wall_top=ns['COL']['abacus_top']
    tw,th,tz=(ns['TROPHY'][k] for k in ('width_m','height_m','centre_z_m'))
    b=plan['central_roof_break_x'];setback=plan['central_to_chamber_setback']
    structural=[]
    site_grade.colonnade_base(ns,code,c)
    for sign,x in zip((-1,1),plan['window_centres']):
        walls=Mesh(code+' chamber ashlar '+str(x))
        lo,hi=sorted((sign*plan['side_wall_inner_tip_x'],sign*plan['chamber_outer_x']))
        dims=spec['dimensions']['exterior_window'];half=dims['width_m']/2
        pier_x=sign*abs(plan['pier_centres'][-1])
        pier_edges=[pier_x-plan['pier_width']/2,pier_x+plan['pier_width']/2]
        for sy in (-1,1):
            y=sy*plan['chamber_side_wall_centre_y']
            for a,z in [(lo,x-half),(x+half,hi)]:
                edges=sorted({a,z,*[e for e in pier_edges if a<e<z]})
                for start,end in zip(edges,edges[1:]):
                    middle=(start+end)/2
                    is_pier=pier_edges[0]<middle<pier_edges[1]
                    depth=plan['chamber_side_wall_depth'];centre_y=y
                    if is_pier:
                        inner_y=plan['chamber_side_wall_centre_y']-depth/2
                        depth=plan['pier_outer_y']-inner_y
                        centre_y=sy*(plan['pier_outer_y']+inner_y)/2
                    masonry(walls,(middle,centre_y),end-start,depth,.35,wall_top,
                            course=.40,block_width=2 if is_pier else .77)
            masonry(walls,(x,y),dims['width_m'],.36,.35,dims['bottom_z_m'],course=.32)
            masonry(walls,(x,y),dims['width_m'],.36,dims['top_z_m'],wall_top,course=.397)
            # Each anta course is one full-depth stone. An overlapping face
            # skin would leave coincident exposed end caps at the portico.
        outer=sign*plan['end_wall_centre_x']
        masonry(walls,(outer,0),3.68,plan['chamber_side_wall_depth'],.35,wall_top,face='x',course=.40,block_width=.74)
        inner=sign*plan['entrance_wall_centre_x']
        for yy in (-1.41,1.41):
            masonry(walls,(inner,yy),.86,.36,.35,wall_top,face='x',course=.40)
        # Side walls retain their clear openings and physically recessed trophies.
        frame_y=2.225
        for sy in (-1,1):
            walls.cut_box_from_ashlar((x,sy*(frame_y+.020),tz),(tw,.214,th))
        walls.cut_box_from_ashlar((outer+sign*.225,0,tz),(.214,tw,th))
        wall=finish(walls,c,.0025);wall['window_chamber_centre_x']=x
        for sy in (-1,1):
            y=sy*frame_y;normal=(0,sy,0)
            ns['window_frame'](x,y,normal,c)
            face_key=f'{code}_{"NW" if sign>0 else "SE"}_{"SW" if sy>0 else "NE"}'
            kind=spec['trophy_panel_map'][face_key]['motif']
            block('Trophy recessed stone field',(x,y-sy*.100,tz),(tw,.030,th),c,ns['STONE'][1])
            ob=ns['mounted_trophy'](kind,(x,y-sy*.087,tz),normal,c)
            ob['panel_id']=face_key;ob['placement_confidence']=spec['trophy_panel_map'][face_key]['confidence']
        normal=(sign,0,0);xx=outer+sign*.20
        ns['end_panel'](xx,normal,c,code+('_NW' if sign>0 else '_SE'))
        key=f'{code}_{"NW" if sign>0 else "SE"}_end'
        kind=spec['trophy_panel_map'][key]['motif']
        block('End trophy recessed stone field',(xx-sign*.095,0,tz),(.030,tw,th),c,ns['STONE'][1])
        ob=ns['mounted_trophy'](kind,(xx-sign*.082,0,tz),normal,c);ob['panel_id']=key;ob['placement_confidence']=spec['trophy_panel_map'][key]['confidence']
        block('Chamber structural floor — interior deferred',(x,0,.34),(4.1,4.1,.11),c,ns['STONE'][1])
    positions=[a+d for a in plan['column_pair_centres']
               for d in (-plan['column_pair_separation']/2,plan['column_pair_separation']/2)]
    for row,y in enumerate((-1.9,1.9)):
        for i,x in enumerate(positions):
            ns['column'](code+f' fluted Doric column {row*8+i+1:02}',x,y,c)
    for name,rings,mat in [('stepped architrave',envelope.ARCHITRAVE_PROFILE,2),
                           ('stepped cornice',envelope.CORNICE_PROFILE,6)]:
        m=Mesh(code+' '+name);envelope.profile(m,rings,b,setback,mat)
        ob=finish(m,c,.002);structural.append(ob)
        ob['geometry_status']='Photographic stepped envelope; small moulding section estimated'
    m=Mesh(code+' stepped parapet ashlar')
    envelope.parapet(m,24.4,4.78,b,setback,.28,5.13,5.54)
    ob=finish(m,c,.002);structural.append(ob)
    m=Mesh('Recessed stepped roof membrane — build-up unverified')
    m.outline(envelope.outline(23.84,4.22,b-.28,setback),5.215,5.305)
    ob=m.finish([ns['ROOF']],c,.001);structural.append(ob)
    m=Mesh(code+' stepped entablature')
    envelope.ring(m,24.36,4.8,b,setback,.24,4.42,4.90,2)
    frieze=finish(m,c,.002);structural.append(frieze)
    texts=spec['exterior_inscriptions']
    for sy in (-1,1):
        normal=(0,sy,0);face_y=sy*2.40
        text=(texts['NE_inner_SW'] if sy>0 else texts['NE_outer_NE']) if code=='NE' else (texts['SW_outer_SW'] if sy>0 else texts['SW_inner_NE'])
        engrave(frieze,code+' long inscription '+str(sy),text,(0,face_y+sy*.0001,4.66),
                normal,.29,plan['maximum_text_width'],c)
        for x in plan['pier_centres']:
            cutter=block('Frieze floral recess cutter',(x,face_y-sy*.008,4.66),(.82,.020,.275),c,ns['STONE'][2],0)
            mod=frieze.modifiers.new('18 mm floral field recess','BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.context.view_layer.objects.active=frieze
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
            ob=ns['mounted_flora']('frieze-foliage',(x,face_y-sy*.020,4.66),normal,c)
            ob['support_object']=frieze.name
        heads=sorted(positions+[a+d for a in plan['pier_centres']
                                for d in (-plan['pier_pair_separation']/2,plan['pier_pair_separation']/2)])
        for i,x in enumerate(heads):
            ob=ns['mounted'](ns['reliefs'].lion_head(),(x,sy*2.430,5.015),normal,c,smooth=True)
            if not ob.data.get('surface_reduced'):
                check=ns['simplify_relief'](ob,ROOT/'research/relief-data/cornice-lion.npz',ratio=.24)
                check['empty_background_faces_removed_after_check']=ns['trim_empty_relief_background'](ob)
                check['check_scope']='Numeric-grid approximation before removing empty backing; carving retained'
                ns['RELIEF_APPROXIMATION_LOG'].append(check);ob.data['surface_reduced']=True
            ob['mask_id']=f'{code}_{"SW" if sy>0 else "NE"}_{i+1:02}'
    engrave(frieze,code+' NW date',texts[code+'_NW_date'],(12.1801,0,4.66),(1,0,0),.30,3.24,c)
    for x in plan['pier_centres']:
        for y in (-plan['lamp_y'],plan['lamp_y']):ns['lamp'](x,y,c)
    for ob in c.objects:
        ob['assembly']=code;ob['plan_reference']='research/colonnade_plan_projection_study.json'
    return structural
