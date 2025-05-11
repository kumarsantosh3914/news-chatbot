import asyncio
from typing import AsyncGenerator, List, Optional

import google.generativeai as genai

from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize the Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use.
        """
        self.model_name = model_name
        self.generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
    
    def _build_prompt(self, query: str, contexts: List[str]) -> str:
        """Build a prompt for the Gemini model.
        
        Args:
            query: User question.
            contexts: List of context passages.
            
        Returns:
            Formatted prompt string.
        """
        # Combine contexts with separators
        context_text = "\n\n".join([f"[Context {i+1}]: {ctx}" for i, ctx in enumerate(contexts)])
        
        # Build the complete prompt
        prompt = f"""You are a helpful assistant that answers questions about news articles.
Based on the following contexts from news articles, please answer the user's question.
If you don't know the answer or if the contexts don't provide enough information, say so.

{context_text}

User Question: {query}

Answer:"""
        
        return prompt
    
    async def generate_response(self, query: str, contexts: List[str]) -> str:
        """Generate a response using the Gemini API.
        
        Args:
            query: User question.
            contexts: List of context passages.
            
        Returns:
            Generated response.
        """
        prompt = self._build_prompt(query, contexts)
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "I'm sorry, I encountered an error while generating a response."
    
    async def stream_response(self, query: str, contexts: List[str]) -> AsyncGenerator[str, None]:
        """Stream a response from the Gemini API.
        
        Args:
            query: User question.
            contexts: List of context passages.
            
        Yields:
            Chunks of the generated response.
        """
        prompt = self._build_prompt(query, contexts)
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config
            )
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, 'parts') and chunk.parts:
                    yield chunk.parts[0].text
                await asyncio.sleep(0.01)  # Small delay to prevent CPU hogging
                
        except Exception as e:
            yield "I'm sorry, I encountered an error while generating a response."


# Singleton instance
llm_service = GeminiService()

async def get_llm_response(query: str, context: str) -> str:
    """Get a response from the LLM service.
    
    Args:
        query: User question.
        context: Context information for the response.
        
    Returns:
        Generated response.
    """
    return await llm_service.generate_response(query, [context])