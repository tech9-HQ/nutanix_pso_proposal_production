from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import generate_proposal_crewai
from app.routers.auth import router as auth_router

app = FastAPI()

# ----------------------------
# CORS MIDDLEWARE (REQUIRED)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow localhost, file://, etc.
    allow_credentials=True,
    allow_methods=["*"],          # <--- THIS FIXES OPTIONS 405
    allow_headers=["*"],          # <--- REQUIRED for JSON/AUTH headers
)

# ----------------------------
# ROUTERS
# ----------------------------
app.include_router(generate_proposal_crewai.router)
app.include_router(auth_router)
