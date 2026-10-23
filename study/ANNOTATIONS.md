# Annotations inside the displayed charts

Every view includes a finding and why it is highlighted, drawn as Vega/Vega-Lite marks inside the chart. These callouts complement the story paragraphs. Rings, outlines, leader lines and matching A/B badges identify the relevant marks. Additional map-margin annotations explain meaningful low values and geographic gaps.

| View | Highlighted evidence | Why the annotation matters |
| --- | --- | --- |
| Statewide route overview | Largest council cluster: Murrindindi, 32 routes; maximum distance: Upper Yarra, 95 km; 152 eastern versus 43 western representative points | Distinguishes geographic concentration from an unusually long distance commitment. Named-route focus receives its own contextual callout. |
| Council supply map | Highest resident-adjusted supply, greatest total distance and Cardinia’s lowest positive supply | Explains how population changes the leader, while making the small recorded local choice set visible. The minimum is explicitly among the 32 councils with walking records. |
| Proportional-symbol map | Largest matching council cluster, longest matching route and eastern share of matching points | Explains geographic choice concentration and the upper distance commitment. All three findings follow grade/access filters. |
| Grade/terrain heatmap | Largest joint cell: 31 Grade 3/short-steep routes; comparison: 20 Grade 4/short-steep routes | Identifies the dominant pairing and demonstrates that the same terrain occurs across grades. |
| Median distance | Highest median: Grade 5, 7.36 km; lowest: Grade 1, 0.7 km, only two routes | Highlights typical distance differences and explains the limitation of the tiny minimum group. |
| Parallel profiles | Longest matching route or the selected route | Explains why the profile is highlighted and compares its combined demands. If a selected route is outside the filters, an explicit on-chart note identifies the longest-match fallback. |
| Experience bars | Largest terrain group: 83 short-steep routes; 53 advise experience | Shows preparation needs that a short distance can conceal. |
| Kilometre mosaic | Largest distance share: routes with short steep hills, 390.82 km / 55.3%; flat routes contribute 5.3% | Makes the contrast concrete and explains why checking terrain matters when choosing a gentler outing. These are the full distances of routes with each terrain description. |
| Distance strip | 151/195 at or below 5 km; Upper Yarra’s 95 km maximum; Grade 5’s 34 km maximum | Contrasts the short-route majority with exceptional longer commitments. |
| Accessibility waffle | Low recorded access: 15/180 rated routes, 8.3%; 15 unrated excluded | Explains the small documented shortlist and why missing ratings cannot be treated as “no”. |
| Population/supply ranks | Largest shown rank gap: Whittlesea, 1→30; lowest supply rank: Cardinia, 4→32 | Shows that population leadership does not imply high recorded kilometres per resident. |
| Duration bars | Most common: under one hour, 111 routes; least common: overnight, two routes | Highlights common brief outings while keeping rare longer commitments visible. |
| Regional route detail | Longest and shortest routes in the selected council | Shows the local range of distance commitments, with an explicit warning that short does not mean easy. A single-record council does not receive a redundant minimum. |
| Equal-area grid | Peak: 13 routes, 6.7%; a circled empty cell | Reveals a cluster that council totals can hide and explains that zero dataset points does not establish an absence of local walks. |

The annotation pipeline is `scripts/prepare_chart_annotations.py`, called by `scripts/prepare_verified_charts.py`. Fixed findings refer to the retained 195-record snapshot; population values and comparison groups are documented in the source methods. Filtered findings are calculated within the chart. Rebuild and version assets after changes to data or specifications.

## Numbered browser review

The reviewed layouts spread the supply-map labels into the side margins and place Cardinia below its anchor. Median extrema use matching A/B point badges. Circled A/B profile callouts compare distance with the matching median and connect terrain/duration to the selected route. The experience callout sits at the top right with a leader. The mosaic has a taller plot and labels every terrain's kilometre share. The shortlist map uses its margins for A/B findings and a matching-set summary. Duration findings use separate A/B callouts linked to the bar labels. Repeated absence warnings are removed, and the equal-area grid is enlarged.

These placement refinements are implemented by `scripts/refine_annotation_layouts.py`, called during the annotation build.

Paired annotation references use outlined, white-filled A/B circles at both the callout and the highlighted mark. This convention is shared by the duration, profile, median and symbol-map comparisons.

The symbol-map council callout A now occupies the lower-right open margin, with its matching A marker retained on the council. Callout B remains beside the longest-route explanation at the upper right. The public grade guide precedes the first map.
