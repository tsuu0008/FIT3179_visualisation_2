"""Layout refinements for the numbered browser review, 23 October 2026."""
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INK='#24443f'
ORANGE='#b94e13'
BLUE='#0072B2'


def text(lines, x, y, name, size=11.5, color=INK):
    return {'name':name,'data':{'values':[{}]},
            'mark':{'type':'text','align':'left','baseline':'top','font':'Inter','fontSize':size,
                    'fontWeight':600,'lineBreak':'\n','lineHeight':16,'color':color},
            'encoding':{'x':{'value':x},'y':{'value':y},'text':{'value':'\n'.join(lines)}}}


def screen_anchor(transforms, frame, scale, cy, x, y):
    return copy.deepcopy(transforms)+[
        {'calculate':f'{frame}[0]+(({x})-width/2)/({scale})*180/PI','as':'review_lon'},
        {'calculate':f'(2*atan(exp(log(tan(PI/4+{frame}[1]*PI/360))+(({cy})-({y}))/({scale})))-PI/2)*180/PI','as':'review_lat'}]


def badges(name, code, encoding, transforms=None, data=None, color=ORANGE):
    """Shared circled-letter style for annotation headings and reference marks."""
    source={}
    if transforms is not None:source['transform']=copy.deepcopy(transforms)
    if data is not None:source['data']=copy.deepcopy(data)
    tooltip={'value':f'Annotation {code}'}
    return [
        {**source,'name':name+'_circle',
         'mark':{'type':'point','shape':'circle','filled':True,'fill':'white','stroke':color,'strokeWidth':1.7,'size':250},
         'encoding':{**copy.deepcopy(encoding),'tooltip':tooltip}},
        {**source,'name':name+'_letter',
         'mark':{'type':'text','fontSize':10,'fontWeight':700,'color':color,'align':'center','baseline':'middle'},
         'encoding':{**copy.deepcopy(encoding),'text':{'value':code},'tooltip':tooltip}}]


def refine(d,n,rows):
    if n==1:
        for m in d['marks'][0]['marks']:
            label=m.get('encode',{}).get('update',{}).get('text',{}).get('value')
            if isinstance(label,list) and label and str(label[0]).startswith('East of 145'):
                m['encode']['update']['text']['value']=[label[0],'78% of recorded route points lie on the eastern side.','This concentration changes the regional choice set.']
    if n==2:
        # The existing map has open margins; attach the two labels to those margins.
        scale=d['projection']['scale']['expr'];cy='(height-70)/2'
        d['layer']=[l for l in d['layer'] if l.get('name') not in ['insight_low_supply_back']]
        for l in d['layer']:
            region=l.get('data',{}).get('values',[{}])[0].get('region_name')
            kind=l.get('mark',{}).get('type')
            if region in ['Murrindindi','Yarra Ranges']:
                isleft=region=='Murrindindi'
                x='12' if isleft else 'width-12'
                y=78 if isleft else 140
                if kind=='text' and l.get('encoding',{}).get('text',{}).get('field')=='annotation':
                    l['encoding']={'x':{'value':{'expr':x}},'y':{'value':y},'text':{'field':'annotation'}}
                    l['mark'].update(align='left' if isleft else 'right',baseline='top',dy=0,fontSize=12,lineHeight=17)
                    for t in l.get('transform',[]):
                        if t.get('as')=='annotation':
                            t['calculate']=("metric === 'resident' ? 'Murrindindi · highest supply\\n844.2 km / 100,000 residents\\nA small population lifts the ratio.' : 'Murrindindi · 132.1 km\\n32 routes in one council\\nA concentrated set of local choices.'" if isleft else
                                            "metric === 'resident' ? 'Yarra Ranges · 95.5 km / 100k\\nMore total km, lower supply per resident.\\nPopulation changes the regional leader.' : 'Yarra Ranges · largest total\\n153.7 recorded kilometres\\nThe largest network by distance.'")
                if kind=='rule':
                    l['transform']=screen_anchor([t for t in l['transform'] if t.get('as') not in ['review_lon','review_lat']], 'mapFrame',scale,cy,'180' if isleft else 'width-180',str(y+60))
                    l['encoding']['longitude2']={'field':'review_lon'};l['encoding']['latitude2']={'field':'review_lat'}
            if l.get('name')=='insight_low_supply_note':
                l['encoding']['x']={'value':{'expr':'width*.34'}}
                l['encoding']['y']={'value':{'expr':'height-111'}}
                for t in l['transform']:
                    t['calculate']="metric === 'resident' ? 'Cardinia · lowest positive supply\\n0.97 km / 100k · lowest of 32 councils with tracks\\nSmall recorded supply beside a large population.' : 'Cardinia · lowest positive total\\n1.3 km · lowest of 32 councils with tracks\\nA small recorded local choice set.'"
            if l.get('name')=='insight_low_supply_leader':
                l['transform']=screen_anchor([t for t in l['transform'] if t.get('as') not in ['label_lon','label_lat','review_lon','review_lat']], 'mapFrame',scale,cy,'width*.48','height-117')
                l['encoding']['longitude2']={'field':'review_lon'};l['encoding']['latitude2']={'field':'review_lat'}
            for t in l.get('transform',[]):
                if t.get('as')=='note' and 'WHAT THE MAP COVERS' in t.get('calculate',''):
                    t['calculate']="'DATA SNAPSHOT\\n195 official walking records\\nABS residents: 30 June 2025'"
    if n==3:
        d['height']=650
        d['projection']['scale']['expr']='min(max(width-300,300)/mapFrame[2],(height-70)/mapFrame[3])'
        d['projection']['translate']['expr']='[width/2,(height-70)/2]'
        d['layer']=[l for l in d['layer'] if not l.get('name','').startswith('symbolFooter')]
        cohort_filter="(chosenCode === 'All' || datum.grade === chosenCode) && (!accessOnly || datum.access === 'Full' || datum.access === 'Partial')"
        heading_badges=[]
        for l in d['layer']:
            if l.get('name') in ['areaNumberHalo','routeNumberHalo']:
                l['mark'].update(size=250,strokeWidth=1.7)
            if l.get('encoding',{}).get('text',{}).get('field')=='annotation':
                isroute=any('annotation_name' in t.get('calculate','') for t in l.get('transform',[]))
                l['encoding']['x']={'value':{'expr':'width-153' if isroute else 'width-245'}}
                l['encoding']['y']={'value':{'expr':'height*.29' if isroute else 'height-150'}}
                l['mark'].update(fontSize=11,lineHeight=16)
                for t in l['transform']:
                    if t.get('as')=='annotation':
                        t['calculate']=("datum.annotation_name + '\\n' + format(datum.length_km,'.1f') + ' km · ' + datum.grade + '\\nLongest matching route\\n' + (datum.length_km > datum.matched_median ? format(datum.length_km/datum.matched_median,'.1f') + '× matching median\\nAn unusually long outing.' : 'Matches the middle distance.')" if isroute else
                                        "datum.lga + '\\n' + datum.n + (datum.n === 1 ? ' matching route' : ' matching routes') + '\\nLargest council cluster\\nMore choices concentrate\\nin this council area.'")
                heading_badges.extend(badges('review_symbol_heading_'+('B' if isroute else 'A'),'B' if isroute else 'A',
                    {'x':{'value':{'expr':'width-167' if isroute else 'width-259'}},'y':{'value':{'expr':'height*.29+5' if isroute else 'height-145'}}},
                    l['transform'],l['data'],l['mark']['color']))
            if l.get('name')=='insight_filtered_concentration':
                l['encoding']['x']={'value':{'expr':'width-267'}}
        d['layer'].extend(heading_badges)
        d['layer'].append({'name':'review_selection_context','data':{'url':'data/trails.json'},
            'transform':[{'filter':cohort_filter},{'aggregate':[{'op':'count','as':'n'},{'op':'sum','field':'length_km','as':'km'},{'op':'median','field':'length_km','as':'middle'}]},
                         {'filter':'datum.n > 0'},
                         {'calculate':"'CURRENT SELECTION\\n' + datum.n + (datum.n === 1 ? ' route · ' : ' routes · ') + format(datum.km,'.1f') + ' km\\nMiddle distance: ' + format(datum.middle,'.1f') + ' km\\nCompare A and B with\\nthis matching set.'",'as':'note'}],
            'mark':{'type':'text','align':'left','baseline':'top','fontSize':11,'fontWeight':600,'lineHeight':16,'lineBreak':'\n','color':INK},
            'encoding':{'x':{'value':12},'y':{'value':{'expr':'height*.60'}},'text':{'field':'note'}}})
    if n==5:
        for l in d['layer']:
            if l.get('name')=='insight_explanation':
                l['encoding']['text']['value']='Highest median: Grade 5 · 7.36 km.\nLongest typical distance among these groups.\nLowest median: Grade 1 · 0.7 km (2 routes).\nThe tiny group makes this minimum less representative.'
        for letter,y in [('A',-67),('B',-37)]:
            d['layer'].extend(badges('review_median_heading_'+letter,letter,{'x':{'value':-14},'y':{'value':y}},data={'values':[{}]}))
        encoding=copy.deepcopy(d['layer'][1]['encoding']);encoding.pop('color',None)
        tr=[{'filter':"datum.grade === 'Grade 5' || datum.grade === 'Grade 1'"},{'calculate':"datum.grade === 'Grade 5' ? 'A' : 'B'",'as':'badge'}]
        d['layer'].extend([
            {'name':'review_median_badges','transform':tr,'mark':{'type':'point','filled':True,'fill':'white','stroke':ORANGE,'strokeWidth':1.7,'size':250},'encoding':encoding},
            {'name':'review_median_letters','transform':tr,'mark':{'type':'text','fontWeight':700,'fontSize':10,'color':ORANGE,'align':'center','baseline':'middle'},'encoding':{**encoding,'text':{'field':'badge'}}}])
    if n==6:
        d['height']=600
        d['transform'][2]['joinaggregate'].append({'op':'median','field':'length_km','as':'matching_middle'})
        selected=next(l['transform'][0]['filter'] for l in d['layer'] if l.get('mark',{}).get('type')=='line' and l.get('transform'))
        for l in d['layer']:
            if l.get('encoding',{}).get('text',{}).get('field')=='insight_annotation':l['encoding']['y']={'value':-128}
        xy=copy.deepcopy(d['layer'][1]['encoding']);xy={k:v for k,v in xy.items() if k in ['x','y']}
        for axis,code,xpos,expr in [
            (1,'A','width*.28',"'Distance comparison\\n' + format(datum.length_km,'.1f') + ' km · ' + format(datum.length_km/datum.matching_middle,'.1f') + '× matching median\\nShows how far this route departs from typical.'"),
            (3,'B','width*.65',"'Demands beyond distance\\n' + datum.gradient + ' · ' + datum.grade + '\\n' + datum.duration_group + '\\nTerrain and time also shape the commitment.'")]:
            tr=[{'filter':selected},{'filter':f'datum.axis === {axis}'}]
            d['layer'].append({'name':f'review_profile_note_{axis}','transform':tr+[{'calculate':expr,'as':'note'}],
                'mark':{'type':'text','fontSize':11,'fontWeight':600,'lineBreak':'\n','lineHeight':15,'align':'left','baseline':'top','color':ORANGE},
                'encoding':{'x':{'value':{'expr':xpos}},'y':{'value':-65},'text':{'field':'note'}}})
            d['layer'].append({'name':f'review_profile_leader_{axis}','transform':tr,'mark':{'type':'rule','color':ORANGE,'strokeDash':[3,3],'opacity':.7},
                'encoding':{**xy,'x2':{'value':{'expr':f'{xpos}+40'}},'y2':{'value':-4}}})
            # Offset the circled letters from the route points, and repeat the
            # same badges beside the headings to identify them as annotations.
            for position,enc in [
                ('point',{**xy,'xOffset':{'value':-14},'yOffset':{'value':-13}}),
                ('heading',{'x':{'value':{'expr':f'{xpos}-14'}},'y':{'value':-60}})]:
                d['layer'].extend(badges(f'review_profile_badge_{axis}_{position}',code,enc,tr))
    if n==7:
        d['height']=600
        for l in d['layer']:
            if l.get('name')=='insight_explanation':
                l['encoding']['x']={'value':{'expr':'max(0,width-260)'}}
                l['encoding']['y']={'value':-77}
                l['encoding']['text']['value']='Short steep hills: 83 routes (largest group).\n53 advise experience:\n48 recommended + 5 experienced.\nPreparation matters even on a short walk.'
        d['layer'].append({'name':'review_experience_leader','data':{'values':[{'gradient':'Short steep hills','n':83}]},
            'mark':{'type':'rule','color':ORANGE,'strokeWidth':1.3,'strokeDash':[3,3]},
            'encoding':{'x':{'field':'n','type':'quantitative'},'y':copy.deepcopy(d['layer'][0]['encoding']['y']),
                        'x2':{'value':{'expr':'width-90'}},'y2':{'value':-8}}})
    if n==8:
        d['height']=600
        for l in d['layer']:
            if l.get('name')=='insight_explanation':
                l['encoding']['y']={'value':-90};l['mark']['fontSize']=11.5
                l['encoding']['text']['value']='Routes with short steep hills: 390.82 km.\nFlat routes: just 5.3% of the 706.52 km shown.\nFor a gentler outing, check the terrain first.'
        headline=text(['55.3% · LARGEST DISTANCE SHARE'],0,-112,'review_mosaic_headline',size=13,color=ORANGE)
        headline['mark']['fontWeight']=700
        d['layer'].append(headline)
        blocks=json.loads((ROOT/'data/mosaic.json').read_text());total=sum(b['km'] for b in blocks)
        cols=[]
        for terrain in dict.fromkeys(b['gradient'] for b in blocks):
            group=[b for b in blocks if b['gradient']==terrain]
            cols.append({'center':(min(b['x0'] for b in group)+max(b['x1'] for b in group))/2,'share':sum(b['km'] for b in group)/total,'terrain':terrain})
        d['layer'].append(text(['Each terrain’s share of represented kilometres:'],0,-36,'review_mosaic_share_title',size=11))
        d['layer'].append({'name':'review_mosaic_percentages','data':{'values':cols},
            'mark':{'type':'text','fontSize':11.5,'fontWeight':700,'baseline':'bottom','color':INK},
            'encoding':{'x':{'field':'center','type':'quantitative','scale':{'domain':[0,1]}},'y':{'value':-9},'text':{'field':'share','format':'.1%'},
                        'tooltip':[{'field':'terrain','title':'Terrain'},{'field':'share','title':'Kilometre share','format':'.1%'}]}})
    if n==10:
        for l in d['layer']:
            t=l.get('encoding',{}).get('text',{})
            if str(t.get('value','')).startswith(('LOW RECORDED ACCESS','ACCESS-RECORDED SHORTLIST')):
                t['value']='ACCESS-RECORDED SHORTLIST\n15 of 180 rated routes · 8.3%\n\nA small documented set when\naccess is part of the decision.\n\n165 rated routes record no access.\n15 unrated excluded.\n8 coloured cells: rounded share.'
    if n==12:
        d['layer']=[l for l in d['layer'] if l.get('name')!='insight_explanation']
        d['layer'].append(text(['MOST COMMON: UNDER 1 HOUR','111 routes · 57% of all 195 records','Most recorded options fit a brief outing.'],0,-66,'review_duration_max',size=12))
        d['layer'].append(text(['LEAST COMMON: OVERNIGHT','2 routes · 1% of all 195 records','A small group needs an overnight time commitment.'],{'expr':'width*.55'},-66,'review_duration_min',size=12))
        for l in d['layer']:
            if l.get('encoding',{}).get('text',{}).get('field')=='label':
                l['mark']['dx']={'expr':"datum.duration_group === 'Under 1 hour' || datum.duration_group === 'Overnight' ? 32 : 8"}
        for code,category,x in [('A','Under 1 hour','-14'),('B','Overnight','width*.55-14')]:
            d['layer'].extend(badges('review_duration_heading_'+code,code,{'x':{'value':{'expr':x}},'y':{'value':-60}},data={'values':[{}]}))
            enc=copy.deepcopy(d['layer'][1]['encoding']);enc.pop('text',None)
            enc['xOffset']={'value':12}
            d['layer'].extend(badges('review_duration_reference_'+code,code,enc,[{'filter':{'field':'duration_group','equal':category}}]))
    if n==14:
        d['height']=680
        for l in d['layer']:
            if l.get('name') in ['gridPeakBadge','gridFooterABadge']:
                l['mark'].update(size=250,strokeWidth=1.7)
            if l.get('name')=='insight_empty_bin_note':
                l['encoding']['text']['value']='Circled cell: 0 recorded route points.\n65 occupied bins contain all 195 points.\nHighlights uneven local coverage.'
