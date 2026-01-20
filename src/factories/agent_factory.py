from typing import TYPE_CHECKING
from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_core.runnables import Runnable

if TYPE_CHECKING:
    from src.core.agents.models.base import BaseLLM

class AgentFactory:
    async def lc_create_agent(
        self,
        llm: "BaseLLM",
        system_prompt: SystemMessage
    ) -> Runnable:
        from data.init_configs import MIDDLEWARE_SERVICE
        
        # llm_instance = await llm.get_llm()
        agent = create_agent(
            model=llm,
            system_prompt=system_prompt,
            middleware=MIDDLEWARE_SERVICE.middlewares,
        ) 

        return agent