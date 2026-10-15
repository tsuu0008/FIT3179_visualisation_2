# Walking the Uneven Map — complete website

Updated 14 October 2026.

Unzip this archive and open `index.html`. Data and chart specifications are included in `data-bundle.js`, so a local web server is optional. Internet access is required for the pinned Vega, Vega-Lite, Vega-Embed libraries and fonts. To update GitHub Pages, upload the contents of this folder, including the bundle, scripts, styles, chart specifications and data. Creating this ZIP does not publish the website.

## What changed

- Chart 6 is now parallel coordinates, replacing the alluvial. Each of the 194 trails has a profile across grade, distance, estimated time and terrain. It uses Vega 5; the other 11 charts use Vega-Lite 5.
- Grade selection emphasises its profiles; the trail picker traces a single profile. Two example buttons identify the 48-hour Track Ninety Six and the 95 km Upper Yarra route. The latter has no recorded time.
- Distance and time use square-root scales with raw-unit ticks. Grade and terrain are ordered categories. A labelled grey lane retains missing values separately from zero: 45 missing times, 4 grades and 7 terrain values. There are no inferred zero times or categorical flow widths.
- Map frames follow the geographical aspect rather than filling oversized page rectangles. The fixed overview and regional detail sit side by side on desktop, then stack on narrower screens. Standalone map cards use compact centred widths. Regional boundaries alone are highlighted in the interactive maps.
- Narrative explains the network's geographic scope, the 152 trail midpoints east of 145°E, the difference between route geometries and midpoints, the population denominator, and how to interpret an empty selection. In-plot longest-route labels and outlier annotations remain.
- Each control has a single plot scope. There is no shared global shortlist state.

## Independent controls

| Figure | Controls | Scope |
| --- | --- | --- |
| Victoria overview | Hover only | Static full network |
| Regional detail | Area, grade, area presets, zoom, reset | Regional detail only |
| Supply map | Per-resident / total kilometres, area, reset, click council | Supply map only |
| Parallel coordinates | Grade, trail, outlier examples, reset | Parallel coordinates only |
| Trail circle map | Area, grade, maximum distance, access, presets, zoom, point selection, reset | Trail map only |
| Distance strip plot | Grade, maximum distance, presets, point selection, reset | Distance plot only |
| Time scatterplot | Grade, maximum distance, presets, point selection, reset | Time plot only |

Visible counts show the active conditions. The time plot starts with 149 trails with positive recorded time; the map and distance views can show all 194. Short-walk presets change the distance/time plot ranges so the change is easy to inspect. A selected point is emphasised only in its own figure.

## Other preserved improvements

Grade explanation precedes the first map. Charts 4/5 and 7/8 retain aligned paired cards. The mosaic names terrain shares on its horizontal axis and grade shares on its vertical axis. Annotations sit inside plotting areas, including labelled outliers and values. Data-source references remain in IEEE style at the bottom.

## Validation

All 12 main charts and the regional detail rendered in Chromium without page errors at 1440, 1024 and 390 pixels. Control tests compare every other chart's SVG before and after each action to check isolation. Tests cover regional selection, grade, supply metric, supply area, parallel grade and outlier selection, short-walk presets, an empty Monash map selection and local reset. The parallel chart retains the first axis at the left of its phone scroll container. No page overflow is introduced. Source chart JSON and the embedded bundle are synchronized.
