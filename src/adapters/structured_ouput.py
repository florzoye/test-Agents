from typing import Type, Any, Literal
from src.adapters.base import LLMAdapter
from langchain_core.language_models import BaseChatModel

class StructuredOutputAdapter(LLMAdapter):
    def __init__(
        self, 
        schema: Type[Any],
        *,
        method: Literal["function_calling", "json_mode", "json_schema"] = "json_schema",
        include_raw: bool = False,
    ):
        """
        Schema supports only:
        - Pydantic BaseModel
        - TypedDict classes
        """
        self._schema = schema
        self._method = method
        self._include_raw = include_raw

    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        return llm.with_structured_output(
            self._schema,
            method=self._method,
            include_raw=self._include_raw
        )