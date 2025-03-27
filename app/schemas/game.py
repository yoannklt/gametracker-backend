from pydantic import BaseModel
from datetime import datetime

class GameCreate(BaseModel):
    composition: str
    victory: bool
    
class GameOut(BaseModel):
    id: int
    composition: str
    victory: bool
    timestamp: datetime
    
    model_config = {
        "from_attributes": True
    }
    
class GameUpdate(BaseModel):
    composition: str
    victory: bool