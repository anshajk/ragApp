import time
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from src.config import settings
from src.models.schemas import (
    QueryRequest, RAGResponse, HealthResponse, ErrorResponse,
    DocumentMetadata, RetrievedDocument
)
from src.services.document_service import DocumentService
from src.services.retrieval_service import RetrievalService
from src.services.generation_service import GenerationService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A Retrieval-Augmented Generation (RAG) application using OpenAI",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
retrieval_service = RetrievalService()
generation_service = GenerationService()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else None,
            timestamp=datetime.now()
        ).dict()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check vector database connection
        stats = retrieval_service.get_collection_stats()
        db_status = "healthy" if "error" not in stats else "unhealthy"
        
        return HealthResponse(
            status="healthy" if db_status == "healthy" else "degraded",
            timestamp=datetime.now(),
            version=settings.app_version,
            services={
                "vector_database": db_status,
                "document_count": stats.get("total_documents", 0)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version=settings.app_version,
            services={"error": str(e)}
        )


@app.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file type
        supported_formats = document_service.get_supported_formats()
        if file.content_type not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {supported_formats}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process the document
        result = await document_service.process_uploaded_file(
            file_content, file.filename, file.content_type
        )
        
        return {
            "message": "Document uploaded and processed successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=RAGResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    start_time = time.time()
    
    try:
        # Retrieve relevant documents
        retrieved_docs = await retrieval_service.retrieve_documents(
            request.query, 
            k=request.max_results
        )
        
        # Generate response
        if retrieved_docs:
            answer = await generation_service.generate_response(request.query, retrieved_docs)
        else:
            answer = "I couldn't find any relevant information in the uploaded documents to answer your question."
        
        response_time = time.time() - start_time
        
        return RAGResponse(
            query=request.query,
            answer=answer,
            sources=retrieved_docs if request.include_sources else [],
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/stats")
async def get_document_stats():
    """Get statistics about uploaded documents"""
    try:
        stats = retrieval_service.get_collection_stats()
        return {
            "total_documents": stats.get("total_documents", 0),
            "collection_name": stats.get("collection_name", "unknown"),
            "supported_formats": document_service.get_supported_formats()
        }
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents")
async def clear_all_documents():
    """Clear all documents from the vector database"""
    try:
        success = retrieval_service.delete_collection()
        if success:
            # Recreate the collection
            retrieval_service.collection = retrieval_service._get_or_create_collection()
            return {"message": "All documents cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear documents")
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "A Retrieval-Augmented Generation (RAG) application using OpenAI",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "query": "/query", 
            "stats": "/documents/stats",
            "clear": "/documents (DELETE)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )