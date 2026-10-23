#!/usr/bin/env python3
"""Import all records marked for walking from a complete official WFS export.

Usage: python scripts/verify_official_sources.py export.geojson abs_population.json
The ABS JSON must contain code/population records extracted from Table 2, column D
of the linked 2024–25 ABS LGA workbook. Full official route geometry is preserved.
Numeric hours are never inferred from categorical duration descriptions.
"""
import collections
import gzip
import hashlib
import json
import pathlib
import re
import sys
from rebuild_data import in_feature, midpoint
from grade_labels import grade_label

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SOURCE = 'https://opendata.maps.vic.gov.au/geoserver/wfs'
DURATIONS = {'SHORT (<1 HOUR)': 'Under 1 hour', 'MEDIUM (1-4 HOURS)': '1–4 hours',
             'DAY (>4 HOURS)': 'Over 4 hours', 'OVERNIGHT': 'Overnight',
             'MULTIPLE DAYS': 'Multiple days'}

def normal(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def main():
    export_path, pop_path = map(pathlib.Path, sys.argv[1:])
    raw = export_path.read_bytes()
    export = json.loads(raw)
    features = export['features']
    assert export['numberMatched'] == export['numberReturned'] == len(features), 'Incomplete WFS export'
    walking = [f for f in features if f['properties'].get('w_activity') == 'Y']
    index = collections.defaultdict(list)
    for f in walking:
        index[normal(f['properties']['name'])].append(f)
    retained = json.loads((DATA / 'trails.json').read_text())
    # Preserve stable IDs for existing records and include every walking record.
    old_by_name = {normal(r['name']): r for r in retained}
    used_ids = {r['id'] for r in retained}
    areas = json.loads((DATA / 'lga.geojson').read_text())['features']
    selected = []
    for f in walking:
        p = f['properties']
        r = old_by_name.get(normal(p['name']))
        if r is None:
            local_id = int(f['id'].rsplit('.', 1)[1])
            if local_id in used_ids:
                local_id = max(used_ids) + 1
            used_ids.add(local_id)
            r = {'id': local_id, 'name': p['name'], 'length_km': float(p['w_distance']),
                 'hours': None, 'gradient': p['w_gradient'] or 'Unknown',
                 'steps': p['w_steps'] or 'Unknown', 'experience': p['w_expert'] or 'Unknown',
                 'access': p['dis_access'].title() if p['dis_access'] else 'Not Recorded',
                 'signage': p['qual_mark'] or 'Unknown', 'track_quality': p['qual_track'] or 'Unknown'}
        selected.append(r)
    retained = sorted(selected, key=lambda r: r['id'])
    cohort_path = DATA / 'raw' / 'study_cohort.json'
    cohort = [{'id': r['id'], 'name': r['name']} for r in retained]
    cohort_path.write_text(json.dumps(cohort, indent=2) + '\n')
    assert len(cohort) == len(retained) == len(walking)
    by_id = {r['id']: r for r in retained}
    comparisons, matches, assignment_changes = [], {}, []
    population = {r['code']: r for r in json.loads(pop_path.read_text())}
    lgas = json.loads((DATA / 'lga_stats.json').read_text())
    pop_comparison = [{'code': r['code'], 'name': r['name'], 'retained': r['population'],
                       'abs_2025': population[r['code']]['population'],
                       'matches': r['population'] == population[r['code']]['population']} for r in lgas]
    assert all(r['matches'] for r in pop_comparison), 'Population mismatch: review before changing observations'
    for c in cohort:
        candidates = index[normal(c['name'])]
        assert len(candidates) == 1, f'Ambiguous source match: {c["name"]}'
        f = candidates[0]
        p = f['properties']
        r = by_id[c['id']]
        assert p['w_distuom'] == 'km' and p['w_timeuom'] == 'h'
        assert p['w_grade'] in [None, '', '3'] + [f'C{i}' for i in range(1, 7)]
        raw_hours = float(p['w_time']) if p['w_time'] not in [None, ''] else None
        comparisons.append({'id': r['id'], 'name': r['name'], 'official_feature_id': f['id'],
            'newly_included': normal(r['name']) not in old_by_name,
            'serial_no': p['serial_no'],
            'distance_matches': r['length_km'] == float(p['w_distance']),
            'terrain_matches': r['gradient'] == (p['w_gradient'] or 'Unknown'),
            'experience_matches': r['experience'] == (p['w_expert'] or 'Unknown'),
            'access_matches': r['access'] == (p['dis_access'].title() if p['dis_access'] else 'Not Recorded'),
            'previous_difficulty_label': r.get('grade', r.get('track_code')),
            'official_track_code': p['w_grade'] or None,
            'previous_hours': r['hours'], 'official_hours': raw_hours,
            'official_duration_category': p['w_durdesc']})
        r.pop('grade', None)
        point = midpoint(f['geometry'])
        council = [a['properties']['name'] for a in areas if in_feature(point, a)]
        assert len(council) == 1, f'Review council assignment: {r["name"]}: {council}'
        if r.get('lga') and r['lga'] != council[0]:
            assignment_changes.append({'name': r['name'], 'previous': r['lga'], 'current': council[0]})
        r.update(track_code=p['w_grade'] or 'Unknown', hours=raw_hours,
            lga=council[0], longitude=round(point[0], 7), latitude=round(point[1], 7),
            duration_group=DURATIONS.get(p['w_durdesc'], 'Not recorded'),
            source_duration=p['w_durdesc'], source_feature_id=f['id'], source_serial_no=p['serial_no'],
            source_track_code=p['w_grade'], source_export_date=p['export_date'],
            closure=p['clos_stat'] or 'Not recorded')
        r['grade'] = grade_label(r['track_code'])
        matches[r['id']] = f
    assert all(all(r[k] for k in ['distance_matches', 'terrain_matches', 'experience_matches', 'access_matches']) for r in comparisons)
    (DATA / 'trails.json').write_text(json.dumps(retained, ensure_ascii=False, indent=2) + '\n')
    geometry = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'geometry': matches[r['id']]['geometry'], 'properties': r.copy()}
        for r in retained]}
    (DATA / 'trails.geojson').write_text(json.dumps(geometry, ensure_ascii=False, separators=(',', ':')) + '\n')
    (DATA / 'raw' / 'official_recweb_tracks_20261023.geojson.gz').write_bytes(gzip.compress(raw, mtime=0))
    (DATA / 'raw' / 'abs_population_2025.json').write_bytes(pop_path.read_bytes())
    report = {'checked_date': '2026-10-23', 'source': SOURCE,
        'source_feature_type': 'open-data-platform:recweb_tracks', 'source_crs': 'EPSG:4326',
        'download_parameters': {'service': 'WFS', 'version': '2.0.0', 'request': 'GetFeature',
            'typeNames': 'open-data-platform:recweb_tracks', 'outputFormat': 'application/json',
            'srsName': 'EPSG:4326', 'count': 1000},
        'raw_sha256': hashlib.sha256(raw).hexdigest(),
        'number_matched': export['numberMatched'], 'number_returned': len(features),
        'official_walking_records': len(walking), 'study_routes': len(retained),
        'selection': "w_activity == 'Y'", 'geometry': 'Full official coordinates without file-level simplification',
        'council_assignment': 'Length-weighted route midpoint inside bundled LGA polygons',
        'changed_council_assignments': assignment_changes,
        'initial_council_corrections': assignment_changes,
        'excluded_walking_records': [{'feature_id': f['id'], 'name': f['properties']['name']}
            for f in walking if normal(f['properties']['name']) not in {normal(r['name']) for r in retained}],
        'population_workbook': '32180DS0002_2024-25.xlsx', 'population_table': 'Table 2',
        'population_column': 'D (ERP at 30 June 2025)', 'population': pop_comparison,
        'trail_comparison': comparisons,
        'limits': ['Source classifications are preserved as published; inclusion is not a quality certification.',
                   'Midpoint assignment places an entire route in one council even when it crosses boundaries.',
                   'Bundled LGA boundary vintage remains unverified.']}
    audit_path = DATA / 'source_audit.json'
    if audit_path.exists():
        previous = json.loads(audit_path.read_text())
        report['initial_council_corrections'] = previous.get('initial_council_corrections', previous.get('changed_council_assignments', [])) or assignment_changes
        if previous.get('raw_sha256') == report['raw_sha256']:
            baseline = {r['id']: r for r in previous['trail_comparison']}
            for r in report['trail_comparison']:
                for key in ['previous_difficulty_label', 'previous_hours', 'newly_included']:
                    if r['id'] in baseline:
                        if key in baseline[r['id']]:
                            r[key] = baseline[r['id']][key]
    audit_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'matched_routes':len(retained),'population_matches':len(pop_comparison),
                      'source_walking_records':len(walking),'excluded':report['excluded_walking_records'],
                      'changed_council_assignments':assignment_changes},indent=2))

if __name__ == '__main__':
    main()
