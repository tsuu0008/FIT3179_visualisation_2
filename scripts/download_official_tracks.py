#!/usr/bin/env python3
"""Download all walking records as WGS84 GeoJSON; fail rather than replace data on errors.

python scripts/download_official_tracks.py /tmp/official-tracks.geojson
The verified project refresh uses the WFS schema in verify_official_sources.py.
This ArcGIS export must be reviewed and adapted before use with that verifier.

After import, regenerate charts and review all narrative figures before publishing.
"""
import json
import pathlib
import sys
import urllib.parse
import urllib.request

SERVICE = 'https://maps.ffm.vic.gov.au/arcgis/rest/services/land_class_use_culture/MapServer/24/query'


def query(params):
    url = SERVICE + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=45) as response:
        result = json.load(response)
    if 'error' in result:
        raise RuntimeError(result['error'])
    return result


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    base = {'where': "W_ACTIVITY='Y'", 'f': 'json'}
    ids = query({**base, 'returnIdsOnly': 'true'}).get('objectIds')
    if not ids:
        raise RuntimeError('No IDs returned; existing project data have not been changed.')
    features = []
    for offset in range(0, len(ids), 100):
        page = query({'objectIds': ','.join(map(str, sorted(ids)[offset:offset+100])),
                      'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'f': 'geojson'})
        if page.get('exceededTransferLimit'):
            raise RuntimeError('Truncated export; existing project data have not been changed.')
        features.extend(page['features'])
    if len(features) != len(ids) or len({f['properties']['OBJECTID'] for f in features}) != len(ids):
        raise RuntimeError('Incomplete or duplicate export; refusing to save.')
    output = pathlib.Path(sys.argv[1])
    output.write_text(json.dumps({'type': 'FeatureCollection', 'features': features}, ensure_ascii=False))
    print(f'Saved {len(features)} official walking records to {output}')


if __name__ == '__main__':
    main()
