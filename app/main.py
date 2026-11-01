"""
VakeelAI LegalTech Platform
===========================
FastAPI Backend Application
- District Court Case Scraper (eCourts portal reverse engineered)
- Pure-Python Legal Draft Template Generator (Deterministic Rule-Based Engine)
- Modern React + Shadcn UI + Framer Motion Dashboard
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_scraper import router as scraper_router
from app.api.routes_drafting import router as drafting_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="VakeelAI - eCourts Intelligence & Legal Draft Studio",
    description=(
        "Enterprise LegalTech Suite: Programmatic eCourts district court scraper "
        "and rule-based pure-Python legal draft template generator."
    ),
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static production bundle
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

dist_dir = static_dir / "dist"
dist_assets = dist_dir / "assets"
if dist_assets.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_assets)), name="assets")

# Include API Routers
app.include_router(scraper_router)
app.include_router(drafting_router)


@app.get("/")
def index():
    """Renders the single-page application entrypoint."""
    dist_index = dist_dir / "index.html"
    return FileResponse(str(dist_index))


@app.get("/health")
def health_check():
    """Application healthcheck."""
    return {"status": "ok", "service": "vakeelai-platform", "version": "1.0.0"}
