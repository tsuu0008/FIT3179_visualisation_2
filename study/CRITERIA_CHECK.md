# Criteria and feedback review — 23 October 2026

This is an implementation inventory, not a grading guarantee. The rubric's final classification of advanced idioms belongs to the teaching team.

## Chart breadth

There are 14 displayed Vega-Lite specifications. The statewide route map and regional detail are one map idiom; counting them together leaves 13 views. Similar views should not be counted as distinct advanced idioms.

| Candidate advanced idiom | Specification | Analytical purpose |
| --- | --- | --- |
| Route/network map | 01 and 13 | Locate actual walking routes, then inspect a region. |
| Choropleth map | 02 | Compare council supply with population normalisation. |
| Proportional-symbol map | 03 | Compare individual trail distances and grades geographically. |
| Equal-area gridded map | 14 | Locate concentrations using equal-size cells rather than councils. |
| Heatmap | 04 | Compare joint grade and terrain counts. |
| Parallel coordinates | 06 | Compare four attributes of a trail. |
| Mosaic | 08 | Show distance shares by terrain and grade. |
| Waffle | 10 | Communicate the small recorded access share. |

These are eight candidate advanced idioms, including four geographic types. Median-distance, stacked-bar, strip, rank and scatter views provide supporting comparisons; their variants are not used to inflate this advanced-idiom count. No Sankey, node-link or radial chart was added because the current data does not supply a corresponding flow, relationship or cyclic question.

## Responses to feedback

- Complex charts now have nearby reading instructions, explicit denominators and defined scales. The narrative focuses on useful walking choices for a general audience.
- Direct annotations identify a pattern and explain its meaning. The grid highlights its exact peak cell using a short leader and matching numbered note.
- The first pair remains an equal-width split; broad comparisons use the available width; laptop breakpoints stack cramped cards. Browser inspection at 1280 px and 1024 px found no horizontal plot overflow or text clipped by an SVG frame.
- Grade labels, distinct point shapes and solid-dot legends supplement the colour palette. Numeric counts use sequential colour.
- Original observations and source URLs remain unchanged. The new map is a documented aggregation, not another source or a new official snapshot.

## Submission items still requiring attention

- The rubric requests reliable, current sources. The existing trail extraction, boundary vintage and population provenance remain unverified; do not claim this layout revision resolves that requirement. See DATA_SOURCES.md.
- Submit the required hand-drawn sketches and written report yourself. The report should link tasks to marks/channels, justify the grid and discuss its cell size, origin and midpoint limitations.
- Explain the code and interactions in your interview. INTERVIEW_GUIDE.md covers the new grid alongside existing charts.
- Confirm the teaching team's interpretation of advanced maps/idioms if the precise count is important to the target grade.
