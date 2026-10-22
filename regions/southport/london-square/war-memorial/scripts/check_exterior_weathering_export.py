"""Verify actual portable colour data and texture bindings in the delivered GLB."""
from pathlib import Path
import json,struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'models/london-square-exterior.glb').read_bytes()
n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:]
aged={i:m for i,m in enumerate(doc['materials']) if m.get('extras',{}).get('weathering_attribute')}
assert aged,'No aged stone materials exported'
for m in aged.values():
    assert 'baseColorTexture' in m['pbrMetallicRoughness'],(m['name'],'Base stone texture lost')
    assert 'normalTexture' in m,(m['name'],'Stone micro-normal lost')
records=[]
for mesh in doc['meshes']:
    for p in mesh['primitives']:
        if p.get('material') not in aged:continue
        assert 'COLOR_0' in p['attributes'],(mesh['name'],'Weathering missing')
        a=doc['accessors'][p['attributes']['COLOR_0']];v=doc['bufferViews'][a['bufferView']]
        assert a['type'] in ('VEC3','VEC4')
        width=int(a['type'][-1]);kind={5126:'<f4',5123:'<u2',5121:'u1'}[a['componentType']]
        stride=v.get('byteStride',np.dtype(kind).itemsize*width)
        arr=np.ndarray((a['count'],width),dtype=kind,buffer=binary,
                       offset=v.get('byteOffset',0)+a.get('byteOffset',0),
                       strides=(stride,np.dtype(kind).itemsize)).astype(float)
        if a.get('normalized'):arr/=np.iinfo(np.dtype(kind)).max
        assert np.isfinite(arr).all() and arr[:,:3].min()>.69 and arr.max()<=1.00001
        if width==4:assert np.allclose(arr[:,3],1),'Weathering must not change opacity'
        records.append({'mesh':mesh['name'],'vertices':a['count'],
                        'min_rgb':float(arr[:,:3].min()),'max_rgb':float(arr[:,:3].max())})
assert len(records)>30 and min(r['min_rgb'] for r in records)<.85
report={'status':'passed','aged_materials':len(aged),'weathered_primitives':len(records),
        'base_and_normal_texture_bindings_retained':True,'opacity_unchanged':True,
        'records':records,'scope':'Checks data survived export; not photometric calibration'}
(ROOT/'research/exterior_weathering_export_check.json').write_text(json.dumps(report,indent=2)+'\n')
print('EXTERIOR_WEATHERING_EXPORT_VERIFIED',len(aged),'materials',len(records),'primitives')
