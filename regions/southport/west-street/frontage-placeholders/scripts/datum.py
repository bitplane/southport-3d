"""Existing Nevill datum, blending to the Lord corridor at the south seam."""
def grade(x,y):
    slope=2.9995/207.07
    near=max(0,min(1,(x+97.84)/16))
    return -.7995+slope*max(0,y-65+24*near)
