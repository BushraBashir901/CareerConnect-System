from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AiBot(Base):
    __tablename__ = "ai_bots"

    #Primary Key
    bot_id = Column(Integer, primary_key=True, index=True)
    
    #Basic Info
    bot_name = Column(String(255), nullable=False)
    bot_type = Column(String(50), nullable=True)  # e.g., "Interview", "Assessment"
    bot_description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reports = relationship("Report", back_populates="ai_bots")
    interviews = relationship("Interview", back_populates="ai_bots")
   
    
