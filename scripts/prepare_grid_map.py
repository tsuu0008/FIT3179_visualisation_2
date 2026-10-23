#!/usr/bin/env python3
"""Count retained trail midpoints in a fixed 25 km equal-area grid.

Uses a spherical Lambert azimuthal equal-area projection centred on 145 E,
37 S (mean Earth radius 6,371,008.8 m). Coordinates in the derived GeoJSON
are projected metres, not longitude/latitude; chart 14 uses an identity
projection with a flipped vertical axis. Original inputs are never written.
"""
import collections
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CELL = 25000
RADIUS = 6371008.8
LON0, LAT0 = map(math.radians, (145, -37))


def project(lon, lat):
    lam, phi = math.radians(lon) - LON0, math.radians(lat)
    k = math.sqrt(2 / (1 + math.sin(LAT0) * math.sin(phi)
                      + math.cos(LAT0) * math.cos(phi) * math.cos(lam)))
    return [RADIUS * k * math.cos(phi) * math.sin(lam),
            RADIUS * k * (math.cos(LAT0) * math.sin(phi)
                          - math.sin(LAT0) * math.cos(phi) * math.cos(lam))]


def project_coordinates(coords):
    if isinstance(coords[0], (int, float)):
        return [round(v, 3) for v in project(*coords[:2])]
    return [project_coordinates(c) for c in coords]


def main():
    raw = (DATA / 'trails.json').read_bytes()
    rows = json.loads(raw)
    groups = collections.defaultdict(list)
    for row in rows:
        x, y = project(row['longitude'], row['latitude'])
        groups[(math.floor(x / CELL), math.floor(y / CELL))].append(row)
    cells = []
    for (column, row), trails in sorted(groups.items()):
        x0, y0 = column * CELL, row * CELL
        count = len(trails)
        areas = collections.Counter(t['lga'] for t in trails)
        cells.append({'cell_id': f'{column}:{row}', 'column': column, 'row': row,
                      'x0': x0, 'x1': x0 + CELL, 'y0': y0, 'y1': y0 + CELL,
                      'cx': x0 + CELL / 2, 'cy': y0 + CELL / 2,
                      'trail_count': count, 'share': count / len(rows),
                      'count_band': '1' if count == 1 else '2–3' if count <= 3 else '4–6' if count <= 6 else '7–13',
                      'trail_km': round(sum(t['length_km'] or 0 for t in trails), 3),
                      'areas': '; '.join(f'{n}: {c}' for n, c in areas.most_common()),
                      'trail_ids': sorted(t['id'] for t in trails)})
    assert sum(c['trail_count'] for c in cells) == len(rows)
    assert sorted(i for c in cells for i in c['trail_ids']) == sorted(t['id'] for t in rows)
    peak = max(cells, key=lambda c: c['trail_count'])
    # The fixed legend is intentionally explicit; review it if the snapshot changes.
    assert peak['trail_count'] <= 13, 'Update the grid legend for a changed snapshot.'
    outline = copy.deepcopy(json.loads((DATA / 'victoria_outline.geojson').read_text()))
    outline['geometry']['coordinates'] = project_coordinates(outline['geometry']['coordinates'])
    outline['properties'] = {'name': 'Victoria', 'coordinate_system': 'Spherical LAEA projected metres'}
    output = {'metadata': {'cell_width_m': CELL, 'cell_area_km2': CELL * CELL / 1e6,
                           'projection': 'Spherical Lambert azimuthal equal-area',
                           'centre_lon_lat': [145, -37], 'earth_radius_m': RADIUS,
                           'source_sha256': hashlib.sha256(raw).hexdigest(),
                           'trail_count': len(rows), 'occupied_cells': len(cells),
                           'peak_cell': peak['cell_id'], 'peak_count': peak['trail_count'],
                           'note': 'One representative midpoint per retained trail. Grid origin is the projection centre; counts depend on the fixed grid size and origin.'},
              'cells': cells, 'outline': [outline]}
    (DATA / 'trail_grid.json').write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(json.dumps(output['metadata'], indent=2))


if __name__ == '__main__':
    main()
