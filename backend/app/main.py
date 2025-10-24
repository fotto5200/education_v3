from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes.session import router as session_router
from .routes.item import router as item_router
from .routes.answer import router as answer_router
from .routes.health import router as health_router
from .store import load_mocks
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler as _default_rate_limit_handler
from .util import get_rate_limiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import inspect
import os

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
async def _json_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Delegate to default to compute headers, then wrap JSON
    resp = _default_rate_limit_handler(request, exc)
    if inspect.isawaitable(resp):
        resp = await resp
    data = {"code": "rate_limited", "message": "Too many requests"}
    out = JSONResponse(status_code=resp.status_code, content=data)
    for k, v in resp.headers.items():
        out.headers[k] = v
    return out

app.add_exception_handler(RateLimitExceeded, _json_rate_limit_handler)
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

# Dev-friendly CSP header for media origins
@app.middleware("http")
async def csp_header(request: Request, call_next):
    response = await call_next(request)
    # IMG src allowlist: self + optional extra origins via env IMG_SRC_EXTRA (comma-separated)
    img_src_extra = os.environ.get("IMG_SRC_EXTRA", "").strip()
    extras = [o.strip() for o in img_src_extra.split(",") if o.strip()]
    img_sources = ["'self'"] + extras
    csp = f"default-src 'self'; img-src {' '.join(img_sources)}; script-src 'self'; style-src 'self' 'unsafe-inline'"
    response.headers.setdefault("Content-Security-Policy", csp)
    return response

app.include_router(session_router, prefix="/api", tags=["session"])
app.include_router(item_router, prefix="/api", tags=["item"])
app.include_router(answer_router, prefix="/api", tags=["answer"])
app.include_router(health_router, prefix="/api", tags=["health"])


# --- Stable JSON error shape for 4xx/5xx ---
@app.exception_handler(HTTPException)
async def _http_exc_handler(request: Request, exc: HTTPException):
    code = exc.detail if isinstance(exc.detail, str) else "http_error"
    msg_map = {400: "Bad request", 401: "Unauthorized", 403: "Forbidden", 404: "Not found"}
    message = msg_map.get(exc.status_code, "Error")
    return JSONResponse(status_code=exc.status_code, content={"code": code, "message": message})


@app.exception_handler(Exception)
async def _generic_exc_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"code": "server_error", "message": "Unexpected error"})
