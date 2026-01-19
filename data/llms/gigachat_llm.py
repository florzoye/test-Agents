from loguru import logger
from langchain_community.llms.gigachat import GigaChat

from src.core.agents.models.base import BaseLLM
from data.configs.llm_config import BASE_LLM_CONFIG
from data.configs.gigachat_config import GIGA_CHAT_CONFIG

class GetGigaChat(BaseLLM):
    def get_llm(self):
        if not self._initialized:
            self._llm = GigaChat(
                model=GIGA_CHAT_CONFIG.GIGA_MODEL,
                credentials=GIGA_CHAT_CONFIG.GIGACHAT_AUTH_KEY,
                scope=GIGA_CHAT_CONFIG.GIGACHAT_SCOPE,
                max_tokens=BASE_LLM_CONFIG.MAX_TOKENS,
                temperature=BASE_LLM_CONFIG.TEMPERATURE,
                timeout=BASE_LLM_CONFIG.TIMEOUT,
                top_p=BASE_LLM_CONFIG.TOP_P,
                verbose=BASE_LLM_CONFIG.VERBOSE,
            )
            self._initialized = True
            logger.info(f'GetGigaChat инициализирован - {repr(GetGigaChat)}')
        return self._llm
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"model={GIGA_CHAT_CONFIG.GIGA_MODEL}, "
            f"scope={GIGA_CHAT_CONFIG.GIGACHAT_SCOPE}, "
            f"max_tokens={BASE_LLM_CONFIG.MAX_TOKENS}, "
            f"temperature={BASE_LLM_CONFIG.TEMPERATURE}, "
            f"timeout={BASE_LLM_CONFIG.TIMEOUT})"
        )

    
