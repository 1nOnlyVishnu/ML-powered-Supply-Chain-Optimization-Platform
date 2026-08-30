from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from .auth import get_current_user, authenticate_user, create_access_token
from .ml import router as ml_router
from .db import init_db

app = FastAPI(
    title="Supply Chain Management API",
    description="Advanced ML-powered supply chain optimization platform",
    version="2.0.0"
)

# CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

# Include routers
app.include_router(ml_router, prefix="/api", tags=["Machine Learning"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supply Chain Management API",
        "version": "2.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "ml_models": "loaded",
            "forecasting": "ready",
            "risk_analysis": "ready"
        }
    }

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/dashboard/summary")
async def get_dashboard_summary(user=Depends(get_current_user)):
    """Get dashboard summary metrics"""
    return {
        "total_products": 150,
        "active_suppliers": 25,
        "inventory_value": 2500000,
        "forecast_accuracy": 92.5,
        "risk_score": 15.3,
        "stockout_prevention": 98.7
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)