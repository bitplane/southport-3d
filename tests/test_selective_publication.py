"""Publishing a snag fix must not lock or replace another worker's draft."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import nullcontext
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import publish_viewer

class SelectivePublicationTests(unittest.TestCase):
    def test_selected_asset_locks_and_retains_previous_other_asset(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            source=root/'selected';source.mkdir();(source/'publication.json').write_text('{}')
            (root/'dist').mkdir()
            previous={'id':'draft','parts':[{'id':'old-checked-part'}]}
            (root/'dist/catalog.json').write_text(json.dumps({'assets':[previous,{'id':'selected'}]}))
            inventory={'selected':(source,{}),'draft':(root/'draft',{})}
            locks=[]
            def lock(root,key):
                locks.append(key)
                return nullcontext()
            with patch.object(publish_viewer,'ROOT',root),patch('build_lock.asset_lock',side_effect=lock),patch.object(publish_viewer,'_publish') as run:
                publish_viewer.publish(SimpleNamespace(asset=['selected']),lambda:inventory,None,None)
                self.assertEqual(locks,['catalog','selected'])
                self.assertEqual(set(run.call_args.args[1]()),{'selected'})
                self.assertEqual(run.call_args.args[4],[previous])

    def test_unknown_selection_fails_before_catalog_mutation(self):
        with patch.object(publish_viewer,'_publish') as run:
            with self.assertRaisesRegex(ValueError,'Unknown publication assets'):
                publish_viewer.publish(SimpleNamespace(asset=['typo']),lambda:{},None,None)
            run.assert_not_called()

    def test_selecting_unpublishable_asset_is_an_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError,'no publication recipe'):
                publish_viewer.publish(SimpleNamespace(asset=['draft']),lambda:{'draft':(Path(temporary),{})},None,None)

if __name__=='__main__':unittest.main()
