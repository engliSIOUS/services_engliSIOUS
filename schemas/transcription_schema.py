from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TranscriptionCreate(BaseModel):
    filename: str

class TranscriptionResponse(BaseModel):
    id: str
    filename: str
    file_path: str  # Thêm trường file_path
    text: str
    created_at: datetime
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True