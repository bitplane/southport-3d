"""Continue the two existing boundary datums; interior levels are provisional."""
def grade(x,y):
    slope=2.9995/207.07
    near=max(0,min(1,(50.19-x)/16))
    return -.7995+slope*(24*near+max(0,y-65))
