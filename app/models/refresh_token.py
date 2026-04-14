from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.base_class import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String, nullable=False)
    expires_at = Column(DateTime)
    
    # Relationship back to user
    user = relationship("User", back_populates="refresh_tokens")