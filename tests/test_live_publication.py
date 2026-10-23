"""Live clients need a retirement grace period independent of build timestamps."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from publish_viewer import retire_resources


def test_retirement_survives_multiple_publications_and_reactivation(tmp_path):
    assets = tmp_path / 'assets'
    assets.mkdir()
    for name in ('old.glb', 'new.glb'):
        (assets / name).write_bytes(b'model')
    retire_resources(tmp_path, {'assets/new.glb'}, now=100)
    retire_resources(tmp_path, {'assets/new.glb'}, now=200)
    assert (assets / 'old.glb').exists()
    # Reintroducing a resource cancels its expiry.
    retire_resources(tmp_path, {'assets/new.glb', 'assets/old.glb'}, now=300)
    retire_resources(tmp_path, {'assets/new.glb'}, now=400)
    retire_resources(tmp_path, {'assets/new.glb'}, now=86700)
    assert (assets / 'old.glb').exists()
    retire_resources(tmp_path, {'assets/new.glb'}, now=86801)
    assert not (assets / 'old.glb').exists()
    assert (assets / 'new.glb').exists()


def test_event_stream_announces_only_changed_catalog(tmp_path):
    from io import BytesIO
    from unittest.mock import patch
    from serve import Handler
    catalog = tmp_path / 'catalog.json'
    catalog.write_text('{"revision":"one"}')
    handler = object.__new__(Handler)
    handler.directory = str(tmp_path)
    handler.wfile = BytesIO()
    handler.send_response = lambda status: None
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    calls = 0

    def tick(seconds):
        nonlocal calls
        calls += 1
        if calls == 2:
            catalog.write_text('{"revision":"two"}')
        if calls == 3:
            raise BrokenPipeError()

    with patch('serve.time.sleep', tick):
        handler.events()
    output = handler.wfile.getvalue()
    assert output.count(b'event: catalog') == 2
    assert b': keepalive' in output
