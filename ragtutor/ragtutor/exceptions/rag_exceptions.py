from typing import Optional


class RAGException(Exception):
    """Base exception for RAG operations"""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RAGModelUnavailable(RAGException):
    """Raised when LLM model is unavailable"""

    pass


class RAGDocumentError(RAGException):
    """Raised when document processing fails"""

    pass


class RAGEmbeddingError(RAGException):
    """Raised when embedding generation fails"""

    pass


class RAGVectorStoreError(RAGException):
    """Raised when vector store operations fail"""

    pass


class RAGBadRequest(RAGException):
    """Raised for invalid user input"""

    pass


class RAGInternalError(RAGException):
    """Raised for internal system errors"""

    pass

