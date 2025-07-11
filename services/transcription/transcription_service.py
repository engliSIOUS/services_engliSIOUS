import os
from fastapi import UploadFile
from services.speech_to_text.base import SpeechToTextProvider
from repositories.transcription_repository import TranscriptionRepository
from schemas.user_schema import UserSession
from pydub import AudioSegment
from pathlib import Path
import uuid
import subprocess
import spacy
nlp = spacy.load("en_core_web_sm")


class TranscriptionService:
    def __init__(self, speech_to_text_provider: SpeechToTextProvider, transcription_repo: TranscriptionRepository):
        self.speech_to_text_provider = speech_to_text_provider
        self.transcription_repo = transcription_repo
        # Tạo thư mục audio nếu chưa tồn tại
        os.makedirs("audio", exist_ok=True)

    def convert_aac_to_wav(self,input_path, output_path):
        cmd = [
            "ffmpeg",
            "-y",              # Ghi đè nếu file output tồn tại
            "-i", input_path,  # Đầu vào
            "-ac", "1",        # Mono
            "-ar", "16000",    # Sample rate 16 kHz
            "-c:a", "pcm_s16le",  # Codec: PCM 16-bit little-endian
            "-f", "wav",       # Định dạng file đầu ra
            output_path
        ]
        subprocess.run(cmd, check=True)
    async def get_transcription(self, transcription_id: str, user_session: UserSession) -> dict:
        # Lấy user_id từ session_id
        user_id = user_session.user_id
        # Lấy bản ghi từ MongoDB
        return self.transcription_repo.get_transcription(transcription_id, user_id)

    
    async def transcribe_audio(self, audio_file: UploadFile,user_session:UserSession) -> str:
        user_id = "anonymous"  # Mặc định user_id là "anonymous" nếu không có user_session
        unique_filename = f"{uuid.uuid4()}.wav"
        file_extension = Path(audio_file.filename).suffix.lower()
        # Lưu file audio vào thư mục audio
        file_path = os.path.join("audio", unique_filename)
        temp_file_path = os.path.join("audio", f"temp_{uuid.uuid4()}{file_extension}")
        with open(temp_file_path, "wb") as f:
            f.write(await audio_file.read())

        try:
            if file_extension == '.aac':
                # Chuyển đổi AAC sang WAV
                self.convert_aac_to_wav(temp_file_path, file_path)
                os.remove(temp_file_path)
            elif file_extension != '.wav':
                audio = AudioSegment.from_file(file=temp_file_path, format=file_extension[1:])  # Bỏ dấu chấm
                audio.export(file_path, format="wav")  # Chuyển đổi sang WAV
                os.remove(temp_file_path)  # Xóa file tạm
            else:
                os.rename(temp_file_path, file_path)
            # Lấy user_id từ session_id
            user_id = user_session.user_id
            # Gọi Speech-to-Text service
            text = await self.speech_to_text_provider.transcribe(file_path)
            status = "success"
            error_message = None
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            text = ""
            status = "failed"
            error_message = str(e)

        # Lưu kết quả vào MongoDB, bao gồm file_path
        transcription_id = self.transcription_repo.save_transcription(
            user_id=user_id,
            filename=unique_filename,
            file_path=file_path,
            text=text,
            status=status,
            error_message=error_message
        )

        return transcription_id
    
    def tokenize_text(self,data: str) -> list:
        doc = nlp(data)
        return [str(token) for token in doc if not token.is_punct]
        