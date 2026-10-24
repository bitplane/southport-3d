"""Chapel-specific fittings; placements live in the area plan."""
import math,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'))
from southport3d.geometry import Mesh
from southport3d.street import furniture as generic

def furniture(kind,level='detail',name=None):
    n={'detail':16,'walk':10,'district':6}[level]
    m=Mesh(name or kind)
    if kind=='chapel-lamp':
        m.lathe((0,0),[(0,.13),(.25,.13),(.4,.085),(4.7,.055)],n,1)
        count={'detail':16,'walk':8,'district':4}[level]
        path=[(0,0,4.6)]+[(0,-2.2*(1-math.cos(i*math.pi/2/count)),4.6+1.4*math.sin(i*math.pi/2/count)) for i in range(count+1)]
        m.tube(path,.055,1,max(4,n//2));m.ellipsoid((0,-2.25,5.98),(.18,.40,.10),0,n,max(3,n//2))
        m.ellipsoid((0,-2.25,5.93),(.14,.32,.035),2,n,max(3,n//2))
    elif kind=='steel-bollard':
        m.lathe((0,0),[(0,.075),(.95,.075),(1,.065)],n,1)
        if level!='district':m.lathe((0,0),[(.83,.077),(.86,.077)],n,0)
    elif kind=='planter':
        # Coarse round municipal planter, low planting bound; no invented palm species.
        m.lathe((0,0),[(0,.65),(.12,.72),(.85,.83),(.9,.85)],n,0)
        m.lathe((0,0),[(.902,.73),(.94,.73)],n,7)
    elif kind=='bench' and level=='district':
        for x in [-.72,.72]:m.box((x,0,.23),(.065,.55,.46),0)
        m.box((0,0,.47),(1.9,.46,.05),7)
        m.box((0,.245,.74),(1.9,.055,.31),7)
    else:return generic(kind,'walk' if level=='detail' else level,name)
    return m

def finish(mesh, materials, collection=None):
    import bmesh
    ob=mesh.finish(materials,collection)
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    return ob

def build_lod(name,settings,asset_dir):
    return finish(furniture(settings['kind'],settings['level'],name),[])
