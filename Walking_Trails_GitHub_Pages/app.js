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

const embedOptions = {
  actions: { export: true, source: true, compiled: false, editor: false },
  renderer: "svg",
  tooltip: { theme: "light" },
};

async function loadChart(selector, specUrl) {
  const host = document.querySelector(selector);
  try {
    const response = await fetch(specUrl);
    if (!response.ok) throw new Error(`Could not load ${specUrl}`);
    const spec = await response.json();
    await vegaEmbed(host, spec, embedOptions);
  } catch (error) {
    host.innerHTML = `<p class="chart-error">This chart could not be loaded. ${error.message}</p>`;
  }
}

async function loadSummary() {
  try {
    const stats = await fetch("data/stats.json").then((response) => response.json());
    document.querySelector("#stat-trails").textContent = stats.trail_count.toLocaleString();
    document.querySelector("#stat-km").textContent = `${Math.round(stats.total_km).toLocaleString()} km`;
    document.querySelector("#stat-median").textContent = `${stats.median_km.toFixed(1)} km`;
    document.querySelector("#stat-access").textContent = stats.accessible_count.toLocaleString();
  } catch (_) {
    // Static fallback values in the HTML remain visible.
  }
}

loadSummary();
charts.forEach(([selector, url]) => loadChart(selector, url));
