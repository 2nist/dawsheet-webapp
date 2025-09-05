function show(id) {
  document
    .querySelectorAll(".tab")
    .forEach((t) => t.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}
async function runAnalyze() {
  const body = {
    project_id: getProj(),
    artist: document.getElementById("artist").value || null,
    title: document.getElementById("title").value || null,
    options: { snap: document.getElementById("snap").value },
  };
  const r = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const { job_id } = await r.json();
  const p = await fetch(`/api/analyze/${job_id}/preview`).then((r) => r.json());
  document.getElementById("preview").textContent = JSON.stringify(p, null, 2);
}
async function doImport() {
  const layers = {
    lyrics: document.getElementById("impLyrics").checked,
    sections: document.getElementById("impSections").checked,
    keymode: document.getElementById("impKeymode").checked,
    drums: document.getElementById("impDrums").checked,
  };
  const body = {
    project_id: getProj(),
    sheet_id: getSheetId(),
    tab: "Timeline",
    layers,
  };
  const r = await fetch("/api/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  alert(await r.text());
}
function getProj() {
  return document.getElementById("projId").value.trim();
}
function getSheetId() {
  return document.getElementById("sheetId").value.trim();
}
async function saveBridgeCfg() {
  const cfg = {
    midi_port: document.getElementById("midiPort").value || null,
    osc_host: document.getElementById("oscHost").value,
    osc_port: parseInt(document.getElementById("oscPort").value, 10),
  };
  const r = await fetch("/api/bridge/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cfg),
  });
  document.getElementById("bridgeLog").textContent = await r.text();
}
async function sendMidi() {
  const body = { project_id: getProj(), kind: "drums", bars: 8 };
  const r = await fetch("/api/bridge/midi/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  document.getElementById("bridgeLog").textContent = await r.text();
}
async function sendOSC() {
  const body = { project_id: getProj(), kind: "section_cues" };
  const r = await fetch("/api/bridge/osc/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  document.getElementById("bridgeLog").textContent = await r.text();
}
async function loadLibrary() {
  const r = await fetch("/api/library");
  const j = await r.json();
  document.getElementById("libTable").textContent = JSON.stringify(j, null, 2);
}
loadLibrary();

// Wire the Bridge tab download buttons to include the current ProjectId/SheetId
function download(base) {
  const pid = encodeURIComponent(getProj());
  const sid = encodeURIComponent(getSheetId());
  if (!pid || !sid) {
    alert("Enter Project ID and Sheet ID first.");
    return;
  }
  const url = `${base}?project_id=${pid}&sheet_id=${sid}`;
  window.open(url, "_blank");
}

function openSheet() {
  const sid = getSheetId();
  if (!sid) {
    alert("Enter Sheet ID");
    return;
  }
  window.open(`https://docs.google.com/spreadsheets/d/${sid}/edit`, "_blank");
}
