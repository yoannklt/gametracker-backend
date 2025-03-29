from pydantic import BaseModel
from typing import List
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
    
class CompositionStats(BaseModel):
    composition: List[str]
    games_played: int
    wins: int
    win_rate: float
    avg_placement: float
    
    class Config: {
        "from_attributes": True
    }