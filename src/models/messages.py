from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Source(StrEnum):
    user = 'user'
    agent = 'agent'

class ClientMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    source: Source = Source.user  
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: Source = Source.agent  
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)