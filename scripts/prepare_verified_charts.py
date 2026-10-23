#!/usr/bin/env python3
"""Build the comparisons that use verified source codes and duration categories."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / 'charts'
ROWS = json.loads((ROOT / 'data/trails.json').read_text())
from grade_labels import GRADES, GRADE_COLOURS, grade_label
CODES = GRADES
COLOURS = GRADE_COLOURS
TERRAINS = ['Flat','Gentle hills','Short steep hills','Very steep','Very steep and difficult']
DURATIONS = ['Under 1 hour','1–4 hours','Over 4 hours','Overnight','Multiple days','Not recorded']
COLOUR = {'field':'grade','type':'nominal','scale':{'domain':CODES,'range':COLOURS},
          'legend':{'title':'Recorded grade','orient':'bottom','columns':4,'symbolType':'circle','titleLimit':220}}
TOOLTIP = [{'field':'name','title':'Trail'},{'field':'grade','title':'Recorded grade'},
           {'field':'length_km','title':'Distance (km)','format':'.2f'},
           {'field':'duration_group','title':'Source duration category'},
           {'field':'gradient','title':'Terrain'},{'field':'lga','title':'Council'},
           {'field':'closure','title':'Recorded route status'}]

def base(height=300):
    return {'$schema':'https://vega.github.io/schema/vega-lite/v5.json','width':'container','height':height,
            'background':None,'autosize':{'type':'fit','contains':'padding'},
            'config':{'view':{'stroke':None},'font':'Inter','axis':{'labelFontSize':12,'titleFontSize':12,
            'labelColor':'#405652','titleColor':'#24443f','gridColor':'#e4ebe7'},
            'legend':{'labelFontSize':12,'titleFontSize':12}}}

def save(n, spec):
    p=next(CHARTS.glob(f'{n:02d}_*.json'))
    p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')

def main():
    # Change presentation labels while preserving raw source values in the data.
    def change(x):
        if isinstance(x,list):
            out=[change(v) for v in x]
            if out and isinstance(out[0],dict) and 'legend_grade' in out[0]:
                return [{'legend_grade':grade} for grade in GRADES]
            if 'Grade 1' in out and all(isinstance(v,str) for v in out):
                out=list(dict.fromkeys(out))
            return out
        if isinstance(x,dict):
            d={k:change(v) for k,v in x.items()}
            scale=d.get('scale',{})
            if isinstance(scale,dict) and 'Grade 1' in scale.get('domain',[]):
                scale['domain']=GRADES
                if scale.get('range') and all(isinstance(v,str) and v.startswith('#') for v in scale['range']):
                    scale['range']=GRADE_COLOURS
                elif scale.get('range') and 'circle' in scale['range']:
                    scale['range']=['circle','square','triangle-up','diamond','cross','triangle-down','triangle-left']
            if d.get('field') in ['grade','properties.grade'] and d.get('type')=='ordinal':
                d['type']='nominal'
            return d
        if isinstance(x,str):
            if x in [f'C{i}' for i in range(1,7)]+['3']:
                return grade_label(x)
            x=x.replace('track_code','grade').replace('Recorded track code','Recorded grade')
            x=x.replace('Source code','Grade').replace('Source-code','Grade').replace('source-code','grade')
            x=x.replace('Track code','Grade').replace('Source Code','Grade').replace('source code','recorded grade')
            for i in range(1,6):x=x.replace(f'C{i}',f'Grade {i}')
            return x.replace('C6','Unclassified')
        return x
    for n in [2,3,7,10,11,13,14]:
        p=next(CHARTS.glob(f'{n:02d}_*.json'))
        p.write_text(json.dumps(change(json.loads(p.read_text())),ensure_ascii=False,indent=2)+'\n')
    symbol_path=CHARTS/'03_trail_symbols.json'
    symbols=json.loads(symbol_path.read_text())
    symbols['height']=600
    for layer in symbols.get('layer',[]):
        for encoding in layer.get('encoding',{}).values():
            if isinstance(encoding,dict) and encoding.get('field')=='grade' and isinstance(encoding.get('legend'),dict):
                encoding['title']='Recorded grade'
    symbol_path.write_text(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n')
    detail_path=CHARTS/'13_region_detail.json'
    detail=json.loads(detail_path.read_text())
    # Council polygons already draw the state edge; avoid downloading a second
    # 586 kB outline solely to stroke the same edge again.
    detail['layer']=[l for l in detail['layer'] if l.get('name')!='detailVictoria']
    for param in detail.get('params',[]):
        if param['name']=='chosenLga':
            areas=sorted({r['lga'] for r in ROWS})
            param['bind']['options']=['All']+areas
            param['bind']['labels']=['All Victoria']+areas
    detail['height']=500
    for layer in detail.get('layer',[]):
        colour=layer.get('encoding',{}).get('color',{})
        if colour.get('field')=='properties.grade':
            colour['legend']={'title':'Recorded grade','orient':'bottom','columns':3,
                              'symbolType':'stroke','symbolStrokeWidth':3,'labelFontSize':12,
                              'titleFontSize':12,'labelLimit':125}
    detail_path.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n')
    supply_path=CHARTS/'02_trail_supply.json'
    def supply_labels(value):
        if isinstance(value,dict):return {k:supply_labels(v) for k,v in value.items()}
        if isinstance(value,list):return [supply_labels(v) for v in value]
        if isinstance(value,str):return value.replace('Baw Baw','Yarra Ranges').replace('233.3 km','95.5 km').replace('146.5 km','153.7 km')
        return value
    supply_path.write_text(json.dumps(supply_labels(json.loads(supply_path.read_text())),ensure_ascii=False,indent=2)+'\n')

    heat=base(340)
    heat.update(data={'url':'data/trails.json'},transform=[{'filter':"datum.grade !== 'Unknown' && datum.gradient !== 'Unknown'"},
        {'aggregate':[{'op':'count','as':'trail_count'}],'groupby':['grade','gradient']}])
    enc={'x':{'field':'grade','type':'ordinal','sort':CODES[:-1],'title':'Recorded grade'},
         'y':{'field':'gradient','type':'ordinal','sort':TERRAINS,'title':None,
              'axis':{'labelLimit':145,'labelExpr':"datum.label === 'Very steep and difficult' ? 'Very steep + difficult' : datum.label"}}}
    heat['layer']=[{'mark':{'type':'rect','stroke':'#ffffff','strokeWidth':2},'encoding':{**enc,
        'color':{'field':'trail_count','type':'quantitative','scale':{'scheme':'blues'},'legend':{'title':'Trails','orient':'bottom'}},
        'tooltip':[{'field':'grade','title':'Grade'},{'field':'gradient','title':'Terrain'},{'field':'trail_count','title':'Trails'}]}},
        {'mark':{'type':'text','fontSize':12,'fontWeight':600},'encoding':{**enc,'text':{'field':'trail_count'},
        'color':{'condition':{'test':'datum.trail_count >= 20','value':'white'},'value':'#183e3b'}}}]
    heat['description']='Joint counts of recorded grades and terrain. Missing grades are excluded; the unclassified record stays separate.'
    heat['padding']={'left':8,'right':8,'top':48,'bottom':8}
    heat['layer'].append({'data':{'values':[{'grade':'Grade 4','gradient':'Short steep hills'}]},
        'mark':{'type':'rect','fill':None,'stroke':'#D55E00','strokeWidth':2.5},'encoding':enc})
    heat['layer'].append({'data':{'values':[{}]},'mark':{'type':'text','align':'left','fontSize':12,'fontWeight':600,'lineBreak':'\n','lineHeight':15,'color':'#24443f'},
        'encoding':{'x':{'value':0},'y':{'value':-28},'text':{'value':'Outlined cell: 20 Grade 4 routes\nrecord short steep hills'}}})
    save(4,heat)

    median=base(340)
    median.update(data={'url':'data/trails.json'},transform=[
        {'aggregate':[{'op':'median','field':'length_km','as':'median_km'},{'op':'count','as':'n'}],'groupby':['grade']},
        {'calculate':"format(datum.median_km,'.1f') + ' km · ' + datum.n + (datum.n === 1 ? ' route' : ' routes')",'as':'label'}])
    enc={'y':{'field':'grade','type':'ordinal','sort':CODES,'title':'Grade'},
         'x':{'field':'median_km','type':'quantitative','title':'Median distance (km)','scale':{'domain':[0,10]}}}
    median['layer']=[{'mark':{'type':'rule','strokeWidth':3,'color':'#bccfc8'},'encoding':{**enc,'x2':{'datum':0}}},
        {'mark':{'type':'point','filled':True,'size':95},'encoding':{**enc,'color':{**COLOUR,'legend':None}}},
        {'mark':{'type':'text','align':'left','dx':10,'fontSize':12,'color':'#24443f'},'encoding':{**enc,'text':{'field':'label'}}}]
    median['description']='Median distance by recorded grade, with group counts. Unclassified and unknown source values remain visible.'
    save(5,median)

    pc=base(470)
    pc.update(data={'url':'data/parallel_points.json'},padding={'left':34,'right':88,'top':55,'bottom':45},
              resolve={'axis':{'x':'independent','y':'independent'},'legend':{'color':'independent'}})
    labels=['Longest matching']+[r['name'] for r in sorted(ROWS,key=lambda r:r['name'])]
    ids=[0]+[r['id'] for r in sorted(ROWS,key=lambda r:r['name'])]
    pc['params']=[{'name':'chosenCode','value':'All','bind':{'input':'select','options':['All']+CODES,'name':'Grade: '}},
        {'name':'chosenLga','value':'All','bind':{'input':'select','options':['All']+sorted({r['lga'] for r in ROWS}),'name':'Area: '}},
        {'name':'pickTrail','value':0,'bind':{'input':'select','options':ids,'labels':labels,'name':'Trail: '}}]
    pc['transform']=[{'filter':"(chosenCode === 'All' || datum.grade === chosenCode) && (chosenLga === 'All' || datum.lga === chosenLga)"},
        {'joinaggregate':[{'op':'max','field':'length_km','as':'max_length'}]}]
    xy={'x':{'field':'axis','type':'quantitative','scale':{'domain':[0,3],'nice':False},'axis':None},
        'y':{'field':'position','type':'quantitative','scale':{'domain':[-40,115],'nice':False},'axis':None}}
    ticks=[]
    for axis,vals in [(0,[(i*25,f'Grade {i+1}') for i in range(5)]+[(-30,'Unclassified')]),
        (1,[(100*(v/95)**.5,str(v)+' km') for v in [0,1,5,20,50,95]]),
        (2,[(i*25,t) for i,t in enumerate(['Under 1 h','1–4 h','Over 4 h','Overnight','Multiple days'])]),
        (3,[(i*25,t) for i,t in enumerate(['Flat','Gentle hills','Short steep','Very steep','Very steep + difficult'])])]:
        for pos,label in vals:ticks.append({'axis':axis,'position':pos,'label':label})
        if axis!=1:ticks.append({'axis':axis,'position':-15,'label':'Unknown' if axis==0 else 'Not recorded'})
    selected="pickTrail === datum.id || (pickTrail === 0 && datum.length_km === datum.max_length)"
    pc['layer']=[{'data':{'values':[{'axis':i,'position':-15,'upper':100} for i in range(4)]},'mark':{'type':'rule','color':'#b8c8c1'},
        'encoding':{**xy,'y2':{'field':'upper'}}},
        {'mark':{'type':'line','opacity':.2,'strokeWidth':1,'color':'#9aaba5'},'encoding':{**xy,'detail':{'field':'id'},'order':{'field':'axis'}}},
        {'transform':[{'filter':selected}],'mark':{'type':'line','strokeWidth':3,'strokeDash':[8,4]},
        'encoding':{**xy,'detail':{'field':'id'},'order':{'field':'axis'},'color':COLOUR,'tooltip':TOOLTIP}},
        {'transform':[{'filter':selected}],'mark':{'type':'point','filled':True,'size':70},
        'encoding':{**xy,'color':{**COLOUR,'legend':None},'tooltip':TOOLTIP}},
        {'data':{'values':ticks},'mark':{'type':'text','align':'left','dx':5,'fontSize':11,'color':'#36544e'},
        'encoding':{**xy,'text':{'field':'label'}}},
        {'data':{'values':[{'axis':i,'position':111,'label':t} for i,t in enumerate(['Grade','Distance','Duration','Terrain'])]},
        'mark':{'type':'text','align':'left','fontWeight':600,'fontSize':12,'color':'#143f3a'},'encoding':{**xy,'text':{'field':'label'}}},
        {'transform':[{'filter':selected},{'filter':'datum.axis === 0'}],
        'mark':{'type':'text','align':'left','fontSize':12,'lineBreak':'\n','lineHeight':15,'color':'#143f3a'},
        'encoding':{'x':{'value':0},'y':{'value':-32},'text':{'field':'annotation'}}},
        {'data':{'values':[{'grade':r['grade'],'lga':r['lga']} for r in ROWS]},
         'transform':[{'calculate':"(chosenCode === 'All' || datum.grade === chosenCode) && (chosenLga === 'All' || datum.lga === chosenLga) ? 1 : 0",'as':'matches'},
                      {'aggregate':[{'op':'sum','field':'matches','as':'n'}]},{'filter':'datum.n === 0'}],
         'mark':{'type':'text','fontSize':14},'encoding':{'x':{'value':30},'y':{'value':180},'text':{'value':'No trails match these filters'}}}]
    pc['description']='One line per trail across source track code, square-root distance, source duration category and terrain. Categorical spacing is not an effort or time scale.'
    save(6,pc)

    mosaic=base(340)
    blocks=json.loads((ROOT/'data/mosaic.json').read_text())
    centres=[]
    for terrain in TERRAINS:
        rows=[r for r in blocks if r['gradient']==terrain]
        if rows:
            centres.append(((min(r['x0'] for r in rows)+max(r['x1'] for r in rows))/2,
                            terrain.replace('Short steep hills','Short steep').replace('Very steep and difficult','Steep + difficult')))
    labels=' : '.join(f'abs(datum.value - {x}) < 0.000001 ? {json.dumps(label)}' for x,label in centres)+" : ''"
    mosaic['data']={'url':'data/mosaic.json'}
    mosaic['layer']=[{'mark':{'type':'rect','stroke':'white','strokeWidth':2},'encoding':{
        'x':{'field':'x0','type':'quantitative','title':'Terrain (width shows kilometre share)',
             'axis':{'values':[x for x,label in centres],'labelExpr':labels,'labelAngle':-45,'labelOverlap':False,'labelLimit':140,'labelFontSize':10},'scale':{'domain':[0,1]}},
        'x2':{'field':'x1'},'y':{'field':'y0','type':'quantitative','title':'Grade mix within terrain','axis':{'format':'.0%'},'scale':{'domain':[0,1]}},
        'y2':{'field':'y1'},'color':COLOUR,'tooltip':[{'field':'gradient','title':'Terrain'},{'field':'grade','title':'Grade'},{'field':'km','format':'.2f','title':'Kilometres'}]}},
        {'transform':[{'calculate':'(datum.x0+datum.x1)/2','as':'cx'},{'calculate':'(datum.y0+datum.y1)/2','as':'cy'},
            {'filter':'(datum.x1-datum.x0) > 0.13 && (datum.y1-datum.y0) > 0.12'}],
        'mark':{'type':'text','fontSize':11,'fontWeight':600},
        'encoding':{'x':{'field':'cx','type':'quantitative'},'y':{'field':'cy','type':'quantitative'},'text':{'field':'grade'},
             'color':{'condition':{'test':"datum.grade === 'Grade 5' || datum.grade === 'Unclassified'",'value':'white'},'value':'#152d2a'}}}]
    mosaic['description']='Mosaic area represents kilometres among records with known terrain and recorded grade. Missing recorded grades are excluded explicitly.'
    mosaic['padding']={'left':8,'right':8,'top':48,'bottom':8}
    mosaic['layer'].append({'data':{'values':[{}]},'mark':{'type':'text','align':'left','fontSize':12,'fontWeight':600,'lineBreak':'\n','lineHeight':15,'color':'#24443f'},
        'encoding':{'x':{'value':0},'y':{'value':-28},'text':{'value':'Short steep hills: 390.82 km\n55.3% of represented kilometres'}}})
    save(8,mosaic)

    strip=base(340)
    strip.update(data={'url':'data/distance_points.json'},mark={'type':'point','filled':True,'size':50,'opacity':.65},
        encoding={'x':{'field':'length_km','type':'quantitative','title':'Recorded distance (km; square-root spacing)',
            'scale':{'type':'sqrt','domain':[0,100]},'axis':{'values':[0,1,5,10,20,40,60,95]}},
        'y':{'field':'grade','type':'ordinal','sort':CODES,'title':'Grade'},
        'yOffset':{'field':'lane','type':'quantitative'},'color':{**COLOUR,'legend':None},'tooltip':TOOLTIP})
    strip['description']='Individual trail distances including missing grade records. Vertical offsets only separate overlapping points.'
    strip['layer']=[{'mark':strip.pop('mark'),'encoding':strip.pop('encoding')}]
    strip['layer'].insert(0,{'data':{'values':[{'km':5}]},'mark':{'type':'rule','color':'#788c85','strokeDash':[4,4]},
        'encoding':{'x':{'field':'km','type':'quantitative','scale':{'type':'sqrt','domain':[0,100]}}}})
    for name,label,align,dx in [('Upper Yarra Walking Track','Upper Yarra · 95 km\nMultiple days','right',-8),
                              ('Track Ninety Six','Track Ninety Six · 34 km\nMultiple days','left',8)]:
        encoding={'x':{'field':'length_km','type':'quantitative','scale':{'type':'sqrt','domain':[0,100]}},
                  'y':{'field':'grade','type':'ordinal','sort':CODES},'yOffset':{'field':'lane','type':'quantitative'}}
        strip['layer'].append({'transform':[{'filter':{'field':'name','equal':name}}],
            'mark':{'type':'point','filled':False,'stroke':'#D55E00','strokeWidth':2,'size':160},'encoding':encoding})
        strip['layer'].append({'transform':[{'filter':{'field':'name','equal':name}}],
            'mark':{'type':'text','align':align,'dx':dx,'dy':-15,'lineBreak':'\n','lineHeight':14,'fontSize':11,'fontWeight':600,'color':'#24443f'},
            'encoding':{**encoding,'text':{'value':label}}})
    save(9,strip)

    duration=base(350)
    duration.update(data={'url':'data/trails.json'}, transform=[
        {'aggregate':[{'op':'count','as':'trails'}],'groupby':['duration_group']},
        {'calculate':"datum.trails + ' trails · ' + format(datum.trails / 195, '.0%')",'as':'label'}])
    enc={'y':{'field':'duration_group','type':'ordinal','sort':DURATIONS,'title':None,'axis':{'labelLimit':135}},
         'x':{'field':'trails','type':'quantitative','title':'Number of walking routes','scale':{'domain':[0,140]}}}
    duration['layer']=[
        {'mark':{'type':'bar','height':25,'cornerRadiusEnd':3},'encoding':{**enc,
         'color':{'condition':{'test':"datum.duration_group === 'Not recorded'",'value':'#D55E00'},'value':'#407b73'}}},
        {'mark':{'type':'text','align':'left','dx':8,'fontSize':12,'fontWeight':600,'color':'#24443f'},
         'encoding':{**enc,'text':{'field':'label'}}}]
    duration['description']='Duration categories in plain counts, including all 195 walking records. Labels state counts and shares; no statistical knowledge or inferred exact hours is required.'
    save(12,duration)
    # Rank denominators follow the complete walking cohort and midpoint councils.
    rank_path=CHARTS/'11_rank_gap.json'
    rank=json.loads(rank_path.read_text())
    count=sum(r['trail_count']>0 for r in json.loads((ROOT/'data/lga_stats.json').read_text()))
    def ranks(value):
        if isinstance(value,list):
            for item in value:ranks(item)
        elif isinstance(value,dict):
            if value.get('field') in ['population_rank','supply_rank','rank']:
                if 'scale' in value:value['scale']['domain']=[0,count+1]
                if 'axis' in value and 'values' in value['axis']:
                    value['axis']['values']=[1]+list(range(5,count,5))+[count]
            for item in value.values():ranks(item)
    ranks(rank)
    rank['description']=f'Population and resident-adjusted walking supply ranks among {count} councils with walking records.'
    rank_path.write_text(json.dumps(rank,ensure_ascii=False,indent=2)+'\n')
    from prepare_overview_map import main as prepare_overview
    prepare_overview()
    from prepare_chart_annotations import main as prepare_insight_annotations
    prepare_insight_annotations()
    def route_status(value):
        if isinstance(value,list):
            for item in value:route_status(item)
        elif isinstance(value,dict):
            tooltip=value.get('tooltip')
            if isinstance(tooltip,list):
                name=next((t.get('field') for t in tooltip if t.get('field') in ['name','properties.name'] and t.get('title')=='Trail'),None)
                field='properties.closure' if name=='properties.name' else 'closure'
                if name and not any(t.get('field')==field for t in tooltip):
                    tooltip.append({'field':field,'title':'Recorded route status'})
            for item in value.values():route_status(item)
    # The ordinary experience and access comparisons do not require recorded grades.
    for p in CHARTS.glob('*.json'):
        spec=json.loads(p.read_text())
        route_status(spec)
        p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
        study=ROOT/'study/annotated_charts'/p.with_suffix('.jsonc').name
        study.write_text('// Displayed Vega-Lite specification. See source_audit.json for verification.\n'+p.read_text())

if __name__=='__main__':
    main()
