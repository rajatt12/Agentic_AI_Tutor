import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic AI Tutor"
    VERSION: str = "1.0.0"
    
    @property
    def GROQ_API_KEY(self) -> str:
        load_dotenv(override=True)
        return os.getenv("GROQ_API_KEY", "").strip()
    
    @property
    def GROQ_MODEL(self) -> str:
        return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:rajat123@localhost:5432/ai_tutor_db"
    )
    
    # Server Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
