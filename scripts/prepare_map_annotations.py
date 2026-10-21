#!/usr/bin/env python3
"""Prepare label anchors from the displayed geometry, not estimated locations.

LGA anchors lie inside their polygon. Trail anchors lie on a displayed route
segment near the existing representative location; they are not trail entrances.
"""
import json
import math
import pathlib
import textwrap
from rebuild_data import in_feature

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'


def vertices(value):
    if isinstance(value[0],(int,float)):
        yield value
    else:
        for item in value:yield from vertices(item)


def polygon_anchor(feature):
    geometry=feature['geometry']
    polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
    def twice_area(ring):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))
    polygon=max(polygons,key=lambda p:abs(twice_area(p[0])))
    ring=polygon[0]
    area=twice_area(ring)
    if area:
        cx=sum((a[0]+b[0])*(a[0]*b[1]-b[0]*a[1]) for a,b in zip(ring,ring[1:]+ring[:1]))/(3*area)
        cy=sum((a[1]+b[1])*(a[0]*b[1]-b[0]*a[1]) for a,b in zip(ring,ring[1:]+ring[:1]))/(3*area)
        if in_feature([cx,cy],feature):return cx,cy
    # Intersect a horizontal scanline with all rings; choose an interior interval.
    y=(min(v[1] for v in ring)+max(v[1] for v in ring))/2
    intersections=[]
    for r in polygon:
        for a,b in zip(r,r[1:]+r[:1]):
            if (a[1]>y)!=(b[1]>y):intersections.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
    intersections.sort()
    candidates=[((left+right)/2,y,right-left) for left,right in zip(intersections,intersections[1:])
                if in_feature([(left+right)/2,y],feature)]
    if not candidates:raise ValueError('Cannot find an interior label anchor')
    cx,cy,_=max(candidates,key=lambda item:item[2])
    return cx,cy


def route_anchor(geometry,point):
    lines=geometry['coordinates'] if geometry['type']=='MultiLineString' else [geometry['coordinates']]
    best=None
    for line in lines:
        for a,b in zip(line,line[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]
            t=max(0,min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
            x,y=a[0]+t*dx,a[1]+t*dy
            candidate=((x-point[0])**2+(y-point[1])**2,x,y)
            if best is None or candidate<best:best=candidate
    if best is None:raise ValueError('Empty route')
    return best[1],best[2]


def mercator_frame(features):
    points=[p for f in features for p in vertices(f['geometry']['coordinates'])]
    lo,hi=min(p[0] for p in points),max(p[0] for p in points)
    ys=[math.log(math.tan(math.pi/4+math.radians(p[1])/2)) for p in points]
    bottom,top=min(ys),max(ys)
    return [(lo+hi)/2,math.degrees(2*math.atan(math.exp((bottom+top)/2))-math.pi/2),
            math.radians(hi-lo),top-bottom]


def main():
    lgas=json.loads((DATA/'lga.geojson').read_text())['features']
    outline=json.loads((DATA/'victoria_outline.geojson').read_text())
    routes=json.loads((DATA/'trails.geojson').read_text())['features']
    records=json.loads((DATA/'trails.json').read_text())
    region_points=[]
    for f in lgas+[outline]:
        lon,lat=polygon_anchor(f)
        region_points.append({'name':f['properties']['name'],'lon':lon,'lat':lat,
                              'meaning':'Interior anchor for a regional label, not a trail location'})
    route_points=[]
    by_id={r['id']:r for r in records}
    for f in routes:
        r=by_id[f['properties']['id']]
        lon,lat=route_anchor(f['geometry'],[r['longitude'],r['latitude']])
        route_points.append({'id':r['id'],'lon':lon,'lat':lat,
                             'name_label':textwrap.fill(r['name'],width=26,break_long_words=False,break_on_hyphens=False),
                             'meaning':'Point on displayed route geometry, not an entrance'})
    for name,rows in [('lga_label_points.json',region_points),('route_label_points.json',route_points)]:
        (DATA/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    frames={'All':mercator_frame(lgas)}
    for f in lgas:
        name=f['properties']['name']
        frames[name]=mercator_frame([f]+[t for t in routes if t['properties']['lga']==name])
    # Keep the reserved annotation band free of geographic content after a refresh.
    for num in [2,3,13]:
        p=next((ROOT/'charts').glob(f'{num:02d}_*.json'))
        d=json.loads(p.read_text())
        if num==13:
            for param in d.get('params',[]):
                if param['name']=='regionFrame':param['expr']=json.dumps(frames,separators=(',',':'))+'[chosenLga]'
        else:
            for param in d.get('params',[]):
                if param['name']=='mapFrame':param['expr']=json.dumps(frames['All'],separators=(',',':'))
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        (ROOT/'study/annotated_charts'/p.with_suffix('.jsonc').name).write_text('// Current displayed specification; see DATA_AND_CAVEATS.md for methods.\n'+p.read_text())
    print(f'Prepared {len(region_points)} interior region anchors and {len(route_points)} exact route anchors.')


if __name__=='__main__':main()
