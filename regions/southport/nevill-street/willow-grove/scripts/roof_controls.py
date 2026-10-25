"""Shared chimney envelope: the shaft continues down into the hip roof."""

def chimney_bounds(d):
    right = d['front_left'] + d['front_width']
    # At this near-eaves position the hip is below the old 13.55/13.8 m
    # shaft bases. Start at eaves level, inside the roof, retaining the crown.
    return ((right - 1.15, 6.10, d['front_eaves']),
            (right - .05, 7.70, 16.75))
