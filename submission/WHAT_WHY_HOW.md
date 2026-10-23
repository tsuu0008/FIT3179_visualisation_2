# Walking the Uneven Map: Victoria’s Forest Trails

**Author:** Tony Su · **Unit:** FIT3179 · **Updated:** 23 October 2026

**Visualisation:** https://tsuu0008.github.io/FIT3179_visualisation_2/

**Original hand-drawn sketch:** https://tsuu0008.github.io/FIT3179_visualisation_2/submission/DV2sketch.pdf

## Domain, audience and purpose

The domain is walking opportunities across Victoria’s promoted forest-trail network. The visualisation is designed for a general Australian audience, particularly people considering a forest walk and readers interested in regional provision. It asks: **how does a large trail network translate into usable choices for different people?**

The story moves from the distribution of routes, to supply relative to population, to the demands of individual walks, and finally to recorded accessibility. This sequence helps readers understand why a statewide distance total does not describe everyone’s local or suitable options. It is a presentation with focused exploration, rather than a live navigation or route-safety service.

## What: data, sources and preparation

The complete official Recreation Tracks WFS export contains 366 records. This final revision includes every record with `w_activity=Y`: all 195 walking records, including MCG. The remaining 171 recreation records are outside the walking filter. This supersedes the earlier 194-record sample.

The complete official route geometry is copied without file-level simplification. Route points are length-weighted midpoints. Each full route is assigned to the council containing its midpoint, using the bundled polygons; crossing routes are counted once rather than divided. This correction moves Upper Yarra Walking Track from the earlier Baw Baw assignment to Yarra Ranges. The bundled polygon vintage remains unverified.

Source codes C1-C6 and MCG's literal value `3` remain separate categories, with 56 codes missing. No conversion to public walking Grades 1-5 is asserted. Source duration categories are used directly. Numeric hours are absent for 194 records, while MCG explicitly records five hours. No exact times are invented from categories.

The final records total 875.905 km with a median of 2.2 km. All 80 bundled population counts match the ABS 2024-25 workbook, Table 2, column D (30 June 2025). Fifteen of 180 access-rated records have full or partial access (8.3%); another 15 are unrated. The repository includes the full compressed official response, original ABS workbook, source hashes and record-level audit.

## Why and how: tasks, idioms, marks and channels

| Reader task | Idiom and encoding | Rationale |
| --- | --- | --- |
| Locate routes and inspect a council | Zoomable statewide Leaflet map and regional Vega-Lite route map; full official line geometry locates paths, with blue/orange showing overview selection and source-code colours in the regional view | Connects the regional pattern to individual routes without presenting representative points as entrances |
| Find concentrations independent of council size | Equal-area bin map; fixed 25 km squares use sequential blue and count labels | Equal-size cells reveal local concentrations that a large council can hide; the grid size, origin and representative-point method are disclosed |
| Compare total and resident-adjusted supply | Choropleth; council polygons use sequential colour, with a measure selector | Contrasts absolute kilometres with kilometres per 100,000 residents on the same geography |
| Compare routes geographically | Proportional-symbol map; symbol area shows distance, colour and shape identify source code | Supports a local shortlist using code and access filters; lettered callouts identify the largest matching cluster and longest route |
| Compare population and supply positions | Dumbbell plot; horizontal position shows rank and a connector shows the difference | Makes mismatches between population centres and resident-adjusted supply easy to identify |
| Examine source code and terrain together | Heatmap; rectangular cells and sequential colour show joint counts | Reveals variation within recorded codes while retaining terrain as a separate attribute |
| Compare typical distances and individual variation | Median lollipop and jittered strip; position shows distance, with direct sample-size labels | Pairs a group summary with the underlying spread, including records without codes |
| Read a route’s combined demands | Parallel coordinates; one line links source code, square-root distance, duration category and terrain | Enables a four-attribute comparison; categorical spacing is explicitly not an effort or elapsed-time scale |
| Compare terrain and experience advice | Stacked bars; length counts trails and sections show experience categories | Shows the preparation advice associated with different terrain |
| Compare the network’s physical composition | Mosaic; width is terrain’s kilometre share, height is the source-code mix and rectangle area represents kilometres | Contrasts the heatmap’s route counts with distance-weighted composition |
| Relate distance to source duration categories | Boxplots; horizontal position shows distance, the box spans the middle half and the centre line shows the median | Uses the source’s categorical timing information without inventing exact durations |
| Understand recorded accessibility | Waffle; a 100-cell grid rounds 15/180 to eight coloured cells | Communicates the small rated share, with the exact fraction and excluded unrated records stated alongside it |

The four geographic idioms, heatmap, parallel coordinates, mosaic, waffle and boxplot provide nine candidate advanced idiom types. There are 14 displayed views (one Leaflet overview and 13 Vega-Lite specifications); treating the statewide and regional route maps as one repeated idiom leaves 13 chart views. Final rubric classification remains the teaching team’s decision.

## Interaction, layout and storytelling

The website is one scrollable page with four numbered chapters. Overview zoom, pan, route search and popups, regional selection, map-measure switching, source-code/access filters, route selection and tooltips support specific comparisons. Each control affects its own chart, while surrounding narrative reports the full study set or named examples. Responsive rows stack on smaller laptop screens.

The overview uses blue network lines and an orange selected route over OpenStreetMap. Other views use consistent categorical source-code colours and textual labels; numeric counts and supply use sequential colour. Matching A/B badges connect the symbol-map annotations to their explanations. Reading notes explain the less familiar encodings, transformed scales, missing-value lanes and denominators.

## Relationship to the submitted sketch

The original hand-drawn sketch is preserved without redrawing it. Its title, Victoria overview and regional detail, population-adjusted supply section, population-versus-supply rank comparison, demanding-short-walk theme, conclusion and references remain recognisable in the final page.

The grid map develops the sketch’s uneven-distribution theme. Parallel coordinates and the distance/duration comparison develop its short-walk theme. The accessibility chapter adds a final test of usability. Source checking replaced unsupported public-grade labels and numeric time estimates with recorded categories. The final revision adds the omitted MCG record, full route geometry, a zoomable basemap overview and reproducible midpoint council assignment. These changes preserve the original question while making the evidence and its limits more explicit.

## Sources and AI acknowledgement

1. DEECA / Victorian Government, *Recreation Tracks*, WFS feature type `open-data-platform:recweb_tracks`: https://opendata.maps.vic.gov.au/geoserver/wfs?service=WFS&request=GetCapabilities . Dataset catalogue: https://discover.data.vic.gov.au/dataset/recreation-tracks . ArcGIS field reference: https://maps.ffm.vic.gov.au/arcgis/rest/services/land_class_use_culture/MapServer/24 .
2. ABS, *Regional population, 2024–25*: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25 . Workbook: `32180DS0002_2024-25.xlsx`, Table 2, column D.
3. ABS, *Digital boundary files, ASGS Edition 3*: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files . The retained boundary vintage remains unverified.
4. Parks Victoria, *How walking tracks are rated*: https://www.parks.vic.gov.au/things-to-do/hiking-and-bushwalking/choose-the-right-hike/how-walking-tracks-are-rated . Contextual public-grade guidance, not a mapping for the source codes.

Generative AI assisted with implementation, text editing, visual-design development and source comparisons. The author is responsible for reviewing the code, evidence and final submission. This text is supplied for transfer into the unit’s submission template; it is not represented as the official template itself.
