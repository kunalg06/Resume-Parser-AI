import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "")
    environment: str = os.getenv("ENVIRONMENT", "production")

settings = Settings()

# Validate API key exists
if not settings.perplexity_api_key:
    raise ValueError("PERPLEXITY_API_KEY environment variable required")
