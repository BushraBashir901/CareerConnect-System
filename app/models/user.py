from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base



class User(Base):
    __tablename__ = "users"

    # Primary Key
    user_id = Column(Integer, primary_key=True, index=True)

    google_id = Column(String, unique=True)

    # Basic Info
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)

    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Role (candidate, recruiter, admin)
    role = Column(String, nullable=False)

    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=True)

    # Relationships
    company = relationship("Company", back_populates="users")
    job_applications = relationship("Job_Application", back_populates="user")
    interviews = relationship("Interview", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    # One-to-One relationship with resume
    chatbot_conversations = relationship("ChatbotConversation", back_populates="user")

    user_resume = relationship("UserResume", back_populates="user", uselist=False)