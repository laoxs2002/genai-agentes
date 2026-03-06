"""
RAG: vector store en PostgreSQL (pgvector), embeddings OpenAI small, indexación desde docs/.
"""
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import langchain as lc
from app.core.config import get_settings


def get_vector_store():
    """Devuelve el vector store PGVector (configurado al arrancar la app)."""
    return lc.get_vector_store()


def index_docs() -> int:
    """
    Load markdown files from docs/, split, embed with OpenAI, add to PGVector.
    Returns number of chunks indexed.
    """
    settings = get_settings()
    docs_path = Path(settings.docs_path)
    if not docs_path.is_absolute():
        # Resolve relative to project root (parent of app/)
        docs_path = Path(__file__).resolve().parent.parent.parent / docs_path
    if not docs_path.exists():
        raise RuntimeError(
            f"La carpeta de documentación no existe: {docs_path}. "
            "Crea la carpeta 'docs' en la raíz del proyecto con archivos .md."
        )

    loader = DirectoryLoader(
        str(docs_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    if not documents:
        raise RuntimeError(
            f"No hay archivos .md en {docs_path}. Añade al menos un archivo markdown para indexar."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    vector_store = get_vector_store()
    if vector_store is None:
        raise RuntimeError("Vector store (PGVector) no disponible; ¿Postgres con pgvector levantado?")

    # Clear and re-add so we can re-index idempotently (optional: delete collection or add with ids)
    vector_store.add_documents(chunks)
    return len(chunks)
