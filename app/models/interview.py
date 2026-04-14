from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Interview(Base):
    __tablename__ = "interviews"


    # Primary Key
    interview_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Info
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending")  # pending, ongoing, completed

    # Foreign Keys
    job_application_id = Column(Integer, ForeignKey("job_applications.job_application_id"), nullable=False)
    ai_bot_id = Column(Integer, ForeignKey("ai_bots.bot_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Relationships
    job_applications = relationship("Job_Application", back_populates="interviews")
    ai_bots = relationship("AiBot", back_populates="interviews")
    user = relationship("User", back_populates="interviews")  # Fixed: singular user