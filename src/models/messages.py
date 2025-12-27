from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Source(StrEnum):
    user = 'user'
    agent = 'agent'

class ClientMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    source: Source  
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
