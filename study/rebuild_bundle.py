#!/usr/bin/env python3
"""Pack the readable JSON inputs for direct-open preview. No data processing."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
bundle = {}
for folder in ["charts", "data"]:
    for path in sorted((root / folder).iterdir()):
        if path.suffix in [".json", ".geojson"]:
            bundle[path.relative_to(root).as_posix()] = json.loads(path.read_text())

output = root / "data-bundle.js"
output.write_text(
    "/* Generated JSON package for direct-open preview. */\nwindow.TRAIL_BUNDLE = "
    + json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n"
)
print("Updated data-bundle.js. Reload the page.")
