from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:5173"

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Storage / RAG
    storage_dir: str = "./storage"
    chroma_persist_dir: str = "./chroma"
    chroma_collection: str = "rag_chunks"


settings = Settings()


