# Sources and reproduction — 25 October 2026

## Walking observations

Victorian Government catalogue: https://discover.data.vic.gov.au/dataset/recreation-tracks

The archived 23 October 2026 WFS export contains 366 records; all 195 records with `w_activity=Y` are retained, including MCG. Full route coordinates and all source observations are unchanged. Codes C1–C6 and the separate value “3” are displayed as published; missing codes are Unknown. Public AWTGS grades are not inferred. Duration charts use the source categories, never estimated numeric hours. Twenty source records state FULL CLOSURE.

Original archive: `data/raw/official_recweb_tracks_20261023.geojson.gz`; record audit: `data/source_audit.json`; processed observations: `data/trails.json` and `data/trails.geojson`.

## Population

ABS Regional population 2024–25: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25

The retained workbook is `data/raw/ABS_LGA_2024-25.xlsx`. All 80 population counts match Table 2, column D, at 30 June 2025. Whole-route kilometres are divided by council population and multiplied by 100,000. This measures supply in this recorded network, not route use or crowding.

## Verified boundaries

ABS Local Government Areas 2025, GDA2020: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/LGA_2025_AUST_GDA2020.zip

Downloaded 25 October 2026. The archive SHA-256, processing CRS, all 80 council joins and all 195 midpoint assignments are recorded in `data/boundary_audit.json`. Full official polygons determine council assignment before simplification; the new boundaries change no retained route assignment. Display polygons are simplified by 100 metres in Victorian Lambert (EPSG:3111), transformed to EPSG:4326 and rounded to six decimal places. Route geometry is never simplified.

Route midpoints retain the documented approximate length-weighted longitude/latitude segment method, scaling longitude by cosine of segment latitude. Each complete route is assigned to the polygon covering its midpoint; cross-boundary routes are not split among councils. The map grid uses one such midpoint per route in fixed 25 km equal-area cells.

## Context and attribution

Parks Victoria’s public Grade 1–5 guide is linked as context only: https://www.parks.vic.gov.au/things-to-do/hiking-and-bushwalking/choose-the-right-hike/how-walking-tracks-are-rated . It is not a code-conversion table.

The overview basemap is © OpenStreetMap contributors: https://www.openstreetmap.org/copyright . Attribution appears beside the map.

## Reproduce

Starting from this retained source snapshot:

```bash
python3 scripts/refresh_boundaries.py /path/to/LGA_2025_AUST_GDA2020.zip
python3 scripts/rebuild_data.py
python3 scripts/prepare_verified_charts.py
python3 scripts/version_assets.py
```

The boundary refresh needs pyshp, shapely and pyproj. Observations and original geometry must be verified against the archived source after any future refresh. Recheck narrative values when the source cohort changes.
