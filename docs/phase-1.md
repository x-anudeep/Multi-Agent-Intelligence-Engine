# Phase 1: Enterprise Foundation

## Objective

Build a production-style foundation for the Multi-Agent Intelligence Engine v2.0 so the repo immediately demonstrates serious architecture instead of a tutorial toy.

## Deliverables

- repository scaffold and developer workflow
- domain contracts for supplier intelligence workflows
- policy-based router with model-provider preferences
- specialized agent interfaces and local deterministic implementations
- tool registry abstraction
- optional LangGraph graph builder
- baseline unit and simulation tests

## File Layout

```text
src/maie/core/config.py
src/maie/domain/models.py
src/maie/graph/builder.py
src/maie/graph/state.py
src/maie/routing/policy.py
src/maie/agents/base.py
src/maie/agents/specialists.py
src/maie/runtime/simulator.py
src/maie/tools/registry.py
src/maie/main.py
tests/test_policy.py
tests/test_registry.py
tests/test_simulation.py
```

## Suggested Commit Slices

### Commit 1

Initialize the repository with project metadata, developer tooling, and architecture documentation.

### Commit 2

Add domain contracts, workflow state, policy router, and agent/tool abstractions.

### Commit 3

Wire the local simulator, optional LangGraph graph builder, and baseline tests.

## Phase Exit Criteria

- a reviewer can understand the architecture in under five minutes
- the repo has a runnable local simulation
- the routing logic is testable without any external model provider
- the codebase is ready for Phase 2 provider adapters and observability

