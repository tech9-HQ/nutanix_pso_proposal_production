from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import generate_proposal_crewai
from app.routers.auth import router as auth_router

app = FastAPI()

# ----------------------------
# CORS MIDDLEWARE
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# API ROUTERS
# ----------------------------
app.include_router(generate_proposal_crewai.router)
app.include_router(auth_router)

# ----------------------------
# FRONTEND (STATIC FILES)
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Serve index.html, login.html, script.js, etc. at "/"
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
