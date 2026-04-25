const elements = {
  form: document.getElementById("risk-form"),
  supplierName: document.getElementById("supplier-name"),
  sector: document.getElementById("sector"),
  jurisdiction: document.getElementById("jurisdiction"),
  signalsList: document.getElementById("signals-list"),
  addSignalButton: document.getElementById("add-signal"),
  submitButton: document.getElementById("submit-workflow"),
  formStatus: document.getElementById("form-status"),
  signalTemplate: document.getElementById("signal-template"),
  healthStatus: document.getElementById("health-status"),
  healthMode: document.getElementById("health-mode"),
  riskScore: document.getElementById("risk-score"),
  disruptionProbability: document.getElementById("disruption-probability"),
  workflowStatus: document.getElementById("workflow-status"),
  humanReview: document.getElementById("human-review"),
  complianceDetails: document.getElementById("compliance-details"),
  reportPreview: document.getElementById("report-preview"),
};

function addSignal(defaults = {}) {
  const fragment = elements.signalTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".signal-card");

  card.querySelector(".signal-source").value = defaults.source || "news";
  card.querySelector(".signal-severity").value = String(defaults.severity || 3);
  card.querySelector(".signal-region").value = defaults.region || "";
  card.querySelector(".signal-headline").value = defaults.headline || "";
  card.querySelector(".signal-summary").value = defaults.summary || "";

  card.querySelector(".remove-signal").addEventListener("click", () => {
    if (elements.signalsList.children.length === 1) {
      setStatus("At least one signal is required.", true);
      return;
    }
    card.remove();
    renumberSignals();
  });

  elements.signalsList.appendChild(fragment);
  renumberSignals();
}

function renumberSignals() {
  [...elements.signalsList.querySelectorAll(".signal-card")].forEach((card, index) => {
    card.querySelector(".signal-number").textContent = String(index + 1);
  });
}

function buildPayload() {
  const signals = [...elements.signalsList.querySelectorAll(".signal-card")].map((card) => ({
    source: card.querySelector(".signal-source").value,
    headline: card.querySelector(".signal-headline").value.trim(),
    summary: card.querySelector(".signal-summary").value.trim(),
    severity: Number(card.querySelector(".signal-severity").value),
    region: card.querySelector(".signal-region").value.trim(),
  }));

  return {
    supplier_name: elements.supplierName.value.trim(),
    sector: elements.sector.value,
    jurisdiction: elements.jurisdiction.value.trim(),
    signals,
  };
}

async function runWorkflow(event) {
  event.preventDefault();

  if (!elements.form.reportValidity()) {
    return;
  }

  const payload = buildPayload();
  setStatus("Sending request to backend...");
  elements.submitButton.disabled = true;

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
      throw new Error(result.error || "Backend workflow failed.");
    }

    renderResult(result);
    setStatus("Risk assessment complete.");
  } catch (error) {
    setStatus(error.message || "Backend workflow failed.", true);
  } finally {
    elements.submitButton.disabled = false;
  }
}

async function loadHealth() {
  try {
    const response = await fetch("/api/demo/health");
    const payload = await response.json();
    elements.healthStatus.textContent = payload.status === "ok" ? "Backend online" : "Backend unavailable";
    elements.healthMode.textContent = `${payload.provider_mode} providers`;
  } catch (error) {
    elements.healthStatus.textContent = "Backend unavailable";
    elements.healthMode.textContent = "Check server";
  }
}

function renderResult(result) {
  const dashboard = result.dashboard || {};
  const workflow = result.workflow || {};
  const state = workflow.state_snapshot || {};
  const compliance = dashboard.compliance_review;

  elements.riskScore.textContent = valueOrDash(dashboard.risk_score);
  elements.disruptionProbability.textContent =
    dashboard.disruption_probability === null || dashboard.disruption_probability === undefined
      ? "-"
      : `${Math.round(Number(dashboard.disruption_probability) * 100)}%`;
  elements.workflowStatus.textContent = humanize(dashboard.workflow_status);
  elements.humanReview.textContent = dashboard.requires_human_review ? "Yes" : "No";
  elements.reportPreview.innerHTML = renderMarkdownReport(
    dashboard.report_preview || "No report was generated.",
  );

  const complianceItems = compliance
    ? [
        `Status: ${humanize(compliance.status)}`,
        `Summary: ${compliance.summary}`,
        `Obligations: ${(compliance.obligations || []).join("; ") || "None"}`,
        `Mitigation plan: ${(dashboard.recovery_actions || []).join("; ") || "None"}`,
        `Blocking findings: ${(compliance.blocking_findings || []).join("; ") || "None"}`,
      ]
    : ["Compliance review is still pending for this request."];

  if (state.knowledge_hits && state.knowledge_hits.length) {
    complianceItems.push(`Knowledge hits: ${state.knowledge_hits.length}`);
  }

  renderList(elements.complianceDetails, complianceItems);
}

function renderList(target, items, options = {}) {
  target.innerHTML = "";

  if (!items.length) {
    const item = document.createElement("li");
    item.textContent = "No data available.";
    target.appendChild(item);
    return;
  }

  items.forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = humanize(entry);
    if (options.chip) {
      item.className = "chip";
    }
    target.appendChild(item);
  });
}

function setStatus(message, isError = false) {
  elements.formStatus.textContent = message;
  elements.formStatus.classList.toggle("error", isError);
}

function valueOrDash(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function humanize(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function renderMarkdownReport(markdown) {
  return escapeHtml(markdown)
    .replace(/^# (.*)$/gm, "<h2>$1</h2>")
    .replace(/^## (.*)$/gm, "<h3>$1</h3>")
    .replace(/^- (.*)$/gm, "<li>$1</li>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n{2,}/g, "</p><p>")
    .replace(/\n/g, "<br>");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

elements.form.addEventListener("submit", runWorkflow);
elements.addSignalButton.addEventListener("click", () => addSignal());

addSignal({
  source: "news",
  severity: 4,
  region: "North America",
  headline: "Port congestion delays semiconductor shipments",
  summary: "Shipment timelines are delayed by 10 days.",
});

loadHealth();
