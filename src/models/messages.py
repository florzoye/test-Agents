from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ClientMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    source: str  
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
