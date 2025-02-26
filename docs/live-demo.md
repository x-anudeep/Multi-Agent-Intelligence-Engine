# Live Demo Experience

## Purpose

Wrap the platform in a local browser experience that makes workflow execution easy to inspect in real time.

## Core Components

- standard-library live demo server with browser UI
- curated scenario presets
- analyst-style dashboard for routing, governance, compliance posture, runtime persistence, latency, retrieval, and reporting
- one-command launch path and user-facing documentation

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

## Demo Exit Criteria

- the project can be demonstrated from a browser without external web frameworks
- scenario presets cover high-risk, moderate-risk, and governance cases
- the demo makes routing, governance, and reporting visible in one screen
- the demo exposes runtime metrics such as snapshots, latency, branch coverage, and backend modes
- the launch commands are reliable enough for repeated local runs and demos
