# Data and caveats

| Item | Meaning |
| --- | --- |
| trails.json | 194 records: name/id, length_km, hours, grade, gradient, experience, access, assigned area and representative coordinates. |
| trails.geojson | Actual route geometry and metadata. |
| lga.geojson | 80 boundary features including the unincorporated area; source of population/supply fields. |
| map_regions.json | Area features plus the Victoria outline; used for the regional detail boundary. |
| trail_labels.json | Trail records with shorter names for map annotations; original names remain in tooltips. |
| parallel_points.json | Four prepared rows per trail (776 total), with an axis number and display position; original values remain in tooltips. |
| distance_points.json | Trail records with precomputed lane offsets for the strip plot. |
| mosaic.json | Prepared rectangle coordinates and rounded kilometre labels. |
| lga_stats.json | Prepared area totals and ranks. |
| access_waffle.json | 100 prepared percentage cells. |

The browser starts from processed data. Current plotting-table derivations are included in `scripts/rebuild_data.py`; the original raw-data cleaning, simplification and boundary assignment history remains unavailable. `data/sources.json` explicitly distinguishes verified source pages from retained observations whose lineage is unverified. Official export requests failed during this revision. No new official snapshot is claimed. See `DATA_SOURCES.md` for download links and import instructions. The supplied lga attribute uses a route midpoint assignment; a route can cross boundaries.

## Denominators

- All trails: 194; exact distance sum 871.905 km (headline 872 km), median 2.15 km (headline 2.2 km).
- Grades 1–5: 4, 42, 115, 27, 2 records; Unknown: 4.
- Positive recorded times: 149; missing time: 45.
- Missing terrain: 7.
- Heatmap: 186 records with known grade and terrain.
- Experience bars: 187 records with known terrain and experience.
- Mosaic: both block measurements and coordinates are now rebuilt from the exact 853.805 km with known grade and terrain. Labels round only at display time. This is not the full-network denominator.
- Access: 2 Full + 13 Partial = 15, among 179 rated records. Another 15 have no rating. 100 waffle cells round the share to eight highlighted cells.
- Rank comparison: ranks among 31 positive-trail areas; 18 most populous are displayed.
- At or below 5 km: 150 of 194 trails initially.

The mosaic excludes both unknown terrain and unknown grade. Per-block rounding explains small differences between printed totals and precise rectangle areas.

## Simple local interactions

The regional detail has an area dropdown; the supply map has a measure dropdown; the circle map has grade/access controls; the strip has a grade dropdown; parallel coordinates has an example-trail dropdown. The overview and time chart remain fixed. Each control affects one chart. The regional dropdown includes areas with recorded trails.

Parallel-coordinate prepared positions are 100 × sqrt(km/95), 100 × sqrt(hours/48), 25 × (grade−1), and 25 × terrain index (flat=0, difficult=4). Missing values use −15, below the valid range. Raw-unit axis labels use the same conversions. These display positions are not additional measurements. These conversions are reproduced by scripts/rebuild_data.py when preparing parallel_points.json; the website reads the resulting values.

## Snapshot-specific and perceptual limits

Some count denominators, the 69-trail heatmap note, named outliers, mosaic total and 15/179 label are fixed to this snapshot. Replacing the dataset requires reviewing them. Grade 5 has only two records. Recorded durations are estimates. Mercator is not equal-area, and the browser does not calculate geographic statistics from its displayed polygons.

Square-root axes keep short routes distinguishable but make spacing nonlinear. Grade/terrain are ordered categories with no equal-effort interpretation. Rank gaps lose underlying magnitudes. Colour consistency is provided, but no formal colour-vision evaluation is claimed. Annotations use fixed positions and offsets; they do not use an automatic collision solver.


## Direct annotations and grade accessibility

All 13 chart specifications now include a highlighted feature plus an explanatory label inside the plotting area. Map callouts use pointer lines or matching numbered area/trail highlights. Filtered chart labels recompute from the matching records; empty selections do not retain a stale trail label. Static regional findings describe the retained snapshot.

Grades use blue (#0072B2), amber (#E69F00), teal (#009E73), magenta (#CC79A7) and charcoal (#252525), with unknown in grey. Point charts add different symbols; axes, guide cards and tooltips retain grade numbers. This uses several colours from the Okabe–Ito palette plus charcoal, and avoids a red–green opposing pair. It is not a guarantee for every colour-vision condition; direct labels and shape redundancy carry meaning independently. Sequential colour remains appropriate for numeric supply and heatmap counts.

Callouts have a readable minimum plotting width. Small screens scroll the individual chart horizontally rather than shrinking or overlapping its annotations. Figures were rendered with Vega-Lite 5.20.1 and Vega 5.30.0 at the actual minimum plotting widths; grade/access and region selections were evaluated. Full browser layout QA was unavailable.

## Map and selection refinements

The statewide overview and local detail map occupy equal-width columns on desktop and stack below 900 px. The statewide plot uses a 530 px height and its regional detail uses 440 px so the geography fills the two panels. The supply map places the ratio explanation in its northeast corner and pairs the coverage note with the colour scale in a compact footer. Its 520 px height avoids a separate, distant legend row. The rank plot fills the available horizontal space using a 0–32 domain around the observed ranks 1–31, with vertical rank guides and horizontal row guides. Highlighted-row explanations sit directly above their connectors. The concise supply-map narrative explains population normalisation and dataset coverage. The heatmap leader stops at the highlighted cell's left border, and counts render above leader rules.

The proportional-symbol map pairs its grade and distance legends on the lower left with numbered explanatory callouts on the lower right. Number 1 labels the shaded council polygon; number 2 identifies the exact plotted longest-trail symbol. The latter has a ring sized from the same distance encoding to surround the full symbol. Its geographic content is fitted above this footer. The local detail map retains unboxed callouts above its geography. Leader lines avoid annotation text. Murrindindi is explicitly labelled as an LGA; general council borders remain quiet, while selected areas have a separate fill or outline. Region pointers use a geometry-derived interior point, rather than an average of trail coordinates or a guessed location. Local trail pointers use a nearest point on the displayed route geometry, not an entrance. `scripts/prepare_map_annotations.py` reproduces these anchors and projection frames and is called by the data rebuild. The two anchor tables are derived display aids, not additional observations.

Parallel coordinates now has a persistent six-entry grade legend, 194 named trail choices plus None and Longest matching, and filters for grade, recorded LGA and known/missing time. A live count describes the matching records. If a selected named trail is outside the filters, the chart explains that; empty filters produce an explicit message. The selected time label is positioned on the opposite side of the incoming profile segment.

Validation: all 81 regional anchors were checked inside their polygons; all 194 route anchors were checked on their displayed route lines. All 194 named parallel-coordinate choices and 44 grade/area/time/empty filter states were evaluated. All 46 map filter/area states were checked for separated callout text, leader-to-marker alignment and leader endpoints at the annotation band. Map labels and the heatmap leader were visually inspected in rendered SVGs. Full browser layout QA remains unavailable.

Map refinements: council borders use thin, light strokes behind the trail marks; the northern overview callout has a reserved top margin. The symbol map uses numbered, unboxed callouts beside its legends; the regional detail map keeps them above its geography. Grade legends on route and parallel-coordinate charts use solid circles.

Final symbol-map callouts: 28 grade/access/width combinations were checked for complete labels, separated notes, matching numbered geographic markers and absence of leader lines. The regional count now highlights the entire matching council polygon; the route circle remains centred on the exact selected point.

The distance–time scatterplot uses short vertical pointer lines. Track Ninety Six’s note sits above its highlighted point, and Great Dividing Trail’s note sits below its point. Both notes share their point’s horizontal anchor. Each pointer meets the ring edge and leaves a small gap before the annotation text; the pointers remain on their respective sides of the dashed regression line. The point data and fitted trend are unchanged.

Supply-map area highlights use orange strokes over a wider white casing for contrast against both ends of the teal colour scale. The symbol map uses stronger base boundaries and fully opaque trail symbols, shades the selected council polygon, and sizes the longest-route ring to contain the selected symbol.

The distance strip reserves an annotation band above its grade rows. Adaptive left/right alignment keeps the longest-walk label clear of grade labels for every grade selection, and the 5 km guide stays below that band. Its distance domain extends to 105 km to leave room around the 95 km highlight. The median-distance chart uses a compact 290 px height, a 0–28 km distance axis and a 480 px minimum width so it fits its comparison card.

Chart heights are sized individually to their mark density. Compact heatmap, parallel-coordinate, experience, mosaic, strip, waffle and rank plots reduce unused space. Map narratives align at the top, controls sit above each SVG, and comparison cards keep their own content height. Data files and source attribution are unchanged.

The challenge heatmap fits the actual card width rather than enforcing the shared 620 px minimum. Its terrain labels wrap, all five grade columns stay visible, and a reserved annotation band keeps the callout out of the data cells.

The shortlist map has a larger 680 px plotting specification and a wider desktop column beside the narrative. The first overview retains equal-width panels. Enlarged map geometry, legends, labels and pointer targets use the same projection and source data.
