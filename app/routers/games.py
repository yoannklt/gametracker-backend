from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.schemas.game import GameCreate, GameOut, GameUpdate
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

@router.get("/history", response_model=list[GameOut])
def get_history(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    games = db.query(Game)\
        .filter(Game.user_id == current_user.id)\
        .order_by(Game.timestamp.desc())\
        .all()
    return games

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    stats = (
        db.query(
            Game.composition,
            func.count().label("games_played"),
            func.sum(func.cast(Game.victory, Integer)).label("wins")
        )
        .filter(Game.user_id == current_user.id)
        .group_by(Game.composition)
        .all()
    )
    
    # Formatage du résultat
    result = []
    for compo, games_played, wins in stats:
        win_rate = round((wins / games_played ) * 100, 2) if games_played > 0 else 0.0
        result.append({
            "composition": compo,
            "games_played": games_played,
            "wins": wins,
            "win_rate": win_rate
        })
        
    return result
        
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
        