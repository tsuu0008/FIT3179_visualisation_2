(() => {
"use strict";
const charts = [
  ["#chart-01", "charts/01_trail_network.json"],
  ["#chart-02", "charts/02_lga_access.json"],
  ["#chart-03", "charts/03_trail_symbols.json"],
  ["#chart-04", "charts/04_challenge_heatmap.json"],
  ["#chart-05", "charts/05_length_ridgeline.json"],
  ["#chart-06", "charts/06_parallel_profile.json"],
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
  const selected = state.chosenLga === "All" ? areas : areas.filter(area => area.properties.name === state.chosenLga);
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
    mapScale: Math.min((width-60)/Math.max((east-west)*Math.PI/180,0.001),(height-60)/Math.max(y1-y0,0.001))*mapZoom,
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
  if(selector === "#chart-01") {
    spec.layer[1].transform=[...(spec.layer[1].transform || []),{filter:"chosenLga === 'All' || datum.properties.lga === chosenLga"}];
    spec.layer.slice(2).forEach(layer=>{
      layer.transform=[...(layer.transform || []),{filter:"chosenLga === 'All' || datum.lga === chosenLga"}];
    });
  }
  if(selector === "#chart-02") {
    spec.encoding.color.scale.domain=[0,Math.max(...areas.map(area=>area.properties.trail_km_per_100k || 0))];
    spec.transform=[...(spec.transform || []),{filter:"chosenLga === 'All' || datum.properties.name === chosenLga"}];
  }
  if(spec.layer) spec.layer.push({
    data:{values:clone(areas)},transform:[{filter:"chosenLga !== 'All' && datum.properties.name === chosenLga"}],
    mark:{type:"geoshape",fill:null,stroke:"#b74924",strokeWidth:2},encoding:{shape:{field:"geometry",type:"geojson"}},
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
  const pointNode = selector === "#chart-12" ? spec.layer[0] : dataNode;
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
    if (mapCharts.has(selector)) spec = mapSpec(spec, selector);
    const result = await vegaEmbed(host, spec, embedOptions);
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
        if (areas.some(feature=>feature.properties.name === area)) {
          state.chosenLga=area; mapZoom=1; updateShortlist();
        }
      });
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
  if (action === "reset") { state.chosenLga="All"; mapZoom=1; }
  else if (action === "fit") mapZoom=1;
  else mapZoom=Math.max(1,Math.min(6,mapZoom+(action === "in" ? 0.5 : -0.5)));
  updateShortlist();
}));
})();
