from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ========================
    # API
    # ========================
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # ========================
    # RAG / Vector Database (Qdrant)
    # ========================
    vector_db_host: str = Field("qdrant", env="VECTOR_DB_HOST")
    vector_db_port: int = Field(6333, env="VECTOR_DB_PORT")
    collection_name: str = Field("documents", env="COLLECTION_NAME")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(150, env="CHUNK_OVERLAP")
    top_k: int = Field(5, env="TOP_K")
    pdf: Optional[str] = Field(None, alias="PDF")
    default_document_path: str = "/app/data/coaching.pdf"

    # ========================
    # LLM
    # ========================
    llm_model: str = Field("llama3.2", env="LLM_MODEL")
    llm_base_url: str = Field("http://host.docker.internal:11434/v1", env="LLM_BASE_URL")
    llm_api_key: str = Field("ollama", env="LLM_API_KEY")
    llm_timeout: int = Field(30, env="LLM_TIMEOUT")
    max_tokens: int = Field(512, env="MAX_TOKENS")
    embedding_dim: int = Field(384, env="EMBEDDING_DIM") 

    # ========================
    # Monitoringa
    # ========================
    prometheus_scrape_interval: str = Field("5s", env="PROMETHEUS_SCRAPE_INTERVAL")
    prometheus_host_port: int = Field(9090, env="PROMETHEUS_HOST_PORT")
    grafana_host_port: int = Field(3000, env="GRAFANA_HOST_PORT")

    # ========================
    # Grafana
    # ========================
    grafana_admin_user: str = Field("admin", env="GRAFANA_ADMIN_USER")
    grafana_admin_password: str = Field("admin", env="GRAFANA_ADMIN_PASSWORD")

    # ========================
    # Validators
    # ========================
    @field_validator("pdf")
    @classmethod
    def validate_pdf_path(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pdf_file = Path(v)
        if not pdf_file.exists():
            logger.warning(f"⚠️ PDF file not found: {v}")
        elif pdf_file.suffix.lower() != ".pdf":
            logger.warning(f"⚠️ File is not a PDF: {v}")
        else:
            logger.info(f"✅ PDF file found: {v}")
        return str(pdf_file)

    @model_validator(mode="after")
    def _validate_chunking_and_pdf(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        if not self.pdf:
            self.pdf = self.default_document_path
            logger.info(f"No PDF env var set, using default: {self.pdf}")
        else:
            logger.info(f"Using PDF from env var: {self.pdf}")

        return self

    @property
    def effective_pdf_path(self) -> str:
        return self.pdf


# Create the settings instance
settings = Settings()
