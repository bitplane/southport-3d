"""Retain the central datum; terrain outside surveyed joins is provisional."""
def grade(x,y):
    return -.0075-.022*max(-36,min(36,y))
