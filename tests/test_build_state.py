"""A failed full build must never be reusable as a checked source build."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import subprocess,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import project

class BuildStateTests(unittest.TestCase):
    def test_validation_failure_leaves_no_fresh_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'asset';(source/'scripts').mkdir(parents=True);(source/'research').mkdir()
            spec={'build':dict(prepare='prepare.py',geometry='build.py',export='export.py',validate='validate.py')}
            args=SimpleNamespace(asset='test.asset',stage='all',threads=1,blender='blender')
            def run(command,**kwargs):
                if any(str(c).endswith('/validate.py') for c in command):raise subprocess.CalledProcessError(1,command)
            with patch.object(project,'ROOT',root),patch.object(project,'assets',return_value={'test.asset':(source,spec)}),patch.object(project,'fingerprint',return_value='abc'),patch.object(project.subprocess,'run',side_effect=run):
                with self.assertRaises(subprocess.CalledProcessError):project.build(args)
            self.assertFalse((root/'build/test.asset/source.sha256').exists())

if __name__=='__main__':unittest.main()
