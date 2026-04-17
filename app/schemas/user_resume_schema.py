from pydantic import BaseModel
from datetime import datetime


class User_Resume_Schema(BaseModel):
    """
    Schema for user resume.

    Attributes:
        user_resume_id (int): Primary key.
        user_id (int): Foreign key to users table.
        raw_text (str): Raw text of the resume.
        clear_text (str): Cleaned text of the resume.
        created_at (datetime): Timestamp when the resume was created.

    """
    user_resume_id: int
    user_id: int
    raw_text: str
    clear_text: str
    
class User_Resume_Request(BaseModel):
    pass


class User_Resume_Response(BaseModel):
    pass
