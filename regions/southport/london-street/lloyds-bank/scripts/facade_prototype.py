"""Design-stage arched aperture helpers for the London Street front.

Local elevation coordinates are (frontage distance, height, outward depth).
This is deliberately not integrated until its geometry is checked against the
August 2024 front and the wall/trim surface ownership regression.
"""
import math

def arch_outline(centre, width, bottom, spring, steps=12):
    """Counterclockwise opening polygon for a round-headed window."""
    r=width/2
    points=[(centre-r,bottom),(centre+r,bottom),(centre+r,spring)]
    points.extend((centre+r*math.cos(math.pi*i/steps),spring+r*math.sin(math.pi*i/steps)) for i in range(1,steps+1))
    return points

def arch_band(centre, width, spring, thickness, steps=12):
    """Concentric intrados/extrados points; callers own the bordering wall."""
    inner=width/2;outer=inner+thickness
    return ([(centre+inner*math.cos(math.pi*i/steps),spring+inner*math.sin(math.pi*i/steps)) for i in range(steps+1)],
            [(centre+outer*math.cos(math.pi*i/steps),spring+outer*math.sin(math.pi*i/steps)) for i in range(steps+1)])
