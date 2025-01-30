# Phase 3: Delivery Surface

## Objective

Package the agentic workflow platform as a service that can be consumed by internal teams, client applications, and deployment pipelines.

## Deliverables

- Pydantic API contracts for workflow execution and checkpoint retrieval
- application service that wraps the workflow engine for HTTP delivery
- optional FastAPI app factory and CLI bootstrap
- Docker and Docker Compose assets for local runtime packaging
- Kubernetes manifests for deployment, service exposure, config, and autoscaling

## File Layout

```text
src/maie/api/contracts.py
src/maie/api/app.py
src/maie/api/cli.py
src/maie/application/workflow_service.py
examples/risk_assessment_request.json
Dockerfile
docker-compose.yml
deploy/kubernetes/configmap.yaml
deploy/kubernetes/deployment.yaml
deploy/kubernetes/service.yaml
deploy/kubernetes/hpa.yaml
tests/test_api_contracts.py
tests/test_workflow_service.py
tests/test_delivery_assets.py
```

## Suggested Commit Slices

### Commit 1

Add API contracts and the application service layer for workflow execution.

### Commit 2

Add the optional HTTP delivery surface plus Docker assets.

### Commit 3

Add Kubernetes manifests, docs, examples, and delivery-focused tests.

## Phase Exit Criteria

- the workflow can be invoked through stable request and response contracts
- the repo includes a deployable HTTP entrypoint
- the project can be containerized locally and targeted at Kubernetes
- the service layer is ready for Phase 4 evaluation, governance, and IaC

