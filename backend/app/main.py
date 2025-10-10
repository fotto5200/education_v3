from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.session import router as session_router
from .routes.item import router as item_router
from .routes.answer import router as answer_router
from .store import load_mocks

app = FastAPI(title="Education v3 API", version="0.1.0")

# Allow Vite dev server
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

@app.on_event("startup")
async def startup_event() -> None:
    load_mocks()

app.include_router(session_router, prefix="/api", tags=["session"])
app.include_router(item_router, prefix="/api", tags=["item"])
app.include_router(answer_router, prefix="/api", tags=["answer"])
