# CLAUDE.md

## What this is

LLM Ask API is a small FastAPI service that wraps Anthropic's Claude behind
two REST endpoints. A client sends a question (`GET /ask?q=...` or
`POST /ask` with `{"text": "..."}`), the service forwards it to Claude Haiku
4.5, and returns `{"question": ..., "answer": ...}`. It's deployed on Render
and published as a Docker image (`digitalrower/llm-ask-api`). See
`README.md` for the full API reference, setup walkthrough, and live demo
link.

## Why it's built this way

This is a deliberately small, finished project, not a foundation for a
larger service. There is no plan to add a database, an auth layer, or split
the app across multiple modules. Suggestions to introduce those, or to
migrate frameworks, should be treated as out of scope unless the user asks
for them directly.

Given that scope, a few choices follow directly:

- **Single file.** `src/main.py` holds the app, the rate limiter, the
  Anthropic client, both route handlers, and the shared request logic. A
  two-endpoint service doesn't need routers/services/schemas layering — that
  structure would add indirection without adding clarity here.
- **Rate limiting instead of auth.** The service has no API keys or user
  accounts; anyone with the URL can call it. `slowapi` limits each caller to
  10 requests/minute, which is the actual abuse mitigation. The limiter key
  function reads `X-Forwarded-For` before falling back to the raw remote
  address, because Render terminates connections behind a proxy — without
  that, every caller would share the proxy's IP and the limit would apply
  globally instead of per-client.
- **Fail-fast startup.** The Anthropic client reads `ANTHROPIC_API_KEY` from
  the environment at import time (`os.environ[...]`, not `.get(...)`), so a
  missing key crashes the process on boot rather than surfacing as a
  confusing error on the first request.
- **No conversation state.** Each request is independent by design. There's
  no session or history handling to reason about.

## Architecture

`src/main.py`, top to bottom:

1. `load_dotenv()` pulls `ANTHROPIC_API_KEY` from a local `.env` in
   development; in Docker/Render it's already in the environment.
2. `get_client_ip()` and the `slowapi` `Limiter` set up per-IP rate limiting,
   applied via `@limiter.limit("10/minute")` on both routes.
3. The `Anthropic` client is constructed once at module load.
4. `ask_get` (`GET /ask`) and `ask_post` (`POST /ask`, body validated by the
   `Question` Pydantic model) both delegate to `_ask_claude`.
5. `_ask_claude` calls `client.messages.create(...)` with
   `model="claude-haiku-4-5-20251001"` and `max_tokens=500`, and returns the
   first content block's text.

**Error status codes:**

| Status | When |
|--------|------|
| 200 | Success |
| 422 | FastAPI/Pydantic request validation failure (missing `q`, malformed JSON body) — FastAPI's default, not custom-handled |
| 429 | Rate limit exceeded (`slowapi`) |
| 502 | Any `anthropic.APIError`, including upstream auth failures |
| 500 | Any other unhandled exception |

This matches the error table in `README.md`. If `_ask_claude`'s error
handling changes, update both tables together.

## Working in this repo

**Local run:**

```
pyenv local 3.13.3
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
uvicorn src.main:app --reload
```

Server is at `http://localhost:8000`, interactive docs at `/docs`.

**Docker:** `docker build -t llm-ask-api:latest .` then
`docker run --rm -p 8000:8000 --env-file .env llm-ask-api:latest`. The image
runs as a non-root user; secrets are passed at runtime via `--env-file`,
never baked into the image.

**Changing behavior:**
- Model and token limit are set in `_ask_claude` in `src/main.py`.
- Rate limit is set in the two `@limiter.limit(...)` decorators.

**Verifying changes:** there are no automated tests or CI. After any change,
run the server locally and exercise both routes:

```
curl "localhost:8000/ask?q=what+is+fastapi"
curl -X POST localhost:8000/ask -H "Content-Type: application/json" -d '{"text":"what is fastapi"}'
```

## Files that matter

- `src/main.py` — the entire application
- `requirements.txt` — pinned dependencies
- `Dockerfile`, `.dockerignore` — container build
- `.env.example` — required environment variable template
- `README.md` — user-facing docs (live demo, full API reference, deployment
  steps); keep it in sync with `main.py` when endpoint behavior changes
