#!/usr/bin/env python3
"""Add finding + significance annotations as marks inside every displayed chart.

Fixed findings are calculated from the retained snapshot. Filtered findings use
Vega expressions so labels and highlights describe the currently displayed data.
"""
import copy
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORANGE = '#b94e13'
INK = '#24443f'


def note(lines, y=-52, x=0, name='insight_explanation', size=11):
    return {'name': name, 'data': {'values': [{}]},
            'mark': {'type': 'text', 'align': 'left', 'baseline': 'top', 'font': 'Inter',
                     'fontSize': size, 'fontWeight': 600, 'lineHeight': 15,
                     'lineBreak': '\n', 'color': INK},
            'encoding': {'x': {'value': x}, 'y': {'value': y}, 'text': {'value': '\n'.join(lines)}}}


def ring(filter_expr, encoding):
    return {'name': 'insight_highlight', 'transform': [{'filter': filter_expr}],
            'mark': {'type': 'point', 'filled': False, 'size': 230, 'stroke': ORANGE, 'strokeWidth': 2},
            'encoding': copy.deepcopy(encoding)}


def main():
    rows = json.loads((ROOT/'data/trails.json').read_text())
    for path in sorted((ROOT/'charts').glob('*.json')):
        n = int(path.name[:2])
        d = json.loads(path.read_text())
        d['usermeta'] = {**d.get('usermeta', {}), 'annotation_design':
                        'On-chart highlighted finding with a reason for its significance; filtered findings follow the selected cohort.'}
        if n == 1:
            # Vega's geographic callouts already have leaders to their actual anchors.
            callouts = next(v for v in d['data'] if v['name']=='callouts')
            callouts['values'][0]['label'] = ['Largest council cluster: 32 routes', 'Murrindindi offers more recorded choices', 'Highlights concentration, rather than easy access']
            callouts['values'][1]['label'] = ['Maximum: Upper Yarra · 95 km', 'Over 43× the 2.2 km middle distance', 'Highlights an unusually long commitment']
            callouts['transform'][0]['expr'] = 'pickTrail===0 && zoom<=8'
            marks = d['marks'][0]['marks']
            for m in marks:
                if m.get('from', {}).get('data') != 'callouts': continue
                up = m['encode']['update']
                if m['type']=='rect':
                    up['height']={'value':76}
                    up['width']={'signal':'width>650 ? 310 : width-24'}
                    up['x']={'signal':"width>650 ? (datum.side==='left' ? 16 : width-326) : 12"}
                    up['y']={'signal':"width>650 || datum.side==='left' ? 12 : 94"}
                elif m['type']=='text':
                    up['x']={'signal':"width>650 ? (datum.side==='left' ? 26 : width-316) : 22"}
                    up['y']={'signal':"width>650 || datum.side==='left' ? 25 : 107"}
                    up['fontSize']={'value':11.5}
                    up['lineHeight']={'value':19}
                elif m['type']=='rule':
                    up['x2']={'signal':"width>650 ? (datum.side==='left' ? 38 : width-280) : 32"}
                    up['y2']={'signal':"width>650 || datum.side==='left' ? 88 : 170"}
            selected = next(v for v in d['data'] if v['name']=='selectedRoute')
            selected['transform'].append({'type':'formula','as':'insight', 'expr':
                "[datum.properties.name, format(datum.properties.length_km,'.1f')+' km · '+datum.properties.grade, datum.properties.length_km === 95 ? 'Dataset maximum: highlights the long-distance tail.' : datum.properties.length_km > 2.2 ? 'Above the 2.2 km middle distance: compare the greater distance commitment.' : 'At or below the 2.2 km middle distance: a short route can still be demanding.']"})
            marks.extend([
                {'type':'rect','name':'insight_selected_back','interactive':False,'from':{'data':'selectedRoute'},
                 'encode':{'update':{'x':{'value':12},'y':{'signal':'height-94'},'width':{'signal':'width-24'},'height':{'value':82},'fill':{'value':'white'},'fillOpacity':{'value':.96},'cornerRadius':{'value':5}}}},
                {'type':'text','name':'insight_selected_label','interactive':False,'from':{'data':'selectedRoute'},
                 'encode':{'update':{'x':{'value':24},'y':{'signal':'height-80'},'text':{'field':'insight'},'fontSize':{'value':12},'lineHeight':{'value':20},'fontWeight':{'value':600},'baseline':{'value':'top'},'fill':{'value':INK}}}}
            ])
            d['data'].append({'name':'insight_east_west','values':[{}],
                              'transform':[{'type':'filter','expr':'pickTrail===0 && zoom<=8 && width>650'}]})
            east=sum(r['longitude']>145 for r in rows)
            marks.extend([
                {'type':'rect','interactive':False,'from':{'data':'insight_east_west'},
                 'encode':{'update':{'x':{'value':16},'y':{'signal':'height-91'},'width':{'value':344},'height':{'value':77},'fill':{'value':'white'},'fillOpacity':{'value':.96},'cornerRadius':{'value':5}}}},
                {'type':'text','interactive':False,'from':{'data':'insight_east_west'},
                 'encode':{'update':{'x':{'value':26},'y':{'signal':'height-78'},
                                    'text':{'value':[f'East of 145°E: {east} routes; west: {len(rows)-east}.',
                                                     'Highlights the eastern concentration of records.',
                                                     'Dataset gaps do not mean an absence of local walks.']},
                                    'fontSize':{'value':11},'lineHeight':{'value':19},'fontWeight':{'value':600},'baseline':{'value':'top'},'fill':{'value':INK}}}}
            ])
        else:
            d['layer'] = [l for l in d['layer'] if not l.get('name','').startswith('insight_')]
        if n == 2:
            for layer in d['layer']:
                for t in layer.get('transform',[]):
                    if t.get('as')=='annotation':
                        region=layer.get('data',{}).get('values',[{}])[0].get('region_name')
                        if region=='Murrindindi':
                            t['calculate']="metric === 'resident' ? 'Highest supply: Murrindindi\\n844.2 km per 100,000 residents\\nA small population lifts the ratio.' : 'Murrindindi · 132.1 km\\n32 routes concentrate in one council.\\nA large choice set differs from longest total.'"
                        elif region=='Yarra Ranges':
                            t['calculate']="metric === 'resident' ? 'Yarra Ranges · 95.5 km / 100k\\nLarger total, lower resident-adjusted supply.\\nThe denominator changes the regional leader.' : 'Maximum total: Yarra Ranges\\n153.7 km of recorded routes\\nHighlights the largest network by distance.'"
            lowdata={'values':[{'region_name':'Cardinia'}]}
            lowtr=[{'lookup':'region_name','from':{'data':{'url':'data/lga_label_points.json'},'key':'name','fields':['lon','lat']}},
                   {'calculate':'mapFrame[0]+(18-width/2)/(min((width-28)/mapFrame[2],(height-70)/mapFrame[3]))*180/PI','as':'label_lon'},
                   {'calculate':'(2*atan(exp(log(tan(PI/4+mapFrame[1]*PI/360))+(((height-70)/2)-(height-132))/(min((width-28)/mapFrame[2],(height-70)/mapFrame[3]))))-PI/2)*180/PI','as':'label_lat'}]
            geo={'longitude':{'field':'lon','type':'quantitative'},'latitude':{'field':'lat','type':'quantitative'}}
            d['layer'].extend([
                {'name':'insight_low_supply_ring','data':lowdata,'transform':lowtr,'mark':{'type':'point','filled':False,'stroke':ORANGE,'strokeWidth':2,'size':160},'encoding':geo},
                {'name':'insight_low_supply_leader','data':lowdata,'transform':lowtr,'mark':{'type':'rule','color':ORANGE,'strokeDash':[3,3]},
                 'encoding':{**geo,'longitude2':{'field':'label_lon'},'latitude2':{'field':'label_lat'}}},
                {'name':'insight_low_supply_back','data':{'values':[{}]},
                 'mark':{'type':'rect','fill':'white','fillOpacity':.94,'cornerRadius':4},
                 'encoding':{'x':{'value':4},'x2':{'value':388},'y':{'value':{'expr':'height-133'}},'y2':{'value':{'expr':'height-68'}}}},
                {'name':'insight_low_supply_note','data':lowdata,
                 'transform':[{'calculate':"metric === 'resident' ? 'Lowest positive supply: Cardinia · 0.97 km / 100k\\nAmong the 32 councils with walking records.\\nHighlights limited supply beside a large population.' : 'Lowest positive total: Cardinia · 1.3 km\\nOne walking record in this source.\\nHighlights the small recorded local choice set.'",'as':'note'}],
                 'mark':{'type':'text','fontSize':11.5,'fontWeight':600,'lineBreak':'\n','lineHeight':15,'align':'left','baseline':'top','color':ORANGE},
                 'encoding':{'x':{'value':8},'y':{'value':{'expr':'height-127'}},'text':{'field':'note'}}}
            ])
        if n == 3:
            d['height']=660
            # Reserve a readable footer for the two A/B findings and their reasons.
            d['projection']['scale']['expr']=d['projection']['scale']['expr'].replace('height-154','height-200')
            d['projection']['translate']['expr']=d['projection']['translate']['expr'].replace('height-154','height-200')
            for l in d['layer']:
                if any(t.get('as')=='annotation' and 'annotation_name' in t.get('calculate','') for t in l.get('transform',[])):
                    l['transform']=[t for t in l['transform'] if not any(a.get('as')=='matched_median' for a in t.get('joinaggregate',[]))]
                    l['transform'].insert(1,{'joinaggregate':[{'op':'median','field':'length_km','as':'matched_median'}]})
                for t in l.get('transform',[]):
                    if t.get('as')=='annotation':
                        if 'annotation_name' in t.get('calculate',''):
                            t['calculate']="datum.annotation_name + '\\n' + format(datum.length_km,'.1f') + ' km · ' + datum.grade + '\\nLongest matching route\\n' + (datum.length_km > datum.matched_median ? format(datum.length_km/datum.matched_median,'.1f') + '× matching median: a longer commitment.' : 'Matches the median: no length contrast.')"
                        elif 'datum.lga' in t.get('calculate',''):
                            t['calculate']="datum.lga + ' · ' + datum.n + ' matching routes\\nLargest council cluster\\nHighlights where more choices concentrate.\\nCount covers the whole council.'"
                if l.get('mark',{}).get('type')=='text' and l.get('encoding',{}).get('text',{}).get('field')=='annotation':
                    isroute=any('annotation_name' in t.get('calculate','') for t in l.get('transform',[]))
                    l['encoding']['y']={'value':{'expr':'height-88' if isroute else 'height-162'}}
                    l['mark']['fontSize']=11
                name=l.get('name','')
                if name.startswith('symbolFooter') and 'y' in l.get('encoding',{}):
                    l['encoding']['y']={'value':{'expr':'height-82' if 'B' in name else 'height-156'}}
            d['layer'].append({'name':'insight_filtered_concentration','data':{'url':'data/trails.json'},
                'transform':[{'filter':"(chosenCode === 'All' || datum.grade === chosenCode) && (!accessOnly || datum.access === 'Full' || datum.access === 'Partial')"},
                             {'calculate':'datum.longitude > 145 ? 1 : 0','as':'east'},
                             {'aggregate':[{'op':'count','as':'n'},{'op':'sum','field':'east','as':'east_n'}]},
                             {'filter':'datum.n > 0'},
                             {'calculate':"datum.east_n + ' of ' + datum.n + ' matching points east of 145°E.\\nHighlights the geographic concentration.\\nCounts refer to representative route points.'",'as':'note'}],
                'mark':{'type':'text','align':'left','baseline':'top','fontSize':11,'fontWeight':600,'lineBreak':'\n','lineHeight':15,'color':INK},
                'encoding':{'x':{'value':{'expr':'width-267'}},'y':{'value':4},'text':{'field':'note'}}})
        if n == 4:
            d['height']=430
            d['padding']['top']=76
            d['layer']=[l for l in d['layer'] if not (l.get('mark',{}).get('type')=='text' and 'value' in l.get('encoding',{}).get('text',{}))]
            border=next(l for l in d['layer'] if l.get('mark',{}).get('fill','absent') is None)
            border['data']['values']=[{'grade':'Grade 3','gradient':'Short steep hills'}, {'grade':'Grade 4','gradient':'Short steep hills'}]
            d['layer'].append(note(['Largest cell: 31 Grade 3 routes with short steep hills.',
                                   'Highlights the most common grade–terrain pairing.',
                                   'The outlined Grade 4 cell has 20: terrain crosses grades.'],y=-58))
        if n == 5:
            d['height']=430
            d['padding']={'left':8,'right':8,'top':87,'bottom':8}
            # The farthest point's count label fits inside a half-width laptop card.
            for l in d['layer']:
                if l.get('encoding',{}).get('text',{}).get('field')=='label':
                    l['mark']['align']={'expr':"datum.grade === 'Grade 5' ? 'right' : 'left'"}
                    l['mark']['dx']={'expr':"datum.grade === 'Grade 5' ? -10 : 10"}
            groups={g:[r['length_km'] for r in rows if r['grade']==g] for g in {r['grade'] for r in rows}}
            hi=max(groups,key=lambda g:statistics.median(groups[g]));lo=min(groups,key=lambda g:statistics.median(groups[g]))
            d['layer'].append(ring("datum.grade === 'Grade 5' || datum.grade === 'Grade 1'",d['layer'][1]['encoding']))
            d['layer'].append(note([f'Highest median: {hi} · {statistics.median(groups[hi]):.2f} km.',
                                   'Highlights the longest typical distance, not every route.',
                                   f'Lowest median: {lo} · {statistics.median(groups[lo]):g} km ({len(groups[lo])} routes).',
                                   'Only two observations: interpret this minimum cautiously.'],y=-72))
        if n == 6:
            d['height']=510;d['padding']['top']=90
            d['transform']=[d['transform'][0],
                {'calculate':'datum.id === pickTrail ? 1 : 0','as':'selected_match'},
                {'joinaggregate':[{'op':'max','field':'length_km','as':'max_length'},
                                  {'op':'min','field':'length_km','as':'min_length'},
                                  {'op':'max','field':'selected_match','as':'selected_exists'}]},
                {'calculate':'datum.length_km === datum.max_length ? datum.id : null','as':'longest_candidate'},
                {'joinaggregate':[{'op':'min','field':'longest_candidate','as':'longest_id'}]}]
            for l in d['layer']:
                for t in l.get('transform',[]):
                    if isinstance(t.get('filter'),str) and 'pickTrail' in t['filter'] and 'max_length' in t['filter']:
                        t['filter']='pickTrail === datum.id || ((pickTrail === 0 || datum.selected_exists === 0) && datum.id === datum.longest_id)'
                if l.get('encoding',{}).get('text',{}).get('field')=='annotation':
                    l['encoding']['y']={'value':-67}
                    l['transform'].append({'calculate':
                        "datum.annotation + '\\n' + (pickTrail !== 0 && datum.selected_exists === 0 ? 'Chosen route outside filters; longest matching route shown.\\n' : '') + (datum.length_km === datum.max_length ? 'Longest matching route: shows the upper distance commitment.' : datum.length_km === datum.min_length ? 'Shortest matching route: short distance does not settle terrain demands.' : 'Selected profile: compare its terrain and duration alongside distance.')",'as':'insight_annotation'})
                    l['encoding']['text']['field']='insight_annotation'
        if n == 7:
            d['height']=470;d['padding']['top']=90
            outline={'name':'insight_bar_outline','data':{'values':[{'gradient':'Short steep hills','n':83}]},
                     'mark':{'type':'bar','filled':False,'stroke':ORANGE,'strokeWidth':2},
                     'encoding':{'x':{'field':'n','type':'quantitative'},'x2':{'datum':0},
                                 'y':copy.deepcopy(d['layer'][0]['encoding']['y'])}}
            d['layer'].append(outline)
            d['layer'].append(note(['Largest terrain group: short steep hills · 83 routes.',
                                   '53 advise experience: 48 recommended + 5 experienced.',
                                   'Highlights preparation needs that a short distance',
                                   'alone can conceal.'],y=-73))
        if n == 8:
            d['height']=430;d['padding']['top']=76
            d['layer']=[l for l in d['layer'] if not (l.get('mark',{}).get('type')=='text' and 'value' in l.get('encoding',{}).get('text',{}))]
            blocks=json.loads((ROOT/'data/mosaic.json').read_text());steep=[b for b in blocks if b['gradient']=='Short steep hills']
            d['layer'].append({'name':'insight_terrain_outline','data':{'values':[{'left':min(b['x0'] for b in steep),'right':max(b['x1'] for b in steep)}]},
                              'mark':{'type':'rect','fill':None,'stroke':ORANGE,'strokeWidth':2.5},
                              'encoding':{'x':{'field':'left','type':'quantitative'},'x2':{'field':'right'},'y':{'datum':0},'y2':{'datum':1}}})
            d['layer'].append(note(['Largest kilometre share: short steep hills.',
                                   '390.82 km · 55.3% of the 706.52 km represented.',
                                   'Highlights where most represented distance lies,',
                                   'rather than simply counting the number of routes.'],y=-60,size=10.5))
        if n == 9:
            d['height']=420;d['padding']={'left':8,'right':8,'top':68,'bottom':8}
            for l in d['layer']:
                value=l.get('encoding',{}).get('text',{}).get('value','')
                if value.startswith('Upper Yarra'):
                    l['encoding']['text']['value']='Maximum: Upper Yarra · 95 km\nMultiple days: unusually long commitment'
                elif value.startswith('Track Ninety Six'):
                    l['encoding']['text']['value']='Grade 5 maximum: Track Ninety Six · 34 km\nFar above its group’s 7.36 km middle distance'
                    l['mark']['dy']=-20
            d['layer'].append(note(['151 of 195 routes (77%) are 5 km or shorter.',
                                   'The 5 km guide highlights the short-route majority;',
                                   'the circled maxima show the exceptional long-distance tail.'],y=-52,size=12))
        if n == 10:
            for l in d['layer']:
                text=l.get('encoding',{}).get('text',{})
                if str(text.get('value','')).startswith('15 of 180'):
                    text['value']='LOW RECORDED ACCESS\n15 of 180 rated routes · 8.3%\n\nHighlights a small documented\nshortlist when access matters.\n165 rated routes record no access.\n15 unrated routes are excluded:\nmissing does not mean “no”.\n\n8 coloured cells: rounded share'
                    l['mark']['fontSize']=11
        if n == 11:
            for l in d['layer']:
                for t in l.get('transform',[]):
                    if t.get('as')=='annotation':
                        t['calculate']="datum.name === 'Whittlesea' ? 'Largest shown rank gap · 1 → 30: population leads, supply lags' : 'Lowest supply rank · 4 → 32: populous area, limited km per resident'"
            d['layer'].append({'name':'insight_rank_highlight','transform':[{'filter':"datum.name === 'Whittlesea' || datum.name === 'Cardinia'"}],
                              'mark':{'type':'point','filled':False,'stroke':ORANGE,'strokeWidth':2,'size':170},
                              'encoding':{'x':{'field':'supply_rank','type':'quantitative'},'y':copy.deepcopy(d['layer'][0]['encoding']['y'])}})
        if n == 12:
            d['height']=440;d['padding']={'left':8,'right':8,'top':81,'bottom':8}
            enc=copy.deepcopy(d['layer'][0]['encoding']);enc.pop('color',None)
            d['layer'].append({'name':'insight_duration_outline','transform':[{'filter':"datum.duration_group === 'Under 1 hour' || datum.duration_group === 'Overnight'"}],
                              'mark':{'type':'bar','height':29,'filled':False,'stroke':ORANGE,'strokeWidth':2},'encoding':enc})
            d['layer'].append(note(['Most common: under 1 hour · 111 of 195 routes (57%).',
                                   'Highlights the many brief outings in the recorded set.',
                                   'Least common: overnight · 2 routes (1%). Rare longer commitments',
                                   'still matter when matching a walk to the available time.'],y=-67,size=12))
        if n == 13:
            # Add a second geographic extreme in the open annotation band.
            d['height']=560
            def reserve_band(x):
                if isinstance(x,dict):return {k:reserve_band(v) for k,v in x.items()}
                if isinstance(x,list):return [reserve_band(v) for v in x]
                if isinstance(x,str):return x.replace('height-134','height-186').replace('118+','170+')
                return x
            d=reserve_band(d)
            for l in d['layer']:
                if l.get('mark',{}).get('type')=='rule' and 'lga_label_points' in l.get('data',{}).get('url',''):
                    for t in l.get('transform',[]):
                        if t.get('as')=='callout_lon':t['calculate']=t['calculate'].replace('width*.22','width*.62').replace('width*.50','width*.62')
                        if t.get('as')=='callout_lat':t['calculate']=t['calculate'].replace(')-96',')-155')
                for t in l.get('transform',[]):
                    if t.get('as')=='annotation':
                        if 'annotation_name' in t.get('calculate',''):
                            t['calculate']="datum.annotation_name + '\\n' + format(datum.length_km,'.1f') + ' km · ' + datum.grade + '\\nLongest route in this area\\nShows the local upper distance commitment.'"
                        elif 'chosenLga' in t.get('calculate',''):
                            t['calculate']="(chosenLga === 'All' ? 'Victoria' : chosenLga + ' LGA') + '\\n' + datum.n + (datum.n === 1 ? ' route · ' : ' routes · ') + format(datum.km,'.1f') + ' km\\n' + (datum.n === 1 ? 'Only one walking record: no local range to compare.' : 'Sets the size of the recorded local choice set.')"
                if l.get('mark',{}).get('type')=='text' and l.get('encoding',{}).get('text',{}).get('field')=='annotation':
                    l['mark']['fontSize']=11
            anchor_label=note(['Council interior anchor'],y=146,x={'expr':'width*.62'},name='insight_council_anchor',size=10.5)
            anchor_label['mark'].update(align='center',baseline='bottom',color='#5d7269')
            d['layer'].append(anchor_label)
            longest_text=next(l for l in d['layer'] if l.get('mark',{}).get('type')=='text' and any('annotation_name' in t.get('calculate','') for t in l.get('transform',[])))
            shortest=copy.deepcopy(longest_text)
            shortest['name']='insight_shortest_route'
            shortest['transform'].insert(1,{'joinaggregate':[{'op':'count','as':'local_count'}]})
            shortest['transform'].insert(2,{'filter':'datum.local_count > 1'})
            for t in shortest['transform']:
                if 'window' in t:t['sort'][0]['order']='ascending'
                if t.get('as')=='annotation':t['calculate']="'Shortest: ' + datum.annotation_name + '\\n' + format(datum.length_km,'.2f') + ' km · ' + datum.grade + '\\nHighlights the lower distance commitment;\\nshort distance alone does not mean easy.'"
            shortest['mark']['align']='left';shortest['mark']['color']=ORANGE
            shortest['encoding']['x']={'value':12};shortest['encoding']['y']={'value':76}
            d['layer'].append(shortest)
            d['layer'].append({'name':'insight_shortest_ring','data':copy.deepcopy(shortest['data']),'transform':copy.deepcopy(shortest['transform']),
                              'mark':{'type':'point','filled':False,'stroke':ORANGE,'strokeWidth':2,'size':170},
                              'encoding':{'longitude':{'field':'anchor_lon','type':'quantitative'},'latitude':{'field':'anchor_lat','type':'quantitative'}}})
            d['layer'].append({'name':'insight_shortest_leader','data':copy.deepcopy(shortest['data']),
                'transform':copy.deepcopy(shortest['transform'])+[
                    {'calculate':'regionFrame[0]+((width*.22)-width/2)/(min((width-28)/regionFrame[2],(height-186)/regionFrame[3]))*180/PI','as':'min_label_lon'},
                    {'calculate':'(2*atan(exp(log(tan(PI/4+regionFrame[1]*PI/360))+((170+(height-186)/2)-150)/(min((width-28)/regionFrame[2],(height-186)/regionFrame[3]))))-PI/2)*180/PI','as':'min_label_lat'}],
                'mark':{'type':'rule','color':ORANGE,'strokeDash':[3,3]},
                'encoding':{'longitude':{'field':'anchor_lon','type':'quantitative'},'latitude':{'field':'anchor_lat','type':'quantitative'},
                            'longitude2':{'field':'min_label_lon'},'latitude2':{'field':'min_label_lat'}}})
        if n == 14:
            d['height']=590
            for l in d['layer']:
                text=l.get('encoding',{}).get('text',{})
                if str(text.get('value','')).startswith('Busiest bin:'):
                    text['value']='Maximum bin: 13 routes · 6.7%\nAll 13 assigned to Murrindindi.\nHighlights a local concentration\nthat a council total can hide.'
                    l['encoding']['x']={'value':{'expr':'width-240'}}
                if l.get('name') in ['gridFooterALetter','gridFooterACircle','gridFooterABadge']:
                    l['encoding']['x']={'value':{'expr':'width-255'}}
            enc=copy.deepcopy(next(l for l in d['layer'] if l.get('name')=='gridPeakBadge')['encoding'])
            enc.pop('tooltip',None)
            empty={'values':[{'x':-237500,'y':162500}]}
            d['layer'].append({'name':'insight_empty_bin_ring','data':empty,'mark':{'type':'point','filled':True,'fill':'white','stroke':ORANGE,'strokeWidth':2,'size':180},'encoding':enc})
            lineenc=copy.deepcopy(enc);lineenc.update(x2={'datum':350000},y2={'datum':240000})
            d['layer'].append({'name':'insight_empty_bin_leader','data':empty,'mark':{'type':'rule','color':ORANGE,'strokeDash':[3,3]},'encoding':lineenc})
            d['layer'].append(note(['Circled empty cell: 0 recorded route points.',
                                   'Highlights a gap in this dataset’s coverage.',
                                   'Other local walks may exist: zero is not',
                                   'a complete inventory of walking options.'],y=30,x={'expr':'width-258'},name='insight_empty_bin_note',size=10.5))
        # Vega includes the bounds of negative-position annotation marks itself.
        # A second large explicit top padding would create an empty band above them.
        if n in [4,5,6,7,8,9,12]:
            d.setdefault('padding',{})['top']=8
        if n != 1:
            d['layer'] = [l for l in d['layer'] if not l.get('name','').startswith('review_')]
        from refine_annotation_layouts import refine
        refine(d,n,rows)
        path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
