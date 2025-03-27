from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    puuid = Column(String, unique=True, nullable=True)
    
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2)
    
    games = relationship("Game", back_populates="user", cascade="all, delete")
    role = relationship("Role", back_populates="users")