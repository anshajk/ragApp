# RAG Application Configuration
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-ada-002"

    # Vector Database Configuration
    chroma_persist_directory: str = "./chroma_db"
    collection_name: str = "documents"

    # Application Configuration
    app_name: str = "RAG Application"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # Retrieval Configuration
    retrieval_k: int = 5
    similarity_threshold: float = 0.2

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
