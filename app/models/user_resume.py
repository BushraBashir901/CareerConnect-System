from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserResume(Base):
    __tablename__ = "user_resume"

    # Primary Key
    user_resume_id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Resume Data
    raw_text = Column(String, nullable=False)
    clear_text = Column(JSONB, nullable=False)
    file_path = Column(String, nullable=True)
    filename = Column(String, nullable=True)

    # Relationship
    user = relationship("User", back_populates="user_resume")