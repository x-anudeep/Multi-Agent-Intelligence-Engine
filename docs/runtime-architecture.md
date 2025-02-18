# Runtime Architecture

## Purpose

Extend the workflow foundation with the kinds of runtime capabilities that make an agentic system viable in delivery environments: provider abstraction, checkpointing, telemetry, and deterministic tool-backed orchestration.

## Core Components

- provider registry with OpenAI, Anthropic, and Vertex AI abstractions
- deterministic mock providers for offline development and CI
- intelligence tool pack for news, SEC filings, supplier profile, and regional exposure
- file-backed checkpoint store for workflow audit trails
- telemetry collector for routing, agent, and workflow lifecycle events
- workflow engine that coordinates agents, tools, providers, and persistence

## File Layout

```text
src/maie/providers/base.py
src/maie/providers/mock.py
src/maie/providers/registry.py
src/maie/tools/intelligence.py
src/maie/checkpoints/store.py
src/maie/observability/telemetry.py
src/maie/runtime/engine.py
tests/test_providers.py
tests/test_checkpoints.py
tests/test_engine.py
```

## Readiness Criteria

- each agent can resolve a provider through a common abstraction layer
- each workflow run produces checkpoint history and telemetry events
- local runs remain deterministic and CI-friendly
- the platform is ready for API delivery, containers, and deployment assets
