from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Source(StrEnum):
    client = 'client'
    agent = 'agent'

class BaseMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    content: str
    source: Source
    tg_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
