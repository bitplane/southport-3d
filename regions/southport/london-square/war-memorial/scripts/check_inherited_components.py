"""Check that reused inspection views still represent unchanged components.

Rebuilds can differ in float32 UV rounding on bevelled window capitals.
Allow only sub-micrometre UV deltas at the one-metre texture scale. Geometry,
normals, indices, scene structure, materials and embedded images must match.
"""
from pathlib import Path
import hashlib
import argparse
import json
import struct
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--baseline',required=True,help='Preserved checkpoint directory')
parser.add_argument('--report',required=True,help='Output comparison JSON relative to project root')
parser.add_argument('--components',nargs='+',default=['colonnade-north-east.glb','colonnade-south-west.glb','clustered-lamps.glb'],
                    choices=['obelisk.glb','colonnade-north-east.glb','colonnade-south-west.glb','clustered-lamps.glb'])
args=parser.parse_args()
PREVIOUS=ROOT/args.baseline

def read_glb(path):
    raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0]
    return json.loads(raw[20:20+size]),raw[28+size:],hashlib.sha256(raw).hexdigest()

report={'previous_checkpoint':args.baseline,'components':[],
        'scope':'Supports inheritance only for isolated views of the explicitly checked components; camera and lighting must also remain unchanged'}
for name in args.components:
    old,old_bin,old_sha=read_glb(PREVIOUS/'models'/name)
    new,new_bin,new_sha=read_glb(ROOT/'models'/name)
    assert old==new,(name,'Scene, material or accessor metadata changed')
    assert len(old_bin)==len(new_bin)
    semantics={}
    for mesh in old['meshes']:
        for primitive in mesh['primitives']:
            for semantic,index in primitive['attributes'].items():
                semantics[index]=(mesh['name'],semantic)
    normalized=bytearray(new_bin);changed=[]
    for index,(mesh,semantic) in semantics.items():
        if not semantic.startswith('TEXCOORD_'):continue
        accessor=old['accessors'][index];view=old['bufferViews'][accessor['bufferView']]
        assert accessor['componentType']==5126 and accessor['type']=='VEC2'
        assert view.get('byteStride',8)==8
        start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
        count=accessor['count']*2;end=start+count*4
        a=np.frombuffer(old_bin,dtype='<f4',count=count,offset=start)
        b=np.frombuffer(new_bin,dtype='<f4',count=count,offset=start)
        assert np.all(np.isfinite(a)) and np.all(np.isfinite(b))
        maximum=float(np.max(np.abs(a.astype(float)-b.astype(float))))
        assert maximum<=1e-6,(name,mesh,semantic,maximum)
        if maximum:
            changed.append({'mesh':mesh,'accessor':index,'max_uv_difference':maximum,
                            'changed_components':int(np.count_nonzero(a!=b))})
            normalized[start:end]=old_bin[start:end]
    assert normalized==old_bin,(name,'Non-UV binary content changed')
    report['components'].append({'file':'models/'+name,'previous_sha256':old_sha,'current_sha256':new_sha,
                                'non_uv_content_identical':True,'uv_rounding_only':changed})
(ROOT/args.report).write_text(json.dumps(report,indent=2)+'\n')
print('INHERITED_COMPONENTS_VERIFIED',len(report['components']))
