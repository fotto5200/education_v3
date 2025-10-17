from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes.session import router as session_router
from .routes.item import router as item_router
from .routes.answer import router as answer_router
from .store import load_mocks
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from .util import get_rate_limiter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Education v3 API", version="0.1.0")

@app.on_event("startup")
async def startup_event() -> None:
    load_mocks()

# Serve local media files (SVG/PNG) at /media for development
ROOT = Path(__file__).resolve().parents[2]
app.mount("/media", StaticFiles(directory=ROOT / "media"), name="media")

# Rate limiting (slowapi)
limiter = get_rate_limiter()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Allow Vite dev server (place CORS after slowapi so OPTIONS preflight bypasses limiter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(session_router, prefix="/api", tags=["session"])
app.include_router(item_router, prefix="/api", tags=["item"])
app.include_router(answer_router, prefix="/api", tags=["answer"])
