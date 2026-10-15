# Walking trails — simple HTML version

Updated 15 October 2026. There is **no app.js**.

Open index.html. Near its bottom, the **INSERT THE CHARTS** section contains 13 explicit Vega-Embed calls: 12 main plots and the regional detail map. Each call names its HTML container and readable JSON file.

## Files

- index.html: narrative, controls, direct embeds and the short control section.
- styles.css: layout and presentation.
- charts/: complete specifications, including filters, annotations, responsive settings and reactive map fitting.
- data/: processed input and prepared tables.
- data-bundle.js: generated JSON package for direct-open preview.
- study/: short interview notes and optional commented JSONC copies.

Vega-Embed and the existing custom HTML controls still need a small amount of JavaScript. It is visible together in the HTML. The old 1,165-line commented controller has been replaced with a much shorter inline section, and the regional detail definition has moved into 13_region_detail.json. The parallel coordinates, narratives, in-plot annotations, aligned cards and independent controls remain.

The first three CDN scripts load Vega 5.30.0, Vega-Lite 5.20.1 and Vega-Embed 6.26.0. Chart 06 uses Vega; the others use Vega-Lite. Internet access is needed for those libraries and fonts.

After changing a chart/data JSON file, run `python3 study/rebuild_bundle.py`, then reload. Do not edit the generated bundle manually. JSONC files are study copies, not runnable JSON.

All 12 main plots and regional detail are checked at 1440, 1024 and 390 pixels. Control tests check grade/area filters, metric changes, short-walk presets, zoom, empty results, outlier selection and reset without changing other plots. Desktop and phone figure dimensions are compared with the preceding design. This ZIP does not publish or deploy the site.
