from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default to Postgres in Docker; override via env for local non-Docker usage
    DATABASE_URL: str = "postgresql+psycopg://dawsheet:dawsheet@db:5432/dawsheet"
    CLOUD_RUN_PARSE_URL: str = "https://dawsheet-proxy-service-1046102063670.us-central1.run.app/parse"
    CORS_ORIGINS: str = "*"
    LYRICS_PROVIDER_ENABLED: bool = True


settings = Settings()
