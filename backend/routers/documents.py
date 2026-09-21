from fastapi import APIRouter, HTTPException
from backend.schemas.schemas import DocumentIngestRequest, DocumentIngestResponse
from backend.services.agent_service import agent_service

router = APIRouter(prefix="/api/v1/documents", tags=["Document Ingestion & RAG"])

@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_text_document(doc: DocumentIngestRequest):
    """
    Ingest study materials, textbook chapters, or formula sheets
    into ChromaDB (Dense) and BM25 (Sparse) scoped to student or shared library.
    """
    try:
        chunks_count = agent_service.ingest_document(
            student_id=doc.student_id or "student_001",
            title=doc.title,
            content=doc.content,
            is_shared=bool(doc.is_shared),
            subject=doc.subject or "General"
        )
        owner_str = "Shared Curriculum Library" if doc.is_shared else f"Private Notes ({doc.student_id})"
        return DocumentIngestResponse(
            status="success",
            chunks_indexed=chunks_count,
            message=f"Successfully indexed '{doc.title}' into {owner_str} ({chunks_count} chunks)."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@router.get("/{student_id}")
def list_student_notes(student_id: str):
    """
    List personal study notes for the given student along with shared curriculum stats.
    """
    try:
        return agent_service.list_student_documents(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notes: {str(e)}")
