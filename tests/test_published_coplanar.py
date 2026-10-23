"""Native map-wide scan agrees with the small reference detector."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from coplanar import overlaps
from audit_published_coplanar import primitives

ROOT = Path(__file__).resolve().parents[1]


def test_native_overlap_scan():
    a = np.array([[0., 0, 0], [2, 0, 0], [0, 2, 0]])
    base = [a, a, a+(.2,.2,0), a[::-1], a+(0,0,.005), a+(0,0,.00001),
            np.array([[2.,0,0],[2,2,0],[0,2,0]])]
    # Include enough triangles to exercise internal BVH nodes, far-apart groups,
    # rotations, edge contact, near planes, and genuinely separated trim.
    triangles = []
    for i in range(12):
        theta = .13*i; c,s = np.cos(theta),np.sin(theta)
        rotation = np.array([[c,0,s],[0,1,0],[-s,0,c]])
        triangles.extend([t@rotation.T+[i*20,100,20] for t in base])
    triangles = np.array(triangles)
    expected = {(int(a),int(b)) for a,b,area in overlaps(triangles,range(len(triangles)))}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); executable = tmp/'scan'
        subprocess.run(['g++','-O2','-std=c++17',str(ROOT/'tools/coplanar_scan.cpp'),'-o',str(executable)],check=True)
        triangles.astype('<f8').tofile(tmp/'input')
        subprocess.run([str(executable),str(tmp/'input'),str(tmp/'output')],check=True)
        hits = np.fromfile(tmp/'output',dtype=[('a','<u4'),('b','<u4'),('area','<f8')])
        actual = {(int(h['a']),int(h['b'])) for h in hits}
        assert len(actual)==len(hits), 'BVH duplicated pairs'
        assert actual==expected, (actual-expected, expected-actual)


def test_published_node_and_catalog_transforms():
    points = np.array([[0,0,0],[1,0,0],[0,1,0]],dtype='<f4')
    binary = points.tobytes()+np.array([0,1,2],dtype='<u4').tobytes()
    doc = {'asset':{'version':'2.0'},'buffers':[{'byteLength':len(binary)}],
           'bufferViews':[{'buffer':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':12}],
           'accessors':[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3'},
                        {'bufferView':1,'componentType':5125,'count':3,'type':'SCALAR'}],
           'materials':[{'name':'stone'}],
           'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1,'material':0}]}],
           'nodes':[{'translation':[2,0,0],'children':[1,2,3]},
                    {'name':'first','mesh':0,'scale':[2,1,1]},
                    {'name':'instance','mesh':0,'translation':[0,0,3]},
                    {'name':'mirrored','mesh':0,'scale':[-1,1,1]}],
           'scenes':[{'nodes':[0]}]}
    encoded=json.dumps(doc).encode();encoded+=b' '*((-len(encoded))%4)
    data=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'test.glb';p.write_bytes(data)
        result=list(primitives(p,{'rotationY':np.pi/2,'position':[10,20,30]}))
    assert len(result)==3
    np.testing.assert_allclose(result[0][0][0],[[10,20,28],[10,20,26],[10,21,28]],atol=1e-12)
    np.testing.assert_allclose(result[1][0][0],[[13,20,28],[13,20,27],[13,21,28]],atol=1e-12)

    np.testing.assert_allclose(result[2][0][0],[[10,20,28],[10,21,28],[10,20,29]],atol=1e-12)
