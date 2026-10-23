#!/usr/bin/env python3
"""Version chart, data, script and stylesheet URLs together.

Run after chart/CSS edits, before publishing. File hashes are deterministic;
original observations and external source URLs are never changed.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    # A new chart can otherwise receive an older cached table with different
    # fields, leaving its geographic background visible but its routes blank.
    data_references = 0

    def version_data(value):
        nonlocal data_references
        if isinstance(value, list):
            return [version_data(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: version_data(item) for key, item in value.items()}
        url = result.get('url')
        if isinstance(url, str):
            parsed = urlsplit(url)
            path = parsed.path
            if not parsed.scheme and not parsed.netloc and path.startswith('data/'):
                source = (ROOT / path).resolve()
                source.relative_to((ROOT / 'data').resolve())
                digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
                result['url'] = path + '?v=' + digest
                data_references += 1
        return result

    for chart in sorted((ROOT / 'charts').glob('*.json')):
        spec = version_data(json.loads(chart.read_text()))
        content = json.dumps(spec, ensure_ascii=False, indent=2) + '\n'
        chart.write_text(content)
        study_copy = ROOT / 'study' / 'annotated_charts' / chart.with_suffix('.jsonc').name
        study_copy.write_text('// Vega-Lite specification with versioned source-data URLs.\n' + content)

    page = ROOT / 'index.html'
    content = page.read_text()

    def version(match):
        path = match.group(1)
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]
        return path + '?v=' + digest

    content, count = re.subn(
        r'(styles\.css|scripts/overview_map\.js|data/trails\.geojson|charts/[A-Za-z0-9_]+\.json)(?:\?v=[A-Za-z0-9_-]+)?',
        version, content)
    page.write_text(content)
    print(f'Versioned {data_references} chart-data references and {count} page assets.')


if __name__ == '__main__':
    main()
