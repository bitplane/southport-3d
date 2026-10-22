"""Conditional planar checks for the exterior's vertical revision.

Uses manually observed native pixels, not source-image colours. The lower
registration line follows column feet, not the sloping pavement. This is not
a calibrated camera, and neither corner-pick sensitivity nor inter-view
agreement establishes absolute survey accuracy.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def homography(source, target):
    rows, rhs = [], []
    for (x, y), (u, v) in zip(source, target):
        rows.extend([[x,y,1,0,0,0,-u*x,-u*y],
                     [0,0,0,x,y,1,-v*x,-v*y]])
        rhs.extend([u,v])
    return np.r_[np.linalg.solve(rows, rhs), 1].reshape(3,3)


def project(matrix, points):
    points = np.c_[np.asarray(points), np.ones(len(points))]
    q = points @ matrix.T
    return q[:,:2] / q[:,2:]


source = [[447,842],[3508,733],[3496,1664],[425,1582]]
target = [[-12.2,5.54],[12.2,5.54],[12.2,.35],[-12.2,.35]]
matrix = homography(source, target)
windows = {
    'left': [[599,1183],[697,1183],[697,1452],[592,1448]],
    'right': [[3068,1181],[3224,1181],[3223,1523],[3064,1518]],
}
trophies = {
    'left': [[570,1063],[736,1060],[736,1123],[570,1125]],
    'right': [[3022,1033],[3290,1029],[3290,1101],[3022,1104]],
}


def rectangle_dimensions(points):
    q = project(matrix, points)
    return {'corners_m':q.tolist(),
            'width_m':float(np.mean([q[1,0]-q[0,0],q[2,0]-q[3,0]])),
            'height_m':float(np.mean([q[0,1]-q[3,1],q[1,1]-q[2,1]])),
            'bottom_z_m':float(np.mean(q[2:,1])),
            'top_z_m':float(np.mean(q[:2,1]))}


report = {
    'status':'Conditional whole-facade registration supporting a coupled vertical revision; not a surveyed camera solution',
    'source':'references/images/commons-columns-1.jpg',
    'source_pixels':[3648,2736],
    'source_url':'https://commons.wikimedia.org/wiki/File:Columns,_Southport_Monument_1.JPG',
    'registration_pixels':source, 'assumed_registration_metres':target,
    'registration_notes':[
        'Upper corners use the front parapet line; the wall/cornice depth offset is not solved.',
        'Lower points extrapolate the level structural column-foot line, rather than the pavement edge.',
        '24.4 m front parapet span is the existing estimate within the published 24.6 m overall envelope.',
        'Roof 5.54 m and column-foot 0.35 m share the earlier conditional vertical anchors.',
        'The opening corners follow the front reveal, including its lit return; the dark interior silhouette alone is too narrow.',
    ],
    'image_to_facade_homography':matrix.tolist(),
    'windows':{k:{'pixels':v,**rectangle_dimensions(v)} for k,v in windows.items()},
    'trophies':{k:{'pixels':v,**rectangle_dimensions(v)} for k,v in trophies.items()},
    'end_panel_check':{
        'source':'references/images/iwm-mont_9a.jpg',
        'native_pixels':[855,1280],
        'observations_px':{'frieze_lower_edge_y':178,'structural_foot_y':1256,
                           'panel_top_y':505,'panel_bottom_y':1006,'panel_width_px':243},
        'conditional_height_m':(1006-505)/(1256-178)*(4.42-.35),
        'conditional_bottom_z_m':.35+(1256-1006)/(1256-178)*(4.42-.35),
        'apparent_aspect_height_over_width':501/243,
        'limits':'Near-frontal image, not an orthographic elevation. WMO full-end estimate gives about 1.83 m height / 1.09 m bottom, so the selected shared level is a compromise, not an exact transfer.',
    },
    'selected_dimensions_m':{
        'window':{'width':1.04,'height':1.90,'bottom':1.20,'top':3.10,
                  'jamb_centre_offset':.71,'jamb_width':.38,'band_width':2.30,
                  'band_bottom':3.10,'band_top':3.32},
        'trophy':{'width':1.85,'height':.42,'centre_z':3.75},
        'end_plaque':{'width':.94,'height':1.90,'bottom':1.20,'top':3.10,
                      'band_bottom':3.20,'band_top':3.42,'band_width':2.32},
    },
    'decision':[
        'Use the independent three-view shaft/upper-stack ratio to revise the shaft top to 3.84 m, including a plain capital neck.',
        'Window head and trophy levels from this whole-facade registration agree with the shorter shaft. Revise their fit together with the roof bands.',
        'Preserve the traced end-carving aspect by scaling its width and height together, rather than compressing the figure vertically.',
        'Do not adopt new bay spacing from this registration: depth offsets, corner extrapolation and absolute anchors remain insufficiently constrained.',
    ],
    'limits':[
        'These dimensions remain photographic estimates; approximate uncertainty is 0.15 m in window width and 0.25 m in height/vertical placement.',
        'The two windows disagree by about 0.2 m at the sill. This is retained as evidence of registration/landmark uncertainty, not modelled as different window designs.',
        'The prior 2.1–2.2 apparent window aspect was not a rectified physical aspect: it mixed facade foreshortening with vertical scale.',
        'Global camera intrinsics, lens distortion, depth offsets and the physical datum of IWM height remain unresolved.',
        'End plaque width follows its near-frontal aspect; full depth and frame profiles remain estimated.',
    ],
}
out=ROOT/'research/colonnade_facade_calibration.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print('FACADE_CALIBRATION',json.dumps({k:rectangle_dimensions(v) for k,v in windows.items()}))
