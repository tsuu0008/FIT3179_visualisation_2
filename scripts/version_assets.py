#!/usr/bin/env python3
"""Version chart and stylesheet URLs so browsers request changed assets.

Run after chart/CSS edits, before publishing. File hashes are deterministic;
original observations and external source URLs are never changed.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
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
    print(f'Versioned {count} local chart/stylesheet references.')


if __name__ == '__main__':
    main()
