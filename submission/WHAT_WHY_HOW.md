# Walking the Uneven Map — submission description

## Domain
The visualisation explores walking opportunities in Victoria’s official Recreation Tracks network. It shows where routes are located and how distance, terrain, duration, experience advice and accessibility affect the choice of a walk.

## Why and who
Designed for everyday Victorian walkers, occasional explorers and families, it assumes no statistical or bushwalking expertise. Readers move from choosing an area to comparing route demands, time and access. Murrindindi has 32 recorded routes, but only seven record full or partial access; all seven are partial. Douglas Reserve Walk (400 metres) and Upper Yarra Walking Track (95 km) share source code C4, showing why one classification cannot describe the whole outing.

## What
The Victorian Government’s Recreation Tracks export retrieved on 23 October 2026 contains 366 records. All 195 marked for walking are included, totalling 875.905 km. Twenty routes are marked FULL CLOSURE, so the maps describe the recorded network rather than current availability.

The charts retain the published W_GRADE codes C1–C6 and the separate value “3”. Missing codes are Unknown. No conversion to public Grade 1–5 is made; C6 is a supplied code, not an unclassified record. Published duration categories are used without inferring exact hours.

ABS Regional population 2024–25, Table 2, column D supplies population at 30 June 2025. Combining walking distance with population gives kilometres per 100,000 residents, measuring recorded supply rather than use or crowding.

Council geometry comes from the official ABS Local Government Areas 2025 GDA2020 shapefile, downloaded 25 October 2026. Each route is assigned once using its length-weighted midpoint and the full official polygons. Cross-boundary routes are not split. Display boundaries are simplified by 100 metres in EPSG:3111 and rounded to six decimal places; every official route coordinate is preserved. All 195 council assignments were checked; none changed from the previous version.

## How
All 14 views use Vega or Vega-Lite. Statewide and regional line maps locate actual paths; the overview supports pan, zoom and named-route selection. A choropleth compares total kilometres with population-adjusted supply. A proportional symbol map uses symbol area for distance, and colour and shape for source code. A 25 km equal-area grid counts route midpoints to reveal local clusters.

A heatmap compares code and terrain. Stacked bars show experience advice across terrain groups. A mosaic uses column width for each terrain group’s kilometre share and block height for its code mix; block area therefore represents distance. A lollipop chart compares median distances, while a strip plot reveals individual routes and outliers. Parallel coordinates link a selected route’s code, distance, categorical duration and terrain. Long distances use explained square-root spacing; category spacing is not an effort scale. Duration bars show route counts. Connected dots compare council population and population-adjusted supply ranks.

A waffle chart shows 15 of 180 access-rated routes with full or partial access: 8.3%, rounded to eight of 100 cells. Fifteen unrated routes are excluded. Partial access may cover only some sections.

The single scrolling story uses consistent code colours, reading guides and informative annotations. Filters update their own chart and callouts. The title, main themes and map comparisons follow the original sketch; route profiles, grid and accessibility views extend its central question. The original sketch is preserved unchanged.

## AI acknowledgement
I used OpenAI ChatGPT and Codex to assist with implementation, data checks, visual design and wording. I reviewed and revised the AI-assisted material and take responsibility for the final content, interpretations and claims.
