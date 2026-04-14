from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# Junction table for many-to-many relationship between Job and Applicant
class Job_Application(Base):
    __tablename__ = "job_applications"

    # Surrogate primary key
    job_application_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    job_id = Column(Integer, ForeignKey('jobs.job_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Timestamp
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    jobs = relationship("Job", back_populates="job_applications")
    user = relationship("User", back_populates="job_applications")
    reports = relationship("Report", back_populates="job_applications")
    interviews = relationship("Interview", back_populates="job_applications")