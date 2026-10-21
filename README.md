# Walking the Uneven Map — annotated revision

Updated **21 October 2026** (map and interaction refinement). All 13 Vega-Lite charts include direct explanatory annotations. Grade colours are blue, amber, teal, magenta and charcoal; point charts also use distinct symbols. Smaller screens scroll each plotting surface horizontally to preserve readable labels.

Open `index.html` with **VS Code Live Server**. The site remains buildless HTML, CSS and Vega-Lite JSON specifications. No bundler or custom chart event handler is required.

## Data status

**The 194 existing trail observations were retained. This is not a fresh official-data download.** The official layer and ABS source/download links were checked, but export requests failed in the editing environment. Original trail extraction history and the bundled boundary vintage remain unverified. See [source instructions](study/DATA_SOURCES.md) and [machine-readable status](data/sources.json).

Derived tables were rebuilt reproducibly from the retained inputs. Mosaic group distances retain full precision; rounding occurs in displayed labels only. The exact trail-distance sum is 871.905 km and the median is 2.15 km; headline display rounds those to 872 km and 2.2 km.

```bash
python scripts/rebuild_data.py
```

The downloader and importer can retrieve and process a complete official WGS84 trail export in an environment with access to the service. Review updated annotation values, chart domains, dropdowns and narrative claims before publishing a changed observation dataset.

## Main files

| File | Purpose |
| --- | --- |
| index.html | Narrative, grade guide, source references and 13 embed calls. |
| styles.css | Layout, chart scroll surfaces and responsive styles. |
| charts/*.json | Displayed Vega-Lite specifications, controls and annotations. |
| data/* | Retained observations/geometry, rebuilt plotting tables, sources and statistics. |
| scripts/rebuild_data.py | Reproducible plotting-table derivations and optional official GeoJSON import. |
| scripts/download_official_tracks.py | Complete official walking-track export using batched IDs. |
| study/DATA_SOURCES.md | Exact source links, verification limits and refresh instructions. |
| study/DATA_AND_CAVEATS.md | Denominators, encodings, annotation and verification notes. |
| study/annotated_charts/*.jsonc | Study copies matching the actual displayed charts. |

Local chart controls affect their own plot. Returning to All/All Victoria/None clears the corresponding selection. The surrounding narrative describes the retained snapshot.

## Map and selection refinement

- Full-width overview and additional explanation inside the supply map.
- Gridlines on the rank comparison; heatmap leader ends at the cell border.
- Map annotation bands keep text clear of routes and boundaries. Regional pointers identify an outlined LGA using a geometry-derived interior anchor. Local trail pointers sit on displayed route geometry.
- Parallel coordinates has a visible grade legend, all 194 named trail choices, Longest matching, and grade/area/time filters with live counts and empty-state messages.
- `scripts/prepare_map_annotations.py` prepares geographic label anchors and map frames, and runs during the data rebuild.
