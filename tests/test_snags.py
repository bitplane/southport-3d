"""Queue persistence, task ownership and local HTTP boundary tests."""
import base64
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from email.message import Message
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from snag_store import SnagStore, MAX_BODY
from serve import Handler

PNG='data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\nfixture').decode()


def payload():
    return {'comment':'Window frame is too thick', 'box':[.1,.2,.3,.4], 'screenshot':PNG,
            'photos':[{'name':'../../reference.png','data':PNG}],
            'view':{'camera':{'position':[1,2,3],'quaternion':[0,0,0,1],
                              'target':[4,5,6],'fov':50,'aspect':1.5},
                    'asset':'building', 'quality':'walk', 'parts':[]}}


class SnagTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=SnagStore(Path(self.tmp.name)/'queue')

    def test_round_trip_and_images_stay_in_queue(self):
        record=self.store.create(payload())
        self.assertEqual(record,self.store.read(record['id']))
        self.assertEqual(self.store.list(),[record])
        self.assertEqual(record['status'],'open')
        self.assertEqual(record['photos'][0]['file'],'photo-1.png')
        self.assertTrue(self.store.image(record['id'],'photo-1.png').is_file())
        with self.assertRaises(FileNotFoundError):self.store.image(record['id'],'../snag.json')
        with self.assertRaises(ValueError):self.store.read('../queue')

    def test_invalid_report_leaves_no_partial_task(self):
        for patch in [{'comment':' '}, {'box':[0,0,2,1]}, {'screenshot':'data:image/svg+xml;base64,PHN2Zz4='},
                      {'photos':[{'name':'x','data':PNG}]*6}]:
            with self.subTest(patch=patch):
                data=payload();data.update(patch)
                with self.assertRaises(ValueError):self.store.create(data)
        data=payload();data['view']['camera']['position'][0]=float('nan')
        with self.assertRaises(ValueError):self.store.create(data)
        self.assertEqual(self.store.list(),[])

    def test_claim_is_exclusive_and_resolution_keeps_history(self):
        record=self.store.create(payload());snag_id=record['id']
        def claim(_):
            try:self.store.update(snag_id,'in_progress',claim=True);return True
            except ValueError:return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(claim,range(2))),[False,True])
        done=self.store.update(snag_id,'done','Fixed in abc123; published')
        self.assertEqual(done['status'],'done');self.assertEqual(len(done['history']),2)
        self.assertEqual(done['history'][-1]['note'],'Fixed in abc123; published')

    def request(self, method, path='/api/snags', data=None, **headers):
        handler=Handler.__new__(Handler);handler.snags=self.store;handler.path=path
        body=json.dumps(data).encode() if data is not None else b''
        handler.headers=Message()
        for key,value in {'Host':'localhost:8765','Content-Type':'application/json',
                          'Content-Length':str(len(body)),**headers}.items():handler.headers[key]=value
        handler.rfile=io.BytesIO(body);handler.wfile=io.BytesIO();result={}
        handler.send_response=lambda status:result.update(status=status)
        handler.send_header=lambda *_:None;handler.end_headers=lambda:None
        getattr(handler,'do_'+method)()
        return result['status'],handler.wfile.getvalue()

    def test_http_create_list_read_and_attachment(self):
        status,body=self.request('POST',data=payload(),Origin='http://localhost:8765')
        self.assertEqual(status,201);record=json.loads(body)
        self.assertEqual(len(json.loads(self.request('GET')[1])['snags']),1)
        status,body=self.request('GET',f"/api/snags/{record['id']}")
        self.assertEqual(status,200);self.assertEqual(json.loads(body),record)
        status,body=self.request('GET',f"/api/snags/{record['id']}/files/view.png")
        self.assertEqual(status,200);self.assertTrue(body.startswith(b'\x89PNG'))
        self.assertEqual(self.request('GET',f"/api/snags/{record['id']}/files/snag.json")[0],404)

    def test_http_rejects_cross_origin_wrong_content_type_and_oversize(self):
        self.assertEqual(self.request('POST',data=payload(),Origin='https://elsewhere.example')[0],403)
        self.assertEqual(self.request('POST',data=payload(),**{'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.request('POST',data=payload(),**{'Content-Length':str(MAX_BODY+1)})[0],413)
        self.assertEqual(self.store.list(),[])

if __name__=='__main__':unittest.main()
