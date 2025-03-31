import requests
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from collections import defaultdict
from app.core.config import settings
from app.models.match import Match

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
        
def get_recent_match_ids(puuid: str, region: str, count: int = 10) -> List[str]:
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
    # print(puuid == "ms0UplvcaeM55brRe0Ib-_iBvXz2nkIcLJM_1z3_NJQGwfRFpg-oqpFdfRMyrAWiubx7R_bhbQ7opA")
    try:
        participant = None
        for p in match_data["info"]["participants"]:
            if p["puuid"] == puuid:
                participant = p
                break

        if not participant:
            raise HTTPException(status_code=404, detail="PUUID non trouvé dans ce match")
    except Exception as e:
        raise ValueError(f"Erreur lors de la récupération du participant : {e}")
        
    if not participant:
        raise HTTPException(status_code=404, detail="PUUID non trouvé dans ce match")
    
    try:
        traits = [
            {
                "name": trait.get("name", ""),
                "tier_current": trait.get("tier_current", 0),
                "num_units": trait.get("num_units", 0)
            }
            for trait in participant.get("traits", [])
            if trait.get("tier_current", 0) > 0
        ]

        units = [
            {
                "character_id": unit.get("character_id", ""),
                "tier": unit.get("tier", 0),
                "items": unit.get("itemsName", [])  # ⚠️ On utilise bien "itemsName"
            }
            for unit in participant.get("units", [])
        ]

        return {
            "placement": participant.get("placement", 0),
            "level": participant.get("level", 0),
            "gold_left": participant.get("gold_left", 0),
            "last_round": participant.get("last_round", 0),
            "traits": traits,
            "units": units
        }

    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction des données du joueur: {e}")
    

def compute_stats_by_traits(matches: List[Match]) -> dict:
    stats = defaultdict(lambda: {"wins": 0, "games": 0, "total_placement": 0})
    
    for match in matches:
        traits = match.traits
        if not traits:
            continue
        
        sorted_traits = sorted(traits, key=lambda x: x["tier_current"], reverse=True)
        
        max_tier = sorted_traits[0]["tier_current"]
        main_traits = [t["name"].replace("TFT13_", "").lower() for t in sorted_traits if t["tier_current"] == max_tier]
        
        trait_key = " ".join(sorted(main_traits))
        
        stats[trait_key]["games"] += 1
        stats[trait_key]["total_placement"] += match.placement
        if match.placement <= 4:
            stats[trait_key]["wins"] += 1
            
    result = []
    for trait_key, data in stats.items():
        games = data["games"]
        wins = data["wins"]
        winrate = round((wins / games) * 100, 2)
        avg_placement = round(data["total_placement"] / games, 2)
        result.append({
            "composition": trait_key,
            "games_played": games,
            "wins": wins,
            "win_rate": winrate,
            "avg_placement": avg_placement
        })
    
    return result


def detect_main_composition(traits: dict) -> str:
    """
    Détecte la composition principale basée sur les traits activés (tier_current > 0).
    Retourne une chaîne formatée du type "challenger-bastion"
    """
    # On filtre les traits actifs
    active_traits = [trait for trait in traits if trait["tier_current"] > 0]

    # On trie d'abord par `tier_current`, puis par `num_units` pour départager les égalités
    sorted_traits = sorted(
        active_traits,
        key=lambda t: (t["tier_current"], t["num_units"]),
        reverse=True
    )

    # On prend les 2 traits les plus forts (ou 1 seul si pas assez)
    main_traits = sorted_traits[:2]
    names = [trait["name"].replace("TFT13_", "").lower() for trait in main_traits]

    return "-".join(names)


def store_match_if_not_exists(db: Session, match_data: dict, puuid: str, user_id: int):
    match_id = match_data["metadata"]["match_id"]
    
    existing = db.query(Match).filter_by(match_id=match_id).first()
    if existing:
        return
    
    player_data = extract_player_data(match_data, puuid)
    composition_name = detect_main_composition(player_data["traits"])
    timestamp_ms = match_data["info"]["game_datetime"]
    played_at = datetime.fromtimestamp(timestamp_ms / 1000)
    
    match = Match(
        match_id=match_id,
        puuid=puuid,
        user_id=user_id,
        placement=player_data["placement"],
        level=player_data["level"],
        gold_left=player_data["gold_left"],
        last_round=player_data["last_round"],
        composition_name=composition_name,
        traits=player_data["traits"],
        units=player_data["units"],
        played_at=played_at
    )
    
    db.add(match)
    db.commit()
    
def get_summoner_info(game_name: str, tag_line: str, region: str) -> dict:
    if region not in VALID_REGION:
        raise HTTPException(status_code=400, detail="Région invalide")
    
    account_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    account_res = requests.get(url=account_url, headers=HEADERS)
    if account_res.status_code != 200:
        raise HTTPException(status_code=account_res.status_code, detail="Compte Riot introuvable")
    puuid = account_res.json()["puuid"]
    
    summoner_url = f"https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
    summoner_res = requests.get(url=summoner_url, headers=HEADERS)
    if summoner_res.status_code != 200:
        raise HTTPException(status_code=summoner_res.status_code, detail="Invocateur introuvable")
    summoner_data = summoner_res.json()
    
    summoner_id = summoner_data["id"]
    league_url = f"https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}"
    league_res = requests.get(url=league_url, headers=HEADERS)
    if league_res.status_code != 200:
        raise HTTPException(status_code=league_res.status_code, detail="Classement introuvable")
    league_data = league_res.json()
    
    tft_ranked = next((entry for entry in league_data if entry["queueType"] == "RANKED_TFT"), None)
    
    return {
                "game_name": game_name,
        "tag_line": tag_line,
        "summoner_level": summoner_data["summonerLevel"],
        "profile_icon_id": summoner_data["profileIconId"],
        "tier": tft_ranked["tier"] if tft_ranked else "UNRANKED",
        "rank": tft_ranked["rank"] if tft_ranked else "",
        "league_points": tft_ranked["leaguePoints"] if tft_ranked else 0,
        "wins": tft_ranked["wins"] if tft_ranked else 0,
        "losses": tft_ranked["losses"] if tft_ranked else 0,
        "hot_streak": tft_ranked["hotStreak"] if tft_ranked else False,
    }