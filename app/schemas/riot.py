from pydantic import BaseModel
    
class RiotLinkResponse(BaseModel):
    message: str
    game_name: str
    tag_line: str
    puuid: str