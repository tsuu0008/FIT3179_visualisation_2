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
const state = { chosenGrade: "All", chosenLga: "All", maximumKm: 95, accessOnly: false, selectedTrail: "" };
let trails = [];
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
  if (selector === "#chart-03") spec.projection = { type: "mercator" };
  return spec;
}

async function loadChart(selector, specUrl) {
  const host = document.querySelector(selector);
  try {
    const response = await fetch(specUrl);
    if (!response.ok) throw new Error(`Could not load ${specUrl}`);
    let spec = await response.json();
    if (linkedCharts.has(selector)) spec = linkSpec(spec, selector);
    const result = await vegaEmbed(host, spec, embedOptions);
    if (linkedCharts.has(selector)) {
      linkedViews.set(selector, result.view);
      result.view.addEventListener("click", (_event, item) => {
        const name = item?.datum?.name;
        if (!trails.some((trail) => trail.name === name)) return;
        state.selectedTrail = state.selectedTrail === name ? "" : name;
        updateShortlist();
      });
      syncViews();
    }
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
  for (const view of linkedViews.values()) {
    for (const [name, value] of Object.entries(state)) view.signal(name, value);
    view.runAsync().catch((error) => console.error("Could not update linked view", error));
  }
}
function updateShortlist() {
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
async function loadSummaryAndFilters() {
  try {
    const [statsResponse, trailsResponse] = await Promise.all([fetch("data/stats.json"), fetch("data/trails.json")]);
    if (!statsResponse.ok || !trailsResponse.ok) throw new Error("Could not load trail summary");
    const [stats, records] = await Promise.all([statsResponse.json(), trailsResponse.json()]);
    trails = records;
    document.querySelector("#stat-trails").textContent = stats.trail_count.toLocaleString();
    document.querySelector("#stat-km").textContent = `${Math.round(stats.total_km).toLocaleString()} km`;
    document.querySelector("#stat-median").textContent = `${stats.median_km.toFixed(1)} km`;
    document.querySelector("#stat-access").textContent = stats.accessible_count.toLocaleString();
    const lgaPicker = document.querySelector("#filter-lga");
    [...new Set(trails.map((trail) => trail.lga))].sort().forEach((lga) => lgaPicker.add(new Option(lga, lga)));
    updateShortlist();
  } catch (error) {
    document.querySelector("#shortlist-count").textContent = "The shortlist data could not be loaded. Reload this page to try again.";
    document.querySelectorAll("#shortlist-controls input, #shortlist-controls select, #filter-trail").forEach((control) => { control.disabled = true; });
  }
}
const form = document.querySelector("#shortlist-controls");
form.addEventListener("submit", (event) => event.preventDefault());
form.addEventListener("input", () => {
  state.chosenGrade = document.querySelector("#filter-grade").value;
  state.chosenLga = document.querySelector("#filter-lga").value;
  state.maximumKm = Number(document.querySelector("#filter-distance").value);
  state.accessOnly = document.querySelector("#filter-access").checked;
  updateShortlist();
});
form.addEventListener("reset", (event) => {
  event.preventDefault();
  document.querySelector("#filter-grade").value = "All";
  document.querySelector("#filter-lga").value = "All";
  document.querySelector("#filter-distance").value = "95";
  document.querySelector("#filter-access").checked = false;
  Object.assign(state, { chosenGrade: "All", chosenLga: "All", maximumKm: 95, accessOnly: false, selectedTrail: "" });
  updateShortlist();
});
document.querySelector("#filter-trail").addEventListener("change", (event) => {
  state.selectedTrail = event.target.value;
  updateShortlist();
});
loadSummaryAndFilters();
charts.forEach(([selector, url]) => loadChart(selector, url));
