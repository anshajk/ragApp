import openai
from typing import List
import logging
from src.config import settings
from src.models.schemas import RetrievedDocument

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating responses using OpenAI LLM"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_response(self, query: str, retrieved_docs: List[RetrievedDocument]) -> str:
        """Generate a response based on query and retrieved documents"""
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(retrieved_docs)
            
            # Create the prompt
            prompt = self._create_prompt(query, context)
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. "
                                 "Use only the information from the context to answer questions. "
                                 "If the context doesn't contain enough information to answer the question, "
                                 "say so clearly. Always be accurate and cite the relevant parts of the context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated response for query: {query[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _prepare_context(self, retrieved_docs: List[RetrievedDocument]) -> str:
        """Prepare context from retrieved documents"""
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source_info = doc.metadata.get('filename', 'Unknown source')
            context_parts.append(f"Source {i} ({source_info}):\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a prompt for the LLM"""
        return f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain sufficient information to answer the question, please state that clearly."""