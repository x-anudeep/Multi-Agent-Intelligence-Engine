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
  healthCheckpointBackend: document.getElementById("health-checkpoint-backend"),
  healthStateBackend: document.getElementById("health-state-backend"),
  healthAgents: document.getElementById("health-agents"),
  healthScenarios: document.getElementById("health-scenarios"),
  metricRiskScore: document.getElementById("metric-risk-score"),
  metricDisruption: document.getElementById("metric-disruption"),
  metricCheckpoints: document.getElementById("metric-checkpoints"),
  metricSnapshots: document.getElementById("metric-snapshots"),
  metricTelemetry: document.getElementById("metric-telemetry"),
  metricLatency: document.getElementById("metric-latency"),
  metricBranches: document.getElementById("metric-branches"),
  metricTools: document.getElementById("metric-tools"),
  metricStatus: document.getElementById("metric-status"),
  routingPath: document.getElementById("routing-path"),
  governanceStatus: document.getElementById("governance-status"),
  governanceFindings: document.getElementById("governance-findings"),
  runtimeProfile: document.getElementById("runtime-profile"),
  knowledgeHits: document.getElementById("knowledge-hits"),
  checkpointList: document.getElementById("checkpoint-list"),
  snapshotList: document.getElementById("snapshot-list"),
  modelPipeline: document.getElementById("model-pipeline"),
  complianceStatus: document.getElementById("compliance-status"),
  complianceDetails: document.getElementById("compliance-details"),
  reportPreview: document.getElementById("report-preview"),
  auditTrail: document.getElementById("audit-trail"),
};

async function loadHealth() {
  const response = await fetch("/api/demo/health");
  const payload = await response.json();
  elements.healthEnvironment.textContent = payload.environment;
  elements.healthGovernance.textContent = payload.governance_enabled ? "Enabled" : "Disabled";
  elements.healthCheckpointBackend.textContent = payload.checkpoint_backend;
  elements.healthStateBackend.textContent = payload.state_backend;
  elements.healthAgents.textContent = String(payload.agent_count);
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
  elements.metricSnapshots.textContent = String(dashboard.snapshot_count || 0);
  elements.metricTelemetry.textContent = String(dashboard.telemetry_event_count || 0);
  elements.metricLatency.textContent =
    dashboard.average_event_duration_ms === null || dashboard.average_event_duration_ms === undefined
      ? "-"
      : `${Number(dashboard.average_event_duration_ms).toFixed(2)} ms`;
  elements.metricBranches.textContent = String(dashboard.routing_branch_count || 0);
  elements.metricTools.textContent = String(dashboard.tool_runs || 0);
  elements.metricStatus.textContent = humanizeStatus(dashboard.workflow_status);

  renderList(elements.routingPath, dashboard.routing_targets, { chip: true });
  renderList(elements.governanceFindings, dashboard.governance_findings);
  renderList(elements.runtimeProfile, buildRuntimeProfile(dashboard));
  renderList(elements.knowledgeHits, dashboard.knowledge_hits);
  renderList(
    elements.checkpointList,
    checkpoints.checkpoints.map((checkpoint) => checkpoint.label),
  );
  renderList(elements.snapshotList, dashboard.snapshot_labels);
  renderList(elements.modelPipeline, dashboard.model_invocations, { chip: true });
  renderList(elements.complianceDetails, buildComplianceDetails(dashboard));
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

  if (!dashboard.snapshot_labels.length) {
    renderList(elements.snapshotList, ["No runtime snapshots recorded."]);
  }

  if (!dashboard.model_invocations.length) {
    renderList(elements.modelPipeline, ["No model invocations recorded."], { chip: true });
  }

  const compliance = dashboard.compliance_review;
  if (compliance && compliance.blocking_findings && compliance.blocking_findings.length) {
    elements.complianceStatus.className = "status-badge review";
    elements.complianceStatus.textContent = "Conditional";
  } else if (compliance) {
    elements.complianceStatus.className = "status-badge approved";
    elements.complianceStatus.textContent = "Approved";
  } else {
    elements.complianceStatus.className = "status-badge neutral";
    elements.complianceStatus.textContent = "Not Required";
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

function humanizeStatus(value) {
  if (!value) {
    return "-";
  }
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function buildRuntimeProfile(dashboard) {
  return [
    `Checkpoint store: ${valueOrDash(dashboard.checkpoint_location)}`,
    `Human decision: ${humanizeStatus(dashboard.human_decision)}`,
    `Requires human review: ${dashboard.requires_human_review ? "Yes" : "No"}`,
    `Sector: ${valueOrDash(dashboard.sector)} | Jurisdiction: ${valueOrDash(dashboard.jurisdiction)}`,
  ];
}

function buildComplianceDetails(dashboard) {
  const compliance = dashboard.compliance_review;
  if (!compliance) {
    return ["No compliance review was required for this workflow."];
  }

  return [
    `Status: ${humanizeStatus(compliance.status)}`,
    `Summary: ${compliance.summary}`,
    `Obligations: ${(compliance.obligations || []).join("; ") || "None"}`,
    `Mitigation plan: ${(dashboard.recovery_actions || []).join("; ") || "None"}`,
    `Blocking findings: ${(compliance.blocking_findings || []).join("; ") || "None"}`,
  ];
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
