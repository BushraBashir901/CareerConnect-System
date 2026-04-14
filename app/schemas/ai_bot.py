from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AiBotBase(BaseModel):
    """
    Base schema for AI Bot.

    Contains common fields shared across create, update, and response schemas.
    """
    bot_name: str
    bot_type: Optional[str] = None
    bot_description: Optional[str] = None


class AiBotCreate(AiBotBase):
    """
    Schema used for creating a new AI Bot.

    Inherits all fields from AiBotBase.
    """
    pass


class AiBotUpdate(BaseModel):
    """
    Schema used for updating an AI Bot.

    All fields are optional for partial updates.
    """
    bot_name: Optional[str] = None
    bot_type: Optional[str] = None
    bot_description: Optional[str] = None


class AiBotResponse(AiBotBase):
    """
    Schema used for returning AI Bot data in API responses.

    Includes database-generated fields like IDs and timestamps.
    """
    bot_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }