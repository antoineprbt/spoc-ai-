"use strict";

const $ = (id) => document.getElementById(id);
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const pad = (n) => String(n).padStart(2, "0");
const units = {voltage_v: "V", temperature_c: "°C", particles_ug_m3: "µg/m³", vibration_mm_s: "mm/s"};
const labels = {voltage_v: "Voltage", temperature_c: "Temperature", particles_ug_m3: "Particles", vibration_mm_s: "Vibration"};
const state = {bootstrap: null, run: null, frame: null, index: 0, timer: null, running: false, view: "map", selectedEvent: null, zone: null, busy: false};

function error(message) { $("error-banner").textContent = message; $("error-banner").hidden = !message; }
function announce(message) { $("announcement").textContent = message; }
function activeAlert() { return state.frame.alerts.find((a) => a.zone === state.zone) || (!state.zone ? state.frame.alerts[0] : null); }
function pause() {
  clearTimeout(state.timer); state.timer = null; state.running = false;
  updatePlayback();
}
function updatePlayback() {
  const total = state.run?.frames.length || 14;
  $("scrubber").max = total; $("scrubber").value = state.index;
  $("playback-count").textContent = `${pad(state.index)} / ${total}`;
  $("pause-button").disabled = !state.run || state.index >= total;
  $("pause-button").textContent = state.running ? "Ⅱ Pause" : "▶ Resume";
  $("step-button").disabled = !state.run || state.index >= total;
  $("scrubber").disabled = !state.run;
  $("export-button").disabled = !state.run || state.index === 0;
  $("playback-label").textContent = !state.run ? "Ready to simulate" : state.index >= total ? "Playback complete" : state.running ? "Processing stream" : "Playback paused";
  $("stream-state").innerHTML = `<i class="status-dot"></i> ${!state.run ? "STREAM READY" : state.index >= total ? "STREAM COMPLETE" : state.running ? "REPLAYING" : "PAUSED"}`;
}
function showFrame(index) {
  state.index = index;
  state.frame = index === 0 ? state.bootstrap.initial : state.run.frames[index - 1];
  if (state.selectedEvent && !state.frame.events.some((e) => e.id === state.selectedEvent)) state.selectedEvent = null;
  render();
}
function tick() {
  if (!state.running || !state.run) return;
  if (state.index < state.run.frames.length) showFrame(state.index + 1);
  if (state.index >= state.run.frames.length) {
    pause(); announce(`${state.run.scenario.name} complete. ${state.frame.alerts.length} alert, ${state.frame.anomaly_count} detected anomalies.`);
  } else { state.timer = setTimeout(tick, Number($("speed").value)); }
}
async function runSimulation() {
  if (state.busy) return;
  pause(); error(""); state.busy = true;
  $("run-button").disabled = true; $("scenario").disabled = true; $("reset-button").disabled = true;
  $("run-button").textContent = "Computing…";
  try {
    const response = await fetch("/api/run", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({scenario: $("scenario").value})});
    if (!response.ok) throw new Error("The local engine could not process this scenario.");
    state.run = await response.json(); state.index = 0; state.selectedEvent = null; state.zone = null;
    state.running = true; tick();
    announce("Simulation started. The local model has scored the stream; observations are now revealed in time order.");
  } catch (failure) { error(`${failure.message} Check that the Python server is still running, then retry.`); }
  finally {
    state.busy = false; $("run-button").disabled = false; $("scenario").disabled = false; $("reset-button").disabled = false;
    $("run-button").innerHTML = '<span class="play-icon">▶</span> Run simulation';
  }
}
function reset() {
  pause(); state.run = null; state.index = 0; state.selectedEvent = null; state.zone = null;
  state.frame = state.bootstrap.initial; error(""); render(); announce("Simulation reset. Choose a scenario and run it.");
}
function setView(view) {
  state.view = view;
  for (const name of ["map", "graph", "data"]) {
    $(`${name}-view`).hidden = name !== view;
    $(`${name}-tab`).classList.toggle("active", name === view);
    $(`${name}-tab`).setAttribute("aria-selected", String(name === view));
  }
  if (state.bootstrap) { renderGraph(); renderData(); }
}
function selectEvent(id) { state.selectedEvent = id; renderTimeline(); renderInspector(); }

function render() {
  const frame = state.frame;
  $("metric-events").textContent = pad(frame.events.length);
  $("metric-sensors").innerHTML = `${frame.sensors.filter((s) => s.latest).length}<span class="denominator">/5</span>`;
  $("sensor-caption").textContent = frame.events.length ? "reporting" : "awaiting data";
  $("metric-anomalies").textContent = pad(frame.anomaly_count);
  $("metric-anomalies").classList.toggle("warn", frame.anomaly_count > 0);
  $("metric-priority").textContent = frame.alerts[0]?.score ?? "—";
  $("metric-priority").classList.toggle("warn", frame.alerts.length > 0);
  $("priority-caption").textContent = frame.alerts.length ? "review score / 100" : frame.events.length ? "no active alert" : "awaiting signals";
  $("clock").textContent = frame.time; $("timeline-count").textContent = pad(frame.events.length); $("alert-count").textContent = pad(frame.alerts.length);
  renderTimeline(); renderMap(); renderCamera(); renderSensors(); renderInspector(); renderGraph(); renderData(); updatePlayback();
}

function renderTimeline() {
  const events = state.frame.events;
  if (!events.length) {
    $("timeline").innerHTML = '<div class="empty-timeline"><span class="empty-symbol">⌁</span><h3>Waiting for the first signal</h3><p>Run a scenario to follow sensor readings, camera observations, and field reports as they arrive.</p><span class="tiny-label">14 EVENTS · 2m 40s EXERCISE</span></div>';
    return;
  }
  const previousScroll = $("timeline").scrollTop;
  $("timeline").innerHTML = events.map((e) => `<button class="timeline-event ${e.analysis?.is_anomaly ? "anomaly" : e.stance} ${e.id === state.selectedEvent ? "selected" : ""}" data-event="${e.id}" aria-label="Inspect ${e.id}: ${escapeHTML(e.title)}"><span class="event-meta"><time>${e.time}</time><b>${e.kind.toUpperCase()}</b></span><h3>${escapeHTML(e.title)}</h3><p>${e.id} · ${e.source_id} · ZONE ${e.zone}${e.analysis?.is_anomaly ? " · ANOMALY" : ""}</p></button>`).join("");
  if (state.running) $("timeline").scrollTop = $("timeline").scrollHeight;
  else $("timeline").scrollTop = previousScroll;
}

function renderMap() {
  const zones = state.bootstrap.facility.zones;
  const svg = `<svg class="map-svg" viewBox="90 75 660 465" role="group" aria-label="Fictional Northstar Station schematic. Select a zone to inspect it.">
    <defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#1c2835" stroke-width=".7"/></pattern><pattern id="minorGrid" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="0" cy="0" r=".45" fill="#253442"/></pattern></defs>
    <rect width="800" height="540" fill="url(#minorGrid)"/><rect width="800" height="540" fill="url(#grid)"/>
    <path d="M102 103H700V502H102Z" fill="none" stroke="#374b5f" stroke-width="1" stroke-dasharray="5 5"/>
    <path d="M375 178H405M260 285V325M535 230V270M375 400H405" stroke="#52677a" stroke-width="12"/><path d="M375 178H405M260 285V325M535 230V270M375 400H405" stroke="#14212d" stroke-width="8"/>
    ${[0,1,2,3,4].map((i) => `<text x="${155+i*125}" y="520" class="map-dim">${String(i+1).padStart(2,"0")}</text>`).join("")}
    <text x="77" y="170" class="map-dim">A</text><text x="77" y="300" class="map-dim">B</text><text x="77" y="430" class="map-dim">C</text>
    ${zones.map((z) => {
      const alert = state.frame.alerts.find((a) => a.zone === z.id);
      return `<g class="facility-zone ${alert ? "active" : ""} ${state.zone === z.id ? "selected" : ""}" data-zone="${z.id}" role="button" tabindex="0" aria-label="Zone ${z.id}, ${escapeHTML(z.name)}, ${alert ? "priority " + alert.score : "no active alert"}"><rect class="zone-shape" x="${z.x}" y="${z.y}" width="${z.width}" height="${z.height}" rx="2"/><text class="zone-number" x="${z.x+16}" y="${z.y+25}">ZONE ${z.id}</text><circle class="zone-pip" cx="${z.x+z.width-19}" cy="${z.y+20}" r="3"/><text class="zone-name" x="${z.x+16}" y="${z.y+50}">${escapeHTML(z.name)}</text><text class="zone-caption" x="${z.x+16}" y="${z.y+69}">${alert ? "REVIEW PRIORITY / " + alert.score : state.frame.events.some(e=>e.zone===z.id) ? "NO ACTIVE ALERT" : "AWAITING SIGNALS"}</text>${z.height > 100 ? [0,1,2].map((i)=>`<rect class="equipment" x="${z.x+17+i*62}" y="${z.y+z.height-54}" width="48" height="35" rx="1"/><path d="M${z.x+23+i*62} ${z.y+z.height-43}h20m-20 6h32m-32 6h32" stroke="${alert ? "#89654d" : "#41576a"}" stroke-width="1"/>`).join("") : ""}${z.id === "D" ? `<path d="M${z.x+17} ${z.y+93}h${z.width-34}m-${z.width-34} 31h${z.width-34}" stroke="#34475a" stroke-width="1"/>` : ""}</g>`;
    }).join("")}
    <path d="M737 137v-37m-5 8 5-8 5 8" stroke="#8598aa" stroke-width="1.5" fill="none"/><text x="732" y="90" font-size="10" fill="#9bafc1">N</text><text x="734" y="155" class="map-dim">SIM</text>
    <path d="M27 448v44h44M729 30h44v44" stroke="#41566b" fill="none"/>
  </svg>`;
  $("facility-map").innerHTML = svg;
}

function renderCamera() {
  const event = [...state.frame.events].reverse().find((e) => e.source_id === "CAM-A1");
  const haze = event?.visual === "haze";
  $("camera-feed").innerHTML = `<svg viewBox="0 0 320 170" preserveAspectRatio="xMidYMid slice" role="img" aria-label="${haze ? "Procedural illustration of haze near a fictional equipment cabinet" : "Procedural illustration of an empty fictional equipment bay"}"><defs><linearGradient id="floor" x2="0" y2="1"><stop stop-color="#283944"/><stop offset="1" stop-color="#111b25"/></linearGradient><radialGradient id="haze"><stop stop-color="#c1c9bd" stop-opacity=".48"/><stop offset="1" stop-color="#bac2b7" stop-opacity="0"/></radialGradient><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 0H4" stroke="#080e14" opacity=".3"/></pattern></defs><rect width="320" height="170" fill="#1c2b35"/><path d="m0 0 88 37h145L320 0v170l-87-59H88L0 170Z" fill="#24343e"/><path d="M0 170 88 111h145l87 59" fill="url(#floor)"/><path d="M0 0 88 37v74L0 170M320 0l-87 37v74l87 59M88 37h145M88 111h145" stroke="#6a828c" stroke-opacity=".4" fill="none"/><path d="M0 143h320M0 160h320M90 170l41-59m84 59-21-59M0 40l88 20m145 0 87-20" stroke="#5a7581" opacity=".25"/>
    ${[0,1,2].map((i)=>`<rect x="${100+i*39}" y="49" width="30" height="62" fill="#12212a" stroke="#59707a" stroke-width=".7"/><path d="M${105+i*39} 57h20m-20 5h20m-20 5h20m-20 5h20m-20 5h20m-20 5h20" stroke="#415965"/><rect x="${104+i*39}" y="96" width="3" height="3" fill="${haze && i===0 ? "#e8a079" : "#829f97"}"/>`).join("")}
    <path d="M145 26h40" stroke="#b1c2c1" stroke-width="3" opacity=".5"/>${haze ? '<ellipse cx="132" cy="88" rx="86" ry="45" fill="url(#haze)"/><ellipse cx="160" cy="62" rx="90" ry="52" fill="url(#haze)"/><ellipse cx="99" cy="125" rx="63" ry="34" fill="url(#haze)"/><path d="M85 49h12m-12 0v12m104-12h-12m12 0v12M85 122h12m-12 0v-12m104 12h-12m12 0v-12" fill="none" stroke="#f0a877" stroke-width="1"/>' : ""}<rect width="320" height="170" fill="url(#scan)"/><path d="M13 32v10m-5-5h10M307 135v10m-5-5h10" stroke="#839ba6" stroke-width=".6"/></svg><span class="camera-tag">SYNTHETIC FEED / ILLUSTRATION</span><span class="camera-time">${event?.time || "AWAITING EVENT"}</span>`;
  $("camera-caption").textContent = !event ? "Illustrated placeholder · Awaiting camera event" : haze ? "Authored observation: haze-like shapes · Unverified" : "Authored observation: clear bay · Not proof of safety";
}

function renderSensors() {
  $("sensor-list").innerHTML = state.frame.sensors.map((s) => `<div class="sensor-item"><span>${s.id}</span><small class="${s.status}">${s.status.toUpperCase()}</small></div>`).join("");
}
function renderInspector() {
  const alerts = state.frame.alerts;
  $("alert-queue").innerHTML = alerts.length ? alerts.map((a) => `<button class="alert-item" data-alert="${a.zone}"><span class="alert-number">${a.score}</span><span><strong>${escapeHTML(state.bootstrap.facility.zones.find(z=>z.id===a.zone).name)}</strong><small>${a.level.toUpperCase()} PRIORITY · ${a.event_ids.length} EVENTS</small></span><span class="arrow">›</span></button>`).join("") : `<div class="queue-empty">${state.index ? "No active anomaly alert" : "No signals processed yet"}</div>`;
  const event = state.frame.events.find((e) => e.id === state.selectedEvent);
  if (event) { renderEventDetail(event); return; }
  const alert = activeAlert();
  if (!alert) {
    const zone = state.bootstrap.facility.zones.find((z) => z.id === state.zone);
    $("inspector-content").innerHTML = `<div class="inspector-empty"><span class="eyebrow">${zone ? "ZONE " + zone.id : "ANALYST WORKSPACE"}</span><span class="empty-symbol">⌘</span><h3>${zone ? escapeHTML(zone.name) : state.index ? "No active alert detected" : "Every signal has context."}</h3><p>${state.index ? "The displayed observations do not produce an active anomaly alert here. This does not establish that conditions are safe or that every fault would be detected." : "Start Nightfall to trace a power disturbance across sensors, a synthetic camera observation, and a field report."}</p><ol class="workflow-list"><li><b>01</b> Run the synthetic event stream</li><li><b>02</b> Inspect anomalies and linked evidence</li><li><b>03</b> Review priority and uncertainty</li></ol><div class="uncertainty-box"><span class="tiny-label">SIMULATION BOUNDARY</span><p>All facilities, observations, and readings are fictional. No live systems are connected.</p></div></div>`;
    return;
  }
  const factor = (label, value, max, negative=false) => `<div class="factor-row ${negative ? "negative" : ""}"><div>${label}<div class="factor-track"><i style="width:${Math.min(100,Math.abs(value)/max*100)}%"></i></div></div><b>${value < 0 ? "−" : "+"}${Math.abs(value).toFixed(1)}</b></div>`;
  $("inspector-content").innerHTML = `<div class="review-label">ANALYST REVIEW REQUIRED</div><h3 class="inspector-title">Unusual conditions in zone ${alert.zone}</h3><p class="detail-meta">${alert.id} · ${alert.event_ids.length} LINKED OBSERVATIONS</p><div class="priority-block"><div class="score-ring"><svg viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="34" fill="none" stroke="#2d3034" stroke-width="4"/><circle cx="40" cy="40" r="34" fill="none" stroke="#efa477" stroke-width="4" stroke-dasharray="${alert.score / 100 * 213.63} 213.63"/></svg><div class="score-value">${alert.score}<small>/ 100</small></div></div><div class="priority-copy"><b>${alert.level === "review" ? "Needs review" : alert.level[0].toUpperCase()+alert.level.slice(1)+" review priority"}</b><p>Transparent review score.<br>Not a confidence percentage.</p></div></div><div class="factor-title">WHY THIS PRIORITY?</div>${factor("Anomaly strength", alert.factors.anomaly,55)}${factor(`Corroboration · ${alert.support_sources.length} sources`, alert.factors.corroboration,25)}${factor("Authored event severity", alert.factors.severity,20)}${factor(`Contradiction · ${alert.contradict_sources.length} sources`, alert.factors.contradiction,20,true)}<p class="factor-note">Rounded sum, bounded to 0–100. Independent sources count once; corroboration and contradiction cap at two sources.</p><div class="uncertainty-box"><span class="tiny-label">UNCERTAINTY / NOT VERIFIED</span><h4>${alert.uncertainty}</h4><p>${escapeHTML(alert.explanation)}</p></div><button class="text-button detail-link" data-show-links="true">Inspect the evidence links <span>↗</span></button>`;
}
function renderEventDetail(event) {
  const analysis = event.analysis;
  $("inspector-content").innerHTML = `<button class="text-button small-back" data-back="true">← Back to incident</button><div class="review-label">${analysis?.is_anomaly ? "DETECTED ANOMALY" : "SYNTHETIC OBSERVATION"}</div><h3 class="inspector-title">${escapeHTML(event.title)}</h3><p class="detail-meta">${event.id} · ${event.time} · ${event.source_id}</p><p class="event-body">${escapeHTML(event.message)}</p><p class="detail-meta">ZONE ${event.zone} · ${event.event_type.toUpperCase()} · ${event.stance.toUpperCase()}</p>${analysis ? `<div class="readings-detail">${Object.entries(event.readings).map(([f,v])=>`<div class="reading-row"><span>${labels[f]}</span><b>${v} ${units[f]}</b></div>`).join("")}</div><div class="factor-title">MODEL OUTPUT</div><div class="reading-row"><span>Anomaly score (−score_samples)</span><b>${analysis.raw_score.toFixed(4)}</b></div><div class="reading-row"><span>Decision threshold</span><b>${state.bootstrap.model.threshold.toFixed(4)}</b></div><div class="reading-row"><span>Decision value</span><b>${analysis.decision.toFixed(4)}</b></div><p class="factor-note">A negative decision value flags an anomaly. Normalized strength = clamp(−decision / 0.15, 0, 1).</p><div class="uncertainty-box"><span class="tiny-label">DESCRIPTIVE DEVIATION</span><p>${analysis.deviations[0].label}: ${analysis.deviations[0].standard_deviations} baseline standard deviations from its mean. This is a descriptive comparison, not a model feature attribution.</p></div>` : `<div class="uncertainty-box"><span class="tiny-label">AUTHORED INPUT / NO MODEL INFERENCE</span><p>This ${event.kind === "camera" ? "camera observation is a scripted label paired with a procedural illustration; no computer vision is running" : "field report is fictional text; no language model is interpreting it"}. Its stance and severity are scenario inputs.</p></div>`}<button class="text-button detail-link" data-show-links="true">View event connections <span>↗</span></button>`;
}

function renderGraph() {
  const alert = activeAlert() || state.frame.alerts[0];
  if (!alert) {
    $("graph-view").innerHTML = '<div class="inspector-empty"><span class="eyebrow">CORRELATION GRAPH</span><h3 style="margin-top:18px">No active incident links.</h3><p>Run Nightfall or Sensor drift to see how the facility, sources, and observations connect. A link requires related event types, proximity, and a time gap of at most 120 seconds.</p></div>';
    return;
  }
  const graph = state.frame.graph;
  const evidence = state.frame.events.filter((e) => alert.event_ids.includes(e.id));
  const sourceIds = [...new Set(evidence.map((e) => e.source_id))];
  const positions = {station:[45,155], [alert.zone]:[160,155]};
  sourceIds.forEach((id,i)=>{positions[id]=[330,40+i*75];});
  evidence.forEach((e,i)=>{positions[e.id]=[535,18+i*(285/Math.max(1,evidence.length-1))];});
  const nodes = graph.nodes.filter((n)=>positions[n.id]);
  const edges = graph.edges.filter((e)=>positions[e.source]&&positions[e.target]);
  $("graph-view").innerHTML = `<p class="graph-caption">${evidence.length} observations · ${sourceIds.length} sources · Select an event node</p><svg viewBox="0 0 660 340" role="group" aria-label="NetworkX incident graph with facility, zone, source, and event nodes">${edges.map((e)=>{
    const [x1,y1]=positions[e.source], [x2,y2]=positions[e.target];
    const correlation=["correlates","contradicts"].includes(e.relation);
    return `<path d="${correlation ? `M${x1+25} ${y1+10}C${625+Math.abs(y2-y1)*.1} ${y1+10} ${625+Math.abs(y2-y1)*.1} ${y2+10} ${x2+25} ${y2+10}` : `M${x1+25} ${y1+10}L${x2-27} ${y2+10}`}" fill="none" stroke="${e.relation === "contradicts" ? "#a6b8cb" : correlation ? "#c08a69" : "#435264"}" stroke-width="${correlation ? 1.1 : 1}" ${e.relation === "contradicts" ? 'stroke-dasharray="4 3"' : ""} opacity="${correlation ? .6 : .8}"><title>${escapeHTML(e.reason || e.relation)}</title></path>`;
  }).join("")}${nodes.map((n)=>{
    const [x,y] = positions[n.id]; const isEvent = n.kind === "event"; const e = evidence.find(v=>v.id===n.id);
    return `<g ${isEvent ? `class="graph-node" role="button" tabindex="0" data-event="${n.id}" aria-label="Inspect ${n.id}: ${escapeHTML(n.label)}"` : ""}><rect x="${x-28}" y="${y-3}" width="${n.kind === "sensor" || n.kind === "camera" || n.kind === "field" ? 72 : 58}" height="28" rx="3" fill="${e?.analysis?.is_anomaly ? "#3c2b22" : "#1b2734"}" stroke="${e?.analysis?.is_anomaly ? "#c38d6b" : "#4a6077"}"/><text x="${x+1}" y="${y+15}" font-family="monospace" font-size="10" fill="#d5dfeb" text-anchor="middle">${n.id === "station" ? "NS" : n.id === alert.zone ? "ZONE "+n.id : n.id}</text>${!isEvent ? `<text x="${x+1}" y="${y+40}" font-family="monospace" font-size="8" text-anchor="middle" fill="#93a6bb">${n.kind.toUpperCase()}</text>` : ""}<title>${escapeHTML(n.label)}</title></g>`;
  }).join("")}</svg><p class="graph-note">GRAY: STRUCTURE · ORANGE: CORRELATION · DASHED: CONTRADICTION</p><p class="factor-note">Associations support review; they do not prove cause. Graph built by NetworkX.</p>${alert.links.map((link)=>`<div class="link-line"><button data-event="${link.event_id}">${link.event_id}</button><span>↔ ${link.anchor_id} · ${escapeHTML(link.reason)} ${link.relation === "contradicts" ? "Contradictory observation." : "Related observation."}</span></div>`).join("")}`;
}
function renderData() {
  const readings = state.frame.events.filter((e)=>e.analysis);
  $("data-view").innerHTML = `<h3>Multivariate sensor readings</h3><p class="data-intro">Four numeric features per bundle. Orange rows exceed the fitted anomaly threshold. Readings arrive with the stream.</p><table class="data-table"><thead><tr><th>EVENT / SOURCE</th><th>V</th><th>°C</th><th>µg/m³</th><th>mm/s</th><th>SCORE</th></tr></thead><tbody>${readings.map((e)=>`<tr class="${e.analysis.is_anomaly ? "flagged" : ""}"><td><button class="text-button" data-event="${e.id}">${e.id} / ${e.source_id}</button></td>${Object.values(e.readings).map(v=>`<td>${v}</td>`).join("")}<td>${e.analysis.raw_score.toFixed(3)}</td></tr>`).join("") || '<tr><td colspan="6">Awaiting sensor events.</td></tr>'}</tbody></table><p class="model-details">Isolation Forest · 200 trees · seed 42<br>1,000 reference rows · threshold ${state.bootstrap.model.threshold.toFixed(4)}<br>Score = −score_samples; larger is more unusual.<br>Training contamination 2% ≠ real-world false-positive rate.</p>`;
}
function exportEvidence() {
  if (!state.run || state.index === 0) return;
  const payload = {application:"BLACKSITE", simulation:true, disclaimer:"SIMULATION — SYNTHETIC DATA ONLY", scenario:state.run.scenario, displayed_event_count:state.index, model:state.run.model, snapshot:state.frame};
  const blob = new Blob([JSON.stringify(payload,null,2)+"\n"], {type:"application/json"});
  const url = URL.createObjectURL(blob); const a = document.createElement("a");
  a.href = url; a.download = `blacksite-${state.run.scenario.id}-event-${pad(state.index)}.json`; a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000); announce("Displayed evidence exported as JSON.");
}

$("run-button").addEventListener("click",runSimulation);
$("reset-button").addEventListener("click",reset);
$("scenario").addEventListener("change",reset);
$("pause-button").addEventListener("click",()=>{if(state.running) pause(); else {state.running=true;tick();}});
$("step-button").addEventListener("click",()=>{pause();showFrame(Math.min(state.index+1,state.run.frames.length));});
$("scrubber").addEventListener("input",()=>{const index=Number($("scrubber").value);pause();showFrame(index);});
$("speed").addEventListener("change",()=>{if(state.running){clearTimeout(state.timer);state.timer=setTimeout(tick,Number($("speed").value));}});
$("export-button").addEventListener("click",exportEvidence);
$("method-button").addEventListener("click",()=>$("method-dialog").showModal());
$("close-method").addEventListener("click",()=>$("method-dialog").close());
$("method-dialog").addEventListener("click",(event)=>{if(event.target === $("method-dialog")){const r=event.target.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom) event.target.close();}});
$("reduce-motion").checked = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
document.body.classList.toggle("reduce-motion",$("reduce-motion").checked);
$("reduce-motion").addEventListener("change",()=>document.body.classList.toggle("reduce-motion",$("reduce-motion").checked));
document.addEventListener("click",(event)=>{
  const target=event.target.closest("[data-event],[data-zone],[data-alert],[data-view],[data-back],[data-show-links]");
  if(!target || !state.bootstrap) return;
  if(target.dataset.event) selectEvent(target.dataset.event);
  else if(target.dataset.zone || target.dataset.alert){state.zone=target.dataset.zone||target.dataset.alert;state.selectedEvent=null;renderMap();renderInspector();renderGraph();}
  else if(target.dataset.view) setView(target.dataset.view);
  else if(target.dataset.back){state.selectedEvent=null;renderTimeline();renderInspector();}
  else if(target.dataset.showLinks) setView("graph");
});
document.addEventListener("keydown",(event)=>{if(["Enter"," "].includes(event.key)&&event.target.matches("g[role=button]")){event.preventDefault();event.target.dispatchEvent(new MouseEvent("click",{bubbles:true}));}});

async function init() {
  try {
    const response = await fetch("/api/bootstrap"); if(!response.ok) throw new Error("Engine unavailable");
    state.bootstrap=await response.json(); state.frame=state.bootstrap.initial;
    $("scenario").innerHTML=state.bootstrap.scenarios.map(s=>`<option value="${s.id}">${escapeHTML(s.name)}</option>`).join("");
    $("scenario").disabled=false; $("run-button").disabled=false; $("reset-button").disabled=false;
    $("engine-status").innerHTML="<i></i> LOCAL ENGINE READY"; render();
  } catch(failure) {
    $("engine-status").textContent="ENGINE OFFLINE";
    error("Cannot reach the local engine. Start the Python application and open its localhost address; do not open index.html directly. Reload this page after starting the server.");
  }
}
init();
