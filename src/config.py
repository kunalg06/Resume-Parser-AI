from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    perplexity_api_key: str
    openai_api_key: Optional[str] = None
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()