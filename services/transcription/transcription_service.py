import os
from fastapi import UploadFile
from services.speech_to_text.base import SpeechToTextProvider
from repositories.transcription_repository import TranscriptionRepository

class TranscriptionService:
    def __init__(self, speech_to_text_provider: SpeechToTextProvider, transcription_repo: TranscriptionRepository):
        self.speech_to_text_provider = speech_to_text_provider
        self.transcription_repo = transcription_repo
        # Tạo thư mục audio nếu chưa tồn tại
        os.makedirs("audio", exist_ok=True)

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        # Lưu file audio vào thư mục audio
        file_path = os.path.join("audio", audio_file.filename)
        with open(file_path, "wb") as f:
            f.write(await audio_file.read())

        try:
            # Gọi Speech-to-Text service
            text = await self.speech_to_text_provider.transcribe(file_path)
            status = "success"
            error_message = None
        except Exception as e:
            text = ""
            status = "failed"
            error_message = str(e)

        # Lưu kết quả vào MongoDB, bao gồm file_path
        transcription_id = self.transcription_repo.save_transcription(
            filename=audio_file.filename,
            file_path=file_path,
            text=text,
            status=status,
            error_message=error_message
        )

        return transcription_id