"""Use the shared metric bollard controls for reduced representations."""
from southport3d.street import furniture


def street_furniture(name, settings, asset_directory):
    if set(settings) != {'kind', 'level'} or settings['kind'] != 'bollard':
        raise ValueError('Expected the explicit bollard kind and viewing level')
    return furniture(settings['kind'], settings['level'], name).finish([])
