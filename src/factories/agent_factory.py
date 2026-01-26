from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_core.runnables import Runnable

class AgentFactory:
    async def lc_create_agent(self, llm, system_prompt: SystemMessage) -> Runnable:
        from data.init_configs import get_config
        cfg = get_config()
        agent = create_agent(
            model=llm,
            system_prompt=system_prompt,
            middleware=cfg.MIDDLEWARE_SERVICE.middlewares,
            response_format=getattr(llm, "_response_format", None),
        )

        return agent