from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True, nullable=False)
    puuid = Column(String, nullable=False)
    placement = Column(Integer)
    level = Column(Integer)
    gold_left = Column(Integer)
    last_round = Column(Integer)
    
    traits = Column(JSON)
    units = Column(JSON)
    
    played_at = Column(DateTime, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="matches")