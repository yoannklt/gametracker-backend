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