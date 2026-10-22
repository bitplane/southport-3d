"""Check real embedded GLB pixels, including glTF roughness channel packing."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import struct
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'models/london-square-exterior.glb').read_bytes()
n=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+n])
binary=raw[28+n:]
materials=[m for m in doc['materials'] if m.get('extras',{}).get('portable_surface_family')=='Authored obelisk stone surfaces']
assert {m['extras']['surface_key'] for m in materials}=={'pale','aged','pitted','tip-se','tip-sw','tip-nw','tip-ne'}


def pixels(texture_info):
    texture=doc['textures'][texture_info['index']]
    image=doc['images'][texture['source']]
    view=doc['bufferViews'][image['bufferView']]
    start=view.get('byteOffset',0)
    data=binary[start:start+view['byteLength']]
    return np.asarray(Image.open(BytesIO(data)).convert('RGB'))


report={'status':'passed','materials':[],'reference_pixels_embedded':False,
        'scope':'Checks authored maps survive export; does not establish photometric or survey accuracy'}
for m in materials:
    key=m['extras']['surface_key']
    pbr=m['pbrMetallicRoughness']
    actual={'base':pixels(pbr['baseColorTexture']),
            'normal':pixels(m['normalTexture']),
            'roughness':pixels(pbr['metallicRoughnessTexture'])}
    hashes={}
    for kind,a in actual.items():
        source=ROOT/'textures'/f'obelisk-{key}-{kind}.png'
        expected=np.asarray(Image.open(source).convert('RGB'))
        assert a.shape==expected.shape==(1024,1024,3),(key,kind,a.shape)
        if kind=='roughness':
            assert np.max(np.abs(a[:,:,1].astype(int)-expected[:,:,0].astype(int)))<=1,(key,'Roughness green channel differs')
            assert np.max(a[:,:,2])/255*pbr.get('metallicFactor',1)<1e-6,(key,'Unexpected metallic stone')
        else:
            assert np.array_equal(a,expected),(key,kind,'Export altered authored texture pixels')
        hashes[kind]=hashlib.sha256(source.read_bytes()).hexdigest()
    normals=actual['normal'].astype(float)/255*2-1
    lengths=np.linalg.norm(normals,axis=2)
    assert np.min(lengths)>.99 and np.max(lengths)<1.01
    assert np.min(normals[:,:,2])>0
    assert np.ptp(actual['roughness'][:,:,1])>4
    report['materials'].append({'surface':key,'image_sha256':hashes,
                              'embedded_base_and_normal_pixels_identical':True,
                              'packed_roughness_green_verified':True,
                              'normal_unit_length_range':[float(lengths.min()),float(lengths.max())]})
(ROOT/'research/obelisk_surface_export_check.json').write_text(json.dumps(report,indent=2)+'\n')
print('OBELISK_SURFACE_EXPORT_VERIFIED',len(materials),'materials / 21 embedded maps')
