(() => {
"use strict";
const bundle = window.TRAIL_BUNDLE;
const clone = value => JSON.parse(JSON.stringify(value));
const trails = clone(bundle["data/trails.json"]);
const areas = bundle["data/lga.geojson"].features;
const victoriaOutline = bundle["data/victoria_outline.geojson"];
const charts = [
 ["#chart-01","charts/01_trail_network.json"],["#chart-02","charts/02_lga_access.json"],
 ["#chart-03","charts/03_trail_symbols.json"],["#chart-04","charts/04_challenge_heatmap.json"],
 ["#chart-05","charts/05_length_ridgeline.json"],["#chart-06","charts/06_parallel_coordinates.json"],
 ["#chart-07","charts/07_flow_network.json"],["#chart-08","charts/08_terrain_mosaic.json"],
 ["#chart-09","charts/09_beeswarm.json"],["#chart-10","charts/10_access_waffle.json"],
 ["#chart-11","charts/11_rank_gap.json"],["#chart-12","charts/12_pace_scatter.json"]
];
const views = new Map(), mapSizes = new Map();
const mapCharts = new Set(["#chart-01","#chart-02","#chart-03"]);
const localPlots = {"#chart-03":"map", "#chart-09":"distance", "#chart-12":"time"};
const defaults = () => ({chosenGrade:"All",chosenLga:"All",maximumKm:95,accessOnly:false,selectedTrail:"",zoom:1});
const states = Object.fromEntries(Object.keys(localPlots).map(id=>[id,defaults()]));
const detailState = {chosenLga:"All",grade:"All",zoom:1};
const supplyState = {chosenLga:"All",metric:"resident",zoom:1};
let insetView = null;
const embedOptions = {actions:{export:true,source:true,compiled:false,editor:false},renderer:"svg",tooltip:{theme:"light"}};
const filterExpression = "(chosenGrade === 'All' || datum.grade === chosenGrade) && (chosenLga === 'All' || datum.lga === chosenLga) && isValid(datum.length_km) && datum.length_km <= maximumKm && (!accessOnly || datum.access === 'Full' || datum.access === 'Partial')";
function inlineData(node) {
 if (Array.isArray(node)) return node.forEach(inlineData);
 if (!node || typeof node !== "object") return;
 if (node.data?.url && bundle[node.data.url]) {
  const source=bundle[node.data.url], property=node.data.format?.property;
  node.data={values:clone(property ? source[property] : source)};
 }
 // Vega specifications use a named data array.
 if (node.url && bundle[node.url]) { node.values=clone(bundle[node.url]); delete node.url; delete node.format; }
 Object.values(node).forEach(inlineData);
}
function mercatorY(lat) { return Math.log(Math.tan(Math.PI/4+lat*Math.PI/360)); }
function mapState(selector) {
 return selector === "#chart-01" ? {chosenLga:"All",zoom:1} : selector === "#chart-02" ? supplyState : selector === "#network-detail" ? detailState : states[selector];
}
function mapPosition(selector) {
 const state=mapState(selector), selected=state.chosenLga === "All" ? areas : areas.filter(a=>a.properties.name===state.chosenLga);
 let west=Infinity,east=-Infinity,south=Infinity,north=-Infinity;
 function visit(c) {
  if(typeof c[0]==="number") {west=Math.min(west,c[0]);east=Math.max(east,c[0]);south=Math.min(south,c[1]);north=Math.max(north,c[1]);}
  else c.forEach(visit);
 }
 selected.forEach(a=>visit(a.geometry.coordinates));
 const [width,height]=mapSizes.get(selector), y0=mercatorY(south),y1=mercatorY(north);
 return {mapCenter:[(west+east)/2,(2*Math.atan(Math.exp((y0+y1)/2))-Math.PI/2)*180/Math.PI],
  mapScale:Math.min((width-28)/Math.max((east-west)*Math.PI/180,.001),(height-28)/Math.max(y1-y0,.001))*state.zoom};
}
function mapSpec(spec,selector) {
 mapSizes.set(selector,[spec.width,spec.height]);
 const state=mapState(selector), position=mapPosition(selector);
 spec.params=[...(spec.params||[]),...(!localPlots[selector]?[{name:"chosenLga",value:state.chosenLga}]:[]),...Object.entries(position).map(([name,value])=>({name,value}))];
 spec.projection={type:"mercator",center:{expr:"mapCenter"},scale:{expr:"mapScale"},translate:[spec.width/2,spec.height/2],clipExtent:[[0,0],[spec.width,spec.height]]};
 if(selector === "#chart-02") {
  spec.params.push({name:"metric",value:"resident"});
  spec.transform=[{filter:"chosenLga === 'All' || datum.properties.name === chosenLga"},{calculate:"metric === 'resident' ? datum.properties.trail_km_per_100k : datum.properties.trail_km",as:"supplyValue"}];
  const enc=spec.layer[0].encoding.color;
  enc.field="supplyValue";
  enc.title={expr:"metric === 'resident' ? 'Km per 100,000 residents' : 'Total recorded kilometres'"};
  const resident=Math.max(...areas.map(a=>a.properties.trail_km_per_100k||0)),total=Math.max(...areas.map(a=>a.properties.trail_km||0));
  enc.scale.domain=[0,{expr:`metric === 'resident' ? ${resident} : ${total}`}];
  for(const layer of spec.layer.slice(1)) {
   layer.transform=[{window:[{op:"row_number",as:"rank"}],sort:[{field:"supplyValue",order:"descending"}]},{filter:"datum.rank === 1"},
    {calculate:"datum.properties.name + '\\n' + format(datum.supplyValue, '.1f') + (metric === 'resident' ? ' km / 100,000' : ' km recorded')",as:"annotation"}];
   layer.mark.align={expr:"datum.properties.annotation_lon > mapCenter[0] ? 'right' : 'left'"};
   layer.mark.dx={expr:"datum.properties.annotation_lon > mapCenter[0] ? -10 : 10"};
   layer.mark.fontSize=12;
  }
  spec.config.legend.gradientLength=Math.min(280,spec.width-40);
 }
 spec.layer.push({name:"selectedRegion",data:{values:[...clone(areas),clone(victoriaOutline)]},
  transform:[{filter:"chosenLga === 'All' ? datum.properties.name === 'Victoria' : datum.properties.name === chosenLga"}],
  mark:{type:"geoshape",fill:null,stroke:selector==="#chart-01"?"#6f8c7e":"#d95d39",strokeWidth:selector==="#chart-01"?1:2.2},
  encoding:{shape:{field:"geometry",type:"geojson"},tooltip:[{field:"properties.name",title:"Area"}]}});
 return spec;
}
function matches(selector) {
 const s=states[selector];
 return trails.filter(t=>(s.chosenGrade==="All"||t.grade===s.chosenGrade)&&(s.chosenLga==="All"||t.lga===s.chosenLga)&&Number.isFinite(t.length_km)&&t.length_km<=s.maximumKm&&(!s.accessOnly||["Full","Partial"].includes(t.access))&&(selector!=="#chart-12"||(Number.isFinite(t.hours)&&t.hours>0)));
}
function keepMapLabelsInside(spec) {
 for (const layer of spec.layer) {
  if (layer.mark?.type !== 'text' || !layer.encoding?.longitude) continue;
  const lon=layer.encoding.longitude.field,lat=layer.encoding.latitude.field;
  const limit=spec.width<500?140:200;
  layer.transform=[...(layer.transform||[]),
   {calculate:`width/2 + mapScale * (datum.${lon}-mapCenter[0]) * 0.0174532925199433`,as:'pointX'},
   {calculate:`height/2 - mapScale * (log(tan(0.7853981633974483+datum.${lat}*0.008726646259971648))-log(tan(0.7853981633974483+mapCenter[1]*0.008726646259971648)))`,as:'pointY'},
   {filter:'datum.pointX > 0 && datum.pointX < width && datum.pointY > 0 && datum.pointY < height'},
   {calculate:`datum.pointX > width/2 ? clamp(datum.pointX-10,${limit+8},width-8) : clamp(datum.pointX+10,8,width-${limit+8})`,as:'labelX'},
   {calculate:'clamp(datum.pointY-16,28,height-30)',as:'labelY'}];
  layer.mark.align={expr:'datum.pointX > width/2 ? "right" : "left"'};layer.mark.dx=0;layer.mark.dy=0;layer.mark.limit=limit;
  delete layer.encoding.longitude;delete layer.encoding.latitude;
  layer.encoding.x={field:'labelX',type:'quantitative',scale:null,axis:null};layer.encoding.y={field:'labelY',type:'quantitative',scale:null,axis:null};
 }
 return spec;
}
function localSpec(spec,selector) {
 const initial={...states[selector],visibleCount:matches(selector).length,distanceExtent:40,timeExtent:50};delete initial.zoom;
 spec.params=[...(spec.params||[]),...Object.entries(initial).map(([name,value])=>({name,value}))];
 const dataNode=selector==="#chart-03"?spec.layer[1]:spec;
 dataNode.transform=[{filter:filterExpression},...(dataNode.transform||[])];
 const points=selector==="#chart-03"?spec.layer[1]:spec.layer[0];
 points.encoding.opacity={condition:{test:"selectedTrail === '' || datum.name === selectedTrail",value:.85},value:.1};
 points.encoding.strokeWidth={condition:{test:"selectedTrail !== '' && datum.name === selectedTrail",value:3},value:.5};
 if(selector==="#chart-03") {
  points.encoding.size.scale={type:"linear",domain:[0,95],range:[22,650]};
  for(const layer of spec.layer.slice(2)) {
   if(layer.data?.values) layer.data.values=layer.data.values.map(t=>({...t,short_name:t.name.replace(/\b(Walking Track|Walking Trail|Walk|Trail|Track)\b/g,'').replace(/\s+/g,' ').trim()}));
   const label=layer.transform?.find(t=>t.as==='label');if(label)label.calculate="datum.short_name + '\\n' + format(datum.length_km, '.1f') + ' km'";
  }
 }
 if(selector==="#chart-09") {
  for(const layer of spec.layer) if(layer.encoding.x?.type==="quantitative") layer.encoding.x.scale={type:"sqrt",domain:[0,{expr:"maximumKm"}],nice:false};
  for(const layer of spec.layer) if(layer.encoding.y?.field==="grade") layer.encoding.y.scale={domain:["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Unknown"]};
  spec.layer[1].transform=[{filter:"maximumKm >= 5"}];spec.layer[2].transform=[{filter:"maximumKm >= 5"}];
 }
 if(selector==="#chart-12") {
  for(const layer of spec.layer) {
   if(layer.encoding.x?.type==="quantitative") layer.encoding.x.scale={domain:[0,{expr:"distanceExtent"}],nice:false};
   if(layer.encoding.y?.type==="quantitative") layer.encoding.y.scale={domain:[0,{expr:"timeExtent"}],nice:false};
  }
 }
 spec.layer.push({data:{values:[{}]},transform:[{filter:"visibleCount === 0"}],mark:{type:"text",fontSize:14,fontWeight:700,color:"#173b37",lineBreak:"\n",stroke:"white",strokeWidth:.5},encoding:{x:{value:{expr:"width/2"}},y:{value:{expr:"height/2"}},text:{value:"No recorded trails match\nTry another grade, area or distance"}}});
 return spec;
}
async function updateLocal(selector) {
 const s=states[selector], prefix=localPlots[selector], found=matches(selector),view=views.get(selector);
 if(!found.some(t=>t.name===s.selectedTrail)) s.selectedTrail="";
 document.querySelector(`#${prefix}-distance-value`).textContent=`${s.maximumKm} km`;
 const area=s.chosenLga==="All"?"Victoria":s.chosenLga;
 const selected=found.find(t=>t.name===s.selectedTrail);
 document.querySelector(`#${prefix}-status`).textContent=`${found.length} of ${selector==="#chart-12"?149:194} ${selector==="#chart-12"?"timed ":""}trails · ${s.chosenGrade==="All"?"all grades":s.chosenGrade} · ≤ ${s.maximumKm} km${selector==="#chart-03"?` · ${area}${s.accessOnly?" · full/partial access":""}`:""}${selected?` · Selected: ${selected.name}`:""}${found.length?"":" · No matching records"}`;
 if(!view)return;
 for(const [name,value] of Object.entries(s)) if(name!=="zoom")view.signal(name,value);
 view.signal("visibleCount",found.length).signal("distanceExtent",Math.max(1,...found.map(t=>t.length_km))*1.08).signal("timeExtent",Math.max(1,...found.map(t=>t.hours||0))*1.08);
 if(selector==="#chart-03") for(const [name,value]of Object.entries(mapPosition(selector)))view.signal(name,value);
 await view.runAsync();
}
function setupLocalControls(selector,prefix) {
 const form=document.querySelector(`#${prefix}-controls`),s=states[selector];
 form.addEventListener("submit",e=>e.preventDefault());
 const read=()=>{
  const area=document.querySelector(`#${prefix}-area`)?.value||"All";
  if(area!==s.chosenLga)s.zoom=1;
  Object.assign(s,{chosenGrade:document.querySelector(`#${prefix}-grade`).value,chosenLga:area,maximumKm:Number(document.querySelector(`#${prefix}-distance`).value),accessOnly:document.querySelector(`#${prefix}-access`)?.checked||false});
  if(selector==="#chart-03")document.querySelector("#map-zoom-value").textContent=`${s.zoom}×`;
  updateLocal(selector);
 };
 form.addEventListener("input",read);
 form.addEventListener("reset",e=>{e.preventDefault();Object.assign(s,defaults());form.querySelectorAll('select').forEach(c=>c.value="All");form.querySelector('input[type=range]').value=95;const access=form.querySelector('input[type=checkbox]');if(access)access.checked=false;if(selector==="#chart-03")document.querySelector("#map-zoom-value").textContent="1×";updateLocal(selector);});
 form.querySelectorAll("[data-preset]").forEach(b=>b.addEventListener("click",()=>{
  if(b.dataset.preset==="short")form.querySelector('input[type=range]').value=5;
  else document.querySelector(`#${prefix}-grade`).value="Grade 3";
  read();
 }));
 if(selector==="#chart-03")for(const action of ["in","out","fit"])document.querySelector(`#map-${action}`).addEventListener("click",()=>{
  s.zoom=action==="fit"?1:Math.max(1,Math.min(4,s.zoom+(action==="in"?.5:-.5)));document.querySelector("#map-zoom-value").textContent=`${s.zoom}×`;updateLocal(selector);
 });
 updateLocal(selector);
}

async function loadChart(selector,specUrl) {
 const host=document.querySelector(selector);
 try {
  let spec=clone(bundle[specUrl]);inlineData(spec);
  if(localPlots[selector])spec=localSpec(spec,selector);
  if(mapCharts.has(selector)) {
   spec.width=Math.max(240,Math.round(host.getBoundingClientRect().width-38));
   // Victoria is broad and shallow. Match the geographical aspect, not a tall page card.
   spec.height=Math.max(190,Math.min(430,Math.round(spec.width/1.4)));
   spec.config.legend.columns=spec.width<500?2:6;
   spec.config.legend.direction="horizontal";spec.config.legend.labelLimit=150;
   if(selector==="#chart-01") {
    spec.config.legend.labelColor="#334155";spec.config.legend.titleColor="#0f172a";
    for(const layer of spec.layer)if(layer.mark?.type==="text") {layer.mark.fontSize=11;layer.mark.limit=170;}
   }
   if(spec.width<500) for(const layer of spec.layer)if(layer.mark?.type==="text") {layer.mark.fontSize=10;layer.mark.limit=140;}
   spec=mapSpec(spec,selector);
   if(selector!=="#chart-01")spec=keepMapLabelsInside(spec);
  }
  if(selector==="#chart-06") {spec.width=Math.max(560,Math.round(host.getBoundingClientRect().width-170));}
    if (!mapCharts.has(selector) && selector !== "#chart-06") {
      const width = Math.round(host.getBoundingClientRect().width);
      const axisRoom = selector === "#chart-04" || selector === "#chart-07" || selector === "#chart-11" ? 175 : selector === "#chart-08" || selector === "#chart-09" || selector === "#chart-12" ? 95 : 65;
      spec.width = selector === "#chart-10" ? Math.min(500, width - 34) : Math.max(200, width - axisRoom);
      if (selector === "#chart-07" || selector === "#chart-08") {
        // Fit the complete figure, including its axes, into the embed content box.
        spec.width = width - 38;
        if (width < 400) {
          if (selector === "#chart-07") {
            spec.config.legend.columns = 1;
            spec.layer[1].mark.fontSize = 9;
            for (const layer of spec.layer) if (layer.encoding.y.axis) layer.encoding.y.axis.labelLimit = 125;
          }
          if (selector === "#chart-08") {
            spec.layer[0].encoding.x.axis.title = ["Terrain", "Column width = share of kilometres"];
            spec.layer[0].encoding.x.axis.titleFontSize = 11;
            spec.layer[0].encoding.x.axis.labelFontSize = 10;
            spec.layer[0].encoding.x.axis.labelAngle = -55;
            spec.layer[1].mark.dy = 10;
            spec.layer[2].mark.fontSize = 11;
            spec.layer[1].transform[0].filter += " && datum.x1 - datum.x0 > 0.09";
          }
        }
      }
      if (selector === "#chart-05") {
        for (const layer of spec.layer) layer.encoding.x.scale = {domain:[0,spec.width < 320 ? 32 : 27],nice:false};
      }
      if (selector === "#chart-10") {
        spec.height = Math.round(spec.width * 10 / 14);
        spec.layer[0].mark.size = Math.pow(spec.width / 14 * 0.88, 2);
        spec.layer[1].mark.size = spec.layer[0].mark.size;
      }
      if (selector === "#chart-09" && width < 560) {
        for(const layer of spec.layer) if(layer.encoding.x?.title) layer.encoding.x.title=["Trail distance (km)","square-root scale"];
      }
      if (width < 560) {
        spec.config.legend.columns = selector === "#chart-07" && width < 400 ? 1 : 2;
        spec.config.legend.direction = "horizontal";
        spec.config.legend.labelLimit = 145;
        for (const layer of spec.layer || []) {
          if (layer.mark?.type === "text") layer.mark.limit = selector === "#chart-09" || selector === "#chart-12" ? 135 : 170;
        }
      }
    }
  const result=await vegaEmbed(host,spec,embedOptions);
  views.set(selector,result.view);
  if(localPlots[selector]) {
   result.view.addEventListener("click",(_event,item)=>{
    const name=item?.datum?.name;
    if(!trails.some(t=>t.name===name))return;
    const s=states[selector];s.selectedTrail=s.selectedTrail===name?"":name;updateLocal(selector);
   });
   await updateLocal(selector);
  }
  if(selector==="#chart-02") {
   result.view.addEventListener("click",(_event,item)=>{
    const area=item?.datum?.properties?.name;
    if(!areas.some(a=>a.properties.name===area))return;
    supplyState.chosenLga=area;document.querySelector("#supply-area").value=area;updateSupply();
   });
   await updateSupply();
  }
  if(selector==="#chart-06")setupParallel(result.view);
  if(selector==="#chart-01")await addNetworkInset();
 } catch(error) {
  const message=document.createElement("p");message.className="chart-error";message.textContent=`This view could not be loaded. ${error.message}`;host.replaceChildren(message);console.error(error);
 }
}

function setupParallel(view) {
 const grade=document.querySelector("#parallel-grade"),picker=document.querySelector("#parallel-trail");
 function update() {
  const selected=trails.filter(t=>grade.value==="All"||t.grade===grade.value),previous=picker.value;
  picker.replaceChildren(new Option("No trail selected",""));
  selected.slice().sort((a,b)=>a.name.localeCompare(b.name)).forEach(t=>picker.add(new Option(t.name,t.name)));
  picker.value=selected.some(t=>t.name===previous)?previous:"";
  view.signal("selectedGrade",grade.value).signal("selectedTrail",picker.value).runAsync();
  document.querySelector("#parallel-status").textContent=`${selected.length} of 194 trail profiles emphasised · ${grade.value==="All"?"all grades":grade.value}${picker.value?` · Tracing ${picker.value}`:" · Choose a trail or try an outlier"}`;
 }
 grade.addEventListener("change",update);picker.addEventListener("change",update);
 document.querySelectorAll("[data-parallel-trail]").forEach(b=>b.addEventListener("click",()=>{grade.value="All";update();picker.value=b.dataset.parallelTrail;update();}));
 document.querySelector("#parallel-reset").addEventListener("click",()=>{grade.value="All";picker.value="";update();});
 update();
}
async function updateSupply() {
 const selected=supplyState.chosenLga==="All"?areas:areas.filter(a=>a.properties.name===supplyState.chosenLga);
 const measure=supplyState.metric==="resident"?"kilometres per 100,000 residents":"total recorded kilometres";
 document.querySelector("#supply-status").textContent=`${supplyState.chosenLga==="All"?"Victoria · 79 councils":supplyState.chosenLga} · ${measure}${selected.length===1?` · ${selected[0].properties.trail_count} recorded trails`:""}`;
 const view=views.get("#chart-02");if(!view)return;
 view.signal("chosenLga",supplyState.chosenLga).signal("metric",supplyState.metric);
 for(const [name,value]of Object.entries(mapPosition("#chart-02")))view.signal(name,value);
 await view.runAsync();
}
function syncInset() {
 if(!insetView)return;
 const selected=trails.filter(t=>(detailState.chosenLga==="All"||t.lga===detailState.chosenLga)&&(detailState.grade==="All"||t.grade===detailState.grade));
 const area=detailState.chosenLga==="All"?"Victoria":detailState.chosenLga;
 document.querySelector(".inset-heading").textContent=`${area} · ${selected.length} trails${detailState.grade==="All"?"":` · ${detailState.grade}`}`;
 document.querySelector("#detail-zoom-value").textContent=`${detailState.zoom}×`;
 insetView.signal("chosenLga",detailState.chosenLga).signal("detailGrade",detailState.grade).signal("detailCount",selected.length);
 for(const [name,value]of Object.entries(mapPosition("#network-detail")))insetView.signal(name,value);
 insetView.runAsync();
}

async function addNetworkInset() {
  const box = document.querySelector('#network-inset');
  const mount = document.querySelector('#detail-map');
  const width = Math.max(240,Math.round(box.getBoundingClientRect().width-30));
  const height = Math.max(200,Math.min(275,Math.round(width*.62)));
  mapSizes.set("#network-detail",[width,height]);
  const position=mapPosition("#network-detail");
  const gradeScale={domain:["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Unknown"],range:["#2a9d8f","#69b578","#e9c46a","#f4a261","#e76f51","#9aa2a6"]};
  const filtered=[{filter:"(chosenLga === 'All' || datum.lga === chosenLga) && (detailGrade === 'All' || datum.grade === detailGrade)"},{window:[{op:"row_number",as:"rank"}],sort:[{field:"length_km",order:"descending"},{field:"name",order:"ascending"}]},{filter:"datum.rank === 1"},{calculate:"datum.name + '\\n' + format(datum.length_km, '.1f') + ' km'",as:"label"}];
  const annotationTrails=trails.map(t=>({...t,short_name:t.name.replace(/\b(Walking Track|Walk|Trail|Track)\b/g, "").replace(/\s+/g," ").trim()}));
  filtered[filtered.length-1].calculate="datum.short_name + '\\n' + format(datum.length_km, '.1f') + ' km'";
  filtered.push(
    {calculate:"width/2 + mapScale * (datum.longitude-mapCenter[0]) * 0.0174532925199433",as:"pointX"},
    {calculate:"height/2 - mapScale*(log(tan(0.7853981633974483+datum.latitude*0.008726646259971648))-log(tan(0.7853981633974483+mapCenter[1]*0.008726646259971648)))",as:"pointY"},
    {filter:"datum.pointX > 8 && datum.pointX < width-8 && datum.pointY > 8 && datum.pointY < height-8"},
    {calculate:"datum.pointX > width/2 ? clamp(datum.pointX-10,155,width-8) : clamp(datum.pointX+10,8,width-155)",as:"labelX"},
    {calculate:"clamp(datum.pointY-16,30,height-30)",as:"labelY"}
  );
  const annotation={data:{values:clone(annotationTrails)},transform:filtered,
    mark:{type:"text",align:{expr:"datum.longitude > mapCenter[0] ? 'right' : 'left'"},dx:0,dy:0,fontSize:11,fontWeight:700,lineBreak:"\n",limit:150,color:"#173b37"},
    encoding:{x:{field:"labelX",type:"quantitative",scale:null,axis:null},y:{field:"labelY",type:"quantitative",scale:null,axis:null},text:{field:"label"},tooltip:[{field:"name",title:"Longest matching trail"},{field:"length_km",title:"Distance (km)"}]}};
  const halo=clone(annotation);halo.mark.stroke="white";halo.mark.strokeWidth=3;
  const ring={data:{values:clone(annotationTrails)},transform:clone(filtered),mark:{type:"point",filled:false,size:150,stroke:"#a64629",strokeWidth:2},encoding:{longitude:{field:"longitude",type:"quantitative"},latitude:{field:"latitude",type:"quantitative"}}};
  const spec={
    $schema:"https://vega.github.io/schema/vega-lite/v5.json",width,height,padding:0,background:"#ffffff",
    config:{view:{stroke:null},text:{font:"Inter"}},
    params:[{name:"chosenLga",value:detailState.chosenLga},{name:"detailGrade",value:detailState.grade},{name:"detailCount",value:194},...Object.entries(position).map(([name,value])=>({name,value}))],
    projection:{type:"mercator",center:{expr:"mapCenter"},scale:{expr:"mapScale"},translate:[width/2,height/2],clipExtent:[[0,0],[width,height]]},
    layer:[
      {name:"detailBase",data:{values:clone(areas)},mark:{type:"geoshape",fill:"#edf3ef",stroke:"#b4c4bc",strokeWidth:.6},encoding:{shape:{field:"geometry",type:"geojson"},tooltip:[{field:"properties.name",title:"Area"}]}},
      {data:{values:clone(bundle["data/trails.geojson"].features)},transform:[{filter:"(chosenLga === 'All' || datum.properties.lga === chosenLga) && (detailGrade === 'All' || datum.properties.grade === detailGrade)"}],mark:{type:"geoshape",filled:false,strokeWidth:2.5},encoding:{shape:{field:"geometry",type:"geojson"},color:{field:"properties.grade",type:"nominal",scale:gradeScale,legend:null},tooltip:[{field:"properties.name",title:"Trail"},{field:"properties.length_km",title:"Distance (km)"},{field:"properties.grade",title:"Grade"}]}},
      {name:"detailRegion",data:{values:[...clone(areas),clone(victoriaOutline)]},transform:[{filter:"chosenLga === 'All' ? datum.properties.name === 'Victoria' : datum.properties.name === chosenLga"}],mark:{type:"geoshape",fill:null,stroke:"#d95d39",strokeWidth:2},encoding:{shape:{field:"geometry",type:"geojson"},tooltip:[{field:"properties.name",title:"Selected area"}]}},
      ring,halo,annotation,
      {data:{values:[{}]},transform:[{filter:"detailCount === 0"}],mark:{type:"text",lineBreak:"\n",fontSize:12,fontWeight:700,color:"#173b37",stroke:"white",strokeWidth:.4},encoding:{x:{value:width/2},y:{value:height/2},text:{value:"No recorded trails\nin this selection"}}}
    ]
  };
  const result=await vegaEmbed(mount,spec,{actions:false,renderer:"svg",tooltip:{theme:"light"}});
  insetView=result.view;
  insetView.addEventListener("click",(_event,item)=>{
    const name=item?.datum?.properties?.name;
    if (name === "Victoria" || areas.some(f=>f.properties.name === name)) {
      detailState.chosenLga=name === "Victoria" ? "All" : name;detailState.zoom=1;document.querySelector('#detail-area').value=detailState.chosenLga;syncInset();
    }
  });
  syncInset();
}

for (const [selector,prefix] of Object.entries(localPlots)) setupLocalControls(selector,prefix);
document.querySelector('#supply-area').addEventListener('change',e=>{supplyState.chosenLga=e.target.value;updateSupply();});
document.querySelectorAll('[name=supply-metric]').forEach(r=>r.addEventListener('change',()=>{supplyState.metric=r.value;updateSupply();}));
document.querySelector('#supply-reset').addEventListener('click',()=>{supplyState.chosenLga='All';supplyState.metric='resident';document.querySelector('#supply-area').value='All';document.querySelector('[name=supply-metric][value=resident]').checked=true;updateSupply();});
document.querySelector('#detail-area').addEventListener('change',e=>{detailState.chosenLga=e.target.value;detailState.zoom=1;syncInset();});
document.querySelector('#detail-grade').addEventListener('change',e=>{detailState.grade=e.target.value;syncInset();});
document.querySelectorAll('[data-detail-area]').forEach(b=>b.addEventListener('click',()=>{detailState.chosenLga=b.dataset.detailArea;detailState.zoom=1;document.querySelector('#detail-area').value=detailState.chosenLga;syncInset();}));
document.querySelector('#detail-reset').addEventListener('click',()=>{Object.assign(detailState,{chosenLga:'All',grade:'All',zoom:1});document.querySelector('#detail-area').value='All';document.querySelector('#detail-grade').value='All';syncInset();});
for (const action of ['in','out','fit']) document.querySelector(`#detail-${action}`).addEventListener('click',()=>{detailState.zoom=action==='fit'?1:Math.max(1,Math.min(4,detailState.zoom+(action==='in'?.5:-.5)));syncInset();});
const stats=bundle['data/stats.json'];
document.querySelector('#stat-trails').textContent=stats.trail_count.toLocaleString();
document.querySelector('#stat-km').textContent=`${Math.round(stats.total_km).toLocaleString()} km`;
document.querySelector('#stat-median').textContent=`${stats.median_km.toFixed(1)} km`;
document.querySelector('#stat-access').textContent=stats.accessible_count;
updateSupply();
charts.forEach(([selector,url])=>loadChart(selector,url));
})();
