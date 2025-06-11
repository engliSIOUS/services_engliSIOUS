import azure.cognitiveservices.speech as speechsdk
import os
import tempfile

class TextToSpeechService:
    @staticmethod
    async def synthesize_speech(text: str, voice: str, output_format: str) -> str:
        """
        Tổng hợp giọng nói từ văn bản sử dụng Azure Speech Service.
        Trả về đường dẫn file âm thanh tạm thời.
        """
        temp_file = None
        try:
            # Cấu hình Azure Speech
            speech_config = speechsdk.SpeechConfig(subscription=os.getenv('AZURE_API_KEY'), region=os.getenv('AZURE_REGION'))
            speech_config.speech_synthesis_voice_name = voice
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat[output_format]
            )

            # Tạo file tạm để lưu âm thanh
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            # Thực hiện tổng hợp giọng nói
            result = synthesizer.speak_text_async(text).get()

            # Kiểm tra kết quả
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return temp_file.name
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                raise Exception(
                    f"TTS failed: {cancellation_details.reason}, Error: {cancellation_details.error_details}"
                )

        except Exception as e:
            raise Exception(f"Error in TTS: {str(e)}")

        finally:
            # Đóng file tạm (nhưng không xóa, để controller xử lý)
            if temp_file:
                temp_file.close()
