from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
from app.services.riot_service import compute_stats_by_traits
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.schemas.game import CompositionStats, UnitStats, TraitStats
from app.schemas.match import MatchOut
from app.models.match import Match
from app.models.user import User

router = APIRouter(prefix="/games", tags=["games"])

def get_db ():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@router.get("/history", response_model=List[MatchOut])
def get_history(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
    ):
    matches = (
        db.query(Match)
        .filter(Match.user_id == current_user.id)
        .order_by(Match.played_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    if not matches:
        raise HTTPException(status_code=404, detail="Aucun match trouvé.")
    
    return matches
               
        
@router.get("/stats", response_model=List[CompositionStats])
def get_composition_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matches = (
        db.query(Match)
        .filter(Match.user_id == current_user.id)
        .all()
    )

    return compute_stats_by_traits(matches)


@router.get("/top-units", response_model=List[UnitStats])
def get_top_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matches = db.query(Match).filter(Match.user_id == current_user.id).all()
    
    if not matches:
        raise HTTPException(status_code=404, detail="Aucun match trouvé pour l'utilisateur")
    
    unit_counter = Counter()
    win_counter = Counter()
    
    for match in matches:
        placement = match.placement
        for unit in match.units:
            cid = unit["character_id"]
            unit_counter[cid] += 1
            if placement <= 4:
                win_counter[cid] += 1
            
    top_units = unit_counter.most_common(5)
    
    return [
        {
            "character_id": cid,
            "count": count,
            "winrate": round((win_counter[cid] / count) * 100, 2) if count > 0 else 0.0
        }
        for cid, count in top_units
    ]


@router.get("/top-traits", response_model=List[TraitStats])
def get_top_traits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matches = db.query(Match).filter(Match.user_id == current_user.id).all()
    
    if not matches:
        raise HTTPException(status_code=404, detail="Aucun match trouvé pour l'utilisateur")
    
    trait_counter = Counter()
    win_counter = Counter()
    
    for match in matches:
        placement = match.placement
        for trait in match.traits:
            tn = trait["name"]
            trait_counter[tn] += 1
            if placement <= 4:
                win_counter[tn] += 1
            
    top_traits = trait_counter.most_common(5)
    
    return [
        {
            "name": tn.replace("TFT13_", "").lower(),
            "count": count,
            "winrate": round((win_counter[tn] / count) * 100, 2) if count > 0 else 0.0
        }
        for tn, count in top_traits
    ]