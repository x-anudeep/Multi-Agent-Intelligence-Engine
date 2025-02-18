# Foundation

## Purpose

Define the core architecture for the Multi-Agent Intelligence Engine, including domain contracts, workflow state, routing, specialized agents, and local execution support.

## Core Components

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

## Readiness Criteria

- a reviewer can understand the architecture in under five minutes
- the repo has a runnable local simulation
- the routing logic is testable without any external model provider
- the codebase is ready for provider adapters and observability
