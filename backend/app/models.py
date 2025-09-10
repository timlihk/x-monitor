from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MonitoredTerm(Base):
    __tablename__ = "monitored_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False, index=True)
    restrict_following = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    results = relationship("Result", back_populates="monitored_term")

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("monitored_terms.id"), nullable=False)
    tweets_raw = Column(JSON)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    monitored_term = relationship("MonitoredTerm", back_populates="results")