# Walking the Uneven Map: Finding a Walk in Victoria

**Author:** Tony Su · **Unit:** FIT3179 · **Updated:** 23 October 2026

**Website:** https://tsuu0008.github.io/FIT3179_visualisation_2/

**Original hand-drawn sketch:** https://tsuu0008.github.io/FIT3179_visualisation_2/submission/DV2sketch.pdf

This description is prepared for transfer into the unit’s official submission template.

## Domain, who and why

The domain is walking opportunities in Victoria’s published Recreation Tracks network. The audience is everyday Victorian walkers, occasional explorers and families, including groups with different experience and access needs. No statistical or bushwalking expertise is assumed.

The central question is: **what turns a line on a map into a walk that fits your day and the people coming along?** A free afternoon connects four decisions: find a place, understand the walk’s demands, fit the available time, and consider access. Murrindindi’s 32 routes become seven with recorded partial access; two Grade 4 walks, Douglas Reserve Walk and Upper Yarra Walking Track, show how the same grade can cover very different time commitments. The ending returns to the opening question.

## What: data and preparation

The Victorian Government’s Recreation Tracks export, retrieved on 23 October 2026, contains 366 recreation records. All 195 marked for walking are included: 875.905 km in total. Route attributes describe distance, grade, terrain, duration, experience and access. The source also marks 20 routes as fully closed; the page describes the recorded network, not current availability.

Australian Bureau of Statistics population estimates at 30 June 2025 provide a second source. Population and trail distance are combined by council to calculate kilometres per 100,000 residents, allowing comparisons between places of different population sizes.

Full official route coordinates and raw classifications are retained. C1–C5 display as Grade 1–5; numeric 3 joins Grade 3, C6 remains Unclassified, and missing grades remain Unknown. These display labels do not independently certify equivalence to public walking grades. Duration uses published categories, without invented exact times.

A length-weighted route midpoint assigns each whole route to one council. Cross-boundary routes are counted once. The retained council-boundary vintage remains unverified. Fifteen of 180 access-rated routes record full or partial access; 15 unrated routes are excluded from the 8.3% figure. The repository retains the source export, population workbook, hashes and record-level audit.

## How: tasks and design choices

| Reader task | Idioms, marks and channels | Why this helps |
| --- | --- | --- |
| Find an area and inspect a route | Statewide and regional line maps; projected coordinates locate paths, colour shows selection or grade | Links regional patterns to actual route shapes. The overview supports pan, zoom and named-route focus. |
| Find local concentrations | Equal-area grid map; fixed 25 km squares use sequential blue and count labels | Shows clusters without giving larger councils more visual weight. Each route contributes one midpoint. |
| Compare walking opportunities beside different populations | Choropleth and rank comparison; colour encodes kilometres or kilometres per resident, aligned positions show ranks | Reveals that the largest network and highest per-resident provision can have different leaders. |
| Compare possible walks geographically | Sized-symbol map; symbol area encodes distance, colour and shape encode grade | Grade/access filters narrow the possibilities while circled A/B notes identify the largest matching council group and longest route. |
| Understand physical demands | Grade/terrain heatmap, experience stacked bars and distance-weighted mosaic | Counts reveal common combinations; the mosaic’s column width and block area reveal their kilometre contributions. |
| Compare distance and time | Median lollipop, distance strip, parallel coordinates and duration bars | Pairs group summaries with individual routes. A selected profile joins grade, distance, duration and terrain; duration bars retain ordinary counts. |
| Understand recorded access | Waffle chart; eight of 100 cells represent the rounded 8.3% share | Makes the small documented starting list visible while printing the exact 15-of-180 fraction. |

There are 14 views, using Vega or Vega-Lite. Repeated statewide/regional route maps count as one idiom. Four map types, heatmap, parallel coordinates, mosaic and waffle provide eight candidate advanced idioms; final classification belongs to the teaching team. JSON specifications are linked from the page.

The four numbered chapters form one scrolling presentation. Informative chart annotations state a finding and its significance; reading guides explain unfamiliar encodings. Grade colours remain consistent, and paired annotation references use circled A/B badges. Long distances use explained square-root spacing in the strip/profile views. Category spacing is not an effort scale. Filters update their own chart; static narrative describes the full network or named examples. Laptop layouts fit without horizontal page scrolling.

## Sketch, sources and acknowledgement

The original hand-drawn sketch is preserved unchanged. The title, grade guide, overview/detail maps, population comparison, demanding-short-walk theme, conclusion and references remain recognisable. The grid, route profiles and access chapter develop that same walking-opportunity question.

- [Victorian Government Recreation Tracks](https://discover.data.vic.gov.au/dataset/recreation-tracks): route observations and geometry.
- [ABS Regional population, 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25): Table 2, column D of the LGA workbook.
- [ABS digital boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files): boundary reference; retained vintage is unverified.
- [Parks Victoria walking grades](https://www.parks.vic.gov.au/things-to-do/hiking-and-bushwalking/choose-the-right-hike/how-walking-tracks-are-rated): public grade-guide context.
- [OpenStreetMap contributors](https://www.openstreetmap.org/copyright): overview basemap, attributed beside the map.

Generative AI assisted with implementation, text editing, design development and source comparisons. The author is responsible for reviewing the final work and submission. Reproduction and audit details are in `study/DATA_SOURCES.md`.
