"""Fit repeated cornice-pair spacing without treating raw pixels as metres.

The six pair centres define a one-dimensional projectivity. Absolute pitch
still depends on a separate, explicitly estimated chamber-centre anchor.
"""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sources=[
    {'id':'flickr-7465690872','pixels':[3072,1836],
     'url':'https://www.flickr.com/photos/rossendalewadey/7465690872',
     'mask_pairs_x_px':[[542,688],[957,1060],[1346,1453],[1740,1842],[2127,2230],[2495,2630]],
     'window_axes_at_cornice_y_x_px':[285,2864],
     'window_transfer':'Opening head centres about 290 and 2861 px, transferred upward along the observed jamb directions; approximate, ±8 px.',
     'uncertainty_px':4},
    {'id':'commons-columns-1','pixels':[3648,2736],
     'url':'https://commons.wikimedia.org/wiki/File:Columns,_Southport_Monument_1.JPG',
     'mask_pairs_x_px':[[815,928],[1152,1240],[1494,1586],[1857,1958],[2252,2360],[2654,2814]],
     'window_axes_at_cornice_y_x_px':[657,3149],
     'window_transfer':'Front-reveal head centres 648 and 3146 px; transferred along jamb axes to cornice height. Window plane is set back and its parallax remains unresolved.',
     'uncertainty_px':4},
]
q=np.arange(6,dtype=float)-2.5
for s in sources:
    pairs=np.asarray(s['mask_pairs_x_px'],float);x=pairs.mean(axis=1)
    a,b,c=np.linalg.lstsq(np.c_[q,np.ones(6),-x*q],x,rcond=None)[0]
    predicted=(a*q+b)/(c*q+1)
    def inverse(x):return (np.asarray(x)-b)/(a-c*np.asarray(x))
    normalised=inverse(pairs)
    window_q=inverse(s['window_axes_at_cornice_y_x_px'])
    s['fit']={'formula':'x_px = (a*q+b)/(c*q+1); q is bay units from the central axis',
              'a_b_c':[a,b,c],'observed_pair_centres_x_px':x.tolist(),
              'residuals_px':(predicted-x).tolist(),
              'rms_px':float(np.sqrt(np.mean((predicted-x)**2))),
              'within_pair_bay_fractions':np.diff(normalised,axis=1).ravel().tolist(),
              'window_axes_bay_units':window_q.tolist(),
              'conditional_pitch_m':19.70/(window_q[1]-window_q[0])}
report={
 'status':'Conditional photographic plan / roof projection study; reviewed geometry adopted in checkpoint 0.12',
 'sources':sources,
 'geometric_evidence':[
  'Six cornice-mask pair centres follow the same repeated pitch: two end-pier pairs plus four column pairs.',
  'Commons columns 2, Commons columns 1, WMO Southport_2 and Flickr show the complete central roof/frieze projecting forward relative to the window-chamber portions. There is no return to a recessed plane between each end pier and the columns.',
  'The current model puts the lamp/pier axis too near its window frame, and gives the four column pairs too large a pitch relative to the chamber locations.',
 ],
 'absolute_anchor':{
  'published_overall_length_m':24.6,'published_max_depth_m':4.9,
  'assumed_chamber_external_square_m':4.4,
  'assumed_end_wall_outer_x_m':12.05,
  'assumed_window_centres_x_m':[-9.85,9.85],
  'basis':'A square chamber is described by Historic England. The 4.4 m wall envelope and 0.25 m maximum cornice allowance are estimates within the IWM overall dimensions, not measured plan dimensions.',
  'links':['https://historicengland.org.uk/listing/the-list/list-entry/1379604','https://memorials.iwm.org.uk/memorial/1228'],
 },
 'selected_candidate_m':{
  'bay_pitch':3.0,'column_pair_separation':.80,'pier_pair_separation':1.08,
  'column_pair_centres':[-4.5,-1.5,1.5,4.5],'pier_centres':[-7.5,7.5],
  'pier_width':1.30,'window_centres':[-9.85,9.85],
  'central_to_chamber_setback':.12,'central_roof_break_x':8.15,
  'chamber_side_wall_centre_y':2.02,'chamber_side_wall_depth':.36,
  'pier_outer_y':2.32,'end_wall_centre_x':11.87,'entrance_wall_centre_x':7.83,
  'chamber_outer_x':12.05,'chamber_entrance_x':7.65,'side_wall_inner_tip_x':6.85,
  'lamp_y':2.85,'maximum_text_width':12.7,
 },
 'previous_plan_m':{'bay_pitch':3.5,'column_pair_separation':.70,'pier_centres':[-8.64,8.64],'window_centres':[-9.75,9.75]},
 'limits':[
  'Small pixel residuals establish a repeated-pattern fit, not the accuracy of the absolute pitch.',
  'Both conditional pitches share the same chamber-centre assumption; they are not independent metric surveys.',
  'Roof masks, windows, column shafts and lamps lie in different depth planes. The one-dimensional fit does not solve their parallax or full camera intrinsics.',
  'Candidate bay pitch remains uncertain by roughly 0.15 m; chamber plan, pier width, 0.12 m setback and moulding contours are estimated.',
  'Only exterior/structural shell geometry is included. Interior Ionic columns, coffered ceilings and name panels remain deferred.',
 ],
 'next_action':'Retain conditional dimensions and source observations; completed comparison is recorded in colonnade_plan_study_review.json. Further absolute calibration requires new evidence.'
}
(ROOT/'research/colonnade_plan_projection_study.json').write_text(json.dumps(report,indent=2)+'\n')
print('PLAN_SPACING_FIT',[(s['id'],s['fit']['rms_px'],s['fit']['conditional_pitch_m']) for s in sources])
