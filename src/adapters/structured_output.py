from typing import Type, Any
from src.adapters.base import LLMAdapter
from langchain_core.language_models import BaseChatModel
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy

class StructuredOutputAdapter(LLMAdapter):
    def __init__(
        self, 
        schema: Type[Any],
        *,
        strategy: str = "auto",  # "tool", "provider" или "auto"
        strict: bool | None = None,
        handle_errors: bool | str = True
    ):
        self.schema = schema
        self.strategy = strategy
        self.strict = strict
        self.handle_errors = handle_errors

    def get_response_format(self):
        if self.strategy == "provider":
            return ProviderStrategy(schema=self.schema, strict=self.strict)
        if self.strategy == "tool":
            return ToolStrategy(schema=self.schema, handle_errors=self.handle_errors)
        return self.schema

    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        llm._response_format = self.get_response_format()
        return llm
