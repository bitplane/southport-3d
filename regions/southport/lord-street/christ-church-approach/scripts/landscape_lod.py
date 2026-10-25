import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(os.environ.get('SOUTHPORT_REPO_ROOT',Path(__file__).resolve().parents[5]))/'lib'))
from southport3d.landscape import tree as source_tree

def tree(level='detail', name='Tree'):
    """Outward canopy shells with triangular, non-degenerate pole caps.

    Keep this repair local until the shared ellipsoid's other callers have been
    audited. Bark uses different primitives and must retain its winding.
    """
    mesh=source_tree(level,name)
    for i,(face,material) in enumerate(zip(mesh.faces,mesh.indices)):
        if material==0:
            continue
        unique=[];positions=set()
        for vertex in reversed(face):
            position=tuple(round(c,8) for c in mesh.vertices[vertex])
            if position not in positions:
                unique.append(vertex);positions.add(position)
        assert len(unique)>=3
        mesh.faces[i]=tuple(unique)
    return mesh

def build_lod(name,settings,asset_dir):
    return tree(settings['level'],name).finish([])
