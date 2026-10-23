/* Controls for the Vega overview; the complete map is defined in its JSON. */
(() => {
  const host = document.getElementById('chart-01');
  const picker = document.getElementById('overview-route');
  const reset = document.getElementById('overview-reset');
  const status = document.getElementById('overview-status');
  if (!host || !picker) return;
  vegaEmbed(host, host.dataset.spec, {actions: false, renderer: 'svg', width: host.clientWidth})
    .then(({view}) => {
      const routes = view.data('routes').map(feature => feature.properties);
      routes.sort((a, b) => a.name.localeCompare(b.name)).forEach(route => {
        const option = document.createElement('option');
        option.value = route.id;
        option.textContent = route.name;
        picker.append(option);
      });
      const refresh = () => {
        const route = routes.find(route => route.id === Number(picker.value));
        status.textContent = route
          ? `${route.name} · ${route.length_km} km · ${route.grade} · ${route.duration_group}.${route.closure !== 'Not recorded' ? ' Recorded status: ' + route.closure + '.' : ''} Orange follows the selected official path.`
          : `${routes.length} walking routes. Drag the map, use + / −, or select a route to inspect its full path.`;
      };
      picker.disabled = false;
      reset.disabled = false;
      picker.addEventListener('change', () => {
        view.signal('pickTrail', Number(picker.value)).runAsync().then(refresh);
      });
      reset.addEventListener('click', () => {
        picker.value = '0';
        view.signal('pickTrail', 0).signal('reset', Date.now()).runAsync().then(refresh);
      });
      for (const [id, signal] of [['overview-zoom-in', 'zoomIn'], ['overview-zoom-out', 'zoomOut']]) {
        const button = document.getElementById(id);
        button.disabled = false;
        button.addEventListener('click', () => view.signal(signal, Date.now()).runAsync());
      }
      new ResizeObserver(entries => {
        const width = entries[0].contentRect.width;
        if (width > 0) view.width(width).runAsync();
      }).observe(host);
      refresh();
    })
    .catch(error => {
      status.textContent = 'The overview could not load. Refresh the page to retry.';
      console.error(error);
    });
})();
