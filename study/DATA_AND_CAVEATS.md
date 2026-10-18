# Data and caveats

| Item | Meaning |
| --- | --- |
| trails.json | 194 records: name/id, length_km, hours, grade, gradient, experience, access, assigned area and representative coordinates. |
| trails.geojson | Actual route geometry and metadata. |
| lga.geojson | 80 boundary features including the unincorporated area; source of population/supply fields. |
| map_regions.json | Area features plus the Victoria outline; used for the selected border only. |
| trail_labels.json | Trail records with shorter names for map annotations; original names remain in tooltips. |
| parallel_points.json | Four prepared rows per trail (776 total), with an axis number and display position; original values remain in tooltips. |
| distance_points.json | Trail records with precomputed lane offsets for the strip plot. |
| mosaic.json | Prepared rectangle coordinates and rounded kilometre labels. |
| lga_stats.json | Prepared area totals and ranks. |
| access_waffle.json | 100 prepared percentage cells. |

The browser starts from processed data. Original raw-data cleaning, boundary assignment and derivation scripts are not included. The supplied lga attribute uses a route midpoint assignment; a route can cross boundaries.

## Denominators

- All trails: 194; headline total 871.9 km, median 2.2 km.
- Grades 1–5: 4, 42, 115, 27, 2 records; Unknown: 4.
- Positive recorded times: 149; missing time: 45.
- Missing terrain: 7.
- Heatmap: 186 records with known grade and terrain.
- Experience bars: 187 records with known terrain and experience.
- Mosaic: coordinates match 853.805 unrounded km with known grade and terrain. Rounded per-block labels sum to 853.7 km. This is not the full-network denominator.
- Access: 2 Full + 13 Partial = 15, among 179 rated records. Another 15 have no rating. 100 waffle cells round the share to eight highlighted cells.
- Rank comparison: ranks among 31 positive-trail areas; 18 most populous are displayed.
- At or below 5 km: 150 of 194 trails initially.

The mosaic excludes both unknown terrain and unknown grade. Per-block rounding explains small differences between printed totals and precise rectangle areas.

## Simple local interactions

The regional detail has an area dropdown; the supply map has a measure dropdown; the circle map has grade/access controls; the strip has a grade dropdown; parallel coordinates has an example-trail dropdown. The overview and time chart remain fixed. Each control affects one chart. The regional dropdown includes areas with recorded trails.

Parallel-coordinate prepared positions are 100 × sqrt(km/95), 100 × sqrt(hours/48), 25 × (grade−1), and 25 × terrain index (flat=0, difficult=4). Missing values use −15, below the valid range. Raw-unit axis labels use the same conversions. These display positions are not additional measurements. These conversions were applied when preparing parallel_points.json; the website only reads the resulting values.

## Snapshot-specific and perceptual limits

Some count denominators, the 69-trail heatmap note, named outliers, mosaic total and 15/179 label are fixed to this snapshot. Replacing the dataset requires reviewing them. Grade 5 has only two records. Recorded durations are estimates. Mercator is not equal-area, and the browser does not calculate geographic statistics from its displayed polygons.

Square-root axes keep short routes distinguishable but make spacing nonlinear. Grade/terrain are ordered categories with no equal-effort interpretation. Rank gaps lose underlying magnitudes. Colour consistency is provided, but no formal colour-vision evaluation is claimed. Annotations use fixed positions and offsets; they do not use an automatic collision solver.
