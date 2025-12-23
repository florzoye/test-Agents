from dataclasses import dataclass

from langchain.tools import BaseTool
from langchain.agents import create_agent
from langchain_community.llms.gigachat import GigaChat

from data.configs.llm_config import giga_chat_config
from core.agents.tools.base_tools import dialog_tools


class DialogAgent:
    def __init__(self):
        self.llm = GigaChat(
            credentials=giga_chat_config.GIGACHAT_AUTH_KEY,
            scope=giga_chat_config.GIGACHAT_SCOPE,
            model=giga_chat_config.LLM_MODEL,  
            temperature=giga_chat_config.TEMPERATURE,
            max_tokens=giga_chat_config.MAX_TOKENS,
            verify_ssl_certs=False,
        )
        self.agent = None


    async def create(self, tools: list[BaseTool]):
        self.agent = create_agent(
            llm=self.llm,
            tools=tools,
            agent_type="chat-conversational-react-description",
            verbose=True,
            system_prompt='',
            context_schema=''
        )
        return self.agent