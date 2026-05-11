import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from anthropic import Anthropic, APIError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


load_dotenv() # reads .env from current directory

app = FastAPI()

# Custom function to get real client IP on Render (which proxies requests)
def get_client_ip(request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_client_ip)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

class Question(BaseModel):
    text: str

@app.get("/ask")
@limiter.limit("10/minute")
def ask_get(request: Request, q: str):
    return _ask_claude(q)

@app.post("/ask")
@limiter.limit("10/minute")
def ask_post(request: Request, question: Question):
    return _ask_claude(question.text)

def _ask_claude(text: str):
    try: 
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": text}]
        ) 
        return {"question": text, "answer": message.content[0].text}

    except APIError as e:
        # 502 Bad Gateway indicates an upstream server (Anthropic) error
        raise HTTPException(status_code=502, detail=f"Upstream API Error: {str(e)}")
    except Exception:
        # 500 Internal Server Error for unhandled logic failures
        raise HTTPException(status_code=500, detail="Internal Server Error")

        