from pydantic import BaseModel
from typing import List
    
# USERS
class RiotLinkResponse(BaseModel):
    message: str
    game_name: str
    tag_line: str
    puuid: str
   
   
# MATCHES 
class Trait(BaseModel):
    name: str
    tier_current: int
    num_units: int
    
class Unit(BaseModel):
    character_id: str
    tier: int
    items: List[str]
    
class PlayerMatchData(BaseModel):
    placement: int
    level: int
    gold_left: int
    last_round: int
    traits: List[Trait]
    units: List[Unit]
