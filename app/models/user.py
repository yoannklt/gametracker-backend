from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    game_name = Column(String, nullable=True)
    tag_line = Column(String, nullable=True)
    puuid = Column(String, unique=True, nullable=True)
    region = Column(String, nullable=True)
    
    role = relationship("Role", back_populates="users")
    matches = relationship("Match", back_populates="user")