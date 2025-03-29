import requests
from fastapi import HTTPException
from app.core.config import settings

API_KEY = settings.RIOT_API_KEY
HEADERS = { "X-Riot-Token": API_KEY }
VALID_REGION = {"europe", "americas", "asia", "esport"}

def get_puuid_from_riot(game_name: str, tag_line: str, region: str):
    # Traitement des données reçues
    game_name = game_name.lower()
    tag_line = tag_line.lower()
    region = region.lower()
    if region not in VALID_REGION:
        raise HTTPException(status_code=400, detail="Région Invalide")
    
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()["puuid"]
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur API Riot: {response.status_code} - {response.text}"
        )
        
def get_recent_match_ids(puuid: str, region: str, count: int = 10):
    if region not in VALID_REGION:
        raise HTTPException(status_code=400, detail="Région invalide")
    
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur API Riot: {response.status_code} - {response.text}"
        )
        
def get_match_details(match_id: str, region: str):
    region = region.lower()
    if region not in VALID_REGION:
        raise HTTPException(status_code=400, detail="Région invalide")
    
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur API Riot: {response.status_code} - {response.text}"
        )
        
def extract_player_data(match_data: dict, puuid: str) -> dict:
    try:
        participant = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
        
        if not participant:
            raise HTTPException(status_code=404, detail="PUUID non trouvé dans ce match")

        traits = [
            {
                "name": trait["name"],
                "tier_current": trait["tier_current"],
                "num_units": trait["num_units"]
            }
            for trait in participant["traits"]
            if trait["tier_current"] > 0
        ]

        units = [
            {
                "character_id": unit["character_id"],
                "tier": unit["tier"],
                "items": unit.get("itemNames", [])
            }
            for unit in participant["units"]
        ]

        return {
            "placement": participant["placement"],
            "level": participant["level"],
            "gold_left": participant["gold_left"],
            "last_round": participant["last_round"], 
            "traits": traits,
            "units": units
        }

    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Champ manquant dans la réponse Riot : {e}")
