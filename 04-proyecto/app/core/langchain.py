"""
PostgresSaver (checkpointer), PostgresStore (long-term), PGVector (RAG) y embeddings.
Todo en la misma PostgreSQL con pgvector; recursos creados al arrancar la app.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.postgres import PostgresSaver

from app.core.config import get_settings

if TYPE_CHECKING:
    from langchain_postgres import PGVector

_settings = get_settings()

# Connection string for PostgreSQL (checkpointer, store y RAG)
_db_uri = _settings.database_url
if "?" not in _db_uri and "sslmode" not in _db_uri:
    _db_uri = f"{_db_uri.rstrip('/')}?sslmode=disable"


def get_pgvector_connection_uri() -> str:
    """URI para langchain-postgres PGVector (sync con psycopg): postgresql+psycopg://..."""
    base = _settings.database_url.strip()
    if base.startswith("postgresql://"):
        base = "postgresql+psycopg://" + base[len("postgresql://") :]
    elif not base.startswith("postgresql+psycopg://"):
        base = "postgresql+psycopg://" + base.split("://", 1)[-1] if "://" in base else base
    if "?" not in base and "sslmode" not in base:
        base = f"{base.rstrip('/')}?sslmode=disable"
    return base

# Set by lifespan in main.py
checkpointer: PostgresSaver | None = None
store = None  # PostgresStore or InMemoryStore
vector_store: "PGVector | None" = None
embeddings: OpenAIEmbeddings | None = None


def get_db_uri() -> str:
    return _db_uri


def get_embeddings() -> OpenAIEmbeddings:
    """OpenAI embeddings (text-embedding-3-small) para RAG."""
    global embeddings
    if embeddings is None:
        embeddings = OpenAIEmbeddings(
            model=_settings.embedding_model,
            api_key=_settings.openai_api_key,
        )
    return embeddings


def get_vector_store() -> "PGVector | None":
    return vector_store


def set_vector_store(vs: "PGVector") -> None:
    global vector_store
    vector_store = vs
