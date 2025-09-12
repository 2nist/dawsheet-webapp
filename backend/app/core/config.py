from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "DAWSheet API"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # CORS settings
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000"
    ]

    # Database settings (for future use)
    database_url: str = "sqlite:///./songs.db"

    class Config:
        env_file = ".env"

settings = Settings()
