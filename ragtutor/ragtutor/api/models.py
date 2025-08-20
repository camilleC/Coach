from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import re


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)
    collection_name: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_-]+$')

    @field_validator('query', mode='before')
    def sanitize_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Query cannot be empty')
        # Basic sanitization
        v = re.sub(r"[<>\"';]", '', v)
        return v


class DocumentSource(BaseModel):
    text: str
    metadata: Dict[str, Any]
    confidence_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    query: str
    confidence_score: float


class DocumentUpload(BaseModel):
    filename: str = Field(..., pattern=r'^[a-zA-Z0-9._-]+\.pdf$')
    content: bytes
    collection_name: Optional[str] = None

    @field_validator('content')
    def validate_pdf(cls, v):
        if not v.startswith(b'%PDF'):
            raise ValueError('Invalid PDF format')
        if len(v) > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError('File too large')
        return v


class UploadResponse(BaseModel):
    success: bool
    message: str
    document_id: str
    chunks_created: int

