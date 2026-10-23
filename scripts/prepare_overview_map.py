#!/usr/bin/env python3
"""Build a Vega slippy-map overview with full official walking-route geometry."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def points(value):
    if isinstance(value[0], (int, float)):
        yield value
    else:
        for child in value:
            yield from points(child)


def frame(coords):
    coords = list(coords)
    xs = [(p[0]+180)/360 for p in coords]
    ys = [(1-math.asinh(math.tan(math.radians(p[1])))/math.pi)/2 for p in coords]
    return {'x': (min(xs)+max(xs))/2, 'y': (min(ys)+max(ys))/2,
            'dx': max(max(xs)-min(xs), .00001), 'dy': max(max(ys)-min(ys), .00001)}


def main():
    features = json.loads((ROOT/'data/trails.geojson').read_text())['features']
    frames = {'0': frame([[140.95, -39.15], [150.05, -34]])}
    for feature in features:
        frames[str(feature['properties']['id'])] = frame(points(feature['geometry']['coordinates']))
    default = frames['0']
    anchors = json.loads((ROOT/'data/lga_label_points.json').read_text())
    routes = json.loads((ROOT/'data/route_label_points.json').read_text())
    upper = next(f['properties'] for f in features if f['properties']['name']=='Upper Yarra Walking Track')
    callouts = []
    for anchor, side, label in [
        (next(a for a in anchors if a['name']=='Murrindindi'), 'left', ['Murrindindi: 32 walking routes', 'The largest recorded council cluster']),
        (next(a for a in routes if a['id']==upper['id']), 'right', ['Upper Yarra Walking Track: 95 km', 'The longest route in this dataset'])]:
        location = frame([[anchor['lon'], anchor['lat']]])
        callouts.append({'mx': location['x'], 'my': location['y'], 'side': side, 'label': label})
    spec = {'$schema': 'https://vega.github.io/schema/vega/v5.json',
            'description': 'Full official walking routes over geographic map tiles. Vega handles projection, pan, zoom, route selection and tooltips.',
            'width': 1100, 'height': 560, 'padding': 0, 'autosize': {'type': 'fit', 'resize': True},
            'background': '#dbe8ee', 'signals': [
                {'name': 'pickTrail', 'value': 0}, {'name': 'reset', 'value': 0},
                {'name': 'zoomIn', 'value': 0}, {'name': 'zoomOut', 'value': 0},
                {'name': 'frames', 'value': frames},
                {'name': 'frame', 'update': 'frames[pickTrail] || frames[0]'},
                {'name': 'fitZoom', 'update': 'clamp(log(min((width-60)/(256*frame.dx),(height-90)/(256*frame.dy)))/LN2,5,16)'},
                {'name': 'zoom', 'init': 'fitZoom', 'on': [
                    {'events': {'signal': 'fitZoom'}, 'update': 'fitZoom'},
                    {'events': {'signal': 'reset'}, 'update': 'fitZoom'},
                    {'events': {'signal': 'zoomIn'}, 'update': 'min(zoom+1,16)'},
                    {'events': {'signal': 'zoomOut'}, 'update': 'max(zoom-1,5)'}]},
                {'name': 'world', 'update': '256 * pow(2,zoom)'},
                {'name': 'tileZoom', 'update': 'floor(zoom)'},
                {'name': 'tileSize', 'update': '256 * pow(2,zoom-tileZoom)'},
                {'name': 'dragStart', 'value': None, 'on': [
                    {'events': 'view:pointerdown', 'update': '[x(),y(),center[0],center[1]]'}]},
                {'name': 'center', 'value': [default['x'], default['y']], 'on': [
                    {'events': {'signal': 'frame'}, 'update': '[frame.x,frame.y]'},
                    {'events': {'signal': 'reset'}, 'update': '[frame.x,frame.y]'},
                    {'events': '[view:pointerdown, window:pointerup] > window:pointermove',
                     'update': 'dragStart ? [clamp(dragStart[2]+(dragStart[0]-x())/world,0,1),clamp(dragStart[3]+(dragStart[1]-y())/world,.01,.99)] : center'}]},
                {'name': 'left', 'update': 'center[0]*world-width/2'},
                {'name': 'top', 'update': 'center[1]*world-height/2'},
                {'name': 'tileColumns', 'update': 'ceil(width/tileSize)+1'},
                {'name': 'tileRows', 'update': 'ceil(height/tileSize)+1'}],
            'projections': [{'name': 'mapProjection', 'type': 'mercator',
                             'scale': {'signal': 'world/(2*PI)'},
                             'translate': [{'signal': 'width/2-center[0]*world+world/2'},
                                           {'signal': 'height/2-center[1]*world+world/2'}]}],
            'data': [
                {'name': 'tiles', 'transform': [
                    {'type': 'sequence', 'start': 0, 'stop': {'signal': 'tileColumns*tileRows'}, 'as': 'index'},
                    {'type': 'formula', 'expr': 'floor(left/tileSize)+datum.index%tileColumns', 'as': 'tx'},
                    {'type': 'formula', 'expr': 'floor(top/tileSize)+floor(datum.index/tileColumns)', 'as': 'ty'},
                    {'type': 'filter', 'expr': 'datum.tx>=0 && datum.ty>=0 && datum.tx<pow(2,tileZoom) && datum.ty<pow(2,tileZoom)'},
                    {'type': 'formula', 'expr': "'https://tile.openstreetmap.org/'+tileZoom+'/'+datum.tx+'/'+datum.ty+'.png'", 'as': 'tileUrl'}]},
                {'name': 'routes', 'url': 'data/trails.geojson', 'format': {'type': 'json', 'property': 'features'}},
                {'name': 'callouts', 'values': callouts, 'transform': [
                    {'type': 'filter', 'expr': 'pickTrail===0 && zoom<=8 && width>650'}]},
                {'name': 'selectedRoute', 'source': 'routes', 'transform': [
                    {'type': 'filter', 'expr': 'pickTrail !== 0 && datum.properties.id === pickTrail'}]}],
            'marks': [{'type': 'group', 'name': 'mapSurface', 'clip': True,
                       'encode': {'update': {'width': {'signal': 'width'}, 'height': {'signal': 'height'}}},
                       'marks': [
                           {'type': 'image', 'interactive': False, 'from': {'data': 'tiles'},
                            'encode': {'update': {'url': {'field': 'tileUrl'},
                                                 'x': {'signal': 'datum.tx*tileSize-left'},
                                                 'y': {'signal': 'datum.ty*tileSize-top'},
                                                 'width': {'signal': 'tileSize'}, 'height': {'signal': 'tileSize'}}}},
                           {'type': 'shape', 'name': 'walkingRoutes', 'from': {'data': 'routes'},
                            'encode': {'update': {'fill': {'value': None}, 'stroke': {'value': '#3155d9'},
                                                 'strokeWidth': {'value': 2.3},
                                                 'opacity': {'signal': 'pickTrail===0 ? .95 : .25'},
                                                 'tooltip': {'signal': "{'Trail':datum.properties.name,'Recorded grade':datum.properties.grade,'Distance (km)':datum.properties.length_km,'Duration':datum.properties.duration_group,'Recorded route status':datum.properties.closure,'Council':datum.properties.lga}"}}},
                            'transform': [{'type': 'geoshape', 'projection': 'mapProjection'}]},
                           {'type': 'shape', 'name': 'selectedWalkingRoute', 'from': {'data': 'selectedRoute'},
                            'encode': {'update': {'fill': {'value': None}, 'stroke': {'value': '#D55E00'},
                                                 'strokeWidth': {'value': 4}, 'tooltip': {'signal': "{'Trail':datum.properties.name,'Recorded grade':datum.properties.grade,'Distance (km)':datum.properties.length_km,'Duration':datum.properties.duration_group,'Recorded route status':datum.properties.closure}"}}},
                            'transform': [{'type': 'geoshape', 'projection': 'mapProjection'}]},
                           {'type': 'rule', 'interactive': False, 'from': {'data': 'callouts'},
                            'encode': {'update': {'x': {'signal': 'datum.mx*world-left'}, 'y': {'signal': 'datum.my*world-top'},
                                                 'x2': {'signal': "datum.side==='left' ? 38 : width-280"}, 'y2': {'value': 70},
                                                 'stroke': {'value': '#405952'}, 'strokeDash': {'value': [4,3]}}}},
                           {'type': 'symbol', 'interactive': False, 'from': {'data': 'callouts'},
                            'encode': {'update': {'x': {'signal': 'datum.mx*world-left'}, 'y': {'signal': 'datum.my*world-top'},
                                                 'size': {'value': 150}, 'fill': {'value': 'white'}, 'stroke': {'value': '#405952'}}}},
                           {'type': 'rect', 'interactive': False, 'from': {'data': 'callouts'},
                            'encode': {'update': {'x': {'signal': "datum.side==='left' ? 20 : width-300"}, 'y': {'value': 15},
                                                 'width': {'value': 280}, 'height': {'value': 56},
                                                 'fill': {'value': '#ffffff'}, 'fillOpacity': {'value': .95}, 'cornerRadius': {'value': 5}}}},
                           {'type': 'text', 'interactive': False, 'from': {'data': 'callouts'},
                            'encode': {'update': {'x': {'signal': "datum.side==='left' ? 30 : width-290"}, 'y': {'value': 29},
                                                 'text': {'field': 'label'}, 'fontSize': {'value': 13}, 'lineHeight': {'value': 20},
                                                 'fontWeight': {'value': 600}, 'fill': {'value': '#183c36'},
                                                 'baseline': {'value': 'top'}}}}]}]}
    (ROOT/'charts/01_trail_network.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
