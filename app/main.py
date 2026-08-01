from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import menu, chat, orders

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="🍛 Spice Garden Restaurant API — Powered by Groq + LangChain",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(menu.router)
app.include_router(chat.router)
app.include_router(orders.router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "🍛 Spice Garden API is running!",
        "model": "llama-3.1-8b-instant (Groq)",
        "docs": "/docs",
    }

@app.get("/api/health", tags=["Health"])
def health():
    return {
        "api": "ok",
        "model": "llama-3.1-8b-instant",
        "provider": "Groq",
        "status": "running",
    }