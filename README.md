# Walking the Uneven Map

An interactive FIT3179 Data Visualisation 2 project about Victoria's promoted state-forest walking trails.

## Run locally

Serve this folder with a local web server. For example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Publish with GitHub Pages

1. Upload everything in this folder to the root of a public GitHub repository.
2. Open **Settings → Pages**.
3. Select **Deploy from a branch**, choose `main` and `/ (root)`, then save.
4. Test the published URL in an incognito window.

## Project structure

- `index.html` — single-page visual story
- `styles.css` — responsive page styling
- `app.js` — loads the chart specifications
- `charts/` — 12 human-readable chart specifications (11 Vega-Lite and one Vega alluvial)
- `data/` — processed data files used by the charts

## Data sources

- Victorian Government, [Recreation Tracks](https://discover.data.vic.gov.au/dataset/recreation-tracks), supplied dataset snapshot.
- Australian Bureau of Statistics, [Regional population 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25), released 31 March 2026.

## Important scope limitation

The Victorian recreation dataset represents promoted tracks managed mainly in State Forest. It does not contain every urban path, national-park walk or informal trail in Victoria. Each trail is assigned to the LGA containing its midpoint for this visualisation.

## AI acknowledgement

Generative AI was used to assist with code, editing and design development. The author remains responsible for checking the data transformations, claims and final submission.

## Story and connected views

The page follows one question: how do location, walking demands and recorded accessibility shape usable trail choices?

1. Place: the route network leads into per-resident supply and the population–supply rank comparison.
2. Demands: grades, distances, alluvial combinations, terrain and experience describe different aspects of difficulty.
3. Shortlist: one set of grade, local government area, maximum distance and access filters updates the individual-trail map, distance view and time comparison. Clicking a trail or choosing its name highlights it across those views. Reset restores the full shortlist.
4. Access: the story returns to the whole network, explains the accessibility denominator and connects that constraint back to the shortlist.

The distance view includes unknown-grade trails. The time view excludes records without a positive time estimate; its count is stated beside the filters. Full-network summary statistics and chapter comparisons remain fixed when the shortlist changes.

Sources appear as numbered in-text citations with linked IEEE-style references at the bottom. The original supplied dataset snapshot is retained; the source-page access date does not imply that the data was downloaded again.

## Area exploration and map zoom

The overview and shortlist area menus contain 80 council/local-area names from the boundary dataset. They are present in the HTML, so the menu does not wait for a data request to populate. Selecting an area fits the detail inset, supply map and shortlist map to that area's boundary; the large overview keeps the state extent and outlines the selection. You can also click a boundary or use the five area shortcuts. The +/− buttons and sliders change map magnification; “Fit selected area” restores its extent, and “Show all Victoria” returns to the statewide view.

The geographic units are councils/local government areas, not suburbs. Some areas contain no promoted forest tracks in this dataset; an empty shortlist is reported explicitly. Full-network narrative summaries remain fixed.

`data-bundle.js` includes every chart specification and dataset used by the app. Runtime chart data is embedded in memory, so opening `index.html` directly does not require fetching local JSON files. An internet connection is still needed for the Vega libraries and web fonts. Keep the `charts/` and `data/` folders for source inspection.

When updating GitHub Pages, upload all files, including `data-bundle.js`, `app.js`, `index.html` and `styles.css`. The page uses versioned script and stylesheet links to reduce stale browser-cache problems.

## Alluvial diagram update — 14 October 2026

Chart 6 now follows Grade → Distance → Estimated time → Steps → Signage. Grade is the first column and identifies the ribbon colours; no separate legend is repeated below the chart. Ribbon width encodes counts of trails with the same complete combination, not median normalised values. All 194 trails are retained across 99 distinct combinations, with missing values as Unknown. Every column totals 194; 45 trails have no recorded time estimate.

Use the dropdown or click a grade label to highlight a grade. Hover a ribbon for its full combination and trail count. Double-click to reset. This chart describes the full network and is independent of shortlist filters. It uses Vega v5; the other charts use Vega-Lite. Both are supported by vegaEmbed. The matching source JSON and embedded data-bundle entry have been updated together.

This archive contains the complete website, all 12 chart specifications, all original processed data and the updated bundle. Unzip and open `index.html`, or upload the contents of this folder to the existing GitHub Pages repository. Internet access is required for the Vega libraries and fonts. The live website has not been changed by creating this archive.

The walking-grade explanation now appears before the first route map, so the colour meanings are introduced before any grade-coloured map or chart.

## Annotations inside the plots — 14 October 2026

External annotation boxes have been removed. The narrative and reading instructions remain above each figure. Data annotations now sit within the plotting area: labelled and ringed outliers, a leader pointing to the 69-trail heatmap cell, median sample sizes, a highlighted Grade 3 alluvial node with its count and percentage, a 48-trail label inside its experience bar, a terrain value and percentage within the mosaic, a filtered short-distance count and outlier in the strip plot, an access callout connected to the highlighted waffle squares, rank mismatch labels and a regression slope annotation.

The overview map's inset follows the selected area, zoom and grade. Its title states the matching trail count, and a labelled ring identifies the longest matching trail. The main map outlines only the selected region, with Victoria outlined for the statewide selection. On phones the detail panel is placed below the overview within the same chart card.

Grade explanation remains before the first map, Grade remains the leftmost alluvial column, maps retain their enlarged cards, and the repeated alluvial legend stays removed.

Validation: all 12 main charts and the regional inset rendered in Chromium. Highlighting, area filters, inset visibility, empty results and reset were checked. Desktop (1440 px) and phone (390 px) layouts were inspected; no external annotation boxes remain.

## Detail-map controls — 14 October 2026

The first large map remains a fixed Victoria overview. Area selection changes its outline only; the small map fits the selected area and follows the zoom controls. Selecting Victoria outlines the state instead of automatically highlighting Murrindindi. The grade legend filters the detail map while leaving the main route network visible. The inset title and longest-trail annotation follow its current area and grade; empty selections are stated within the map. The detail panel appears below the overview on phones so its controls remain useful.

The Victoria outline is a display outline dissolved from the existing simplified LGA boundaries; it is used only for drawing selection borders, not assigning trails or calculating statistics. Labels have white halos and space between their leader lines and text.

Verification: main overview geometry stayed unchanged through area, zoom and grade changes. Selecting Grade 3 showed 115 trails in the detail map; reset restored Victoria and 194 trails. The selected outline was verified as one Victoria feature or the chosen council, and an empty Monash selection displayed its in-map message. All 12 main charts and the inset rendered at desktop and phone widths.

## Aligned terrain and distance comparison

The heatmap and median-distance cards share their text and plot tracks on desktop, giving them matching top/bottom edges and aligned plotting starts. Both plotting areas are 360 units high. The heatmap legend sits within its empty upper-left cells, and the median chart uses a tighter axis range with enough room for the two-line Grade 5 annotation. On narrow screens the cards stack normally.

Verified aligned card edges and plot starts at 1440 px and 1024 px, and no page overflow at 390 px. All 12 charts rendered successfully.

## Mosaic chart axes

Chart 8 labels all five terrain categories on the x-axis. Its title explains that column width represents the share of recorded kilometres. The y-axis is labelled Grade share within each terrain (%) with ticks from 0% to 100%. Rotated terrain labels are retained for every column. Source JSON and the offline data bundle match. All 12 charts and the map controls were verified in Chromium, including the phone layout.
