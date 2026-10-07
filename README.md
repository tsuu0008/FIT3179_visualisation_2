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
- `charts/` — 12 human-readable Vega-Lite JSON specifications
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
2. Demands: grades, distances, combined profiles, terrain and experience describe different aspects of difficulty.
3. Shortlist: one set of grade, local government area, maximum distance and access filters updates the individual-trail map, distance view and time comparison. Clicking a trail or choosing its name highlights it across those views. Reset restores the full shortlist.
4. Access: the story returns to the whole network, explains the accessibility denominator and connects that constraint back to the shortlist.

The distance view includes unknown-grade trails. The time view excludes records without a positive time estimate; its count is stated beside the filters. Full-network summary statistics and chapter comparisons remain fixed when the shortlist changes.

Sources appear as numbered in-text citations with linked IEEE-style references at the bottom. The original supplied dataset snapshot is retained; the source-page access date does not imply that the data was downloaded again.

## Area exploration and map zoom

The overview and shortlist area menus contain 80 council/local-area names from the boundary dataset. They are present in the HTML, so the menu does not wait for a data request to populate. Selecting an area fits all three maps to that area's boundary and updates the shortlist. You can also click a boundary or use the five area shortcuts. The +/− buttons and sliders change map magnification; “Fit selected area” restores its extent, and “Show all Victoria” returns to the statewide view.

The geographic units are councils/local government areas, not suburbs. Some areas contain no promoted forest tracks in this dataset; an empty shortlist is reported explicitly. Full-network narrative summaries remain fixed.

`data-bundle.js` includes every chart specification and dataset used by the app. Runtime chart data is embedded in memory, so opening `index.html` directly does not require fetching local JSON files. An internet connection is still needed for the Vega libraries and web fonts. Keep the `charts/` and `data/` folders for source inspection.

When updating GitHub Pages, upload all files, including `data-bundle.js`, `app.js`, `index.html` and `styles.css`. The page uses versioned script and stylesheet links to reduce stale browser-cache problems.
