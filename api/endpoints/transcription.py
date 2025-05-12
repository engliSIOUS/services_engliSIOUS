from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from dependencies.dependencies import get_transcription_service
from dependencies.dependencies import get_transcription_repository
from services.transcription.transcription_service import TranscriptionService
from repositories.transcription_repository import TranscriptionRepository
from schemas.transcription_schema import TranscriptionResponse
from pathlib import Path
router = APIRouter()

@router.post("/transcriptions/", response_model=TranscriptionResponse)
async def create_transcription(
    audio_file: UploadFile = File(...),
    service: TranscriptionService = Depends(get_transcription_service),
    repo: TranscriptionRepository = Depends(get_transcription_repository)
):
    file_extension = Path(audio_file.filename).suffix.lower()
    if file_extension != '.wav':
        raise HTTPException(status_code=400, detail="Only WAV files are allowed")
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    transcription_id = await service.transcribe_audio(audio_file)
    transcription = repo.get_transcription(transcription_id)
    
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
    repo: TranscriptionRepository = Depends(get_transcription_repository)
):
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