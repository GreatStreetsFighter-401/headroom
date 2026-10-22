/* Headroom — the model in the browser.
   A Web Worker that loads Pyodide (CPython compiled to WebAssembly), installs
   the model's own source files from site/model/ (published by `headroom site`
   and checked against src/ by the test suite) and runs headroom.model.web.run.
   Nothing here re-implements the model: a number produced in this worker came
   from the same Python that produced the committed results.

   Messages in:  {type: "init"}
                 {type: "run", id, towns, overrides, draws, seed}
   Messages out: {type: "status", stage, detail}
                 {type: "ready", python, numpy}
                 {type: "result", id, result, ms}
                 {type: "error", id?, message} */
"use strict";

const PYODIDE_VERSION = "0.27.7";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

let pyodide = null;
let runJson = null;
let ready = false;
const queue = [];

function status(stage, detail) { self.postMessage({ type: "status", stage, detail: detail || "" }); }

async function init(indexURL) {
  // A self-hosted copy of the runtime (the page's `?pyodide=<dir>/`) stands in
  // for the CDN where a network blocks it; the files are the same release.
  const base = indexURL ? new URL(indexURL, self.location.href).href : PYODIDE_URL;
  status("loading", `fetching Pyodide ${PYODIDE_VERSION} (CPython for WebAssembly, ~10 MB, cached by the browser)`);
  self.importScripts(`${base}pyodide.js`);
  pyodide = await self.loadPyodide({ indexURL: base });
  status("loading", "loading numpy and PyYAML");
  await pyodide.loadPackage(["numpy", "pyyaml"]);
  status("loading", "installing the model's source files");
  const files = await (await fetch("model/files.json")).json();
  pyodide.FS.mkdirTree("/model");
  for (const rel of files) {
    const text = await (await fetch(`model/${rel}`)).text();
    const dir = rel.includes("/") ? rel.slice(0, rel.lastIndexOf("/")) : "";
    if (dir) pyodide.FS.mkdirTree(`/model/${dir}`);
    pyodide.FS.writeFile(`/model/${rel}`, text);
  }
  const info = await pyodide.runPythonAsync(`
import sys, json
sys.path.insert(0, "/model/src")
import numpy
from headroom.model import web
json.dumps({"python": sys.version.split()[0], "numpy": numpy.__version__})
`);
  runJson = pyodide.globals.get("web").run_json;
  ready = true;
  self.postMessage({ type: "ready", ...JSON.parse(info) });
  while (queue.length) run(queue.shift());
}

function run(msg) {
  const t0 = performance.now();
  try {
    const out = runJson(JSON.stringify(msg.towns), JSON.stringify(msg.overrides || {}), msg.draws || null, msg.seed || null);
    self.postMessage({ type: "result", id: msg.id, result: JSON.parse(out), ms: Math.round(performance.now() - t0) });
  } catch (e) {
    self.postMessage({ type: "error", id: msg.id, message: String(e && e.message || e) });
  }
}

self.onmessage = (ev) => {
  const msg = ev.data || {};
  if (msg.type === "init") {
    init(msg.indexURL).catch((e) => self.postMessage({ type: "error", message: `engine failed to load: ${String(e && e.message || e)}` }));
  } else if (msg.type === "run") {
    if (ready) run(msg); else queue.push(msg);
  }
};
