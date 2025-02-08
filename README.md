# Multi-Agent Intelligence Engine v2.0

Enterprise-grade agentic workflow foundation for financial-services supply chain risk assessment.

## Problem

Banks and financial institutions depend on global supplier networks. When adverse news, SEC filings, and supplier risk signals appear, analysts need a reliable system that can collect evidence, score disruption risk, and generate executive-ready summaries with clear escalation paths.

## Phase 1 Goal

Phase 1 establishes the engineering backbone of the platform:

- typed workflow state
- policy-based routing
- specialized agent contracts
- tool registry abstraction
- local simulation loop
- optional LangGraph graph builder
- baseline tests

## Phase 2 Goal

Phase 2 upgrades the foundation into a more enterprise-like runtime:

- multi-provider abstraction layer for OpenAI, Anthropic, and Vertex AI
- deterministic tool-backed research flow
- workflow checkpointing for auditability and replay
- telemetry events for each routing and agent step
- orchestrated engine that packages state, checkpoints, and execution metadata

## Phase 3 Goal

Phase 3 turns the runtime into a delivery-ready service:

- Pydantic request and response contracts for workflow execution
- application service layer for API-friendly orchestration
- optional FastAPI HTTP surface for enterprise integration
- Docker and Docker Compose assets for local delivery
- Kubernetes manifests for deployment, service exposure, and autoscaling

## Phase 4 Goal

Phase 4 adds the operational intelligence layer expected in enterprise AI delivery:

- local RAG-style retrieval to ground the research agent in policy and domain guidance
- governance review with request inspection and response sanitization
- evaluation harness with reusable dataset-driven scoring
- Terraform assets for provisioning cluster, registry, and deployment foundations

## High-Level Architecture

```text
Inbound Risk Signals
        |
        v
  Workflow State -----------------------------+
        |                                     |
        v                                     |
  Policy Router ----> Agent Selection         |
        |              |                      |
        |              +--> Research Agent ---+
        |              +--> Risk Scoring Agent
        |              +--> Report Agent
        |              +--> Human Review Agent
        |
        +--> Tool Registry
        |
        +--> Observability / Checkpointing (Phase 2+)
```

## Project Structure

```text
.
├── docs/
├── src/maie/
│   ├── agents/
│   ├── core/
│   ├── domain/
│   ├── graph/
│   ├── routing/
│   ├── runtime/
│   └── tools/
└── tests/
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
PYTHONPATH=src python -m maie
```

The local run uses deterministic mock providers so the workflow stays testable without any cloud credentials.

## API Run

After installing API dependencies, the service can be started with:

```bash
python -m pip install -e ".[dev]"
PYTHONPATH=src python -m maie.api.cli
```

Example workflow request:

```json
{
  "supplier_name": "Apex Components",
  "signals": [
    {
      "source": "news",
      "headline": "Port congestion delays high-value semiconductor shipments",
      "summary": "Major logistics bottlenecks are extending shipment timelines by 10 days.",
      "severity": 4,
      "region": "North America"
    },
    {
      "source": "sec_filing",
      "headline": "Supplier disclosed material uncertainty tied to debt covenants",
      "summary": "Latest filing highlights liquidity pressure and refinancing risk.",
      "severity": 5,
      "region": "United States"
    }
  ]
}
```

Container and deployment assets are available in `Dockerfile`, `docker-compose.yml`, and `deploy/kubernetes/`.

## Evaluation Run

Phase 4 includes an offline evaluation harness and a sample dataset:

```bash
PYTHONPATH=src python -m maie.evaluation.cli examples/evals/phase4_eval_cases.json
```

Knowledge documents live under `knowledge/financial-services/`, and Terraform assets live under `infra/terraform/`.

## Why This Matters For Accenture

This repo is intentionally shaped around the kind of work an AI Native Software Engineer does in enterprise delivery:

- policy-driven agent orchestration instead of linear prompt chaining
- modular agent and tool abstractions that can support multiple model providers
- domain-specific workflow state designed for auditability and later evaluation harnesses
- clear separation between proof-of-concept logic and production extensions like telemetry, checkpointing, and human review
