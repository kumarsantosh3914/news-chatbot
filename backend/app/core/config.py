import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    PROJECT_NAME: str = "News Chatbot"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_USERNAME: Optional[str] = None
    
    # Vector DB settings (Qdrant Cloud)
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "news_articles"
    
    # Embedding and LLM API keys
    JINA_API_KEY: str
    GEMINI_API_KEY: str
    NEWS_API_KEY: str  # NewsAPI key for fetching news articles
    
    # PostgreSQL settings (Optional)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None
    
    # Session configuration (hardcoded, not from env)
    SESSION_TTL: int = 3600  # 1 hour
    MESSAGE_TTL: int = 86400  # 24 hours
    MAX_SESSION_MESSAGES: int = 100
    
    # News sources
    NEWS_SOURCES_PATH: str = "data/news_sources.json"
    NEWS_UPDATE_INTERVAL: int = 3600  # 1 hour
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> Optional[str]:
        """Get SQLAlchemy database URI."""
        if all([
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        ]):
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return None
    
    @property
    def REDIS_URI(self) -> str:
        """Get Redis URI."""
        auth = ""
        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            auth = f"{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@"
        elif self.REDIS_PASSWORD:
            auth = f":{self.REDIS_PASSWORD}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()