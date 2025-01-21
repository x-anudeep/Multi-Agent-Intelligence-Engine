# Phase 2: Enterprise Runtime

## Objective

Extend the workflow foundation with the kinds of runtime capabilities that make an agentic system viable in delivery environments: provider abstraction, checkpointing, telemetry, and deterministic tool-backed orchestration.

## Deliverables

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

## Suggested Commit Slices

### Commit 1

Add provider abstractions and a reusable intelligence tool pack.

### Commit 2

Add checkpointing, telemetry, and configuration for enterprise workflow traces.

### Commit 3

Wire the workflow engine, integrate the agents, and add Phase 2 tests.

## Phase Exit Criteria

- each agent can resolve a provider through a common abstraction layer
- each workflow run produces checkpoint history and telemetry events
- local runs remain deterministic and CI-friendly
- the platform is ready for Phase 3 API delivery, containers, and deployment assets

