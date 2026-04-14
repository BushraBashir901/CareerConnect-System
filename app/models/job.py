from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Job(Base):
    __tablename__ = "jobs"

    #Primary Key
    job_id = Column(Integer, primary_key=True, index=True)

    #Basic Info
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    salary_range = Column(String(255), nullable=True)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    #foreign key to companies table
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")  # Fixed: singular company
    job_applications = relationship("Job_Application", back_populates="jobs")

