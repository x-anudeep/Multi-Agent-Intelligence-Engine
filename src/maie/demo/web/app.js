const state = {
  scenarios: [],
  selectedScenarioId: null,
};

const elements = {
  scenarioList: document.getElementById("scenario-list"),
  requestEditor: document.getElementById("request-editor"),
  runButton: document.getElementById("run-demo"),
  reloadButton: document.getElementById("reload-scenarios"),
  formatButton: document.getElementById("format-json"),
  runStatus: document.getElementById("run-status"),
  healthEnvironment: document.getElementById("health-environment"),
  healthGovernance: document.getElementById("health-governance"),
  healthScenarios: document.getElementById("health-scenarios"),
  metricRiskScore: document.getElementById("metric-risk-score"),
  metricDisruption: document.getElementById("metric-disruption"),
  metricCheckpoints: document.getElementById("metric-checkpoints"),
  metricTelemetry: document.getElementById("metric-telemetry"),
  routingPath: document.getElementById("routing-path"),
  governanceStatus: document.getElementById("governance-status"),
  governanceFindings: document.getElementById("governance-findings"),
  knowledgeHits: document.getElementById("knowledge-hits"),
  checkpointList: document.getElementById("checkpoint-list"),
  reportPreview: document.getElementById("report-preview"),
  auditTrail: document.getElementById("audit-trail"),
};

async function loadHealth() {
  const response = await fetch("/api/demo/health");
  const payload = await response.json();
  elements.healthEnvironment.textContent = payload.environment;
  elements.healthGovernance.textContent = payload.governance_enabled ? "Enabled" : "Disabled";
  elements.healthScenarios.textContent = String(payload.scenarios_available);
}

async function loadScenarios() {
  setStatus("Loading scenarios...");
  const response = await fetch("/api/demo/scenarios");
  const payload = await response.json();
  state.scenarios = payload.scenarios || [];
  elements.scenarioList.innerHTML = "";

  state.scenarios.forEach((scenario, index) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "scenario-card";
    card.innerHTML = `
      <header>
        <h3>${escapeHtml(scenario.title)}</h3>
        <span class="scenario-badge">${escapeHtml(scenario.badge)}</span>
      </header>
      <p>${escapeHtml(scenario.summary)}</p>
    `;
    card.addEventListener("click", () => selectScenario(scenario.id));
    elements.scenarioList.appendChild(card);
    scenario._element = card;

    if (index === 0) {
      selectScenario(scenario.id);
    }
  });

  setStatus("Scenarios ready.");
}

function selectScenario(scenarioId) {
  state.selectedScenarioId = scenarioId;
  const selected = state.scenarios.find((scenario) => scenario.id === scenarioId);
  if (!selected) {
    return;
  }

  state.scenarios.forEach((scenario) => {
    scenario._element?.classList.toggle("active", scenario.id === scenarioId);
  });

  elements.requestEditor.value = JSON.stringify(selected.request, null, 2);
}

function formatJsonEditor() {
  try {
    const parsed = JSON.parse(elements.requestEditor.value);
    elements.requestEditor.value = JSON.stringify(parsed, null, 2);
    setStatus("JSON formatted.");
  } catch (error) {
    setStatus("JSON formatting failed. Fix the request body first.", true);
  }
}

async function runWorkflow() {
  let payload;
  try {
    payload = JSON.parse(elements.requestEditor.value);
  } catch (error) {
    setStatus("Request JSON is invalid.", true);
    return;
  }

  setStatus("Running workflow...");
  elements.runButton.disabled = true;

  try {
    const response = await fetch("/api/demo/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Live demo execution failed.");
    }
    renderResult(result);
    setStatus("Workflow complete.");
  } catch (error) {
    setStatus(error.message || "Live demo execution failed.", true);
  } finally {
    elements.runButton.disabled = false;
  }
}

function renderResult(result) {
  const workflow = result.workflow;
  const dashboard = result.dashboard;
  const checkpoints = result.checkpoints;

  elements.metricRiskScore.textContent = valueOrDash(dashboard.risk_score);
  elements.metricDisruption.textContent =
    dashboard.disruption_probability === null
      ? "-"
      : `${Number(dashboard.disruption_probability * 100).toFixed(0)}%`;
  elements.metricCheckpoints.textContent = String(dashboard.checkpoint_count || 0);
  elements.metricTelemetry.textContent = String(dashboard.telemetry_event_count || 0);

  renderList(elements.routingPath, dashboard.routing_targets, { chip: true });
  renderList(elements.governanceFindings, dashboard.governance_findings);
  renderList(elements.knowledgeHits, dashboard.knowledge_hits);
  renderList(
    elements.checkpointList,
    checkpoints.checkpoints.map((checkpoint) => checkpoint.label),
  );
  renderList(elements.auditTrail, dashboard.audit_trail);

  elements.reportPreview.textContent =
    dashboard.report_preview || "No report preview available.";

  const statusClass = dashboard.governance_approved ? "approved" : "review";
  elements.governanceStatus.className = `status-badge ${statusClass}`;
  elements.governanceStatus.textContent = dashboard.governance_approved
    ? "Approved"
    : "Review Needed";

  if (!dashboard.governance_findings.length) {
    renderList(elements.governanceFindings, ["No governance findings triggered for this run."]);
  }

  if (!dashboard.knowledge_hits.length) {
    renderList(elements.knowledgeHits, ["No knowledge retrieval hits were attached to this run."]);
  }

  if (!dashboard.audit_trail.length) {
    renderList(elements.auditTrail, ["No audit trail events recorded."]);
  }
}

function renderList(target, items, options = {}) {
  target.innerHTML = "";
  if (!items || !items.length) {
    const item = document.createElement("li");
    item.textContent = "No data available.";
    target.appendChild(item);
    return;
  }

  items.forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    if (options.chip) {
      target.appendChild(item);
      return;
    }
    target.appendChild(item);
  });
}

function setStatus(message, isError = false) {
  elements.runStatus.textContent = message;
  elements.runStatus.style.color = isError ? "#a64d2d" : "";
}

function valueOrDash(value) {
  return value === null || value === undefined ? "-" : String(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

elements.runButton.addEventListener("click", runWorkflow);
elements.reloadButton.addEventListener("click", loadScenarios);
elements.formatButton.addEventListener("click", formatJsonEditor);

Promise.all([loadHealth(), loadScenarios()]).catch((error) => {
  setStatus(error.message || "Demo initialization failed.", true);
});

