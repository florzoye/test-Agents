from typing import TypedDict, List
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel

class ClientInfo(TypedDict):
    pass

class PreprocessedData(TypedDict):
    client_data: ClientModel
    message_history:List[BaseMessage]
    current_message: BaseMessage

class ChainState(TypedDict):
    response: str | None
    should_continue: bool
    client_info: dict | None
    message: BaseMessage | None
    preprocessed_data: PreprocessedData | None