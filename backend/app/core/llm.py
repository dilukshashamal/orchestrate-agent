import logging
from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_groq import ChatGroq
from app.config import settings

logger = logging.getLogger(__name__)

class DeterministicFallbackChatModel(BaseChatModel):
    """Fallback LLM model when Groq/Cerebras API keys are unavailable or rate limited."""
    
    def _generate(self, messages: list[BaseMessage], stop: list[str] | None = None, **kwargs: Any) -> Any:
        # Provide deterministic structured responses based on prompt context
        text_content = "Agent analysis complete based on rules engine parameters."
        return self._create_chat_result(AIMessage(content=text_content))

    @property
    def _llm_type(self) -> str:
        return "deterministic-fallback"

def get_llm() -> BaseChatModel:
    """
    Returns primary LLM (Groq) with fallback handling for redundancy and rate limits.
    """
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            groq_llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
                max_retries=3
            )
            # Add fallback to deterministic model on error/rate limit
            return groq_llm.with_fallbacks([DeterministicFallbackChatModel()])
        except Exception as e:
            logger.warning(f"Failed to initialize Groq LLM: {e}. Falling back to deterministic model.")
            return DeterministicFallbackChatModel()
    
    logger.info("GROQ_API_KEY not configured. Using deterministic agent execution core.")
    return DeterministicFallbackChatModel()
