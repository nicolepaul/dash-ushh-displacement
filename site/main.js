// Static, server-less replacement for the Dash callbacks: every dropdown
// combination was precomputed at build time (scripts/build_static_data.py)
// into data.json, so switching a dropdown here is just a lookup + a
// Plotly.react() -- no server round-trip.

const PANELS = [
  { key: "damage", selectId: "factor-damage-selector", graphId: "factor-damage-graph" },
  { key: "duration", selectId: "factor-duration-selector", graphId: "factor-duration-graph" },
  { key: "geo", selectId: "geo-duration-selector", graphId: "geo-duration-graph" },
];

const PLOTLY_CONFIG = { responsive: true };

async function main() {
  const res = await fetch("data.json");
  const { panels, options, defaults } = await res.json();

  for (const { key, selectId, graphId } of PANELS) {
    const select = document.getElementById(selectId);
    const graphEl = document.getElementById(graphId);

    for (const { label, value } of options[key]) {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = label;
      select.appendChild(opt);
    }
    select.value = defaults[key];

    const render = (value) => {
      const fig = panels[key][value];
      Plotly.react(graphEl, fig.data, fig.layout, PLOTLY_CONFIG);
    };

    render(defaults[key]);
    select.addEventListener("change", (e) => render(e.target.value));
  }
}

main();
