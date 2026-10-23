# Interview guide

## A short introduction

“My project examines the location, difficulty and recorded accessibility of 194 Victorian walking trails. HTML holds the story, CSS controls the layout, and Vega-Lite JSON describes the charts. One Vega-Embed call inserts each chart into its HTML container.”

## Why each chart is here

| Chart | Why I chose it | Main code idea |
| --- | --- | --- |
| 01 Route map | Show the actual network's geography. | geoshape boundaries and route lines; colour = grade. |
| 02 Supply map | Compare supply across areas. | geoshape fill colour = km per resident or total km. |
| 03 Circle map | Compare location, distance and grade together. | longitude/latitude position, size = km, colour = grade. |
| 04 Heatmap | Find common grade/terrain combinations. | aggregate count, rect marks, text values. |
| 05 Median distance | Compare the typical distance in each grade. | aggregate median, rule + point + text. |
| 06 Parallel coordinates | Follow one trail across four attributes. | prepared axis positions, grouped line marks, one highlighted example. |
| 07 Stacked bars | Compare trail counts and experience requirements. | count trails and stack bars by experience. |
| 08 Mosaic | Compare kilometre shares across terrain and grade. | prepared x0/x1/y0/y1 rectangle coordinates. |
| 09 Distance strip | Show variation hidden by a median. | one circle per trail; x = distance, y = grade, offset = lane. |
| 10 Waffle | Make a small access percentage easy to see. | 100 prepared cells; eight coloured cells approximate 8.4%. |
| 11 Dumbbell | Show the gap between two rankings. | rule joins population/supply ranks; two coloured endpoints. |
| 12 Scatterplot | Show distance/time relationships and outliers. | x/y quantitative positions, regression line and labels. |
| 13 Regional detail | Separate routes that overlap statewide. | filter by area; fit the projection to the remaining shapes. |
| 14 Equal-area grid map | Reveal local concentrations without unequal council sizes. | project midpoints to equal-area coordinates; bin into 25 km squares; colour = trail count. |

## One interaction to explain

The distance strip has this parameter:

```json
"params": [{
  "name": "chosenGrade",
  "value": "All",
  "bind": {"input": "select", "options": ["All", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Unknown"]}
}]
```

Its transform uses:

```json
{"filter": "chosenGrade === 'All' || datum.grade === chosenGrade"}
```

Say: **“The dropdown changes chosenGrade. The filter keeps every row when All is selected, or keeps rows with the selected grade. Vega-Lite redraws this plot automatically.”**

- `datum` means the current data row.
- `===` means equal to.
- `||` means OR; `&&` means AND.
- Each JSON file has separate parameters, so its dropdown affects only that chart.

No custom JavaScript controls or zoom handlers are involved. The fixed overview has no filter. The small regional map has its own area dropdown.

## A few meanings to remember

- A median is the middle value. Grade 5's 21 km median comes from only two trails.
- In the circle map, symbol area increases with distance, with a minimum size for visibility. A midpoint is not an entrance.
- In parallel coordinates, each line is one trail, not a journey. Grade/terrain are ordered categories; equal gaps do not mean equal effort.
- Distance/time positions in parallel coordinates are prepared using square roots. Tick labels show raw km/hours. Missing values have a separate grey lane, never zero.
- The strip also uses a square-root distance axis. Its vertical offsets separate dots; they are not another measured variable.
- Stacked bars count trails. Mosaic blocks measure kilometres: width = terrain share, height = grade share within that terrain, area = their combined share.
- Access is 15/179 rated trails = 8.4%. Fifteen more trails have no rating and are excluded. The waffle rounds to eight cells.
- A rank gap is not a kilometre gap. A scatterplot association is not proof of a cause.

## A useful answer structure

“I wanted to show ___. I chose ___ because ___. Position/colour/size represents ___. In the JSON, ___ implements it. One limitation is ___.”

Example: “I wanted to find common grade/terrain combinations. A heatmap uses two categorical axes and colour for count. I group and count records, draw rectangles, then add number labels. Colour is less precise than aligned bars, so the numbers help.”

The supplied inputs are already processed. Do not claim the website performs the original cleaning or spatial boundary assignment. The full dataset has 194 trails; only 149 have positive recorded times, so the time plot has a different denominator.


## Explaining the new map

“Council totals depend on council size. A fixed 25 km equal-area grid compares equally sized locations. Each trail contributes its representative midpoint once, giving 194 trails in 65 occupied cells. The busiest cell contains 13 trails, all assigned to Murrindindi. The orange outline identifies that exact cell. The short numbered pointer links it to the explanation above the map.”

The preprocessing uses a spherical Lambert azimuthal equal-area projection centred on 145°E, 37°S. Vega uses an identity projection with the same scale and translation as the rectangle axes. Grid size and origin affect counts. Midpoints are not entrances; empty cells do not establish that no walks exist there. Source observations have not been refreshed.
