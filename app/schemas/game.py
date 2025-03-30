from pydantic import BaseModel
    
class CompositionStats(BaseModel):
    composition: str
    games_played: int
    wins: int
    win_rate: float
    avg_placement: float
    
    class Config: {
        "from_attributes": True
    }
    
class UnitStats(BaseModel):
    character_id: str
    count: int
    winrate: float
    
class TraitStats(BaseModel):
    name: str
    count: int
    winrate: float