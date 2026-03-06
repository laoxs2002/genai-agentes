from fastapi import APIRouter, HTTPException

from app.agents.rag import index_docs
from app.schemas.responses import IndexDocsResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/index-docs", response_model=IndexDocsResponse)
async def index_docs_endpoint():
    """Indexa el contenido de docs/ en PostgreSQL (pgvector, embeddings OpenAI). Ejecutar al menos una vez y tras cambiar documentación."""
    try:
        n = index_docs()
        if n == 0:
            raise HTTPException(
                status_code=503,
                detail="No se indexó ningún chunk. Comprueba que la carpeta docs/ existe, tiene archivos .md y que Postgres (pgvector) está levantado.",
            )
        return IndexDocsResponse(status="ok", chunks_indexed=n)
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
