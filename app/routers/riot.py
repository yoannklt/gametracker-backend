from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import RiotAccount
from app.services.riot_service import get_puuid_from_riot, get_recent_match_ids, get_match_details, extract_player_data, store_match_if_not_exists
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.riot import RiotLinkResponse, PlayerMatchData

router = APIRouter(prefix="/riot", tags=["riot"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.put("/link-riot", response_model=RiotLinkResponse)
def link_riot_account(data: RiotAccount, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    puuid = get_puuid_from_riot(data.game_name, data.tag_line, data.region)
    
    current_user.game_name = data.game_name.lower()
    current_user.tag_line = data.tag_line.lower()
    current_user.puuid = puuid
    current_user.region = data.region.lower()
    
    user = db.merge(current_user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Compte Riot lié avec succès!",
        "game_name": current_user.game_name,
        "tag_line": current_user.tag_line,
        "puuid": current_user.puuid
    }
    
@router.get("/matches")
def get_user_matchs_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.puuid or not current_user.region:
        raise HTTPException(
            status_code=400, detail="Compte Riot non lié"
        )
    
    match_ids =  get_recent_match_ids(current_user.puuid, current_user.region)
    return {
        "message": "Matchs récupérés avec succès",
        "match_ids": match_ids
    }
    
@router.get("/match/{match_id}", response_model=PlayerMatchData)
def get_match_info(match_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.puuid or not current_user.region:
        raise HTTPException(status_code=400, detail="Compte Riot non lié ou région non définie")
    
    match_details = get_match_details(match_id, current_user.region)
    player_data = extract_player_data(match_details, current_user.puuid)
    return player_data


@router.get("/history", response_model=list[PlayerMatchData])
def get_match_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.puuid or not current_user.region:
        raise HTTPException(status_code=400, detail="Compte Riot non liée ou région non définie")
    
    match_ids = get_recent_match_ids(current_user.puuid, current_user.region)
    
    results = []
    
    for match_id in match_ids:
        try:
            match_data = get_match_details(match_id, current_user.region)
            store_match_if_not_exists(db, match_data, current_user.puuid, current_user.id)
            player_data = extract_player_data(match_data, current_user.puuid)
            results.append(player_data)
        except Exception as e:
            print(f"Erreur lorts du traitement du match {match_id} : {e}")
            continue
    
    return results