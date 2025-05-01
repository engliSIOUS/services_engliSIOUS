from abc import ABC, abstractmethod

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> str:
        pass