# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    # Accept anything for now
    return {
        "access_token": "dev-token",
        "user_id": payload.email,
        "email": payload.email,
        "full_name": payload.email.split("@")[0].title(),
    }

async def get_current_user():
    # Dummy: accept all requests
    return {"email": "admin@example.com", "full_name": "Admin User"}

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user
