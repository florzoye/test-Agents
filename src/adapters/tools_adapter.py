from typing import List
from src.adapters.base import LLMAdapter
from langchain_core.tools.base import BaseTool
from langchain_core.language_models import BaseChatModel

class BindToolsAdapter(LLMAdapter):
    def __init__(self, tools: List[BaseTool] | None):
        self._tools = tools
    
    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        if self._tools is None:
            return llm
        return llm.bind_tools(tools=self._tools)
        
           
        