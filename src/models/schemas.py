from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    pass


class DocumentMetadata(BaseModel):
    """Document metadata model"""
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime
    chunk_count: int


class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    max_results: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum number of results to return")
    include_sources: Optional[bool] = Field(default=True, description="Whether to include source information")


class RetrievedDocument(BaseModel):
    """Model for retrieved document chunks"""
    content: str
    metadata: dict
    similarity_score: float


class RAGResponse(BaseModel):
    """Response model for RAG queries"""
    query: str
    answer: str
    sources: List[RetrievedDocument]
    response_time: float


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    services: dict


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime