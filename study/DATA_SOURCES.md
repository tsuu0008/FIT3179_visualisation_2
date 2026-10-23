# Sources and reproducibility - 23 October 2026

## Official walking records

Catalogue: https://discover.data.vic.gov.au/dataset/recreation-tracks . DataVic lists a last update of 23 October 2026 and daily updates.

Endpoint: https://opendata.maps.vic.gov.au/geoserver/wfs . Query: `service=WFS`, `version=2.0.0`, `request=GetFeature`, `typeNames=open-data-platform:recweb_tracks`, `outputFormat=application/json`, `srsName=EPSG:4326`, `count=1000`.

The complete response contains 366 recreation records. Every record with `w_activity=Y` is included: **195 walking records**, including MCG. No walking record is excluded. The previous 194-route sample is superseded. Source classifications are preserved as published; inclusion is not a data-quality certification.

Full official geometry is copied without file-level simplification. The first map uses Vega with an OpenStreetMap basemap so its route linework can be inspected by zooming. The blue network and orange selected route do not encode difficulty. Other charts use documented display-grade categories.

Display labels normalise C1–C5 to Grade 1–5 and the numeric value `3` to Grade 3. C6 is shown as Unclassified; absent values are Unknown. The raw fields remain unchanged. This presentation rule is not an independent certification of equivalence to public AWTGS grades. The five-card public-grade guide is contextual guidance from Parks Victoria. Numeric hours are missing for 194 records; MCG records five hours. All duration comparisons use the actual categories, without inferring hours from a category.

Route midpoints use an approximate length-weighted calculation on longitude/latitude segments, with longitude scaled by cosine of segment latitude. Each full route is assigned once to the bundled council polygon containing its midpoint. This reproducible rule moves Upper Yarra Walking Track from the old Baw Baw assignment to Yarra Ranges. Routes crossing council boundaries are not split. The bundled polygon vintage remains unverified.

The compressed raw response, source hash, processed records and full route geometry are preserved in `data/raw/official_recweb_tracks_20261023.geojson.gz`, `data/source_audit.json`, `data/trails.json` and `data/trails.geojson`.

## Population and basemap

ABS publication: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25 . Workbook: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0002_2024-25.xlsx . All 80 bundled resident counts match Table 2, column D (30 June 2025). The original workbook and extracted counts are preserved under `data/raw/`. Area, density and growth values are not separately certified by that count comparison.

Council boundary source: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files . This reference does not establish the vintage of the bundled polygons.

Basemap: https://www.openstreetmap.org/copyright . Standard HTTPS tile requests use the browser cache, visible attribution and normal browser referrer; no tile bulk download or prefetch is implemented. Vega: https://vega.github.io/vega/ . Basemap content and route data have separate sources.

## Reproduce

Decompress the official archive to `official_export.geojson`, then run:

```bash
python3 scripts/verify_official_sources.py official_export.geojson data/raw/abs_population_2025.json
python3 scripts/rebuild_data.py
python3 scripts/prepare_verified_charts.py
python3 scripts/version_assets.py
```

The legacy ArcGIS downloader is an optional alternative utility. The verifier expects the documented lower-case WFS schema. Check any future source changes before publishing, and update the narrative if totals or categories change.
