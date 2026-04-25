# Multi-Agent Intelligence Engine v2.0

Enterprise-grade agentic workflow platform for financial-services supply chain risk assessment.

## Overview

Banks and financial institutions depend on global supplier networks. When adverse news, SEC filings, and supplier risk signals appear, analysts need a reliable system that can collect evidence, score disruption risk, and generate executive-ready summaries with clear escalation paths.

## Platform Capabilities

- typed workflow state and policy-based routing
- specialized research, scoring, compliance, reporting, and human review agents
- live multi-provider orchestration across Gemini, Ollama, and OpenRouter
- deterministic tool-backed research with relational checkpointing, runtime snapshots, and telemetry
- API contracts, container runtime assets, and Kubernetes manifests
- local knowledge retrieval, governance review, and evaluation harnesses
- browser-based live demo with direct supplier risk input and formatted backend results

## High-Level Architecture

```text
Inbound Risk Signals
        |
        v
  Workflow State / Runtime Snapshots ---------+
        |                                     |
        v                                     |
  Policy Router ----> Agent Selection         |
        |              |                      |
        |              +--> Research Agent ---+
        |              +--> Risk Scoring Agent
        |              +--> Compliance Review Agent
        |              +--> Report Agent
        |              +--> Human Review Agent
        |
        +--> Tool Registry
        |
        +--> Observability / Checkpointing
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

Set `GEMINI_API_KEY`, `OLLAMA_API_KEY`, and `OPENROUTER_API_KEY` in `.env` for the finished live provider workflow.
The test suite still uses offline providers so the repository remains verifiable without cloud credentials.

## Documentation

- `docs/foundation.md`
- `docs/runtime-architecture.md`
- `docs/service-delivery.md`
- `docs/governance-evaluation-iac.md`
- `docs/live-demo.md`
- `docs/render-deploy.md`

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

The project includes an offline evaluation harness and a sample dataset:

```bash
PYTHONPATH=src python -m maie.evaluation.cli examples/evals/workflow_eval_cases.json
```

Knowledge documents live under `knowledge/financial-services/`, and Terraform assets live under `infra/terraform/`.

Benchmark mode measures pass rate, latency, checkpoint volume, snapshot volume, and branch coverage:

```bash
make benchmark
```

## Live Demo Run

The platform includes a local browser demo that runs without FastAPI, Streamlit, or any frontend framework:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
PYTHONPATH=src .venv/bin/python -m maie.demo.cli
```

Or with `make`:

```bash
make demo
```

Open `http://127.0.0.1:8090` in your browser to use the live demo.

The live dashboard exposes:

- routing path and branch coverage
- checkpoints and runtime snapshots
- telemetry volume and average event duration
- compliance posture, governance findings, and recovery actions
- model pipeline activity and the final executive brief
- a plain-English scenario builder that drafts runnable workflow JSON

## Engineering Principles

This repository is designed around production-oriented agentic workflow engineering:

- policy-driven agent orchestration instead of linear prompt chaining
- modular agent and tool abstractions that can support multiple model providers
- domain-specific workflow state designed for auditability and evaluation
- clear separation between workflow logic, delivery surfaces, and operational controls
- Postgres-ready checkpoint persistence with SQLite fallback and Redis-ready runtime snapshots
