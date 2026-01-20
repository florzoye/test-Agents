from datetime import datetime
from src.enum.client import Source
from pydantic import BaseModel, Field, ConfigDict

class BaseMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    content: str
    source: Source
    tg_id: int | str | None = None
    tg_nick: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
