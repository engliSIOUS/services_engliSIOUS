import azure.cognitiveservices.speech as speechsdk
from .base import SpeechToTextProvider
import os
class AzureSpeechToTextProvider(SpeechToTextProvider):
    def __init__(self, subscription_key: str, region: str):
        self.subscription_key = subscription_key
        self.region = region

    async def transcribe(self, audio_file_path: str) -> str:
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config,language="en-US")

        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise Exception("No speech could be recognized")
        else:
            raise Exception(f"Speech recognition failed: {result.error_details}")