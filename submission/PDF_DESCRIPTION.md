# Walking the Uneven Map - submission description

## Domain
The visualisation explores walking opportunities in Victoria’s official Recreation Tracks network. It helps readers understand where routes are located and how distance, terrain, walking time and accessibility affect their choice of a walk.

## Why and who
Designed for everyday Victorian walkers, occasional explorers and families, it assumes no statistical or bushwalking expertise. Readers first choose an area, then compare route demands, time and access. Murrindindi has 32 recorded routes, but only seven record full or partial access; all seven are partial. Douglas Reserve Walk (400 metres) and Upper Yarra Walking Track (95 km) share recorded Grade 4, showing why grade alone is insufficient.

## What
The Victorian Government’s Recreation Tracks export retrieved on 23 October 2026 contains 366 records. All 195 marked for walking are included, totalling 875.905 km. Twenty routes are marked FULL CLOSURE, so inclusion does not indicate current availability.

Grade 1–5 are readable labels standardised from the source walking-grade field. Missing values remain Unknown; out-of-range values remain Unclassified. Raw values are retained. The five grade cards summarise observed route counts, median distances and terrain; they do not certify routes against the public walking-grade guide. Published walking-time categories are retained.

Population at 30 June 2025 comes from ABS Regional population 2024–25, Table 2, column D of the LGA workbook. Kilometres per 100,000 residents measures recorded supply relative to population, rather than path use or crowding.

Council geometry comes from the official ABS Local Government Areas 2025 GDA2020 shapefile. Each route is assigned once using its length-weighted midpoint and the full polygons; cross-boundary routes are not split. All 195 assignments were checked, with none changed. Display outlines are simplified by 100 metres in EPSG:3111; original route coordinates are preserved.

## How
All 14 charts and maps use Vega or Vega-Lite. Statewide and regional line maps locate actual paths; the overview supports pan, zoom and named-route selection. A choropleth compares total kilometres with population-adjusted supply. A proportional symbol map uses symbol area for distance and colour and shape for recorded grade. An equal-area grid map counts route midpoints in 25 km squares.

A heatmap compares grade and terrain. Stacked bars compare experience advice across terrain groups. A mosaic uses column width for each terrain group’s kilometre share and block height for its grade mix, so block area represents distance. Reading guides explain both dimensions.

A lollipop chart compares median distances; an individual-distance strip plot shows variation and unusually long routes. Parallel coordinates connect a selected route’s grade, distance, duration and terrain. Readers follow one highlighted route across the columns; category spacing does not measure effort. Long distances use explained square-root spacing. Duration bars count routes by published walking-time category. Connected dots compare council population and supply ranks; line length measures a rank gap, not kilometres or change over time.

A waffle chart shows 15 of 180 access-rated routes with full or partial access: 8.3%, rounded to eight of 100 cells. Fifteen unrated routes are excluded. Partial access may cover only some sections. Four of the 15 full/partial-access routes are marked fully closed in the source snapshot.

The single scrolling story retains its original layout, chart types and consistent grade colours. Annotations explain findings and their significance; circled letters link callouts to marks. Filters update their own chart and annotations. The original sketch is preserved unchanged. The website screenshots break between complete chart cards or paired rows.

## AI acknowledgement
I used OpenAI ChatGPT and Codex to assist with coding, data checks and wording. I reviewed and revised the AI-assisted material and take responsibility for the final content, data interpretations and claims.
