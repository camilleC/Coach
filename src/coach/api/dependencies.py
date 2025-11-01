from typing import Optional

from ..exceptions.rag_exceptions import RAGInternalError


_rag_service: Optional[object] = None


def set_rag_service(service: object) -> None:
    global _rag_service
    _rag_service = service


async def get_rag_service():
    if _rag_service is None:
        raise RAGInternalError("RAG service not initialized")
    return _rag_service

