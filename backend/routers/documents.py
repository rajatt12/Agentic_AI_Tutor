from fastapi import APIRouter, HTTPException
from backend.schemas.schemas import DocumentIngestRequest, DocumentIngestResponse
from backend.services.agent_service import agent_service

router = APIRouter(prefix="/api/v1/documents", tags=["Document Ingestion & RAG"])

@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_text_document(doc: DocumentIngestRequest):
    """
    Ingest study materials, textbook chapters, or formula sheets
    into ChromaDB (Dense) and BM25 (Sparse) for hybrid retrieval.
    """
    try:
        chunks_count = agent_service.ingest_document(
            title=doc.title,
            content=doc.content
        )
        return DocumentIngestResponse(
            status="success",
            chunks_indexed=chunks_count,
            message=f"Successfully indexed '{doc.title}' into Hybrid Vector & BM25 store ({chunks_count} chunks)."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")
