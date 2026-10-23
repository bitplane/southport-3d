"""Incremental stages must prove inputs, outputs, failures and read-only leaves."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_state


@pytest.fixture
def recipe(tmp_path, monkeypatch):
    root=tmp_path
    source=root/'regions/test';(source/'scripts').mkdir(parents=True);(source/'research').mkdir()
    (root/'lib').mkdir();(root/'tools').mkdir()
    for name in ('trace_run.py','build_state.py'):
        (root/'tools'/name).write_text((Path(build_state.__file__).parent/name).read_text())
    (root/'lib/used.py').write_text('VALUE="geometry"\n')
    (root/'lib/unrelated.py').write_text('VALUE=1\n')
    (source/'research/layout.json').write_text('{}')
    spec={'id':'test.asset','build':dict(prepare='prepare.py',geometry='build.py',export='export.py',validate='validate.py',render='render.py')}
    (source/'asset.json').write_text(json.dumps(spec))
    common="from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\n"
    scripts={'prepare.py':"(ROOT/'textures/map.txt').write_text('texture')",
             'build.py':"import os,sys\nsys.path.insert(0,os.environ['SOUTHPORT_REPO_ROOT']+'/lib')\nfrom used import VALUE\n(ROOT/'models/test.blend').write_text(VALUE)",
             'export.py':"(ROOT/'models/test.glb').write_text('export')",
             'validate.py':"assert (ROOT/'models/test.blend').read_text()=='geometry'",
             'render.py':"(ROOT/'renders/test.txt').write_text('render')",
             'contact_sheet.py':"pass"}
    for name,body in scripts.items():(source/'scripts'/name).write_text(common+body+'\n')
    monkeypatch.setattr(build_state,'tool_identity',lambda _: {'version':'test'})
    real_run=subprocess.run
    def run(command,**kwargs):
        if command[0]=='fake-blender':command=[sys.executable,command[command.index('--python')+1],*command[command.index('--')+1:]]
        return real_run(command,**kwargs)
    monkeypatch.setattr(build_state.subprocess,'run',run)
    def stages():return build_state.Stages(root,source,spec,root/'build/test.asset','fake-blender',1)
    return root,source,stages


def test_runtime_dependencies_and_leaf_only_changes(recipe):
    root,source,make=recipe;s=make()
    for stage in ('master','export','validate','render'):s.execute(stage)
    assert all(make().reason(stage) is None for stage in ('master','export','validate','render'))
    (root/'lib/unrelated.py').write_text('VALUE=2\n')
    assert make().reason('master') is None
    with (source/'scripts/render.py').open('a') as f:f.write('\n# camera change\n')
    assert make().reason('master') is None
    assert make().reason('render')
    (root/'lib/used.py').write_text('VALUE="changed"\n')
    assert 'used.py' in make().reason('master')


def test_corrupt_output_failure_and_read_only_master(recipe):
    root,source,make=recipe;s=make();s.execute('master')
    blend=root/'build/test.asset/models/test.blend';blend.write_text('corrupt')
    assert 'output missing or changed' in make().reason('master')
    s.execute('master')
    (source/'scripts/validate.py').write_text("raise RuntimeError('bad geometry')")
    with pytest.raises(subprocess.CalledProcessError):s.execute('validate')
    assert make().reason('validate')=='no successful stage record'
    (source/'scripts/render.py').write_text("from pathlib import Path\n(Path(__file__).resolve().parents[1]/'models/test.blend').write_text('mutated')")
    with pytest.raises(ValueError,match='mutated master'):s.execute('render')
    assert make().reason('master')


def test_input_change_during_build_is_not_blessed(recipe,monkeypatch):
    root,source,make=recipe;s=make();original=s.run_script
    def run(script,*args,**kwargs):
        original(script,*args,**kwargs)
        if script=='build.py':(root/'lib/used.py').write_text('VALUE="edited concurrently"\n')
    monkeypatch.setattr(s,'run_script',run)
    with pytest.raises(ValueError,match='Dependency changed'):s.execute('master')
    assert make().reason('master')=='no successful stage record'


def test_force_same_inputs_same_key_and_tool_identity_invalidation(recipe,monkeypatch):
    root,source,make=recipe;s=make();s.execute('master');key=s.state['nodes']['master']['key']
    s.execute('master',force=True)
    assert s.state['nodes']['master']['key']==key
    monkeypatch.setattr(build_state,'tool_identity',lambda _:{'version':'different'})
    assert make().reason('master')


def test_cross_asset_reads_and_validation_helpers_are_discovered(recipe):
    root,source,make=recipe
    neighbour=root/'regions/neighbour/research';neighbour.mkdir(parents=True)
    (neighbour/'layout.json').write_text('{}')
    (root/'tools/check_helper.py').write_text('def check(): return True\n')
    (source/'scripts/validate.py').write_text("import os,sys\nfrom pathlib import Path\nrepo=Path(os.environ['SOUTHPORT_REPO_ROOT'])\nsys.path.insert(0,str(repo/'tools'))\nfrom check_helper import check\nassert check()\nassert (repo/'regions/neighbour/research/layout.json').read_text()=='{}'\n")
    s=make();s.execute('master');s.execute('validate')
    assert s.reason('validate') is None
    (neighbour/'layout.json').write_text('{"changed":true}')
    assert 'layout.json' in make().reason('validate')
    assert make().reason('master') is None
    (neighbour/'layout.json').write_text('{}')
    (root/'tools/check_helper.py').write_text('def check(): return False\n')
    assert 'check_helper.py' in make().reason('validate')
    assert make().reason('master') is None


def test_render_edit_does_not_change_package_inputs(recipe):
    root,source,make=recipe;s=make();s.execute('master')
    before=s.inputs('package',[])
    with (source/'scripts/render.py').open('a') as f:f.write('\n# another review view\n')
    assert s.inputs('package',[])==before


def test_partial_render_does_not_bless_full_render_cache(recipe):
    _,_,make=recipe;s=make();s.execute('master');s.execute('render',views=['closeup'])
    assert make().reason('render')


def test_generated_research_survives_between_stages_and_is_checked(recipe):
    root,source,make=recipe
    with (source/'scripts/prepare.py').open('a') as f:
        f.write("(ROOT/'research/materials.json').write_text('generated material manifest')\n")
    with (source/'scripts/export.py').open('a') as f:
        f.write("assert (ROOT/'research/materials.json').read_text()=='generated material manifest'\n(ROOT/'research/export-report.json').write_text('export checked')\n")
    with (source/'scripts/validate.py').open('a') as f:
        f.write("assert (ROOT/'research/export-report.json').read_text()=='export checked'\n")
    s=make()
    for stage in ('master','export','validate','render'):s.execute(stage)
    assert all(make().reason(stage) is None for stage in ('master','export','validate','render'))
    assert not (source/'research/materials.json').exists()
    (root/'build/test.asset/research/materials.json').write_text('corrupted')
    assert 'output missing or changed' in make().reason('master')
    s.execute('master')
    assert (root/'build/test.asset/research/materials.json').read_text()=='generated material manifest'
    assert not (root/'build/test.asset/research/export-report.json').exists()
