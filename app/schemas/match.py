from pydantic import BaseModel
from typing import List
from datetime import datetime

class TraitOut(BaseModel):
    name: str
    tier_current: int
    num_units: int

class UnitOut(BaseModel):
    character_id: str
    tier: int
    items: List[str]

class MatchOut(BaseModel):
    match_id: str
    placement: int
    level: int
    gold_left: int
    last_round: int
    traits: List[TraitOut]
    units: List[UnitOut]
    played_at: datetime

    class Config: {
        "from_attributes": True
    }
    