from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    #Primary Key
    company_id = Column(Integer, primary_key=True, index=True)
    
    #Basic Info
    company_name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")  # Fixed: singular company
    jobs = relationship("Job", back_populates="company")  # Fixed: singular company
    team_invitations = relationship("TeamInvitation", back_populates="company")
    reports = relationship("Report", back_populates="company")  # Fixed: singular company

