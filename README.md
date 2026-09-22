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

- Victorian Government, [Recreation Tracks](https://discover.data.vic.gov.au/dataset/recreation-tracks), updated 20 September 2026.
- Australian Bureau of Statistics, [Regional population 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/latest-release), released 31 March 2026.

## Important scope limitation

The Victorian recreation dataset represents promoted tracks managed mainly in State Forest. It does not contain every urban path, national-park walk or informal trail in Victoria. Each trail is assigned to the LGA containing its midpoint for this visualisation.

## AI acknowledgement

Generative AI was used to assist with code, editing and design development. The author remains responsible for checking the data transformations, claims and final submission.
