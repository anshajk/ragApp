import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.errors import NotFoundError
from typing import List, Dict, Any
import logging
import uuid
from src.config import settings
from src.models.schemas import RetrievedDocument
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for storing and retrieving documents using ChromaDB"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get or create the document collection"""
        try:
            collection = self.client.get_collection(name=settings.collection_name)
            logger.info(f"Retrieved existing collection: {settings.collection_name}")
        except (ValueError, NotFoundError):
            collection = self.client.create_collection(
                name=settings.collection_name,
                metadata={"description": "RAG document collection"},
            )
            logger.info(f"Created new collection: {settings.collection_name}")

        return collection

    async def add_documents(
        self, chunks: List[str], metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """Add document chunks to the vector database"""
        try:
            # Generate embeddings for all chunks
            embeddings = await self.embedding_service.generate_embeddings(chunks)

            # Generate unique IDs for each chunk
            ids = [str(uuid.uuid4()) for _ in chunks]

            sanitized_metadata_list = []
            for metadata in metadata_list:
                sanitized_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, list):
                        sanitized_metadata[key] = ", ".join(map(str, value))
                    else:
                        sanitized_metadata[key] = value
                sanitized_metadata_list.append(sanitized_metadata)

            # Add to ChromaDB
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=sanitized_metadata_list,
                ids=ids,
            )

            logger.info(f"Added {len(chunks)} document chunks to collection")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise Exception(f"Failed to add documents to vector database: {str(e)}")

    async def retrieve_documents(
        self, query: str, k: int = None
    ) -> List[RetrievedDocument]:
        """Retrieve relevant documents for a query"""
        if k is None:
            k = settings.retrieval_k

        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )

            # Convert results to RetrievedDocument objects
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0],
                    )
                ):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1 - distance

                    # Only include documents above similarity threshold
                    if similarity_score >= settings.similarity_threshold:
                        retrieved_docs.append(
                            RetrievedDocument(
                                content=doc,
                                metadata=metadata,
                                similarity_score=similarity_score,
                            )
                        )

            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents for query")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise Exception(f"Failed to retrieve documents: {str(e)}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.collection_name,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}

    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=settings.collection_name)
            logger.info(f"Deleted collection: {settings.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
