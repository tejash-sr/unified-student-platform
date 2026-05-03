"""
Configuration management for the unified student platform.
Handles environment variables, database setup, and AI service credentials.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type safety.
    """
    
    # App Configuration
    app_name: str = "Unified Student Platform"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/student_platform"
    )
    database_echo: bool = debug  # Log SQL queries in debug mode
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # AI/LLM Services
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight, fast
    chroma_collection_name: str = "student_knowledge_base"
    
    # SendGrid Email
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@studentplatform.com")
    
    # Redis (for caching and session management)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Plausible Analytics
    plausible_domain: str = os.getenv("PLAUSIBLE_DOMAIN", "studentplatform.local")
    
    # CORS
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:3000",
    ]
    
    # N8N Webhook
    n8n_webhook_url: Optional[str] = os.getenv("N8N_WEBHOOK_URL")
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Recommendation Engine
    min_user_interactions_for_recommendation: int = 5
    top_n_recommendations: int = 10
    
    # Loan Settings
    min_loan_amount: float = 100000  # INR
    max_loan_amount: float = 5000000  # INR
    default_interest_rate: float = 8.5  # Annual %
    default_tenure_months: int = 180  # 15 years
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance. Using lru_cache ensures
    we only instantiate Settings once per application lifetime.
    """
    return Settings()


# Export for easy imports
settings = get_settings()
