(() => {
"use strict";
const charts = [
  ["#chart-01", "charts/01_trail_network.json"],
  ["#chart-02", "charts/02_lga_access.json"],
  ["#chart-03", "charts/03_trail_symbols.json"],
  ["#chart-04", "charts/04_challenge_heatmap.json"],
  ["#chart-05", "charts/05_length_ridgeline.json"],
  ["#chart-06", "charts/06_alluvial.json"],
  ["#chart-07", "charts/07_flow_network.json"],
  ["#chart-08", "charts/08_terrain_mosaic.json"],
  ["#chart-09", "charts/09_beeswarm.json"],
  ["#chart-10", "charts/10_access_waffle.json"],
  ["#chart-11", "charts/11_rank_gap.json"],
  ["#chart-12", "charts/12_pace_scatter.json"],
];
const linkedCharts = new Set(["#chart-03", "#chart-09", "#chart-12"]);
const linkedViews = new Map();
const mapViews = new Map();
const mapSizes = new Map();
const mapCharts = new Set(["#chart-01", "#chart-02", "#chart-03"]);
const bundle = window.TRAIL_BUNDLE;
let mapZoom = 1;
const clone = (value) => JSON.parse(JSON.stringify(value));
const areas = bundle["data/lga.geojson"].features;
const victoriaOutline = bundle["data/victoria_outline.geojson"];
function inlineData(node) {
  if (Array.isArray(node)) { node.forEach(inlineData); return; }
  if (!node || typeof node !== "object") return;
  if (node.data?.url && bundle[node.data.url]) {
    const source = bundle[node.data.url];
    const property = node.data.format?.property;
    node.data = { values: clone(property ? source[property] : source) };
  }
  Object.values(node).forEach(inlineData);
}
function mercatorY(latitude) {
  return Math.log(Math.tan(Math.PI / 4 + latitude * Math.PI / 360));
}
function mapPosition(selector) {
  const areaName = selector === "#chart-01" ? "All" : state.chosenLga;
  const selected = areaName === "All" ? areas : areas.filter(area => area.properties.name === areaName);
  let west=Infinity, east=-Infinity, south=Infinity, north=-Infinity;
  function visit(coordinates) {
    if (typeof coordinates[0] === "number") {
      west=Math.min(west,coordinates[0]); east=Math.max(east,coordinates[0]);
      south=Math.min(south,coordinates[1]); north=Math.max(north,coordinates[1]);
    } else coordinates.forEach(visit);
  }
  selected.forEach(area => visit(area.geometry.coordinates));
  const [width,height] = mapSizes.get(selector);
  const y0=mercatorY(south), y1=mercatorY(north);
  const centerLat=(2*Math.atan(Math.exp((y0+y1)/2))-Math.PI/2)*180/Math.PI;
  return {
    mapCenter: [(west+east)/2,centerLat],
    mapScale: Math.min((width-60)/Math.max((east-west)*Math.PI/180,0.001),(height-60)/Math.max(y1-y0,0.001))*(selector === "#chart-01" ? 1 : mapZoom),
  };
}
function mapSpec(spec, selector) {
  mapSizes.set(selector,[spec.width,spec.height]);
  const position=mapPosition(selector);
  spec.params=[...(spec.params || []),
    ...(!linkedCharts.has(selector) ? [{name:"chosenLga",value:state.chosenLga}] : []),
    ...Object.entries(position).map(([name,value])=>({name,value}))];
  spec.projection={type:"mercator",center:{expr:"mapCenter"},scale:{expr:"mapScale"},
    translate:[spec.width/2,spec.height/2],clipExtent:[[0,0],[spec.width,spec.height]]};
  if(selector === "#chart-02") {
    spec.layer[0].encoding.color.scale.domain=[0,Math.max(...areas.map(area=>area.properties.trail_km_per_100k || 0))];
    spec.transform=[...(spec.transform || []),{filter:"chosenLga === 'All' || datum.properties.name === chosenLga"}];
  }
  if(spec.layer) spec.layer.push({
    name:"selectedRegion",
    data:{values:[...clone(areas),clone(victoriaOutline)]},
    transform:[{filter:"chosenLga === 'All' ? datum.properties.name === 'Victoria' : datum.properties.name === chosenLga"}],
    mark:{type:"geoshape",fill:null,stroke:"#d95d39",strokeWidth:2.5,strokeDash:[5,3]},
    encoding:{shape:{field:"geometry",type:"geojson"},tooltip:[{field:"properties.name",title:"Selected area"}]},
  });
  return spec;
}
const state = { chosenGrade: "All", chosenLga: "All", maximumKm: 95, accessOnly: false, selectedTrail: "" };
let trails = clone(bundle["data/trails.json"]);
const embedOptions = {
  actions: { export: true, source: true, compiled: false, editor: false },
  renderer: "svg", tooltip: { theme: "light" },
};
const filterExpression = "(chosenGrade === 'All' || datum.grade === chosenGrade) && (chosenLga === 'All' || datum.lga === chosenLga) && isValid(datum.length_km) && datum.length_km <= maximumKm && (!accessOnly || datum.access === 'Full' || datum.access === 'Partial')";

function linkSpec(spec, selector) {
  spec.params = [...(spec.params || []), ...Object.entries(state).map(([name, value]) => ({ name, value }))];
  const dataNode = selector === "#chart-03" ? spec.layer[1] : spec;
  dataNode.transform = [{ filter: filterExpression }, ...(dataNode.transform || [])];
  const pointNode = (selector === "#chart-12" || selector === "#chart-09") ? spec.layer[0] : dataNode;
  pointNode.encoding.opacity = {
    condition: { test: "selectedTrail === '' || datum.name === selectedTrail", value: 0.85 }, value: 0.12,
  };
  pointNode.encoding.strokeWidth = {
    condition: { test: "selectedTrail !== '' && datum.name === selectedTrail", value: 3 }, value: 0.5,
  };
  // Fit the whole state in the shortlist map rather than reusing the wide map's fixed scale.
  if (selector === "#chart-03") { spec.projection = { type: "mercator" }; spec.layer[1].encoding.size.scale.domain=[0,95]; }
  return spec;
}

async function loadChart(selector, specUrl) {
  const host = document.querySelector(selector);
  try {
    let spec = clone(bundle[specUrl]);
    inlineData(spec);
    if (linkedCharts.has(selector)) spec = linkSpec(spec, selector);
    if (mapCharts.has(selector)) {
      // Match the geographical viewport to the actual card width.
      spec.width = Math.max(280, Math.round(host.getBoundingClientRect().width - 12));
      spec.height = Math.max(260, Math.min(720, Math.round(spec.width * 0.68)));
      spec.config.legend.columns = spec.width < 560 ? 2 : 6;
      spec.config.legend.direction = "horizontal";
      spec.config.legend.labelLimit = spec.width < 560 ? 150 : 240;
      if (spec.width < 560) {
        if (selector === "#chart-01") {
          for (const layer of spec.layer.slice(3)) {
            layer.mark.align = "right"; layer.mark.dx = -8;
            layer.encoding.text.value = "Upper Yarra · 95 km";
          }
        }
        for (const layer of spec.layer || []) {
          if (layer.mark?.type === "text") { layer.mark.fontSize = 11; layer.mark.limit = 145; }
        }
      }
      spec = mapSpec(spec, selector);
    }
    if (!mapCharts.has(selector) && selector !== "#chart-06") {
      const width = Math.round(host.getBoundingClientRect().width);
      const axisRoom = selector === "#chart-04" || selector === "#chart-07" || selector === "#chart-11" ? 175 : selector === "#chart-08" || selector === "#chart-09" || selector === "#chart-12" ? 95 : 65;
      spec.width = selector === "#chart-10" ? Math.min(500, width - 34) : Math.max(200, width - axisRoom);
      if (selector === "#chart-05") {
        for (const layer of spec.layer) layer.encoding.x.scale = {domain:[0,spec.width < 320 ? 32 : 27],nice:false};
      }
      if (selector === "#chart-10") {
        spec.height = Math.round(spec.width * 10 / 14);
        spec.layer[0].mark.size = Math.pow(spec.width / 14 * 0.88, 2);
        spec.layer[1].mark.size = spec.layer[0].mark.size;
      }
      if (width < 560) {
        spec.config.legend.columns = 2;
        spec.config.legend.direction = "horizontal";
        spec.config.legend.labelLimit = 145;
        for (const layer of spec.layer || []) {
          if (layer.mark?.type === "text") layer.mark.limit = selector === "#chart-09" || selector === "#chart-12" ? 135 : 170;
        }
      }
    }
    const result = await vegaEmbed(host, spec, embedOptions);
    if (selector === "#chart-06") {
      const picker = document.querySelector("#alluvial-grade");
      const summary = document.querySelector("#alluvial-summary");
      const counts = trails.reduce((out, trail) => { out[trail.grade] = (out[trail.grade] || 0) + 1; return out; }, {});
      function showSelection(grade) {
        picker.value = grade || "All";
        summary.textContent = grade
          ? `${grade}: ${counts[grade]} of ${trails.length} trails highlighted. Column totals describe all trails.`
          : `All ${trails.length} trails shown. Ribbon widths and column totals represent trail counts.`;
      }
      picker.addEventListener("change", () => {
        const grade = picker.value === "All" ? null : picker.value;
        result.view.signal("selectedGrade", grade).runAsync();
        showSelection(grade);
      });
      result.view.addSignalListener("selectedGrade", (_name, grade) => showSelection(grade));
      showSelection(null);
    }
    if (linkedCharts.has(selector)) {
      linkedViews.set(selector, result.view);
      result.view.addEventListener("click", (_event, item) => {
        const name = item?.datum?.name;
        if (!trails.some((trail) => trail.name === name)) return;
        state.selectedTrail = state.selectedTrail === name ? "" : name;
        updateShortlist();
      });
    }
    if (mapCharts.has(selector)) {
      mapViews.set(selector,result.view);
      result.view.addEventListener("click", (_event,item) => {
        const area=item?.datum?.properties?.name;
        if (area === "Victoria" || areas.some(feature=>feature.properties.name === area)) {
          state.chosenLga=area === "Victoria" ? "All" : area; mapZoom=1; updateShortlist();
        }
      });
    }
    if (selector === "#chart-01") {
      result.view.addSignalListener("gradePick", (_name, selected) => {
        const picked = Object.entries(selected || {}).find(([key]) => key.endsWith("grade"))?.[1];
        detailGrade = Array.isArray(picked) && picked.length ? picked[0] : "All";
        syncInset();
      });
      await addNetworkInset();
    }
    syncViews();
  } catch (error) {
    const message = document.createElement("p");
    message.className = "chart-error";
    message.textContent = `This view could not be loaded. ${error.message}`;
    host.replaceChildren(message);
  }
}

function matchingTrails() {
  return trails.filter((trail) =>
    (state.chosenGrade === "All" || trail.grade === state.chosenGrade) &&
    (state.chosenLga === "All" || trail.lga === state.chosenLga) &&
    Number.isFinite(trail.length_km) && trail.length_km <= state.maximumKm &&
    (!state.accessOnly || trail.access === "Full" || trail.access === "Partial")
  );
}
function syncViews() {
  for (const selector of new Set([...linkedViews.keys(),...mapViews.keys()])) {
    const view=linkedViews.get(selector) || mapViews.get(selector);
    if (linkedViews.has(selector)) for (const [name,value] of Object.entries(state)) view.signal(name,value);
    if (mapViews.has(selector)) {
      view.signal("chosenLga",state.chosenLga);
      for (const [name,value] of Object.entries(mapPosition(selector))) view.signal(name,value);
    }
    view.runAsync().catch(error=>console.error("Could not update view",error));
  }
  syncInset();
}
function syncAreaControls() {
  document.querySelector("#filter-lga").value=state.chosenLga;
  document.querySelector("#overview-area").value=state.chosenLga;
  document.querySelectorAll("[data-map-zoom]").forEach(control=>{control.value=String(mapZoom);});
  document.querySelectorAll("[data-zoom-label]").forEach(label=>{label.textContent=`${mapZoom}×`;});
  document.querySelectorAll("[data-area]").forEach(button=>{
    button.setAttribute("aria-pressed",String(button.dataset.area === state.chosenLga));
  });
}
function updateShortlist() {
  syncAreaControls();
  const matching = matchingTrails();
  if (!matching.some((trail) => trail.name === state.selectedTrail)) state.selectedTrail = "";
  const timed = matching.filter((trail) => Number.isFinite(trail.hours) && trail.hours > 0).length;
  document.querySelector("#shortlist-count").textContent = matching.length
    ? `${matching.length} of ${trails.length} trails match. ${timed} have a positive time estimate and appear in the time view.`
    : "No trails match these filters in this dataset. Change the area, grade, distance or access filter to explore other records.";
  const picker = document.querySelector("#filter-trail");
  picker.replaceChildren(new Option("No trail selected", ""));
  [...matching].sort((a, b) => a.name.localeCompare(b.name)).forEach((trail) => picker.add(new Option(trail.name, trail.name)));
  picker.value = state.selectedTrail;
  const detail = document.querySelector("#trail-detail");
  const trail = matching.find((item) => item.name === state.selectedTrail);
  const title = document.createElement("strong");
  title.textContent = trail ? trail.name : "Follow one walk through the story.";
  const copy = document.createElement("span");
  copy.textContent = trail
    ? `${trail.lga} · ${trail.grade} · ${trail.length_km} km · ${trail.hours > 0 ? `${trail.hours} h estimated` : "Time not recorded"} · Access: ${trail.access}. Select the same trail again to clear the highlight.`
    : "Click a trail in any of the three views, or choose its name, to highlight it in the others.";
  detail.replaceChildren(title, copy);
  document.querySelector("#distance-value").textContent = `${state.maximumKm} km`;
  syncViews();
}

let insetView = null;
let detailGrade = "All";
function syncInset() {
  if (!insetView) return;
  const areaName = state.chosenLga === "All" ? "Victoria" : state.chosenLga;
  const selected = trails.filter(t => (state.chosenLga === "All" || t.lga === state.chosenLga) && (detailGrade === "All" || t.grade === detailGrade));
  const heading = document.querySelector("#network-inset .inset-heading");
  heading.textContent = `${areaName} · ${selected.length} trails${detailGrade === "All" ? "" : ` · ${detailGrade}`}`;
  document.querySelector("#network-inset").setAttribute("aria-label", `Detail map of ${areaName}, ${selected.length} recorded trails`);
  insetView.signal("chosenLga",state.chosenLga).signal("detailGrade",detailGrade).signal("detailCount",selected.length);
  for (const [name,value] of Object.entries(mapPosition("#network-detail"))) insetView.signal(name,value);
  insetView.runAsync().catch(error=>console.error("Could not update detail map",error));
}
async function addNetworkInset() {
  const host = document.querySelector("#chart-01");
  if (host.querySelector("#network-inset")) return;
  const box = document.createElement("div");box.id = "network-inset";
  const heading = document.createElement("p");heading.className = "inset-heading";
  heading.textContent = "Victoria · 194 trails";
  const mount = document.createElement("div");box.append(heading, mount);host.append(box);
  const width = Math.max(220,Math.round(box.getBoundingClientRect().width-18));
  const height = Math.max(210,Math.min(225,Math.round(width*.65)));
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
    params:[{name:"chosenLga",value:state.chosenLga},{name:"detailGrade",value:detailGrade},{name:"detailCount",value:194},...Object.entries(position).map(([name,value])=>({name,value}))],
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
      state.chosenLga=name === "Victoria" ? "All" : name;mapZoom=1;updateShortlist();
    }
  });
  syncInset();
}
function loadSummaryAndFilters() {
  const stats=bundle["data/stats.json"];
  document.querySelector("#stat-trails").textContent=stats.trail_count.toLocaleString();
  document.querySelector("#stat-km").textContent=`${Math.round(stats.total_km).toLocaleString()} km`;
  document.querySelector("#stat-median").textContent=`${stats.median_km.toFixed(1)} km`;
  document.querySelector("#stat-access").textContent=stats.accessible_count.toLocaleString();
  updateShortlist();
}
const form = document.querySelector("#shortlist-controls");
form.addEventListener("submit", (event) => event.preventDefault());
function readFilters() {
  if (state.chosenLga !== document.querySelector("#filter-lga").value) mapZoom=1;
  state.chosenGrade = document.querySelector("#filter-grade").value;
  state.chosenLga = document.querySelector("#filter-lga").value;
  state.maximumKm = Number(document.querySelector("#filter-distance").value);
  state.accessOnly = document.querySelector("#filter-access").checked;
  updateShortlist();
}
form.addEventListener("input",readFilters);
form.addEventListener("change",readFilters);
form.addEventListener("reset", (event) => {
  event.preventDefault();
  document.querySelector("#filter-grade").value = "All";
  document.querySelector("#filter-lga").value = "All";
  document.querySelector("#filter-distance").value = "95";
  document.querySelector("#filter-access").checked = false;
  mapZoom=1;
  Object.assign(state, { chosenGrade: "All", chosenLga: "All", maximumKm: 95, accessOnly: false, selectedTrail: "" });
  updateShortlist();
});
document.querySelector("#filter-trail").addEventListener("change", (event) => {
  state.selectedTrail = event.target.value;
  updateShortlist();
});
loadSummaryAndFilters();
charts.forEach(([selector, url]) => loadChart(selector, url));

document.querySelector("#overview-area").addEventListener("change",event=>{
  state.chosenLga=event.target.value; mapZoom=1; updateShortlist();
});
document.querySelectorAll("[data-area]").forEach(button=>button.addEventListener("click",()=>{
  state.chosenLga=button.dataset.area; mapZoom=1; updateShortlist();
}));
document.querySelectorAll("[data-map-zoom]").forEach(control=>control.addEventListener("input",()=>{
  mapZoom=Number(control.value); syncAreaControls(); syncViews();
}));
document.querySelectorAll("[data-map-action]").forEach(button=>button.addEventListener("click",()=>{
  const action=button.dataset.mapAction;
  if (action === "reset") {
    state.chosenLga="All"; mapZoom=1; detailGrade="All";
    const overview=mapViews.get("#chart-01");
    if (overview) overview.data("gradePick_store",[]).runAsync();
  }
  else if (action === "fit") mapZoom=1;
  else mapZoom=Math.max(1,Math.min(6,mapZoom+(action === "in" ? 0.5 : -0.5)));
  updateShortlist();
}));
})();
