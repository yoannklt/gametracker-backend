from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.services.auth_service import create_user, authenticate_user, create_access_token
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency: session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Vérifie l'unicité du mail
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé."
        )
    
    # Vérifie l'unicité du username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username déjà utilisé."
        )
    
    new_user = create_user(user_data, db)
    return new_user

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(user_data.identifier, user_data.password, db)
    acces_token = create_access_token(
        data={"sub": user.username},
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access token": acces_token, "token_type": "bearer"}
