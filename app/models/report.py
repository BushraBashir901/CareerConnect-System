from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    # Primary Key
    report_id = Column(Integer, primary_key=True, index=True)
    
    #basic info
    score = Column(Integer, nullable=False)
    result = Column(String(50), nullable=False) 
    remarks = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    #foreign key
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # Fixed: users.user_id
    bot_id = Column(Integer, ForeignKey('ai_bots.bot_id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    job_application_id = Column(Integer, ForeignKey('job_applications.job_application_id'), nullable=False)
    
    # Relationships
    ai_bots = relationship("AiBot", back_populates="reports")
    job_applications= relationship("Job_Application", back_populates="reports")
    company = relationship("Company", back_populates="reports")  # Fixed: singular company
    
