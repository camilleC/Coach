from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from ..config.settings import settings
from ..exceptions.rag_exceptions import (
    RAGBadRequest,
    RAGModelUnavailable,
    RAGInternalError,
)
from ..core.rag_service import RAGService
from .routes import router
from .dependencies import set_rag_service


# Setup logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = None
    try:
        if not (hasattr(app.state, 'skip_init') and app.state.skip_init):
            service = RAGService()
            await service.initialize()
            set_rag_service(service)
            logger.info("RAG service initialized")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        raise
    finally:
        if service:
            await service.cleanup()
            set_rag_service(None)
            logger.info("RAG service cleaned up")


app = FastAPI(
    title="RAG Tutor API",
    description="AI-powered document Q&A system with full observability",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Instrumentator().instrument(app).expose(app)


@app.exception_handler(RAGBadRequest)
async def bad_request_handler(request, exc: RAGBadRequest):
    raise HTTPException(status_code=400, detail=exc.message)


@app.exception_handler(RAGModelUnavailable)
async def model_unavailable_handler(request, exc: RAGModelUnavailable):
    raise HTTPException(status_code=503, detail=exc.message)


@app.exception_handler(RAGInternalError)
async def internal_error_handler(request, exc: RAGInternalError):
    raise HTTPException(status_code=500, detail=exc.message)


app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-tutor"}


def main():
    import uvicorn

    uvicorn.run("ragtutor.api.main:app", host=settings.api_host, port=settings.api_port, reload=False)


