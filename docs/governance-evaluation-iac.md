# Governance, Evaluation, and IaC

## Purpose

Finish the platform with the controls and measurement systems expected in enterprise AI delivery: grounding, governance, evaluation, and infrastructure as code.

## Core Components

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
examples/evals/workflow_eval_cases.json
infra/terraform/providers.tf
infra/terraform/main.tf
infra/terraform/variables.tf
infra/terraform/outputs.tf
```

## Readiness Criteria

- the research flow can pull domain grounding from a local knowledge base
- workflow requests and responses pass through explicit governance logic
- quality can be measured through reusable evaluation datasets
- the project includes Terraform assets that match the deployment story
