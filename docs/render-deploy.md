# Render Free Deployment

This app should be deployed as a Render Web Service, not GitHub Pages, because the browser UI calls Python backend endpoints and the API keys must stay server-side.

## Deploy

1. Push the repository to GitHub.
2. Open Render and choose **New > Blueprint**.
3. Connect this repository.
4. Render will read `render.yaml`.
5. Add these secret environment variables when prompted:

```text
GEMINI_API_KEY
OLLAMA_API_KEY
OPENROUTER_API_KEY
```

The app runs with:

```bash
PYTHONPATH=src python -m maie.demo.cli --host 0.0.0.0 --port $PORT
```

## Notes

Render Free services can sleep when inactive. The first request after sleep may be slow.

The free deployment uses SQLite checkpoints under `/tmp/maie/checkpoints` and in-memory runtime state. This is fine for demos, but not durable production storage.
