"""Reproduce approximate facade dimensions from Street View screen rays.

The panorama headings/pitches/FOV parameters are taken from the saved URLs.
The FOV parameter is provisionally treated as horizontal; its rendering convention
has not been verified. These calculations are a sensitivity/proportion aid, not
surveyed dimensions or a recovery of the actual camera position. Width is an
external plan constraint. Assumes a rectilinear screenshot and vertical facade;
stitching, edge picking and mapped widths introduce uncertainty. Never use a
roof point as if it were on the front wall: its setback changes the ray scale.
"""
import json
import math
import numpy as np


def measure(width, heading, pitch, fov, left, right, base, landmarks):
    h,p,a=map(math.radians,[heading,pitch,43.5293])
    focal=720/math.tan(math.radians(fov/2))
    right_axis=np.array([math.cos(h),-math.sin(h),0])
    forward=np.array([math.sin(h)*math.cos(p),math.cos(h)*math.cos(p),math.sin(p)])
    up=np.cross(right_axis,forward)
    normal=np.array([math.sin(a),math.cos(a),0])
    along=np.array([math.cos(a),-math.sin(a),0])
    def ray(pixel):
        x,y=pixel
        direction=forward+(x-720)/focal*right_axis+(500-y)/focal*up
        return direction/(direction@normal)
    distance=width/abs((ray(right)-ray(left))@along)
    camera_height=-ray(base)[2]*distance
    return {'distance':round(distance,3),'camera_height':round(camera_height,3),
            'heights':{key:round(camera_height+ray(pt)[2]*(distance+setback),3)
                       for key,(pt,setback) in landmarks.items()}}


if __name__=='__main__':
    result={
      'myers':measure(7.2,40,18,80,[453,282],[1009,242],[398,922],{
          'parapet':([453,282],0),'upper_sill':([490,491],0),
          'upper_head':([492,365],0),'fascia_top':([413,560],0),
          'ridge_with_estimated_setback':([730,207],3.5)}),
      'kba':measure(9.3752,45,15,80,[414,615],[1213,615],[398,923],{
          'eave':([475,360],0),'gable':([618,264],0),
          'fascia':([430,540],0),'window_head':([540,382],0),
          'window_sill':([540,532],0)})}
    print(json.dumps(result,indent=2))
