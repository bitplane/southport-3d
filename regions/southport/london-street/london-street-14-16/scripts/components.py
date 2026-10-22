"""Small authored LoD receivers for the actual casement/sill silhouette."""
from southport3d.geometry import Mesh


def window_receiver(name, settings, asset_directory):
    w=settings['width']/2;h=settings['height']/2
    # The sill projects sideways below the frame only. A bounding rectangle
    # introduces unsupported black corners alongside the upper casement.
    points=[(-w-.04,-h-.07),(w+.04,-h-.07),(w+.04,-h),
            (w,-h),(w,h),(-w,h),(-w,-h),(-w-.04,-h)]
    mesh=Mesh(name)
    mesh.add([(x,y,.11) for x,y in points],[tuple(range(len(points)))])
    return mesh.finish([])
