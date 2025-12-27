from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_community.llms.gigachat import GigaChat

from src.core.agents.models.base import (
    BaseLLM, 
    BaseTool, 
    Runnable,
    BaseAgent, 
    BaseLanguageModel, 
)

from data.configs.llm_config import base_llm_config
from data.configs.ollama_config import ollama_config
from data.configs.gigachat_config import giga_chat_config


class GetGigaChat(BaseLLM):
    async def get_llm(self):
        return GigaChat(
            model=giga_chat_config.GIGA_MODEL,
            credentials=giga_chat_config.GIGACHAT_AUTH_KEY,
            scope=giga_chat_config.GIGACHAT_SCOPE,
            max_tokens=base_llm_config.MAX_TOKENS,
            temperature=base_llm_config.TEMPERATURE,
            timeout=base_llm_config.TIMEOUT,
            top_p=base_llm_config.TOP_P,
            verbose=base_llm_config.VERBOSE,
            
        )

class GetOllamaLLM(BaseLLM):
    async def get_llm(self) -> BaseLanguageModel:
        return ChatOllama(
            model=ollama_config.OLLAMA_MODEL,
            max_tokens=base_llm_config.MAX_TOKENS,
            temperature=base_llm_config.TEMPERATURE,
            timeout=base_llm_config.TIMEOUT,
            top_p=base_llm_config.TOP_P,
            verbose=base_llm_config.VERBOSE,
        )
    

class CreateAgent(BaseAgent):
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool]
    ) -> Runnable:
        llm_instance = await llm.get_llm()
        agent = create_agent(
            model=llm_instance,
            tools=tools,
        )

        return agent