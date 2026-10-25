"""Existing metric families, with the local outward-canopy repair retained."""
import math
from southport3d.geometry import Mesh
from southport3d.street import furniture
from landscape_lod import tree


def hedge(level='detail',name='Hedge'):
    mesh=Mesh(name);segments,rings={'detail':(10,6),'walk':(7,4),'district':(4,3)}[level]
    mesh.box((0,0,.38),(1,.75,.76),0)
    mesh.ellipsoid((0,0,.69),(.53,.43,.35),1,segments,rings)
    if level!='district':
        for x,y,z in [(-.3,-.12,.79),(.3,.08,.84)]:mesh.ellipsoid((x,y,z),(.25,.33,.25),2,segments,rings)
    for i,(face,mat) in enumerate(zip(mesh.faces,mesh.indices)):
        if mat==0:continue
        seen=set();unique=[]
        for vertex in reversed(face):
            p=tuple(round(v,8)for v in mesh.vertices[vertex])
            if p not in seen:unique.append(vertex);seen.add(p)
        mesh.faces[i]=tuple(unique)
    return mesh


def bench(level='detail',name='Bench'):
    """Reuse the family; give its coarse timber seat/back one union shell.

    Their original two boxes overlap by20mm and duplicate the end skins at
    X=±.95. This exact cross-section union preserves every exterior bound.
    """
    mesh=furniture('bench',level,name)
    if level=='district':
        keep=[(face,mat)for face,mat in zip(mesh.faces,mesh.indices)if mat!=7]
        mesh.faces=[face for face,mat in keep];mesh.indices=[mat for face,mat in keep]
        timber=Mesh('Coarse seat and back ownership')
        timber.outline([(-.22,.445),(.24,.445),(.24,.475),(.2725,.475),(.2725,.785),(.2175,.785),(.2175,.495),(-.22,.495)],-.95,.95,7)
        timber.vertices=[(depth,y,z)for y,z,depth in timber.vertices]
        mesh.add(timber.vertices,timber.faces,7)
    return mesh


def build_lod(name,settings,asset_dir):
    kind,level=settings['kind'],settings['level']
    factory={'tree':tree,'hedge':hedge,'bench':bench}.get(kind)
    return (factory(level,name)if factory else furniture(kind,level,name)).finish([])
