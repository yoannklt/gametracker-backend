from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session
from collections import defaultdict
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.schemas.game import GameCreate, GameOut, GameUpdate, CompositionStats
from app.schemas.match import MatchOut
from app.models.match import Match
from app.models.game import Game
from app.models.user import User

router = APIRouter(prefix="/games", tags=["games"])

def get_db ():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/add", response_model=GameOut)
def add_game(game_data: GameCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_game = Game(
        user_id=current_user.id,
        composition=game_data.composition,
        victory=game_data.victory
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game

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
        
@router.delete("/{game_id}/delete")
def delete_game(game_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == current_user.id).first()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partie non trouvée ou accès interdit"
        )
    
    db.delete(game)
    db.commit()
    return {"detail": "Partie supprimée avec succès."}
    
@router.put("/{game_id}/update")
def update_game(game_id: int, game_data: GameUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == current_user.id).first()

    if not game: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partie non trouvée ou accès interdit"
        )
        
    game.composition = game_data.composition
    game.victory = game_data.victory
    db.commit()
    db.refresh(game)
    return game
        
        
@router.get("/stats", response_model=List[CompositionStats])
def get_composition_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matches = (
        db.query(Match)
        .filter(Match.user_id == current_user.id)
        .all()
    )
    print(len(matches))
    stats = defaultdict(lambda: {"games_played": 0, "wins": 0, "placements": []})

    for match in matches:
        unit_names = [unit["character_id"] for unit in match.units]
        unit_names.sort()
        compo_key = tuple(unit_names)

        stats[compo_key]["games_played"] += 1
        if match.placement <= 4:
            stats[compo_key]["wins"] += 1
        stats[compo_key]["placements"].append(match.placement)

    response = []
    for compo, data in stats.items():
        games_played = data["games_played"]
        wins = data["wins"]
        placements = data["placements"]
        avg_placement = sum(placements) / games_played if games_played else 0
        win_rate = (wins / games_played) * 100 if games_played else 0

        response.append(CompositionStats(
            composition=list(compo),
            games_played=games_played,
            wins=wins,
            win_rate=round(win_rate, 2),
            avg_placement=round(avg_placement, 2)
        ))

    return response