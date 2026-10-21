# Data sources and verification — 21 October 2026

The website still uses its retained 194 trail observations. This revision rebuilds plotting tables from those inputs; **it is not a fresh official-data download**. Requests to the official export endpoint failed in the editing environment. No original download date or complete match against the official observations can be certified.

| Input | Official source | Verification status |
| --- | --- | --- |
| Walking routes and attributes | [DEECA State Forest Recreation Tracks, layer 24](https://maps.ffm.vic.gov.au/arcgis/rest/services/land_class_use_culture/MapServer/24) | Layer and relevant field definitions confirmed; retained observations and geometry not fully compared. |
| Population at 30 June 2025 | [ABS Regional population, 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | Publication and LGA workbook link confirmed; retained population values not compared against the workbook. |
| LGA boundaries | [ABS Digital boundary files, Edition 3](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files) | A 2025 shapefile is available. The bundled geometry's vintage remains unknown. |
| Grade explanations | [Parks Victoria, How walking tracks are rated](https://www.parks.vic.gov.au/things-to-do/hiking-and-bushwalking/choose-the-right-hike/how-walking-tracks-are-rated) | Explanatory reference, not an observation dataset. |

The old DataVic dataset URL returned 404 when opened. The references now link to the official ArcGIS service instead. A source link alone does not establish that the existing file was downloaded from it.

## Direct official downloads

- [Population estimates and components by LGA, 2024 to 2025 — XLSX](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0002_2024-25.xlsx)
- [2025 LGA boundaries, GDA2020 — ZIP](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/LGA_2025_AUST_GDA2020.zip)
- [Trail query form](https://maps.ffm.vic.gov.au/arcgis/rest/services/land_class_use_culture/MapServer/24/query): set Where to `W_ACTIVITY='Y'`, Out Fields to `*`, Return Geometry to `true`, Out Spatial Reference to `4326`, and Format to `GeoJSON`. Confirm the response is complete rather than a truncated first page.

The official trail fields are `NAME`, `W_ACTIVITY`, `W_DISTANCE`, `W_DISTUOM`, `W_GRADE`, `W_GRADIENT`, `W_EXPERT`, `W_TIME`, `W_TIMEUOM`, and `DIS_ACCESS`. Distances and durations must be interpreted with their unit fields; missing duration is not zero.

## Reproduce the current derived tables

From the project directory, with Python 3:

```bash
python scripts/rebuild_data.py
```

This recalculates regional kilometre totals, per-resident supply and ranks, exact mosaic areas, parallel-coordinate positions, strip offsets, waffle cells and summary statistics. It retains the existing trail observations, population and boundary geometry. The mosaic now retains exact group sums instead of storing rounded numbers as measurements. Strip offsets only separate overlapping marks; they are not observations.

## Import a complete official trail export

```bash
python scripts/download_official_tracks.py /tmp/official-tracks.geojson
python scripts/rebuild_data.py --official-trails /tmp/official-tracks.geojson
```

Alternatively, download GeoJSON manually using the query form and pass its path to the second command. The downloader retrieves IDs first and then batches them, checks completeness, and stops on errors. An import retains the original export and its SHA-256 digest, records the import time, converts known units, assigns route midpoints to the retained LGA geometry, and rejects ambiguous spatial assignments or unrecognised units/categories. The import time is not a publication or observation date.

An official trail import does not verify or refresh population or boundaries. Match the ABS workbook to LGA codes and record the chosen boundary vintage separately before treating the entire project as verified.

**After any observation update, review chart annotations, fixed scale domains, dropdown options, and narrative statistics before publishing.** The present chart annotations describe the retained snapshot; these are intentionally not labelled as live-data findings.

See [sources.json](../data/sources.json) for machine-readable status. The original raw-data processing and simplification history remain unavailable.
