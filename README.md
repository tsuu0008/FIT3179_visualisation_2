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

The overview and shortlist area menus contain 80 council/local-area names from the boundary dataset. They are present in the HTML, so the menu does not wait for a data request to populate. Selecting an area fits all three maps to that area's boundary and updates the shortlist. You can also click a boundary or use the five area shortcuts. The +/− buttons and sliders change map magnification; “Fit selected area” restores its extent, and “Show all Victoria” returns to the statewide view.

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

The overview map includes a zoomed inset of Murrindindi's 32 trails and labels Rubicon Dam Walk at 11.6 km. A dashed boundary links the regional detail to the statewide map. The inset is hidden for unrelated area selections and on narrow screens so it does not cover the main map. Existing area zoom controls remain available on phones.

Grade explanation remains before the first map, Grade remains the leftmost alluvial column, maps retain their enlarged cards, and the repeated alluvial legend stays removed.

Validation: all 12 main charts and the regional inset rendered in Chromium. Highlighting, area filters, inset visibility, empty results and reset were checked. Desktop (1440 px) and phone (390 px) layouts were inspected; no external annotation boxes remain.
