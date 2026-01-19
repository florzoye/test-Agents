from langchain.agents import create_agent
from langchain_classic.tools import BaseTool
from langchain.messages import SystemMessage
from langchain_core.runnables import Runnable

from src.core.agents.models.base import BaseLLM
from data.init_configs import MIDDLEWARE_SERVICE

class AgentFactory:
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        system_prompt: SystemMessage
    ) -> Runnable:
        llm_instance = await llm.get_llm()
        
        agent = create_agent(
            model=llm_instance,
            system_prompt=system_prompt,
            middleware=MIDDLEWARE_SERVICE.middlewares,
        ) 

        return agent