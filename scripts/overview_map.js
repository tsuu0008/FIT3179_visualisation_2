/* Full official walking-route geometry on a zoomable geographic basemap. */
(() => {
  const container = document.getElementById('chart-01');
  const status = document.getElementById('overview-status');
  const picker = document.getElementById('overview-route');
  const reset = document.getElementById('overview-reset');
  if (!container || !window.L) {
    if (status) status.textContent = 'The map library could not load. Reload to try again.';
    return;
  }
  const map = L.map(container, {scrollWheelZoom: false, minZoom: 5, maxZoom: 19});
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  L.control.scale({imperial: false}).addTo(map);
  map.attributionControl.addAttribution('Routes: <a href="https://discover.data.vic.gov.au/dataset/recreation-tracks">DEECA / DataVic</a>');
  map.fitBounds([[-39.15, 140.95], [-34.0, 150.05]]);
  const normalStyle = {color: '#3155d9', weight: 2.6, opacity: 0.9, smoothFactor: 0, className: 'official-trail'};
  const layers = new Map();
  let routes;
  const showAll = () => {
    if (!routes) return;
    layers.forEach(layer => layer.setStyle(normalStyle));
    picker.value = '';
    map.closePopup();
    map.fitBounds(routes.getBounds(), {padding: [22, 22]});
    status.textContent = `${layers.size} walking routes. Use + / −, double-click, or choose a route to inspect its path.`;
  };
  const focus = id => {
    const layer = layers.get(String(id));
    if (!layer) return showAll();
    layers.forEach(other => other.setStyle({...normalStyle, opacity: 0.25}));
    layer.setStyle({...normalStyle, color: '#d95d39', weight: 4.5, opacity: 1});
    layer.bringToFront();
    map.fitBounds(layer.getBounds(), {padding: [45, 45], maxZoom: 16});
    layer.openPopup();
    const p = layer.feature.properties;
    status.textContent = `${p.name} · ${p.length_km} km · ${p.duration_group}. Orange shows the selected official route.`;
  };
  fetch(container.dataset.routes)
    .then(response => {
      if (!response.ok) throw new Error(`Route data: HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      routes = L.geoJSON(data, {
        style: normalStyle,
        onEachFeature(feature, layer) {
          const p = feature.properties;
          layers.set(String(p.id), layer);
          const tooltip = document.createElement('span');
          tooltip.textContent = p.name;
          layer.bindTooltip(tooltip, {sticky: true});
          const popup = document.createElement('div');
          const title = document.createElement('strong');
          title.textContent = p.name;
          popup.append(title);
          for (const line of [`${p.length_km} km · ${p.duration_group}`, `Recorded code: ${p.track_code}`, `Midpoint council: ${p.lga}`]) {
            const row = document.createElement('div');
            row.textContent = line;
            popup.append(row);
          }
          layer.bindPopup(popup);
          layer.on('click', () => {
            picker.value = String(p.id);
            focus(p.id);
          });
        }
      }).addTo(map);
      [...data.features].sort((a, b) => a.properties.name.localeCompare(b.properties.name)).forEach(feature => {
        const option = document.createElement('option');
        option.value = String(feature.properties.id);
        option.textContent = feature.properties.name;
        picker.append(option);
      });
      picker.disabled = false;
      reset.disabled = false;
      picker.addEventListener('change', () => focus(picker.value));
      reset.addEventListener('click', showAll);
      showAll();
    })
    .catch(error => {
      status.textContent = 'Route data could not load. Reload the page to try again.';
      console.error(error);
    });
  new ResizeObserver(() => map.invalidateSize({pan: false})).observe(container);
})();
