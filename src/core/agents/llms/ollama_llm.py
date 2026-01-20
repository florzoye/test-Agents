from loguru import logger
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel

from src.core.agents.models.base import BaseLLM
from data.init_configs import BASE_LLM_CONFIG
from data.init_configs import OLLAMA_CONFIG

class GetOllamaLLM(BaseLLM):
    _llm: ChatOllama = None
    _initialized: bool = False

    def get_llm(self) -> ChatOllama:
        if not self._initialized:
            self._llm = ChatOllama(
                model=OLLAMA_CONFIG.OLLAMA_MODEL,
                max_tokens=BASE_LLM_CONFIG.MAX_TOKENS,
                temperature=BASE_LLM_CONFIG.TEMPERATURE,
                timeout=BASE_LLM_CONFIG.TIMEOUT,
                top_p=BASE_LLM_CONFIG.TOP_P,
                verbose=BASE_LLM_CONFIG.VERBOSE,
                )
            self._initialized = True
            logger.info(f"GetOllamaLLM инициализирован - {repr(self)}")
        return self._llm
               
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"model={OLLAMA_CONFIG.OLLAMA_MODEL}, "
            f"max_tokens={BASE_LLM_CONFIG.MAX_TOKENS}, "
            f"temperature={BASE_LLM_CONFIG.TEMPERATURE}, "
            f"timeout={BASE_LLM_CONFIG.TIMEOUT})"
        )
    
