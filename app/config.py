import os
from typing import Optional

class Config:
    # Database configuration
    # DB_URL: str = os.getenv("DB_URL", "postgresql+psycopg2://postgres:1234@localhost:5432/postgres")
    DB_URL: str = os.getenv("DB_URL", "postgresql+psycopg2://postgres:chatbotpass@chatbot-2.c7u6oo6sigla.ap-southeast-5.rds.amazonaws.com:5432/chatbot")
    
    # AWS configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-southeast-5")  # Main infrastructure region
    BEDROCK_REGION: str = os.getenv("BEDROCK_REGION", "us-east-1")  # Bedrock-specific region
    EMBEDDING_MODEL_ID: str = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    CHAT_MODEL_ID: str = os.getenv("CHAT_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    
    # CORS configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Common React dev port
        "http://127.0.0.1:3000",
        "https://zus.weishen.studio"
    ]
    
    # API configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

config = Config()
