# Walking the Uneven Map — annotated revision

Updated **23 October 2026** (criteria and readability refinement). All 14 Vega-Lite views include direct explanatory annotations. Grade colours are blue, amber, teal, magenta and charcoal; point charts also use distinct symbols. Laptop layouts resize plots and stack comparison cards to keep labels visible without horizontal scrolling.

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
| index.html | Narrative, grade guide, source references and 14 embed calls. |
| styles.css | Layout, chart sizing and responsive styles. |
| charts/*.json | Displayed Vega-Lite specifications, controls and annotations. |
| data/* | Retained observations/geometry, rebuilt plotting tables, sources and statistics. |
| scripts/rebuild_data.py | Reproducible plotting-table derivations and optional official GeoJSON import. |
| scripts/download_official_tracks.py | Complete official walking-track export using batched IDs. |
| study/DATA_SOURCES.md | Exact source links, verification limits and refresh instructions. |
| study/DATA_AND_CAVEATS.md | Denominators, encodings, annotation and verification notes. |
| study/annotated_charts/*.jsonc | Study copies matching the actual displayed charts. |

Local chart controls affect their own plot. Returning to All/All Victoria/None clears the corresponding selection. The surrounding narrative describes the retained snapshot.

## Map and selection refinement

- Equal-width statewide and regional overview panels; concise explanation balanced with the supply map, plus a compact coverage-and-legend footer.
- Full-width rank comparison with a 1–31 rank range, gridlines and direct row annotations; heatmap leader ends at the cell border.
- Unboxed map annotations keep text clear of routes and light council boundaries. The final map groups its callouts to the right of its grade and distance legends, using matching numbered geographic markers instead of long leader lines. Regional pointers identify an LGA using a geometry-derived interior anchor; the final symbol map highlights the actual council polygon. Local trail pointers sit on displayed route geometry.
- Parallel coordinates has a visible grade legend, all 194 named trail choices, Longest matching, and grade/area/time filters with live counts and empty-state messages.
- `scripts/prepare_map_annotations.py` prepares geographic label anchors and map frames, and runs during the data rebuild.

## Criteria refinement

A fixed 25 km equal-area grid adds a fourth geographic idiom: counts of trail midpoints in equal-size cells. It contains all 194 retained trails across 65 occupied cells, with 13 in the busiest cell. Run `python scripts/prepare_grid_map.py` to rebuild this derived file; the original inputs are not changed.

Reading instructions explain the more complex encodings beside their charts. Annotations interpret highlighted patterns, and the access panel states both the rated denominator and rounding. The first overview stays in equal-width panels on desktop. Browser checks at 1280 px and 1024 px found all 14 views visible without horizontal plot overflow or text clipped by their SVG frames.

See [criteria review](study/CRITERIA_CHECK.md) for the idiom inventory and remaining submission responsibilities.

## Visible bin grid and balanced comparison cards

The square bin map now draws the complete 25 km grid over land, with a pale zero-recorded category and darker occupied bins. The grid is clipped to the existing Victoria outline; trail assignments and counts are unchanged. A compact side-by-side narrative and map replaces the previous full-width map card. Paired comparison cards share text and chart rows, matching their top and bottom edges on desktop; narrow screens stack them.
