from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # PDF Configuration - uses PDF environment variable
    pdf: Optional[str] = Field(None, alias="PDF")  # Maps PDF env var to pdf_path
    default_document_path: str = "/app/data/coach.pdf"  # Works inside Docker

    chunk_size: int = 1000
    chunk_overlap: int = 150

    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    @field_validator('pdf')
    @classmethod
    def validate_pdf_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate PDF path if provided"""
        if v is None:
            return v

        pdf_file = Path(v)
        if not pdf_file.exists():
            logger.warning(f"⚠️ PDF file not found: {v}")
        elif pdf_file.suffix.lower() != '.pdf':
            logger.warning(f"⚠️ File is not a PDF: {v}")
        else:
            logger.info(f"✅ PDF file found: {v}")

        return str(pdf_file)

    @model_validator(mode='after')
    def _validate_chunking_and_pdf(self):
        """Validate chunking parameters and set up PDF path"""
        # Ensure chunk_overlap < chunk_size
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError('chunk_overlap must be less than chunk_size')

        # Set effective PDF path (prioritize environment variable)
        if not self.pdf:
            self.pdf = self.default_document_path
            logger.info(f"No PDF environment variable set, using default: {self.pdf}")
        else:
            logger.info(f"Using PDF from environment variable: {self.pdf}")

        return self

    @property
    def effective_pdf_path(self) -> str:
        """Always return the resolved PDF path"""
        return self.pdf
    
settings = Settings()