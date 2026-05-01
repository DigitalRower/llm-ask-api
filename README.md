# llm-ask-api 

A FastAPI service that accepts questions and returns answers generated 
by Claude (Anthropic). Deployed on Render with environment-variable-based 
API key management.

---

## Live demo

Base URL: `https://your-app-name.onrender.com`

> **Note on cold starts:** The free Render tier sleeps after 15 minutes 
> of inactivity. First request after idle takes 30–60 seconds. 
> Subsequent requests respond in 2–6 seconds.

---

## What it does

Exposes two endpoints:

- `GET /ask?q=your+question` — accepts a question as a URL query parameter
- `POST /ask` — accepts a question as a JSON body

Both call the Anthropic Claude API and return a JSON response containing 
the original question and Claude's answer.

---

## Requirements
- Python 3.13+
- Git
- An Anthropic API key ([get one here](https://console.anthropic.com))


## Local setup

**Clone and enter the project:**

    git clone https://github.com/digitalrower/llm-ask-api.git
    cd llm-ask-api


**Pin Python version (requires pyenv):**

    pyenv local 3.13.3
    python --version              # should show Python 3.13.3

**Create and activate a virtual environment:**

    python -m venv .venv
    source .venv/bin/activate     # Mac/Linux
    # Windows: .venv\Scripts\activate

**Install dependencies:**

    pip install -r requirements.txt

**Set up environment variables:**

    cp .env.example .env

Open `.env` and replace the placeholder with your actual Anthropic API key:

    ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here


---

## Run locally

    uvicorn src.main:app --reload

Server starts at `http://localhost:8000`

Interactive API docs available at `http://localhost:8000/docs`

---

## API reference

### GET /ask

Returns a Claude-generated answer to a question passed as a query parameter.

**Request:**

    GET /ask?q=what+is+retrieval+augmented+generation

**Response:**

```json
{
  "question": "what is retrieval augmented generation",
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that..."
}
```

**Example — browser:**

    https://your-app-name.onrender.com/ask?q=what+is+fastapi

---

### POST /ask

Returns a Claude-generated answer to a question passed as a JSON body.

**Request:**

    POST /ask
    Content-Type: application/json

    {
      "text": "what is retrieval augmented generation"
    }

**Response:**

```json
{
  "question": "what is retrieval augmented generation",
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that..."
}
```

**Example — curl:**

    curl -X POST https://your-app-name.onrender.com/ask \
      -H "Content-Type: application/json" \
      -d '{"text": "what is retrieval augmented generation"}'

**Example — Python:**

```python
import requests

response = requests.post(
    "https://your-app-name.onrender.com/ask",
    json={"text": "what is retrieval augmented generation"}
)
print(response.json()["answer"])
```

---

## Error handling

The API returns standard HTTP error codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request — missing or empty question |
| 401 | Authentication error — invalid API key |
| 429 | Rate limit reached — retry after a moment |
| 500 | Internal server error — check server logs |

---

## Project structure

    llm-ask-api/
    ├── src/
    │   └── main.py          # FastAPI app and endpoint definitions
    ├── .env.example         # Environment variable template
    ├── .gitignore
    ├── requirements.txt
    └── README.md

---

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) — Python web framework
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) — Claude API client
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment variable management
- [Render](https://render.com/) — Cloud deployment (free tier)

---

## Deployment

This service is deployed on Render as a Python web service.

**To deploy your own instance:**

1. Fork this repo
2. Create a new Web Service on Render connected to your fork
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable `ANTHROPIC_API_KEY` in Render's dashboard
6. Deploy

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key from console.anthropic.com |

See `.env.example` for the template.

---

## License

MIT


    