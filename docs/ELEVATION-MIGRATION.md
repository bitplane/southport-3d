# Rough town ground heights

The town map uses editable broad slopes, not a terrain reconstruction. Roads and
paving use simple planar faces between shared height controls. Do not refine the
mesh to follow local raster fluctuations, roof returns, water interpolation or
concrete-surface noise. Review and correct ordinary defects through the main
viewer's snag queue; there is no separate elevation-review application.

## Editing levels

`regions/southport/elevation/ground-controls.json` holds local heights on a 100 m
site grid. Key `i,j` is position `(100*i, 100*j)` metres in the existing memorial
frame. Edit the value in `heights_m` to move that junction of the broad ground
planes. Neighbouring regions read the same controls, so their boundaries agree.
The grid is an inexpensive shared base, not a claim that every road is sampled or
surveyed every 100 m. Only cells intersecting owned ground generate geometry.

Regional elevation files select `type: "control_grid"`, their bounds and paving
offset. Road surfaces subtract the authored 0.12 m kerb allowance. Existing explicit
entrance ramps retain their relative offsets. Concrete courts can use a separate
constant-height or straight-profile surface where a flat platform is needed.
Do not add fine grid refinements. Use a small number of named profile controls for
an actual crest, landing, retaining break or independently established level.

Building floors and roofs remain level. Place foundations and entrances against
the selected ground; do not tilt architecture. Placeholder foundations already
consume regional controls. Existing detailed-building thresholds are repaired as
ordinary snags; do not hold up further town modelling for a comprehensive survey.

Eastbank and Tulketh retain their simple shared longitudinal approach profile and
independent railway level. Marine Way and Venetian decks retain separate profiles.
Water is not walkable ground, and bridge roads must not collapse onto underpasses.
These profiles can be adjusted directly when detailed bridge work reaches them.

## Reference and uncertainty

The initial coarse heights were rounded to 0.1 m from nearby mapped road samples,
using the median of nine nearby DTM values where DSM and DTM differ by less than
0.5 m. Bridge-labelled road lines were excluded. These are rough starting estimates,
not verified ground controls. Outlying cells extrapolate from mapped roads and
need local judgement when used. The source file is fixed and editable: ordinary
builds do not resample the raster or undo edits. Memorial control `(0,0)` retains
the approximate road tie of -0.1 m local.

Local zero's provisional conversion is 6.485294 m ODN, derived from road samples
beside the memorial, not a surveyed benchmark. The private EA 1 m DTM/DSM and
source metadata remain available as research evidence. Classification and gap
interpolation can retain artefacts or remove real sharp breaks. DTM/DSM agreement
is not independent corroboration. Never use water interpolation as a lake survey.

## Checks and publication

Validate finite nondegenerate geometry, authored plane agreement, ownership/seams,
separate upper/lower supports and consistency across LoDs. Raster agreement is not
an acceptance criterion. Keep the existing source reference/audit tools optional;
do not turn their warnings into a detailed terrain-modelling backlog.

Publish selected connected assets with repeated `tools/project.py publish --asset`
arguments. The whole map uses the main viewer and usual snag process. The old
private baseline is retained for comparison. Funland steps, retaining walls and
pier clearances can be refined when those features are modelled; their missing
fine detail is not a blocker to ordinary building work.
