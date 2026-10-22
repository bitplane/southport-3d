"""Small-area metric registration. OSM supplies placement, not building design."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
tree = ET.parse(ROOT / 'references/pages/osm-london-square.xml').getroot()
nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in tree.findall('node')}
origin = nodes['250248091']

def metric(p):
    return ((p[1] - origin[1]) * 111320 * math.cos(math.radians(origin[0])),
            (p[0] - origin[0]) * 111132)

parts = {}
for name, wid in [('SW', '342955330'), ('NE', '342955335')]:
    w = tree.find(f"way[@id='{wid}']")
    pts = [metric(nodes[p.get('ref')]) for p in w.findall('nd')][:-1]
    centre = [sum(p[i] for p in pts)/len(pts) for i in range(2)]
    parts[name] = {'osm_way': wid, 'centre_east_north_m': centre, 'survey_polygon_east_north_m': pts}
dx = parts['NE']['centre_east_north_m'][0]-parts['SW']['centre_east_north_m'][0]
dy = parts['NE']['centre_east_north_m'][1]-parts['SW']['centre_east_north_m'][1]
angle = math.atan2(dy, dx)

def local(p):
    return [p[0]*math.cos(angle)+p[1]*math.sin(angle), -p[0]*math.sin(angle)+p[1]*math.cos(angle)]

for p in parts.values():
    p['centre_site_xy_m'] = local(p['centre_east_north_m'])
roads = []
for way in tree.findall('way'):
    tags = {t.get('k'): t.get('v') for t in way.findall('tag')}
    if tags.get('name') in ('London Square', 'Lord Street', 'Nevill Street', 'London Street') and 'highway' in tags:
        pts = [local(metric(nodes[p.get('ref')])) for p in way.findall('nd')]
        roads.append({'osm_way': way.get('id'), 'name': tags['name'], 'points_site_xy_m': pts})
result = {
    'origin_wgs84_lat_lon': origin,
    'origin_source': 'OSM monument node 250248091; approximate registration, not a land survey',
    'reference_iwm_lat_lon': [53.648699530603, -3.004378011723],
    'reference_iwm_offset_east_north_m': metric((53.648699530603, -3.004378011723)),
    'site_x_direction': 'north-east, towards NE colonnade',
    'site_y_direction': 'north-west, towards obelisk salute inscription',
    'site_rotation_from_east_degrees': math.degrees(angle),
    'north_vector_site_xy': [math.sin(angle), math.cos(angle)],
    'colonnades': parts,
    'road_centrelines': roads,
    'source': 'https://api.openstreetmap.org/api/0.6/map?bbox=-3.0065,53.6473,-3.0024,53.6501',
    'attribution': 'Map placement and road data © OpenStreetMap contributors, ODbL 1.0; https://www.openstreetmap.org/copyright',
    'retrieved_utc': '2026-10-21',
    'limitations': 'Local tangent-plane approximation adequate for this 150 m scene. IWM map marker lies about 5.5 m from OSM monument centre. Pavement and road widths need image verification.'
}
(ROOT / 'research/site_layout.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('road_centrelines','colonnades')}, indent=2))
