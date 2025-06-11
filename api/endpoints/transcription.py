from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dependencies.dependencies import get_transcription_service
from dependencies.dependencies import get_transcription_repository
from services.transcription.transcription_service import TranscriptionService
from repositories.transcription_repository import TranscriptionRepository
from schemas.transcription_schema import TranscriptionResponse
from pathlib import Path
from dependencies.dependencies import get_user_session
from schemas.user_schema import UserSession
from schemas.text2speech_schema import TextToSpeechRequest
from services.text_to_speech.text2speech import TextToSpeechService
import os
import time
router = APIRouter()

@router.post("/transcriptions/", response_model=TranscriptionResponse)
async def create_transcription(
    audio_file: UploadFile = File(...),
    service: TranscriptionService = Depends(get_transcription_service),
    repo: TranscriptionRepository = Depends(get_transcription_repository),
    user_session: UserSession = Depends(get_user_session)
):
    file_extension = Path(audio_file.filename).suffix.lower()
    if file_extension != '.wav':
        raise HTTPException(status_code=400, detail="Only WAV files are allowed")
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    transcription_id = await service.transcribe_audio(audio_file,user_session)
    transcription = repo.get_transcription(transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return TranscriptionResponse(
        id=str(transcription["_id"]),
        filename=transcription["filename"],
        file_path=transcription["file_path"],  # Thêm file_path vào response
        text=transcription["text"],
        created_at=transcription["created_at"],
        status=transcription["status"],
        error_message=transcription["error_message"]
    )

@router.get("/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: str,
    service: TranscriptionService = Depends(get_transcription_service),
    user_session: UserSession = Depends(get_user_session) 
):
    transcription = service.get_transcription(transcription_id, user_session)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return TranscriptionResponse(
        id=str(transcription["_id"]),
        session_id=transcription["session_id"],
        filename=transcription["filename"],
        file_path=transcription["file_path"],  # Thêm file_path vào response
        text=transcription["text"],
        created_at=transcription["created_at"],
        status=transcription["status"],
        error_message=transcription["error_message"]
    )

@router.post("/text-to-speech/", response_class=FileResponse)
async def text_to_speech(request: TextToSpeechRequest):
    temp_file_path = None
    try:
        # Gọi service để tổng hợp giọng nói
        temp_file_path = await TextToSpeechService.synthesize_speech(
            text=request.text,
            voice=request.voice,
            output_format=request.output_format
        )

        # Trả về file âm thanh
        return FileResponse(
            temp_file_path,
            media_type="audio/wav",
            filename="output.wav",
            headers={"Content-Disposition": "attachment; filename=output.wav"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    finally:
        # Xóa file tạm nếu tồn tại
           if temp_file_path and os.path.exists(temp_file_path):
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    os.remove(temp_file_path)
                    break
                except PermissionError:
                    if attempt < max_attempts - 1:
                        time.sleep(0.1)  # Chờ 100ms trước khi thử lại
                    else:
                        print(f"Warning: Could not delete temp file {temp_file_path}")