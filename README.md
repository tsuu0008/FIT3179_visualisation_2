# Walking the Uneven Map

Victoria walking-track visualisation by Tony Su, FIT3179. Updated 23 October 2026.

- [Live website](https://tsuu0008.github.io/FIT3179_visualisation_2/)
- [Original hand-drawn sketch](submission/DV2sketch.pdf)
- [What / Why / How submission description](submission/WHAT_WHY_HOW.md)
- [Source verification](study/DATA_SOURCES.md)

## Coverage and corrections

All **195 records marked for walking** in the official Recreation Tracks export are included, including MCG. The full recreation dataset has 366 records; 171 are not marked for walking. The previous 194-route sample has been superseded.

The first map uses Vega, OpenStreetMap basemap tiles and full official route coordinates. Zoom, pan, select a named route or hover over a line to inspect its path. Blue shows all routes; orange identifies the selected route. The regional route map uses the same official geometry. Thirteen additional Vega-Lite views compare place, supply, route demands and access.

The charts display the published walking codes C1–C6 and the separate source value “3” unchanged. Missing values are Unknown. C6 is retained as a supplied classification, and “3” is not merged with C3. No equivalence to public AWTGS grades is assumed. Terrain, experience, duration and accessibility provide the interpretable route attributes.

Route points are calculated from official geometry using a length-weighted midpoint. Councils are assigned using that midpoint and the bundled polygons. Upper Yarra Walking Track therefore moves from its old Baw Baw assignment to Yarra Ranges. Official ABS 2025 Local Government Area polygons are used; full polygons determine midpoint assignment and display copies are simplified by 100 metres.

## Preview and reproduce

Serve this directory with VS Code Live Server or `python3 -m http.server 8765`, then open http://localhost:8765/ . Basemap tiles and chart/map libraries need internet access. No build step is required.

```bash
python3 scripts/verify_official_sources.py official_export.geojson data/raw/abs_population_2025.json
python3 scripts/rebuild_data.py
python3 scripts/prepare_verified_charts.py
python3 scripts/version_assets.py
```

The archived official export is `data/raw/official_recweb_tracks_20261023.geojson.gz`; decompress it to obtain `official_export.geojson`. The verifier checks the full response, source units, unique names, existing comparison attributes and all 80 ABS population values. The audit stores the source response hash and record-level evidence. `scripts/prepare_overview_map.py` builds the first Vega map and `scripts/overview_map.js` connects its controls; the remaining displayed charts are in `charts/`.

Run the versioning step after data or chart edits. It versions data URLs inside every chart before versioning the page's chart URLs, so a cached table cannot be mixed with a newer specification.

The original two-page sketch is copied unchanged to its submission link. Transfer the prepared description into the unit's official submission template after review. This local revision does not itself publish or submit the work.

The revised page restores the five-classification guide, a four-chapter story, finding-led captions, transitions and direct chart annotations. The regional map sits beside its explanation and keeps a visible grade legend. Duration is presented as simple labelled category counts. All 14 displayed views use Vega or Vega-Lite.

Every displayed chart includes an on-chart finding and its significance. See the [annotation inventory](study/ANNOTATIONS.md) for the maxima, minima, contrasts, missingness and geographic gaps highlighted. Filtered annotations follow the current selection.

The [full criteria review](study/CRITERIA_CHECK.md) records current evidence and remaining submission priorities. Readable chart specifications are linked from the page's methods section. All source-marked routes remain included, including 20 marked FULL CLOSURE; recorded status is exposed during route inspection. Removing a redundant state-outline layer reduces runtime data downloads without changing route geometry.
