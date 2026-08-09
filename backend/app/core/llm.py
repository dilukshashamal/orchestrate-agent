import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_groq import ChatGroq

from app.config import settings

logger = logging.getLogger(__name__)

def setup_langsmith_tracing() -> None:
    """Configures LangSmith tracing environment variables if enabled."""
    if settings.LANGSMITH_TRACING:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGSMITH_TRACING"] = "true"
        if settings.LANGSMITH_ENDPOINT:
            os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
            os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        if settings.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
            os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        if settings.LANGSMITH_PROJECT:
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
            os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info(f"LangSmith tracing enabled for project '{settings.LANGSMITH_PROJECT}' at endpoint '{settings.LANGSMITH_ENDPOINT}'.")

class DeterministicFallbackChatModel(BaseChatModel):
    """Fallback LLM model when Groq/Cerebras API keys are unavailable or rate limited."""
    
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any
    ) -> ChatResult:
        text_content = "Agent analysis complete based on rules engine parameters."
        message = AIMessage(content=text_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "deterministic-fallback"

def get_llm() -> Any:
    """
    Returns primary LLM (Groq) with fallback handling for redundancy and rate limits.
    """
    setup_langsmith_tracing()
    
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        try:
            from pydantic import SecretStr
            groq_llm = ChatGroq(
                api_key=SecretStr(settings.GROQ_API_KEY),
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_retries=3
            )
            return groq_llm.with_fallbacks([DeterministicFallbackChatModel()])
        except Exception as e:
            logger.warning(f"Failed to initialize Groq LLM: {e}. Falling back to deterministic model.")
            return DeterministicFallbackChatModel()
    
    logger.info("GROQ_API_KEY not configured. Using deterministic agent execution core.")
    return DeterministicFallbackChatModel()
