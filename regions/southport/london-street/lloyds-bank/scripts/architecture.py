"""Architectural facade construction prototypes, in local elevation metres.

The wall helper builds front and back skins and only the perimeter reveals,
so clipped wall fragments do not own extra internal caps. The bank recipe must
still check shared edges and all trim against the exported levels.
"""
from southport3d.geometry import Mesh
from southport3d.planar import subtract


def wall_mesh(name, width, height, apertures, thickness=.3, omit_outer_edges=()):
    boundary=[(0,0),(width,0),(width,height),(0,height)]
    surfaces=[boundary]
    for hole in apertures:
        surfaces=[piece for surface in surfaces for piece in subtract(surface,hole)]
    mesh=Mesh(name)
    for surface in surfaces:
        if len(surface)<3: continue
        n=len(surface)
        mesh.add([(x,y,0) for x,y in surface],[tuple(range(n))])
        mesh.add([(x,y,-thickness) for x,y in surface],[tuple(reversed(range(n)))])
    for loop_index,loop in enumerate([boundary,*apertures]):
        for edge_index,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
            if loop_index==0 and edge_index in omit_outer_edges: continue
            mesh.add([(a[0],a[1],0),(b[0],b[1],0),
                      (b[0],b[1],-thickness),(a[0],a[1],-thickness)],[(0,1,2,3)])
    return mesh
