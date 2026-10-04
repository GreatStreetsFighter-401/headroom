/* Headroom — static results page. No build step, no server, no third-party code.
   Reads site/data/*.json written by `headroom site`. Every number shown is in
   those files; the sliders rescale medians client-side and say so. */
(function () {
  "use strict";
  const SCEN = ["adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod"];
  const LABEL = {
    baseline: "Baseline (current law)",
    adu: "Accessory dwelling units",
    missing_middle: "Missing middle (2–6 units)",
    parking: "Parking minimums reduced",
    fees_handbook: "Fees −50 % ($50k baseline)",
    fees_ri: "Fees −50 % (RI actual fees)",
    tod: "Transit-oriented density",
  };
  // Which ledger parameter each scenario's median scales linearly with.
  const SLIDER = {
    adu: "adu_uptake_detached_annual",
    missing_middle: "mm_conversion_rate_annual",
    parking: "supply_cost_elasticity",
    fees_handbook: "supply_cost_elasticity",
    fees_ri: "supply_cost_elasticity",
    tod: "tod_realization_rate_annual",
  };
  const fmt = (v) => Math.round(v).toLocaleString("en-US");
  const el = (id) => document.getElementById(id);
  const h = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") n.className = v; else if (k.startsWith("on")) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
    }
    for (const k of kids) n.append(k instanceof Node ? k : document.createTextNode(String(k)));
    return n;
  };

  const state = { tier: "B", ledger: null, results: {}, towns: {}, manifest: null, scale: {} };

  async function load() {
    state.ledger = await (await fetch("data/ledger.json")).json();
    for (const t of ["A", "B", "C"]) {
      try {
        state.results[t] = await (await fetch(`data/results_tier${t}.json`)).json();
        state.towns[t] = await (await fetch(`data/towns_tier${t}.json`)).json();
      } catch (e) { /* tier not built */ }
    }
    try { state.manifest = await (await fetch("data/manifest.json")).json(); } catch (e) { state.manifest = null; }
    for (const pid of Object.keys(state.ledger.parameters)) state.scale[pid] = 1;
    const sel = el("tier");
    sel.addEventListener("change", () => { state.tier = sel.value; render(); });
    el("why-close").addEventListener("click", () => { el("why").hidden = true; });
    el("why").addEventListener("click", (e) => { if (e.target === el("why")) el("why").hidden = true; });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") el("why").hidden = true; });
    render();
    renderScenarios();
    renderData();
    renderSliders();
  }

  function res() { return state.results[state.tier] || state.results.B; }
  function scaleFor(s) { return s === "baseline" ? 1 : (state.scale[SLIDER[s]] || 1); }

  function render() {
    const r = res();
    if (!r) { el("summary").textContent = "No results built yet. Run `headroom run` then `headroom site`."; return; }
    el("meta").textContent = `tier ${r.meta.tier} · ${r.meta.draws.toLocaleString()} draws · seed ${r.meta.seed} · ${r.meta.years[0]}–${r.meta.years.at(-1)}`;
    renderSummary(r);
    renderChart(r);
    renderSensitivity(r);
    renderTowns(r);
  }

  function renderSummary(r) {
    const box = el("summary"); box.innerHTML = "";
    const b = r.statewide.baseline.five_year;
    box.append(card("Baseline, five years", `${fmt(b.p50)}`, `P10 ${fmt(b.p10)} · P90 ${fmt(b.p90)}`, "baseline", "level, not increment"));
    for (const s of SCEN) {
      const f = r.statewide[s].five_year, k = scaleFor(s);
      box.append(card(LABEL[s], `+${fmt(f.p50 * k)}`, `P10 +${fmt(f.p10 * k)} · P90 +${fmt(f.p90 * k)}`, s,
        k === 1 ? "increment over baseline" : `median rescaled ×${k.toFixed(2)} by the slider`));
    }
  }
  function card(title, big, range, s, note) {
    const c = h("div", { class: "card", style: `border-top-color: var(--${s})` },
      h("h3", {}, title), h("div", { class: "big" }, big), h("div", { class: "range" }, range),
      h("div", { class: "note" }, note));
    if (s !== "baseline") c.append(h("button", { class: "why-link", onclick: () => why(SLIDER[s]) }, "why this number"));
    return c;
  }

  function renderChart(r) {
    const years = r.meta.years, W = 1000, H = 330, L = 70, R = 20, T = 20, B = 30;
    const base = r.statewide.baseline;
    const series = [{ k: "baseline", v: base.p50 }];
    for (const s of SCEN) series.push({ k: s, v: base.p50.map((b, i) => b + r.statewide[s].p50[i] * scaleFor(s)) });
    const ymax = Math.max(...base.p90, ...series.flatMap((s) => s.v)) * 1.08;
    const x = (i) => L + (i / (years.length - 1)) * (W - L - R);
    const y = (v) => T + (1 - v / ymax) * (H - T - B);
    let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
    for (let g = 0; g <= 4; g++) {
      const v = (ymax / 4) * g;
      svg += `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="#e5e9ee"/><text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${fmt(v)}</text>`;
    }
    const band = years.map((_, i) => `${x(i)},${y(base.p90[i])}`).concat(years.map((_, i) => `${x(i)},${y(base.p10[i])}`).reverse()).join(" ");
    svg += `<polygon points="${band}" fill="var(--band)"/>`;
    for (const s of series) {
      const d = s.v.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
      svg += `<path d="${d}" fill="none" stroke="var(--${s.k})" stroke-width="${s.k === "baseline" ? 3 : 2}" ${s.k === "baseline" ? "" : 'stroke-dasharray="6 4"'}/>`;
    }
    years.forEach((yr, i) => { svg += `<text x="${x(i)}" y="${H - 22}" text-anchor="middle">${yr}</text>`; });
    svg += `</svg>`;
    el("chart").innerHTML = svg;
    const legend = h("div", { class: "legend-html" });
    for (const s of series) legend.append(h("span", { style: `color: var(--${s.k})` }, LABEL[s.k]));
    el("chart").append(legend);
    el("chart-note").textContent = `Scenario lines are baseline plus that scenario's median increment, one at a time. Shaded band: baseline P10–P90. Statewide capacity ceiling (ledger: statewide_permit_capacity) applies to every draw.`;
  }

  function renderSliders() {
    const box = el("sliders"); box.innerHTML = "";
    const seen = new Set();
    for (const s of SCEN) {
      const pid = SLIDER[s]; if (seen.has(pid)) continue; seen.add(pid);
      const p = state.ledger.parameters[pid];
      const lo = p.low, hi = p.high, step = (hi - lo) / 200;
      const input = h("input", { type: "range", min: lo, max: hi, step, value: p.default });
      const val = h("span", { class: "val" }, `${p.default} ${p.unit}`);
      input.addEventListener("input", () => {
        state.scale[pid] = Number(input.value) / p.default;
        val.textContent = `${Number(input.value).toPrecision(3)} ${p.unit}`;
        render();
      });
      const reset = h("button", { class: "why-link", onclick: () => { input.value = p.default; state.scale[pid] = 1; val.textContent = `${p.default} ${p.unit}`; render(); } }, "reset");
      box.append(h("div", { class: "slider" },
        h("label", {}, p.label, h("span", { class: `status ${p.status}` }, p.status), val),
        input,
        h("div", { class: "range-note" }, `range ${lo} – ${hi} · `, h("button", { class: "why-link", onclick: () => why(pid) }, "why"), " · ", reset)));
    }
  }

  function renderSensitivity(r) {
    const box = el("sensitivity"); box.innerHTML = "";
    for (const s of SCEN) {
      const rows = (r.sensitivity[s] || []).slice(0, 7);
      if (!rows.length) continue;
      const sec = h("div", { class: "sens" }, h("h3", {}, LABEL[s]));
      for (const row of rows) {
        const w = Math.min(100, Math.abs(row.spearman) * 100);
        sec.append(h("div", { class: "bar" },
          h("span", {}, h("button", { class: "why-link", onclick: () => why(row.parameter) }, row.label), h("span", { class: `status ${row.status}` }, row.status)),
          h("div", { class: "track" }, h("div", { class: `fill ${row.spearman < 0 ? "neg" : ""}`, style: `left:0;width:${w}%` })),
          h("span", { class: "rho" }, `ρ ${row.spearman >= 0 ? "+" : ""}${row.spearman.toFixed(2)}`)));
      }
      box.append(sec);
    }
  }

  let sortKey = "baseline", sortDir = -1;
  function renderTowns(r) {
    const t = el("towns"); t.innerHTML = "";
    const cols = ["baseline", ...SCEN];
    const head = h("tr", {}, h("th", { onclick: () => { sortKey = "name"; sortDir = -sortDir; renderTowns(r); } }, "Municipality"));
    for (const c of cols) head.append(h("th", { onclick: () => { sortKey = c; sortDir = -sortDir; renderTowns(r); } }, LABEL[c]));
    t.append(h("thead", {}, head));
    const body = h("tbody", {});
    const names = Object.keys(r.towns).sort((a, b) => {
      if (sortKey === "name") return a.localeCompare(b) * sortDir;
      return (r.towns[a][sortKey].five_year.p50 - r.towns[b][sortKey].five_year.p50) * sortDir;
    });
    for (const n of names) {
      const tr = h("tr", {}, h("td", {}, n));
      for (const c of cols) {
        const v = r.towns[n][c].five_year.p50 * scaleFor(c);
        tr.append(h("td", {}, c === "baseline" ? fmt(v) : `+${fmt(v)}`));
      }
      body.append(tr);
    }
    const tot = h("tr", { class: "total" }, h("td", {}, "Statewide"));
    for (const c of cols) { const v = r.statewide[c].five_year.p50 * scaleFor(c); tot.append(h("td", {}, c === "baseline" ? fmt(v) : `+${fmt(v)}`)); }
    body.append(tot);
    t.append(body);
  }

  function renderScenarios() {
    const box = el("scenarios"); box.innerHTML = "";
    for (const [id, s] of Object.entries(state.ledger.scenarios)) {
      box.append(h("div", { class: "scen", style: `border-left-color: var(--${id === "fees" ? "fees_handbook" : id})` },
        h("h3", {}, s.label),
        h("p", {}, h("span", { class: "lab" }, "Handbook: "), s.handbook_definition.trim()),
        h("p", {}, h("span", { class: "lab" }, "Modelled as: "), s.modelled_as.trim()),
        s.ri_law_today ? h("p", {}, h("span", { class: "lab" }, "Rhode Island law today: "), s.ri_law_today.trim()) : "",
        s.what_it_cannot_say ? h("p", {}, h("span", { class: "lab" }, "Cannot tell you: "), s.what_it_cannot_say.trim()) : ""));
    }
  }

  function renderData() {
    const box = el("data"); box.innerHTML = "";
    const tw = state.towns[state.tier] || state.towns.B;
    if (tw && tw.permit_undercount) {
      const u = tw.permit_undercount;
      box.append(h("p", {}, `Permit series: Census Building Permits Survey 2018–2025, scaled to the State's 2025 municipal survey (${fmt(u.eoh_2025_statewide || 0)} units) from the Census figure (${fmt(u.bps_2025_statewide)}): ratio ${u.eoh_to_bps_ratio_2025}. `, h("button", { class: "why-link", onclick: () => why("permit_undercount_adjustment") }, "why")));
    }
    if (tw && tw.districts_summary) {
      const d = tw.districts_summary, a = d.allowed_reading_counts;
      box.append(h("p", {}, `Stage 1 join: ${fmt(d.n_points_loaded)} typed structures (E-911) in ${fmt(d.n_polygons)} zoning districts; district text read as single-family-only in ${fmt(a.single_family_only)} districts, allowing more than one unit in ${fmt(a.allows_2plus)}, unreadable in ${fmt(a.unknown)} (the ledger share applies there).`));
    }
    if (tw && tw.transit) {
      box.append(h("p", {}, `Transit: ${tw.transit.n_frequent_stops} frequent stops and ${tw.transit.n_hub_stops} hub stops on service day ${tw.transit.service_day} (RIPTA GTFS).`));
    }
    if (state.manifest) {
      const ul = h("ul", {});
      for (const e of Object.values(state.manifest.entries)) ul.append(h("li", {}, h("code", {}, e.name), ` — ${e.source_title} (${e.publisher}); retrieved ${e.retrieved_at}; sha256 ${e.sha256.slice(0, 12)}…`));
      box.append(h("p", {}, "Files retrieved by ", h("code", {}, "headroom acquire"), ":"), ul);
    }
  }

  function why(pid) {
    const p = state.ledger.parameters[pid];
    if (!p) return;
    const body = el("why-body"); body.innerHTML = "";
    body.append(h("h3", {}, p.label), h("p", {}, h("code", {}, pid), h("span", { class: `status ${p.status}` }, p.status)));
    const dl = h("dl", {});
    const add = (k, v) => { if (v) { dl.append(h("dt", {}, k), h("dd", {}, v)); } };
    add("Default", `${p.default} ${p.unit}`);
    add("Range", p.distribution === "fixed" ? "fixed" : `${p.low} – ${p.high} (${p.distribution})`);
    add("Scenarios", p.scenarios.join(", "));
    add("Source", p.source.trim());
    add("Why this value", p.justification.trim());
    add("RI calibration", (p.ri_calibration || "").trim());
    add("Cannot tell you", (p.what_it_cannot_say || "").trim());
    body.append(dl);
    el("why").hidden = false;
  }

  load();
})();
