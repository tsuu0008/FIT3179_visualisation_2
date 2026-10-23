# Walking the Uneven Map

Victoria walking-track visualisation by Tony Su, FIT3179. Updated 23 October 2026.

- [Live website](https://tsuu0008.github.io/FIT3179_visualisation_2/)
- [Original hand-drawn sketch](submission/DV2sketch.pdf)
- [What / Why / How submission description](submission/WHAT_WHY_HOW.md)
- [Source verification](study/DATA_SOURCES.md)

## Coverage and corrections

All **195 records marked for walking** in the official Recreation Tracks export are included, including MCG. The full recreation dataset has 366 records; 171 are not marked for walking. The previous 194-route sample has been superseded.

The first map uses Leaflet, OpenStreetMap basemap tiles and full official route coordinates. Zoom, pan, select a named route or click a line to inspect its path. Blue shows all routes; orange identifies the selected route. The regional route map uses the same official geometry. Thirteen additional Vega-Lite views compare place, supply, route demands and access.

The source codes C1-C6 and MCG's literal value `3` remain separate categories. No public walking grade is inferred. Duration comparisons use source categories; 194 records have no numeric hours and MCG records five hours. Fifteen of 180 access-rated routes record full or partial access (8.3%); 15 are unrated.

Route points are calculated from official geometry using a length-weighted midpoint. Councils are assigned using that midpoint and the bundled polygons. Upper Yarra Walking Track therefore moves from its old Baw Baw assignment to Yarra Ranges. Council boundary vintage remains unverified; a crossing route is counted once rather than split by boundary.

## Preview and reproduce

Serve this directory with VS Code Live Server or `python3 -m http.server 8765`, then open http://localhost:8765/ . Basemap tiles and chart/map libraries need internet access. No build step is required.

```bash
python3 scripts/verify_official_sources.py official_export.geojson data/raw/abs_population_2025.json
python3 scripts/rebuild_data.py
python3 scripts/prepare_verified_charts.py
python3 scripts/version_assets.py
```

The archived official export is `data/raw/official_recweb_tracks_20261023.geojson.gz`; decompress it to obtain `official_export.geojson`. The verifier checks the full response, source units, unique names, existing comparison attributes and all 80 ABS population values. The audit stores the source response hash and record-level evidence. `scripts/overview_map.js` implements the first map; the remaining displayed charts are in `charts/`.

Run the versioning step after data or chart edits. It versions data URLs inside every chart before versioning the page's chart URLs, so a cached table cannot be mixed with a newer specification.

The original two-page sketch is copied unchanged to its submission link. Transfer the prepared description into the unit's official submission template after review. This local revision does not itself publish or submit the work.
