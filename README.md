# Walking the Uneven Map — lecture-style version

Updated **18 October 2026**: enlarged parallel coordinates to fill its card, added two data-based map insights, fixed overlapping waffle cells, and reduced the side space around the two statewide maps.

Open **index.html** with **VS Code Live Server**, as in the Week 7 lecture:

1. Extract this whole ZIP.
2. Open the extracted project folder in VS Code.
3. Right-click index.html and choose **Open with Live Server**.

Internet access is needed for the three Vega libraries and the fonts. Open through Live Server rather than double-clicking the HTML, because the browser must fetch the JSON files.

## The whole setup

```html
<div id="chart-04"></div>
<script>
  vegaEmbed("#chart-04", "charts/04_challenge_heatmap.json", {actions: false, renderer: "svg"});
</script>
```

The three library scripts must load before this call. The actual page repeats this simple call for its 13 charts. There is no app.js, data bundle, custom loader, event handler, View API or JavaScript sizing helper. All charts now use Vega-Lite.

| File | Purpose |
| --- | --- |
| index.html | Story, empty chart containers and 13 embed calls. |
| styles.css | Layout, colours, spacing and phone styles. |
| charts/*.json | Chart instructions and a few built-in dropdowns. |
| data/* | Processed records, boundaries and prepared plotting tables. |
| study/START_HERE.md | Short code explanation. |
| study/INTERVIEW_GUIDE.md | Why each chart was chosen. |
| study/annotated_charts/*.jsonc | Optional study copies with brief comments; not loaded by the website. |

The regional map, supply map, circle map, parallel coordinates and distance strip have simple local controls. Other charts retain hover tooltips. Custom zoom, click selection, presets, resets, counters and linked updates have been removed. Choose All, All Victoria, or None in a dropdown to undo its selection. The regional picker lists areas containing recorded trails.

To edit a chart, change its JSON and reload the page. There is nothing to rebuild. Both axes, value annotations, colour meanings and the narrative remain. The map projection fits its data automatically. Parallel-coordinate positions are prepared data, with raw units labelled on each axis; phones can scroll that plot horizontally.

Checked at desktop, tablet and phone widths. Each remaining control changes one plot only. This package does not publish the website.

## Layout changes on 18 October

On wide screens, each supply/circle map sits beside its description. On phones they stack. CSS grid defines this layout; no JavaScript sizing helper was added. The waffle has a fixed aspect ratio, and its square area is `pow(min(width/14,height/10)*0.86,2)`: use the smaller cell spacing, leave a gap, then square the side length. This prevents cell overlap when the available width and height differ.

## Parallel plot and story refinement

Parallel coordinates uses `width: "container"` and a 460 px height. An outer `.parallel-scroll` element provides horizontal scrolling, while the inner chart has a 960 px minimum width so its four axes remain readable on phones. No JavaScript sizing helper is needed. The map narrative explains the 150/194 short-walk count and the Grade 3 access-filter example (115 trails reduced to four); these are full-snapshot examples, not live counters.
