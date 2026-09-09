"""
BEM 100 v2.0 - FastAPI Server Application.
Engineered for zero-cost deployment on Render / Fly.io / Hugging Face Spaces.
Adheres strictly to < 512MB RAM constraints with instantaneous (<200ms) responses.
"""

import os
import sys
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.config import settings
from backend.routers import stock, screener, watchlist, market_regime, search

app = FastAPI(
    title="BEM 100 v2.0 Market Engine",
    description="Indian Stock Momentum & Breakout Intelligence Platform API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Next.js PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(stock.router)
app.include_router(screener.router)
app.include_router(watchlist.router)
app.include_router(market_regime.router)
app.include_router(search.router)


@app.get("/health", tags=["System"])
async def health_check():
    """
    Lightweight cold-start probe.
    Allows frontend to detect when a free Render container is waking up.
    """
    return {
        "status": "healthy",
        "engine": "BEM 100 v2.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "memory_safe": True,
        "environment": settings.environment
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "BEM 100 v2.0 Indian Stock Momentum & Breakout Intelligence Platform API",
        "documentation": "/docs",
        "health": "/health"
    }
