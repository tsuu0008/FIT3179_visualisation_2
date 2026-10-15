# The simple version

There is no app.js. Open **index.html**, search for **INSERT THE CHARTS**, and read the explicit Vega-Embed calls.

```html
<div id="chart-04" class="chart"></div>
```

```js
await vegaEmbed("#chart-04", "charts/04_challenge_heatmap.json", options);
```

This means: **draw this JSON chart inside this HTML container**.

| File | Job |
| --- | --- |
| index.html | Story, chart containers, explicit embeds and a short control section. |
| styles.css | Colours, fonts, card sizes and responsive layout. |
| charts/*.json | Data, transforms, marks, encodings, parameters and annotations. |
| data/* | Records, geometry and prepared tables. |
| data-bundle.js | Generated copy of JSON inputs for direct-open preview. |

Vega-Embed and the custom HTML controls still require a small amount of JavaScript. The HTML control section sends values to one chart's parameters; drawing and filtering definitions now live in the JSON. The regional detail has its own file, **13_region_detail.json**.

Read **INTERVIEW_GUIDE.md** next. Commented study copies of all 13 specifications are in **annotated_charts/**; they are not loaded by the website.

After editing a chart or data JSON file, run:

```bash
python3 study/rebuild_bundle.py
```

Then reload the page. Internet access is needed for the three visualisation libraries and fonts.
