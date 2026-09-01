import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RentSense Control Tower API",
    description="Smart rental tracking and fleet intelligence system for construction/heavy equipment",
    version="0.1.0",
)

# CORS setup
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint confirming API status."""
    return {"status": "ok"}
