from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from .config import config
from app.features.chat.router import router as chat_router

from app.models.endpoint_models import *



# Initialize FastAPI app
app = FastAPI(
    title="Zus Coffee Chatbot API",
    description="API for Zus Coffee customer service chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api")

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Zus Coffee Chatbot API is running"
    )



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
