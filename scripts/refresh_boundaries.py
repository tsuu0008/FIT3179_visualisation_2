#!/usr/bin/env python3
"""Use verified ABS 2025 boundaries; assign midpoints before visual simplification.

Usage: python scripts/refresh_boundaries.py /path/LGA_2025_AUST_GDA2020.zip
Requires pyshp, shapely and pyproj. Published route geometry is never simplified.
"""
import hashlib
import json
import pathlib
import sys
import zipfile
import shapefile
from pyproj import Transformer
from shapely.geometry import Point, shape, mapping
from shapely.ops import transform, unary_union

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
URL = 'https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/LGA_2025_AUST_GDA2020.zip'

def rounded(value):
    if isinstance(value, float): return round(value, 6)
    if isinstance(value, (list, tuple)): return [rounded(x) for x in value]
    if isinstance(value, dict): return {k:rounded(v) for k,v in value.items()}
    return value

def main():
    archive = pathlib.Path(sys.argv[1])
    z = zipfile.ZipFile(archive)
    stem = 'LGA_2025_AUST_GDA2020'
    reader = shapefile.Reader(shp=z.open(stem+'.shp'), shx=z.open(stem+'.shx'), dbf=z.open(stem+'.dbf'))
    to_wgs = Transformer.from_crs(7844, 4326, always_xy=True).transform
    to_metres = Transformer.from_crs(7844, 3111, always_xy=True).transform
    to_map = Transformer.from_crs(3111, 4326, always_xy=True).transform
    previous = json.loads((DATA/'lga.geojson').read_text())
    old = {f['properties']['code']: f['properties'] for f in previous['features']}
    full, features = [], []
    for item in reader.iterShapeRecords():
        record = item.record.as_dict()
        if record['STE_CODE21'] != '2' or record['LGA_CODE25'] not in old:
            continue
        geom = shape(item.shape.__geo_interface__)
        assert geom.is_valid and not geom.is_empty
        full.append((record['LGA_CODE25'], transform(to_wgs, geom)))
        simplified = transform(to_map, transform(to_metres, geom).simplify(100, preserve_topology=True))
        props = dict(old[record['LGA_CODE25']])
        props.update(area_km2=record['AREASQKM'], boundary_year=2025, boundary_source='ABS LGA 2025 GDA2020')
        props['population_density'] = props['population']/props['area_km2']
        features.append({'type':'Feature','properties':props,'geometry':rounded(mapping(simplified))})
    assert len(features) == len(old) == 80
    by_code = {f['properties']['code']:f['properties']['name'] for f in features}
    rows = json.loads((DATA/'trails.json').read_text())
    changes, assignments = [], []
    for row in rows:
        point = Point(row['longitude'], row['latitude'])
        matches = [code for code, geom in full if geom.covers(point)]
        assert len(matches) == 1, (row['name'], matches)
        name = by_code[matches[0]]
        assignments.append({'id':row['id'],'name':row['name'],'lga_code':matches[0],'lga':name})
        if row['lga'] != name:
            changes.append({'id':row['id'],'name':row['name'],'previous':row['lga'],'verified_2025':name})
        row['lga'] = name
    (DATA/'trails.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    routes = json.loads((DATA/'trails.geojson').read_text())
    lookup = {r['id']:r for r in rows}
    for f in routes['features']:
        f['properties'].update(lookup[f['properties']['id']])
    (DATA/'trails.geojson').write_text(json.dumps(routes,ensure_ascii=False,separators=(',',':'))+'\n')
    (DATA/'lga.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n')
    outline = {'type':'Feature','properties':{'name':'Victoria'},'geometry':rounded(mapping(unary_union([shape(f['geometry']) for f in features])))}
    (DATA/'victoria_outline.geojson').write_text(json.dumps(outline,separators=(',',':'))+'\n')
    metadata = {'status':'verified-official-ABS-2025-boundaries','boundary_year':2025,'download':URL,
                'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'checked_date':'2026-10-25',
                'input_crs':'EPSG:7844 (GDA2020)','display_crs':'EPSG:4326',
                'simplification':'100 metres in EPSG:3111, preserve_topology=True; display geometry only, coordinates rounded to 6 decimal places',
                'assignment':'Unsimplified official polygon covering each retained route midpoint',
                'council_count':80,'assigned_routes':len(rows),'assignment_changes':changes}
    (DATA/'boundary_audit.json').write_text(json.dumps({**metadata,'assignments':assignments},ensure_ascii=False,indent=2)+'\n')
    sources = json.loads((DATA/'sources.json').read_text())
    sources['boundaries'] = {**metadata,'source':URL.rsplit('/',1)[0],'method':'scripts/refresh_boundaries.py','audit':'boundary_audit.json'}
    sources['trail_records']['limits'] = ['Whole-route midpoint assignment does not split cross-boundary routes.', 'Source classifications are preserved as published; inclusion is not a quality certification.']
    sources['trail_records']['council_assignment'] = metadata['assignment']
    (DATA/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metadata.items() if k in ['council_count','assigned_routes','assignment_changes']},indent=2))

if __name__ == '__main__':
    main()
