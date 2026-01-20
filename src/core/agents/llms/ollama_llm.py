from loguru import logger
from langchain_ollama import ChatOllama

from data.init_configs import get_config
from src.core.agents.models.base import BaseLLM


class GetOllamaLLM(BaseLLM):
    _llm: ChatOllama = None
    _initialized: bool = False
    _ollama_config = None
    _base_llm_config = None

    def get_llm(self) -> ChatOllama:
        if not self._initialized:
            config = get_config()
            
            self._ollama_config = config.OLLAMA_CONFIG
            self._base_llm_config = config.BASE_LLM_CONFIG
            
            self._llm = ChatOllama(
                model=self._ollama_config.OLLAMA_MODEL,
                max_tokens=self._base_llm_config.MAX_TOKENS,
                temperature=self._base_llm_config.TEMPERATURE,
                timeout=self._base_llm_config.TIMEOUT,
                top_p=self._base_llm_config.TOP_P,
                verbose=self._base_llm_config.VERBOSE,
            )
            
            self._initialized = True
            logger.success(f"✓ GetOllamaLLM инициализирован: {self}")
            
        return self._llm
               
    def __repr__(self) -> str:
        if not self._initialized:
            return f"{self.__class__.__name__}(not initialized)"
        
        return (
            f"{self.__class__.__name__}("
            f"model={self._ollama_config.OLLAMA_MODEL}, "
            f"max_tokens={self._base_llm_config.MAX_TOKENS}, "
            f"temperature={self._base_llm_config.TEMPERATURE}, "
            f"timeout={self._base_llm_config.TIMEOUT})"
        )