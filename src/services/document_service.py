import io
import os
from typing import List, Dict, Any, Tuple
import PyPDF2
import docx
from datetime import datetime
import logging
from src.config import settings
from src.utils.text_processing import TextProcessor
from src.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling document upload and processing"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.retrieval_service = RetrievalService()
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
    
    async def process_uploaded_file(self, file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Process an uploaded file and add it to the vector database"""
        try:
            # Validate file size
            if len(file_content) > settings.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed size of {settings.max_file_size} bytes")
            
            # Extract text based on file type
            text = self._extract_text(file_content, filename, content_type)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the file")
            
            # Process the document
            result = await self._process_document(text, filename, content_type, len(file_content))
            
            logger.info(f"Successfully processed file: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            raise Exception(f"Failed to process file: {str(e)}")
    
    def _extract_text(self, file_content: bytes, filename: str, content_type: str) -> str:
        """Extract text from different file types"""
        text = ""
        
        try:
            if content_type == "application/pdf" or filename.lower().endswith('.pdf'):
                text = self._extract_text_from_pdf(file_content)
            elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or filename.lower().endswith('.docx'):
                text = self._extract_text_from_docx(file_content)
            elif content_type == "text/plain" or filename.lower().endswith('.txt'):
                text = file_content.decode('utf-8')
            else:
                # Try to decode as text anyway
                try:
                    text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError(f"Unsupported file type: {content_type}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise ValueError(f"Failed to extract text from file: {str(e)}")
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        text = ""
        pdf_file = io.BytesIO(file_content)
        
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    async def _process_document(self, text: str, filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Process document text and store in vector database"""
        # Clean the text
        cleaned_text = self.text_processor.clean_text(text)
        
        # Split into chunks
        chunks = self.text_processor.chunk_text(
            cleaned_text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        if not chunks:
            raise ValueError("No valid chunks could be created from the document")
        
        # Prepare metadata for each chunk
        base_metadata = {
            "filename": filename,
            "file_type": content_type,
            "file_size": file_size,
            "upload_time": datetime.now().isoformat(),
            "total_chunks": len(chunks)
        }
        
        metadata_list = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_text_length": len(chunk),
                "keywords": self.text_processor.extract_keywords(chunk, max_keywords=5)
            })
            metadata_list.append(chunk_metadata)
        
        # Add to vector database
        chunk_ids = await self.retrieval_service.add_documents(chunks, metadata_list)
        
        return {
            "filename": filename,
            "file_type": content_type,
            "file_size": file_size,
            "chunk_count": len(chunks),
            "chunk_ids": chunk_ids,
            "upload_time": base_metadata["upload_time"]
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]