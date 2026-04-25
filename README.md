# Multi-Agent Intelligence Engine v2.0

Enterprise-grade agentic workflow platform for financial-services supply chain risk assessment.

[Live Demo](https://multi-agent-intelligence-engine.onrender.com)

## Overview

Banks and financial institutions depend on global supplier networks. When adverse news, SEC filings, and supplier risk signals appear, analysts need a reliable system that can collect evidence, score disruption risk, and generate executive-ready summaries with clear escalation paths.

The Multi-Agent Intelligence Engine coordinates specialist agents across research, risk scoring, compliance review, reporting, and human escalation. It is designed for auditable workflow execution with typed state, policy routing, runtime snapshots, checkpoint persistence, telemetry, and deployable browser/API surfaces.

## Platform Capabilities

- Typed workflow state and policy-based routing
- Specialist research, risk scoring, compliance, reporting, and human review agents
- Live provider orchestration across Gemini, Ollama, and OpenRouter
- Deterministic tool-backed research with relational checkpointing, runtime snapshots, and telemetry
- Local knowledge retrieval, governance review, evaluation harnesses, and benchmark mode
- FastAPI contracts, container runtime assets, Kubernetes manifests, and Render deployment config
- Browser-based live demo with direct supplier risk input, scenario presets, and formatted backend results

## Live Demo

Use the hosted demo here:

https://multi-agent-intelligence-engine.onrender.com

The demo dashboard exposes:

- Routing path and branch coverage
- Checkpoints and runtime snapshots
- Telemetry volume and average event duration
- Compliance posture, governance findings, and recovery actions
- Model pipeline activity and the final executive brief
- A plain-English scenario builder that drafts runnable workflow JSON

Render Free services can sleep when inactive, so the first request after a quiet period may take a moment.

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
├── deploy/
├── docs/
├── examples/
├── infra/
├── knowledge/
├── src/maie/
│   ├── agents/
│   ├── api/
│   ├── application/
│   ├── checkpoints/
│   ├── core/
│   ├── demo/
│   ├── domain/
│   ├── evaluation/
│   ├── governance/
│   ├── graph/
│   ├── knowledge/
│   ├── observability/
│   ├── providers/
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
maie
```

Set `GEMINI_API_KEY`, `OLLAMA_API_KEY`, and `OPENROUTER_API_KEY` in `.env` for the live provider workflow. The test suite uses offline providers so the repository remains verifiable without cloud credentials.

## Local Demo

Run the browser demo locally:

```bash
maie-demo
```

Or with `make`:

```bash
make demo
```

Open `http://127.0.0.1:8090` in your browser.

## API Run

Start the FastAPI service with:

```bash
maie-api
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

## Evaluation And Benchmarking

Run the offline evaluation harness against the sample dataset:

```bash
maie-eval examples/evals/workflow_eval_cases.json
```

Benchmark mode measures pass rate, latency, checkpoint volume, snapshot volume, and branch coverage:

```bash
make benchmark
```

Knowledge documents live under `knowledge/financial-services/`, and Terraform assets live under `infra/terraform/`.

## Deployment

Container and deployment assets are available in:

- `Dockerfile`
- `docker-compose.yml`
- `render.yaml`
- `deploy/kubernetes/`
- `infra/terraform/`

The Render Blueprint runs the browser demo as a web service:

```bash
PYTHONPATH=src python -m maie.demo.cli --host 0.0.0.0 --port $PORT
```

Required secret environment variables:

```text
GEMINI_API_KEY
OLLAMA_API_KEY
OPENROUTER_API_KEY
```

See `docs/render-deploy.md` for the Render setup notes.

## Documentation

- `docs/foundation.md`
- `docs/runtime-architecture.md`
- `docs/service-delivery.md`
- `docs/governance-evaluation-iac.md`
- `docs/live-demo.md`
- `docs/render-deploy.md`

## Engineering Principles

This repository is designed around production-oriented agentic workflow engineering:

- Policy-driven agent orchestration instead of linear prompt chaining
- Modular agent and tool abstractions that support multiple model providers
- Domain-specific workflow state designed for auditability and evaluation
- Clear separation between workflow logic, delivery surfaces, and operational controls
- Postgres-ready checkpoint persistence with SQLite fallback and Redis-ready runtime snapshots
