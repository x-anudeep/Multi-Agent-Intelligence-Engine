# Phase 4: Quality, Governance, and IaC

## Objective

Finish the platform with the controls and measurement systems expected in enterprise AI delivery: grounding, governance, evaluation, and infrastructure as code.

## Deliverables

- local RAG-style retrieval layer for policy and domain grounding
- governance review and response sanitization
- dataset-driven evaluation harness with CLI entrypoint
- Terraform assets for GKE-oriented deployment foundations

## File Layout

```text
src/maie/knowledge/documents.py
src/maie/knowledge/retriever.py
src/maie/governance/policies.py
src/maie/evaluation/contracts.py
src/maie/evaluation/harness.py
src/maie/evaluation/cli.py
knowledge/financial-services/
examples/evals/phase4_eval_cases.json
infra/terraform/providers.tf
infra/terraform/main.tf
infra/terraform/variables.tf
infra/terraform/outputs.tf
```

## Suggested Commit Slices

### Commit 1

Add knowledge retrieval and governance controls to the workflow platform.

### Commit 2

Add the evaluation harness, CLI, and sample dataset.

### Commit 3

Add Terraform infrastructure assets, docs, and final Phase 4 tests.

## Phase Exit Criteria

- the research flow can pull domain grounding from a local knowledge base
- workflow requests and responses pass through explicit governance logic
- quality can be measured through reusable evaluation datasets
- the project includes Terraform assets that match the deployment story

