from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI (env: OPENAI_API_KEY)
    openai_api_key: str = ""
    model_name: str = "gpt-5-nano"
    embedding_model: str = "text-embedding-3-small"

    # Tavily (env: TAVILY_API_KEY; la librería también la lee por defecto)
    tavily_api_key: str = ""

    # PostgreSQL (checkpointer, store y RAG con pgvector)
    database_url: str = "postgresql://postgres:postgres@localhost:5434/postgres"

    # RAG: nombre de la tabla/colección de vectores en Postgres (pgvector)
    rag_collection_name: str = "soporte_docs"

    # Docs path for RAG indexation
    docs_path: str = "docs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
