from loguru import logger
from langchain_community.llms.gigachat import GigaChat
from langchain_core.language_models import BaseChatModel

from src.core.agents.models.base import BaseLLM

class GetGigaChat(BaseLLM):
    _llm: GigaChat = None
    _initialized: bool = False
    _giga_config = None
    _base_llm_config = None

    def get_llm(self) -> BaseChatModel:
        if not self._initialized:
            from data.init_configs import get_config
            
            config = get_config()
            self._giga_config = config.GIGA_CHAT_CONFIG
            self._base_llm_config = config.BASE_LLM_CONFIG
            
            self._llm = GigaChat(
                model=self._giga_config.GIGA_MODEL,
                credentials=self._giga_config.GIGACHAT_AUTH_KEY,
                scope=self._giga_config.GIGACHAT_SCOPE,
                max_tokens=self._base_llm_config.MAX_TOKENS,
                temperature=self._base_llm_config.TEMPERATURE,
                timeout=self._base_llm_config.TIMEOUT,
                top_p=self._base_llm_config.TOP_P,
                verbose=self._base_llm_config.VERBOSE,
            )
            self._initialized = True
            logger.success(f'✓ GetGigaChat инициализирован - {self!r}')
        
        return self._llm
    
    def __repr__(self) -> str:
        if self._initialized and self._giga_config and self._base_llm_config:
            return (
                f"{self.__class__.__name__}("
                f"model={self._giga_config.GIGA_MODEL}, "
                f"scope={self._giga_config.GIGACHAT_SCOPE}, "
                f"max_tokens={self._base_llm_config.MAX_TOKENS}, "
                f"temperature={self._base_llm_config.TEMPERATURE}, "
                f"timeout={self._base_llm_config.TIMEOUT})"
            )
        return f"{self.__class__.__name__}(not initialized)"