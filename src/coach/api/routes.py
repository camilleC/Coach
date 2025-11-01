import logging
from typing import List

from fastapi import APIRouter, Depends
from tenacity import retry, stop_after_attempt, wait_exponential

from ..exceptions.rag_exceptions import (
    RAGModelUnavailable,
    RAGBadRequest,
    RAGInternalError,
    RAGDocumentError,
)
from ..core.rag_service import RAGService
from .models import QueryRequest, QueryResponse, DocumentUpload, UploadResponse
from ..utils.metrics import (
    rag_queries_total,
    rag_query_duration,
    rag_errors_total,
    vector_operations_total,
)
from .dependencies import get_rag_service


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def query_documents(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Query documents with automatic retry logic"""
    collection_label = request.collection_name or "default"
    try:
        rag_queries_total.labels(collection=collection_label, status="started").inc()
        with rag_query_duration.time():
            result = await rag_service.query(
                query=request.query,
                top_k=request.top_k,
                collection_name=request.collection_name,
            )

        rag_queries_total.labels(collection=collection_label, status="succeeded").inc()
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            query=request.query,
            confidence_score=result["confidence_score"],
        )

    except RAGModelUnavailable:
        rag_errors_total.labels(error_type="model_unavailable").inc()
        rag_queries_total.labels(collection=collection_label, status="failed").inc()
        raise
    except RAGBadRequest:
        rag_errors_total.labels(error_type="bad_request").inc()
        rag_queries_total.labels(collection=collection_label, status="failed").inc()
        raise
    except Exception as e:
        rag_errors_total.labels(error_type="internal_error").inc()
        rag_queries_total.labels(collection=collection_label, status="failed").inc()
        logger.error(f"Query failed: {e}")
        raise RAGInternalError("Query processing failed")


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    upload: DocumentUpload,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Upload and process a document"""
    try:
        vector_operations_total.labels(operation="upload", status="started").inc()

        result = await rag_service.ingest_document(
            filename=upload.filename,
            content=upload.content,
            collection_name=upload.collection_name,
        )

        vector_operations_total.labels(operation="upload", status="succeeded").inc()
        return UploadResponse(
            success=True,
            message=f"Document processed: {result['chunks_created']} chunks created",
            document_id=result["document_id"],
            chunks_created=result["chunks_created"],
        )

    except RAGDocumentError:
        vector_operations_total.labels(operation="upload", status="failed").inc()
        rag_errors_total.labels(error_type="document_error").inc()
        raise
    except Exception as e:
        vector_operations_total.labels(operation="upload", status="failed").inc()
        rag_errors_total.labels(error_type="internal_error").inc()
        logger.error(f"Upload failed: {e}")
        raise RAGInternalError("Document upload failed")


@router.get("/collections")
async def list_collections(rag_service: RAGService = Depends(get_rag_service)):
    """List available document collections"""
    try:
        collections = await rag_service.list_collections()
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise RAGInternalError("Failed to retrieve collections")


