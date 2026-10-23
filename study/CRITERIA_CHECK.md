# Full criteria review — 23 October 2026

Reviewed against the supplied **FIT3179 Data Visualisation 2 v1.2** brief. This is an evidence inventory and improvement record, not a predicted mark.

| Rubric item | Weight | Current evidence and remaining limits |
| --- | --- | --- |
| Hand-drawn sketch | 2% | The original two-page hand-drawn PDF is preserved unchanged at `submission/DV2sketch.pdf`. The walking topic, title, grade guide, overview/detail maps, population comparison, short-but-demanding theme, conclusion and references remain recognisable. The original sketch itself is assessed by the teaching team. |
| Idioms and complexity | 8% | 14 displayed Vega/Vega-Lite views. Four geographic types: route map, choropleth, sized-symbol map and equal-area grid. Heatmap, parallel coordinates, mosaic and waffle bring the candidate advanced-idiom total to eight. Repeated statewide/regional route maps count once. Effectiveness and final idiom classification remain marking decisions. |
| Layout, colour and figure-ground | 3% | Shared margins, responsive columns, paired chart boundaries, consistent grade colours, clear cards and map-margin callouts. Laptop views have been checked at 1024, 1096 and 1280 px without horizontal page overflow. See `LAYOUT_REVIEW.md`. |
| Typography | 2% | DM Serif Display distinguishes major story headings; Inter supports body text, controls and diagrams. Reading guides have a secondary hierarchy, and conclusion paragraphs are left aligned in a constrained reading column. Compact diagram labels need to be judged at the actual laptop size. |
| Story, annotations, grammar and style | 5% | Explicit everyday Victorian audience; a free-afternoon opening connects place, route demands, time and access; recurring examples develop the argument; the conclusion answers the opening. Grade meanings precede first use. All 14 views include an on-chart finding and its significance, with circled references where needed. Author, date, sources and AI acknowledgement are visible. See `NARRATIVE_REVIEW.md` and `ANNOTATIONS.md`. |
| Domain, who, what, why and how | 2% | `submission/WHAT_WHY_HOW.md` now provides a shorter, task-led description with source details, idiom rationale, interactions, limitations, sketch relationship and AI acknowledgement. It is prepared text, not the unit's official submission template. |
| Interview | 3% | The author reports that the interview is already complete. Interview materials were not changed during this review. |

## Requirements outside the rubric rows

- **One scrolling page:** all major story sections remain on one page; navigation scrolls to sections. Filters affect their own chart.
- **Vega/Vega-Lite:** one Vega overview plus 13 Vega-Lite views. Readable JSON specifications have direct links in an expandable methods section and a footer link.
- **At least three map idioms:** four geographic types are present. The duplicate regional line map is not counted as a new idiom.
- **Two sources combined:** official Victorian walking routes and ABS population at 30 June 2025 are joined by council for distance-per-resident comparisons.
- **Accurate scope:** all 195 walking records remain included. Raw classifications, categorical durations and every official route coordinate are preserved. The source marks 20 routes FULL CLOSURE; a scope note and route inspection now expose that fact without silently excluding them.
- **Loading:** removing the redundant regional state-outline layer avoids a 585,786-byte data download. The shared council polygons still draw the state edge. The page now references 12 unique runtime data files totalling 3,427,580 bytes before HTTP compression, excluding chart specifications, libraries, fonts and external map tiles. This is a payload measurement, not a network-speed benchmark.
- **Sources and external elements:** data references, Parks Victoria grade context and OpenStreetMap basemap attribution are linked. Generative-AI assistance is acknowledged in the page and description.
- **Public access:** the GitHub Pages check could not be completed from this environment: browser name resolution failed and the web reader could not access the URL. This does not establish that the public site is down. The current local changes have not been pushed, so public deployment still needs checking separately.

## Improvements made in this review

1. Shortened the written description and tied idiom choices to reader tasks.
2. Added discoverable links to all 14 human-readable chart JSON files.
3. Disclosed the 20 source-marked closures near the coverage note; added recorded status to route tooltips and the overview's selected-route text.
4. Removed a redundant outline download while preserving all official route geometry and observations.

## Remaining priorities

1. **Publish and verify:** after the author publishes the intended revision, check the public page, all embedded charts, the JSON links, data links and original-sketch PDF from an unsigned-in browser. Public accessibility is an explicit submission requirement.
2. **Official template:** transfer the reviewed description and final URLs into the template supplied by the unit before Moodle submission.
3. **Boundary provenance:** the retained council geometry's vintage remains unverified. Midpoint assignment also counts a whole cross-boundary route in one council. Both limitations are disclosed; they are not resolved by layout or narrative changes.

No additional charts, decorative filler or repeated caveats were added to chase a rubric count. The current evidence should be assessed on whether each view contributes to the connected story.
