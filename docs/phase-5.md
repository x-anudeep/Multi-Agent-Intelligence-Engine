# Phase 5: Live Demo Experience

## Objective

Wrap the platform in a recruiter-friendly live demo that can be launched locally and used to walk through enterprise workflow execution in real time.

## Deliverables

- standard-library live demo server with browser UI
- curated recruiter walkthrough scenarios
- analyst-style dashboard for routing, governance, retrieval, and reporting
- one-command launch path and portfolio-ready documentation

## File Layout

```text
src/maie/demo/service.py
src/maie/demo/server.py
src/maie/demo/cli.py
src/maie/demo/data/scenarios.json
src/maie/demo/web/index.html
src/maie/demo/web/styles.css
src/maie/demo/web/app.js
tests/test_demo_service.py
tests/test_demo_assets.py
tests/test_demo_server.py
```

## Suggested Commit Slices

### Commit 1

Add the live demo backend and scenario service.

### Commit 2

Add the interactive browser UI and launch tooling.

### Commit 3

Add Phase 5 docs, tests, and final demo guidance.

## Demo Exit Criteria

- the project can be demonstrated from a browser without external web frameworks
- scenario presets cover high-risk, moderate-risk, and governance cases
- the demo makes routing, governance, and reporting visible in one screen
- the launch commands are reliable enough for recruiter screenshares and interviews

