from functools import lru_cache
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    app_name: str = "LegalEase"
    environment: str = "development"
    gemini_api_key: str = ""
    gemini_model: str = Field(default="gemini-2.5-flash")
    frontend_url: str = "http://localhost:8501"
    max_text_chars: int = 50000

    @classmethod
    def from_env(cls):
        return cls(
            environment=os.getenv("ENVIRONMENT", "development"),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:8501"),
        )

@lru_cache
def get_settings():
    return Settings.from_env()
