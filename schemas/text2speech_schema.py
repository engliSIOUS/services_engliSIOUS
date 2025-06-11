from pydantic import BaseModel
class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "en-US-JennyNeural"  # Giọng mặc định: Jenny (tiếng Anh Mỹ)
    output_format: str = "Riff24Khz16BitMonoPcm"  # Định dạng âm thanh