from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core import langchain as lc

# DB URI for Postgres (checkpointer + store)
def _get_db_uri() -> str:
    return lc.get_db_uri()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """PostgresSaver, PostgresStore y PGVector (misma BD) para checkpointer, store y RAG."""
    settings = get_settings()
    cm_checkpointer = None
    cm_store = None
    checkpointer = None
    store = None

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from langgraph.store.postgres import PostgresStore

        db_uri = _get_db_uri()
        cm_checkpointer = PostgresSaver.from_conn_string(db_uri)
        checkpointer = cm_checkpointer.__enter__()
        checkpointer.setup()

        cm_store = PostgresStore.from_conn_string(db_uri)
        store = cm_store.__enter__()
        store.setup()

        lc.checkpointer = checkpointer
        lc.store = store
    except Exception as e:
        # Postgres no disponible (ej. docker-compose no levantado): usar memoria
        import logging
        logging.getLogger("app.main").warning("Postgres no disponible, usando memoria: %s", e)
        from langgraph.checkpoint.memory import InMemorySaver
        from langgraph.store.memory import InMemoryStore
        lc.checkpointer = InMemorySaver()
        lc.store = InMemoryStore()
        cm_checkpointer = None
        cm_store = None

    # RAG: vector store en la misma Postgres (langchain-postgres PGVector)
    from langchain_postgres import PGVector
    lc.embeddings = lc.get_embeddings()
    try:
        lc.vector_store = PGVector(
            connection=lc.get_pgvector_connection_uri(),
            embeddings=lc.embeddings,
            collection_name=settings.rag_collection_name,
            create_extension=True,
        )
    except Exception:
        lc.vector_store = None

    from app.agents.supervisor import build_supervisor
    app.state.supervisor = build_supervisor(lc.checkpointer, lc.store)
    app.state.checkpointer = lc.checkpointer
    app.state.store = lc.store
    app.state.vector_store = lc.vector_store

    yield

    # Shutdown: exit context managers
    if cm_store is not None and store is not None:
        try:
            cm_store.__exit__(None, None, None)
        except Exception:
            pass
    if cm_checkpointer is not None and checkpointer is not None:
        try:
            cm_checkpointer.__exit__(None, None, None)
        except Exception:
            pass


app = FastAPI(
    title="Soporte Agentes API",
    description="API REST de asistente de soporte con base de conocimiento (LangChain agents, RAG, memoria)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
