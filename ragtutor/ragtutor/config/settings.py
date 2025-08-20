from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # RAG Configuration
    vector_db_persist_dir: str = "./storage/chroma"
    collection_name: str = "documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5

    # LLM Configuration
    llm_model: str = "llama3.2"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_timeout: int = 30
    max_tokens: int = 512

    # Monitoring
    prometheus_scrape_interval: str = "5s"
    grafana_host_port: int = 3000
    prometheus_host_port: int = 9090

    class Config:
        env_file = ".env"
        extra = "ignore"  # <-- add this line

    @model_validator(mode='after')
    def _validate_chunking(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError('chunk_overlap must be less than chunk_size')
        return self


settings = Settings()
