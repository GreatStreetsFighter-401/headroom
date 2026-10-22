/* Headroom — results page. No build step, no server, no third-party code on the
   page itself. Reads site/data/*.json written by `headroom site`. "Try an
   assumption" re-runs the model in a Web Worker (site/worker.js → Pyodide, the
   same Python as the CLI); when that engine cannot load, the sliders fall back
   to rescaling the committed medians and say so. */
(function () {
  "use strict";
  const SCEN = ["adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod", "combined"];
  const LABEL = {
    baseline: "Baseline (current law)",
    adu: "Accessory dwelling units",
    missing_middle: "Missing middle (2–6 units)",
    parking: "Parking minimums reduced",
    fees_handbook: "Fees −50 % ($50k baseline)",
    fees_ri: "Fees −50 % (RI actual fees)",
    tod: "Transit-oriented density",
    combined: "All five together (upper bound)",
  };
  // Slider groups, in page order, keyed by the ledger's scenario ids.
  const GROUPS = [
    ["all", "Baseline and every scenario"],
    ["adu", "Accessory dwelling units"],
    ["missing_middle", "Missing middle"],
    ["parking", "Parking"],
    ["fees", "Development fees"],
    ["tod", "Transit-oriented density"],
  ];
  // Fallback only (engine unavailable): which parameter each scenario's median
  // scales linearly with, so a slider still does something honest.
  const LINEAR = {
    adu: "adu_uptake_detached_annual",
    missing_middle: "mm_conversion_rate_annual",
    parking: "supply_cost_elasticity",
    fees_handbook: "supply_cost_elasticity",
    fees_ri: "supply_cost_elasticity",
    tod: "tod_realization_rate_annual",
    combined: null,
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

  const state = {
    tier: "B", ledger: null, results: {}, towns: {}, manifest: null,
    overrides: {},            // pid -> pinned value
    live: {},                 // tier -> result of the last in-browser run with the current overrides
    liveMeta: null,           // {ms, draws, pinned} of the run being shown
    engine: { status: "idle", detail: "" },
    worker: null, runId: 0, timer: null,
  };

  // ------------------------------------------------------------------ load
  async function load() {
    state.ledger = await (await fetch("data/ledger.json")).json();
    for (const t of ["A", "B", "C"]) {
      try {
        state.results[t] = await (await fetch(`data/results_tier${t}.json`)).json();
        state.towns[t] = await (await fetch(`data/towns_tier${t}.json`)).json();
      } catch (e) { /* tier not built */ }
    }
    try { state.manifest = await (await fetch("data/manifest.json")).json(); } catch (e) { state.manifest = null; }
    try { state.calibration = await (await fetch("data/calibration.json")).json(); } catch (e) { state.calibration = null; }
    try { state.hindcast = await (await fetch("data/hindcast.json")).json(); } catch (e) { state.hindcast = null; }
    const sel = el("tier");
    sel.addEventListener("change", () => { state.tier = sel.value; if (hasOverrides()) requestRun(); else render(); renderData(); });
    el("draws").addEventListener("change", () => { if (hasOverrides()) requestRun(); });
    el("reset-all").addEventListener("click", resetAll);
    el("why-close").addEventListener("click", () => { el("why").hidden = true; });
    el("why").addEventListener("click", (e) => { if (e.target === el("why")) el("why").hidden = true; });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") el("why").hidden = true; });
    render();
    renderScenarios();
    renderData();
    renderSliders();
    renderValidation();
    startEngine();
  }

  // ---------------------------------------------------------------- engine
  function startEngine() {
    if (!window.Worker) { setEngine("failed", "this browser has no Web Workers; sliders rescale the committed medians instead"); return; }
    try {
      state.worker = new Worker("worker.js");
    } catch (e) {
      setEngine("failed", `could not start the engine (${e.message}); sliders rescale the committed medians instead`);
      return;
    }
    state.worker.onmessage = (ev) => {
      const m = ev.data || {};
      if (m.type === "status") setEngine("loading", m.detail);
      else if (m.type === "ready") { setEngine("ready", `Python ${m.python}, numpy ${m.numpy}, running in this browser`); if (hasOverrides()) requestRun(); selftest(); }
      else if (m.type === "result") onResult(m);
      else if (m.type === "error") {
        if (m.id == null) setEngine("failed", `${m.message}; sliders rescale the committed medians instead`);
        else { setEngine("ready", `run ${m.id} failed: ${m.message}`); el("try-status").textContent = `The run failed: ${m.message}`; }
      }
    };
    state.worker.onerror = (e) => setEngine("failed", `engine error: ${e.message || "unknown"}; sliders rescale the committed medians instead`);
    setEngine("loading", "starting");
    // `?pyodide=<dir>/` points the worker at a self-hosted copy of the runtime.
    const indexURL = new URLSearchParams(location.search).get("pyodide") || null;
    state.worker.postMessage({ type: "init", indexURL });
  }
  function setEngine(status, detail) {
    state.engine = { status, detail };
    const box = el("engine"); box.className = `engine ${status}`;
    const lead = { idle: "Model engine", loading: "Model engine loading", ready: "Model engine ready", running: "Model running", failed: "Model engine unavailable" }[status];
    box.textContent = `${lead} — ${detail}`;
    renderSliders();
  }
  function hasOverrides() { return Object.keys(state.overrides).length > 0; }
  function engineReady() { return state.engine.status === "ready" || state.engine.status === "running"; }

  function requestRun() {
    if (!hasOverrides()) { state.live = {}; state.liveMeta = null; render(); return; }
    if (!engineReady()) { render(); return; }       // fallback rendering
    clearTimeout(state.timer);
    state.timer = setTimeout(() => {
      const id = ++state.runId;
      const towns = state.towns[state.tier] || state.towns.B;
      const draws = Number(el("draws").value);
      setEngine("running", `${draws.toLocaleString()} draws with ${Object.keys(state.overrides).length} assumption(s) pinned`);
      el("try-status").textContent = "running…";
      state.worker.postMessage({ type: "run", id, towns, overrides: state.overrides, draws, seed: state.ledger.meta.seed, tier: state.tier });
    }, 200);
  }
  function onResult(m) {
    if (m.id !== state.runId) return;  // a newer run is in flight
    state.live[state.tier] = m.result;
    state.liveMeta = { ms: m.ms, draws: m.result.meta.draws, pinned: m.result.meta.pinned };
    setEngine("ready", `last run: ${m.result.meta.draws.toLocaleString()} draws in ${(m.ms / 1000).toFixed(1)} s`);
    el("try-status").textContent = `Re-run in your browser: ${m.result.meta.draws.toLocaleString()} draws, ${(m.ms / 1000).toFixed(1)} s, ${Object.keys(m.result.meta.pinned).length} assumption(s) pinned.`;
    render();
  }
  function resetAll() {
    state.overrides = {}; state.live = {}; state.liveMeta = null;
    el("try-status").textContent = "";
    renderSliders(); render();
  }

  // --------------------------------------------------------------- results
  function committed() { return state.results[state.tier] || state.results.B; }
  function res() { return (hasOverrides() && state.live[state.tier]) || committed(); }
  function showingLive() { return hasOverrides() && !!state.live[state.tier]; }
  // Linear fallback: only when the engine is down and the pinned parameter is one the median scales with.
  function scaleFor(s) {
    if (showingLive() || engineReady() || s === "baseline" || !LINEAR[s]) return 1;
    const pid = LINEAR[s];
    return pid in state.overrides ? state.overrides[pid] / state.ledger.parameters[pid].default : 1;
  }

  function render() {
    const r = res();
    if (!r) { el("summary").textContent = "No results built yet. Run `headroom run` then `headroom site`."; return; }
    const live = showingLive();
    el("meta").textContent = live
      ? `tier ${r.meta.tier} · ${r.meta.draws.toLocaleString()} draws · seed ${r.meta.seed} · ${r.meta.years[0]}–${r.meta.years.at(-1)} · re-run in your browser`
      : `tier ${r.meta.tier} · ${r.meta.draws.toLocaleString()} draws · seed ${r.meta.seed} · ${r.meta.years[0]}–${r.meta.years.at(-1)} · committed run`;
    renderSummary(r);
    renderChart(r);
    renderSensitivity(r);
    renderTowns(r);
  }

  function renderSummary(r) {
    const box = el("summary"); box.innerHTML = "";
    const live = showingLive();
    const b = r.statewide.baseline.five_year;
    box.append(card("Baseline, five years", `${fmt(b.p50)}`, `P10 ${fmt(b.p10)} · P90 ${fmt(b.p90)}`, "baseline", live ? "level, not increment · re-run" : "level, not increment"));
    for (const s of SCEN) {
      const f = r.statewide[s].five_year, k = scaleFor(s);
      const note = live ? "increment over baseline · re-run with your assumptions" : k === 1 ? "increment over baseline" : `median rescaled ×${k.toFixed(2)} (engine unavailable)`;
      box.append(card(LABEL[s], `+${fmt(f.p50 * k)}`, `P10 +${fmt(f.p10 * k)} · P90 +${fmt(f.p90 * k)}`, s, note, live));
    }
  }
  function card(title, big, range, s, note, live) {
    const c = h("div", { class: "card", style: `border-top-color: var(--${s})` },
      h("h3", {}, title), h("div", { class: "big" }, big), h("div", { class: "range" }, range),
      h("div", { class: `note ${live ? "rerun" : ""}` }, note));
    if (s !== "baseline" && LINEAR[s]) c.append(h("button", { class: "why-link", onclick: () => why(LINEAR[s]) }, "why this number"));
    if (s === "combined") c.append(h("button", { class: "why-link", onclick: () => why("statewide_capacity_multiple") }, "why capped"));
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
    el("chart-note").textContent = `Scenario lines are baseline plus that scenario's median increment, one at a time. Shaded band: baseline P10–P90. A statewide capacity ceiling (ledger: statewide_capacity_multiple, a multiple of the recent permit level) applies to every total.${showingLive() ? " Shown: your re-run." : ""}`;
  }

  // --------------------------------------------------------------- sliders
  function groupOf(p) {
    const ids = p.scenarios || [];
    if (ids.includes("all")) return "all";
    for (const [g] of GROUPS) if (ids.includes(g)) return g;
    return "all";
  }
  function renderSliders() {
    const box = el("sliders"); if (!box || !state.ledger) return;
    box.innerHTML = "";
    const ready = engineReady(), failed = state.engine.status === "failed";
    const params = Object.values(state.ledger.parameters).filter((p) => p.distribution !== "fixed");
    for (const [g, title] of GROUPS) {
      const members = params.filter((p) => groupOf(p) === g);
      if (!members.length) continue;
      box.append(h("div", { class: "slider-group" }, title));
      for (const p of members) {
        const pid = p.id;
        const pinned = pid in state.overrides;
        const linear = Object.values(LINEAR).includes(pid);
        const enabled = ready || (failed && linear);
        const lo = p.low, hi = p.high, step = (hi - lo) / 200;
        const current = pinned ? state.overrides[pid] : p.default;
        const input = h("input", { type: "range", min: lo, max: hi, step, value: current });
        if (!enabled) input.disabled = true;
        const val = h("span", { class: "val" }, `${Number(current).toPrecision(3)} ${p.unit}`);
        const row = h("div", { class: `slider ${pinned ? "pinned" : ""}` });
        input.addEventListener("input", () => {
          state.overrides[pid] = Number(input.value);
          val.textContent = `${Number(input.value).toPrecision(3)} ${p.unit}`;
          row.classList.add("pinned");
          requestRun();
        });
        const reset = h("button", { class: "why-link", onclick: () => {
          delete state.overrides[pid]; input.value = p.default; val.textContent = `${Number(p.default).toPrecision(3)} ${p.unit}`;
          row.classList.remove("pinned"); requestRun();
        } }, "unpin");
        const hint = !ready && !failed ? " · waiting for the engine" : (!enabled ? " · needs the engine" : "");
        row.append(
          h("label", {}, p.label, h("span", { class: `status ${p.status}` }, p.status), val),
          input,
          h("div", { class: "range-note" }, `range ${lo} – ${hi} (${p.distribution})${hint} · `, h("button", { class: "why-link", onclick: () => why(pid) }, "why"), " · ", reset));
        box.append(row);
      }
    }
  }

  // ----------------------------------------------------------- sensitivity
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
    if (showingLive()) box.append(h("p", { class: "note" }, "From your re-run; a pinned assumption has no correlation to report and is absent from its scenario's list."));
  }

  // ----------------------------------------------------------------- towns
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

  // ------------------------------------------------------------ validation
  function renderValidation() {
    const box = el("validation"); if (!box) return; box.innerHTML = "";
    const c = state.calibration, hc = state.hindcast;
    if (c) {
      box.append(h("p", {}, h("strong", {}, "ADU calibration. "),
        `Under current law the model counts ${fmt(c.eligible_lots_detached_by_right_today_sewer_adjusted)} single-family lots eligible for a detached ADU by right (sewer-adjusted) and ${fmt(c.eligible_lots_conversion_sewer_adjusted)} for a within-footprint conversion. With the default rates it implies ${fmt(c.implied_2024_if_ramp_year_1)} ADU permits in 2024 if that was ramp year one and ${fmt(c.implied_2024_if_ramp_year_2)} if year two; Rhode Island permitted ${c.observed_2024_adu_permits} (${c.observed_source}). `,
        h("button", { class: "why-link", onclick: () => why("adu_uptake_detached_annual") }, "why")));
    }
    if (hc) {
      box.append(h("p", {}, h("strong", {}, "Baseline hindcast. "),
        `Fit on 2018–${hc.fit_through}, scored on ${hc.test_years.join(" and ")} (Census level, ${hc.n_town_years} town-years): mean absolute error of the median ${hc.mean_absolute_error_p50} units per town-year; statewide the median was ${hc.statewide_error_pct}% off (${fmt(hc.statewide_p50)} vs ${fmt(hc.statewide_observed)} observed) — a trend through ${hc.fit_through} misses the 2024–25 surge; ${Math.round(hc.share_inside_p10_p90 * 100)}% of observed town-years fell inside the P10–P90 band. `,
        h("button", { class: "why-link", onclick: () => why("baseline_noise_cv") }, "why")));
    }
    if (!c && !hc) box.textContent = "Run `headroom hindcast` and `headroom site` to populate.";
  }

  // ------------------------------------------------------------- scenarios
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

  // ------------------------------------------------------------------ data
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

  // ------------------------------------------------------------------- why
  function why(pid) {
    const p = state.ledger.parameters[pid];
    if (!p) return;
    const body = el("why-body"); body.innerHTML = "";
    body.append(h("h3", {}, p.label), h("p", {}, h("code", {}, pid), h("span", { class: `status ${p.status}` }, p.status)));
    const dl = h("dl", {});
    const add = (k, v) => { if (v) { dl.append(h("dt", {}, k), h("dd", {}, v)); } };
    add("Default", `${p.default} ${p.unit}`);
    add("Range", p.distribution === "fixed" ? "fixed" : `${p.low} – ${p.high} (${p.distribution})`);
    if (pid in state.overrides) add("Pinned at", `${state.overrides[pid]} ${p.unit} (your choice; the committed run samples the range)`);
    add("Scenarios", p.scenarios.join(", "));
    add("Source", p.source.trim());
    add("Why this value", p.justification.trim());
    add("RI calibration", (p.ri_calibration || "").trim());
    add("Cannot tell you", (p.what_it_cannot_say || "").trim());
    body.append(dl);
    el("why").hidden = false;
  }

  // -------------------------------------------------------------- selftest
  // `?selftest=1`: once the engine is ready, pin the ADU uptake at its upper
  // bound, run, and publish the outcome on the page for an automated check.
  function selftest() {
    if (!/[?&]selftest=1/.test(location.search) || window.__selftestStarted) return;
    window.__selftestStarted = true;
    const pid = "adu_uptake_detached_annual", p = state.ledger.parameters[pid];
    const before = committed().statewide.adu.five_year.p50;
    state.overrides[pid] = p.high;
    renderSliders();
    const wait = setInterval(() => {
      if (!showingLive()) return;
      clearInterval(wait);
      const after = state.live[state.tier].statewide.adu.five_year.p50;
      const out = { pid, pinned_at: p.high, adu_p50_committed: before, adu_p50_rerun: after, ms: state.liveMeta.ms, draws: state.liveMeta.draws, engine: state.live[state.tier].meta.engine };
      const pre = h("pre", { id: "selftest" }, JSON.stringify(out));
      document.body.append(pre);
      console.log("SELFTEST " + JSON.stringify(out));
    }, 100);
    requestRun();
  }

  load();
})();
