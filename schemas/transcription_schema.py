from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "en-US-JennyNeural"  # Giọng mặc định: Jenny (tiếng Anh Mỹ)
    output_format: str = "Riff24Khz16BitMonoPcm"  # Định dạng âm thanh

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