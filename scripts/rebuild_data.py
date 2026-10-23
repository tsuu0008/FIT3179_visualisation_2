#!/usr/bin/env python3
"""Rebuild plotting tables from the retained snapshot, or import an official WGS84 export.

python scripts/rebuild_data.py
python scripts/verify_official_sources.py export.geojson abs_population.json

Official source refresh is owned by verify_official_sources.py. This script
only derives plotting tables and never invents numeric durations or grades.
"""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import math
import pathlib
import re
import statistics
from grade_labels import GRADES, grade_label

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CODES = [f'C{i}' for i in range(1, 7)] + ['3', 'Unknown']
DURATIONS = ['Under 1 hour', '1–4 hours', 'Over 4 hours', 'Overnight', 'Multiple days']
TERRAINS = ['Flat', 'Gentle hills', 'Short steep hills', 'Very steep', 'Very steep and difficult']
SERVICE = 'https://maps.ffm.vic.gov.au/arcgis/rest/services/land_class_use_culture/MapServer/24'


def read(name):
    return json.loads((DATA / name).read_text())


def write(name, obj):
    options = {'separators': (',', ':')} if name.endswith('.geojson') or name == 'map_regions.json' else {'indent': 2}
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, **options) + '\n')


def number(value):
    try:
        n = float(str(value).replace(',', '').strip())
        return n if math.isfinite(n) and n >= 0 else None
    except (ValueError, TypeError):
        return None


def unit_value(value, unit, kind):
    n = number(value)
    if n is None or (kind == 'time' and n == 0):
        return None
    unit = str(unit or '').strip().lower()
    units = {'distance': {'km': 1, 'kms': 1, 'kilometres': 1, 'm': .001, 'metres': .001},
             'time': {'hr': 1, 'hrs': 1, 'h': 1, 'hours': 1, 'min': 1/60, 'mins': 1/60,
                      'minutes': 1/60, 'day': 24, 'days': 24, 'd': 24}}
    if unit not in units[kind]:
        raise ValueError(f'Unrecognised {kind} unit {unit!r}; review the raw export before importing.')
    return n * units[kind][unit]


def midpoint(geom):
    lines = geom['coordinates'] if geom['type'] == 'MultiLineString' else [geom['coordinates']]
    segments = [(a, b, math.hypot((b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2)), b[1]-a[1]))
                for line in lines for a, b in zip(line, line[1:])]
    target = sum(s[2] for s in segments)/2
    for a, b, length in segments:
        if target <= length and length:
            t = target/length
            return [a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])]
        target -= length
    raise ValueError('Empty route geometry')


def in_ring(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:]+ring[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside = not inside
    return inside


def in_feature(point, feature):
    g = feature['geometry']
    polygons = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    return any(in_ring(point, poly[0]) and not any(in_ring(point, hole) for hole in poly[1:]) for poly in polygons)


def normal(value, fallback='Unknown'):
    s = str(value or '').strip()
    return s if s else fallback



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()
    lgas = read('lga.geojson')
    provenance = read('sources.json') if (DATA / 'sources.json').exists() else {}
    rows = read('trails.json')
    for row in rows:
        row['grade'] = grade_label(row['track_code'])
    write('trails.json', rows)
    assert len({r['id'] for r in rows}) == len(rows), 'Duplicate IDs'
    assert all(r['track_code'] in CODES for r in rows)
    grouped = collections.defaultdict(list)
    for r in rows:
        grouped[r['lga']].append(r)
    stats = []
    for f in lgas['features']:
        p = f['properties']
        trails = grouped.pop(p['name'], [])
        km = sum(r['length_km'] or 0 for r in trails)
        p.update(trail_count=len(trails), trail_km=round(km, 3),
                 trail_km_per_100k=round(km/p['population']*100000, 3) if p['population'] else None)
        stats.append({k: p.get(k) for k in ['code','name','population','area_km2','population_density',
                                          'population_growth','trail_count','trail_km','trail_km_per_100k']})
    assert not grouped, f'Unmatched LGAs: {list(grouped)}'
    positive = [s for s in stats if s['trail_count']]
    for field, key in [('population', 'population_rank'), ('trail_km_per_100k', 'supply_rank')]:
        for rank, s in enumerate(sorted(positive, key=lambda r: (-(r[field] or 0), r['name'])), 1):
            s[key] = rank
    write('lga.geojson', lgas)
    write('lga_stats.json', stats)
    outline = read('victoria_outline.geojson')
    write('map_regions.json', {'type': 'FeatureCollection', 'features': lgas['features']+[outline]})
    old_labels = {r['id']: r.get('short_name', r['name']) for r in read('trail_labels.json')}
    labels = []
    for r in rows:
        group = [t for t in rows if t['lga'] == r['lga']]
        middle = (min(t['longitude'] for t in group) + max(t['longitude'] for t in group))/2
        align = 'right' if r['longitude'] >= middle else 'left'
        labels.append({**r, 'short_name': old_labels.get(r['id'], r['name']),
                       'annotation_align': align, 'annotation_dx': -12 if align == 'right' else 12})
    write('trail_labels.json', labels)
    max_km = max(r['length_km'] or 0 for r in rows)
    max_hours = max(r['hours'] or 0 for r in rows)
    parallel = []
    for r in rows:
        positions = [(int(r['grade'][-1])-1)*25 if r['grade'].startswith('Grade ') else -30 if r['grade']=='Unclassified' else -15,
                     100*math.sqrt(r['length_km']/max_km) if r['length_km'] is not None else -15,
                     DURATIONS.index(r['duration_group'])*25 if r['duration_group'] in DURATIONS else -15,
                     TERRAINS.index(r['gradient'])*25 if r['gradient'] in TERRAINS else -15]
        annotation = r['name']+'\n'+f"{r['length_km']:g} km · "+r['duration_group']
        for axis, position in enumerate(positions):
            parallel.append({**{k: r[k] for k in ['id','name','grade','track_code','length_km','hours','duration_group','gradient','lga','closure']},
                             'axis': axis, 'position': round(position, 5), 'annotation': annotation})
    write('parallel_points.json', parallel)
    points = []
    for grade in GRADES:
        group = sorted([r for r in rows if r['grade'] == grade], key=lambda r: (r['length_km'] or 0, r['id']))
        for i, r in enumerate(group):
            points.append({**r, 'lane': (i % 5)-2})
    write('distance_points.json', points)
    groups = collections.defaultdict(float)
    for r in rows:
        if r['grade'] != 'Unknown' and r['gradient'] in TERRAINS and r['length_km'] is not None:
            groups[(r['gradient'], r['grade'])] += r['length_km']
    total = sum(groups.values())
    mosaic, left = [], 0
    for terrain in TERRAINS:
        terrain_total = sum(v for (t, g), v in groups.items() if t == terrain)
        if not terrain_total:
            continue
        right, bottom = left+terrain_total/total, 0
        for grade in GRADES[:-1]:
            km = groups.get((terrain, grade), 0)
            if km:
                top = bottom+km/terrain_total
                mosaic.append({'gradient':terrain,'grade':grade,'km':round(km, 6),
                               'x0':left,'x1':right,'y0':bottom,'y1':top})
                bottom = top
        left = right
    write('mosaic.json', mosaic)
    accessible = sum(r['access'] in ['Full','Partial'] for r in rows)
    rated = sum(r['access'] in ['Full','Partial','None'] for r in rows)
    cells = round(accessible/rated*100) if rated else 0
    write('access_waffle.json', [{'cell':i+1,'column':i%10,'row':i//10,
                                'status':'Full or partial access' if i<cells else 'No disabled access'} for i in range(100)])
    lengths = [r['length_km'] for r in rows if r['length_km'] is not None]
    summary = {'trail_count':len(rows),'total_km':round(sum(lengths),3),'median_km':round(statistics.median(lengths),6),
               'coded_pct':round(sum(r['track_code']!='Unknown' for r in rows)/len(rows)*100),
               'accessible_count':accessible,'rated_count':rated,'access_pct':accessible/rated*100,
               'positive_time_count':sum(bool(r['hours']) for r in rows),'mosaic_km':round(total,6),
               'closed_count':sum('clos' in r['closure'].lower() and 'no closure' not in r['closure'].lower() for r in rows)}
    write('stats.json', summary)
    provenance['derived_tables'] = {'status':'rebuilt-after-official-attribute-check',
                                    'method':'scripts/rebuild_data.py','totals':summary}
    provenance['trail_records']['retained_file_sha256'] = {
        name: hashlib.sha256((DATA/name).read_bytes()).hexdigest()
        for name in ['trails.json','trails.geojson']}
    provenance['trail_records']['public_grades'] = (
        'Display-label normalisation only: C1-C5 become Grade 1-5; numeric 3 joins Grade 3; '
        'C6 is Unclassified; missing values are Unknown. Raw fields are unchanged. '
        'This does not independently certify equivalence to public AWTGS grades.')
    write('sources.json', provenance)
    from prepare_map_annotations import main as prepare_annotation_geometry
    prepare_annotation_geometry()
    from prepare_grid_map import main as prepare_grid
    prepare_grid()
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
