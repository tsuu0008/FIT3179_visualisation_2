# Simple interview guide

## Explain the project

“I use HTML for the story and chart containers, CSS for layout, and Vega/Vega-Lite JSON for chart instructions. Explicit Vega-Embed calls at the bottom of my HTML draw each chart. A short section reads the existing controls and changes one chart's parameters at a time.”

## Understand one call

```js
await vegaEmbed("#chart-04", "charts/04_challenge_heatmap.json", options);
```

- First argument: **where** to draw; matches an HTML id.
- Second argument: **what** to draw; the chart specification.
- options: SVG, export/tooltips and the direct-open data loader.
- await: finish creating this chart before continuing.

Interactive charts save their `.view`, the live object that receives control updates. Static charts do not need a saved variable.

The HTML's first three CDN scripts load Vega, Vega-Lite and Vega-Embed. The JSON's `$schema` URL identifies its grammar; it does not load the drawing library.

## Read JSON in this order

| Key | Meaning |
| --- | --- |
| data | Which records? |
| transform | Which filtering or calculation? |
| mark | Draw rectangles, points, lines, text or geographic shapes? |
| encoding | What controls position, colour, size and text? |
| layer | What is drawn over earlier things? |
| params | Which values can controls change? |
| config | Shared fonts, legends and appearance. |

Chart 06 uses Vega directly: signals, named scales and grouped marks control its parallel axes. The other 12 specification files use Vega-Lite (including the regional detail).

## Each idiom in one sentence

| File | Why it is used | Limitation to recognise |
| --- | --- | --- |
| 01_trail_network | Actual route geography shows where the network lies. | Overlapping lines do not reveal exact trail counts. |
| 02_trail_supply | A choropleth reveals geographic patterns in supply per resident or total length. | Small populations can produce high ratios. |
| 03_trail_symbols | Selectable midpoint circles communicate location, grade and distance. | A midpoint is not necessarily an entrance; symbols overlap. |
| 04_challenge_heatmap | Colour reveals common grade/terrain combinations in a compact grid. | Bars would support more precise magnitude comparisons. |
| 05_median_distance | Aligned dots compare typical distances with less influence from extremes. | A median hides variation; Grade 5 has only two records. |
| 06_parallel_coordinates | One profile traces the same trail across grade, distance, time and terrain. | Lines overlap; slope is not a physical rate or movement. |
| 07_experience_bars | Stacked bars show terrain totals and experience composition in trail counts. | Middle segments have no common baseline. |
| 08_terrain_mosaic | Width and height jointly show kilometre shares by terrain and grade. | More complex than bars; small blocks are harder to read. |
| 09_distance_strip | Individual points reveal distance variation hidden by a median. | Lane offsets only reduce overlaps; they are not another measured attribute. |
| 10_access_waffle | A percentage grid communicates uncommon recorded access. | Cells round the percentage, so exact text is necessary. |
| 11_rank_gap | Connected endpoints show population/supply rank mismatch. | Rank gaps cannot give kilometre differences or ratios. |
| 12_distance_time | A scatterplot shows the relationship between two continuous quantities. | A fitted association is not a causal explanation. |
| 13_region_detail | A local map separates routes that overlap statewide. | Zoom clips geometry while the counter still counts attribute matches. |

## Explain one interaction

1. A reader chooses a grade in the HTML dropdown.
2. The short `connectPlot()` function reads its value.
3. It sends the value to that map's `chosenGrade` signal.
4. The JSON's filter selects matching records.
5. The chart redraws and the counter updates.

```js
view.signal("chosenGrade", grade).runAsync();
```

Say: **“Set this chart's grade parameter, then redraw it.”** Other plots have separate Views. The overview receives no filter updates.

The same small helper handles map, distance and time controls. Supply, regional detail and parallel coordinates have short, separate update functions. Zoom calculations and selected-region layers now live in JSON.

## Important visual meanings

- Route line: geographic shape, not a count or a distance-sized stroke.
- Circle: representative midpoint. Size means symbol area, not radius; its runtime area has a minimum size.
- Heatmap cell: trail count for that category pair.
- Median: middle distance, not the mean.
- Parallel profile: one trail. Missing time has its own lane, not zero hours.
- Stacked bars count trails. Mosaic blocks measure kilometres.
- Mosaic width: terrain share. Height: grade share within that terrain. Area: joint share of included kilometres.
- Waffle: 100 percentage cells; 15 of 179 rated records = about 8.4%, rounded to eight coloured cells.
- Dumbbell: two ranks, with 1 highest. The arrow is a comparison, not a time trend.
- Scatter slope: hours per kilometre. Tooltip distance/time is speed in km/h.

## Why there is still a generated data file

`data-bundle.js` copies the JSON files so the ZIP can open directly without a local server. The short loader reads it, while the embed calls visibly name the readable specifications. Edit JSON, then rebuild the package; do not manually edit the generated file.

`fitSize()` only chooses dimensions and compact legends. Map bounds are prepared data in map_bounds.json, and their reactive projection expressions are inside the map JSON files.

## Interview answer template

“I wanted to show ___. I chose ___ because ___. Position/colour/size represents ___. The JSON implements this using ___. One limitation is ___.”

Example: “I use a heatmap to compare grade/terrain combinations. Position identifies the categories and colour shows count. I aggregate trails by grade and terrain, then draw rectangles and number labels. Bars would be better for precise magnitude comparisons.”

## Be accurate about limitations

The input data is already processed; the original raw-data spatial join is not included. Some annotations and denominators are fixed to this snapshot. Missing fields create different included sets. Dimensions are measured when loading; reload at a new viewport to recalculate them. Label clamping helps clipping but is not a general collision solver.

A small amount of JavaScript is still necessary for Vega-Embed and custom HTML controls. The simpler structure exposes the embed calls and moves the chart definitions into JSON; it does not hide the old application in a different file.
