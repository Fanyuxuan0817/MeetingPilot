import os
import sys
import asyncio
from functools import partial
from loguru import logger

if sys.platform == "win32":
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from faster_whisper import WhisperModel


class TranscriptionService:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        self.device = os.getenv("WHISPER_DEVICE", "cpu")
        self.compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "float32")

        logger.info(
            f"🚀 [MeetingPilot] Loading Faster-Whisper model: {self.model_size} on {self.device}..."
        )
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("✅ [MeetingPilot] Whisper model loaded successfully.")
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ [MeetingPilot] Failed to load Whisper model: {str(e)}")
            raise e

    async def transcribe_audio(self, audio_path: str) -> list[dict]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at: {audio_path}")

        logger.info(f"🎙️ [MeetingPilot] Starting transcription for: {audio_path}")

        loop = asyncio.get_running_loop()

        whisper_func = partial(
            self.model.transcribe,
            audio_path,
            beam_size=5,
            word_timestamps=False,
        )

        try:
            segments, info = await loop.run_in_executor(None, whisper_func)

            logger.info(
                f"🌍 [MeetingPilot] Detected language: '{info.language}' (Prob: {info.language_probability:.2f})"
            )

            def collect_segments():
                chunks = []
                for idx, segment in enumerate(segments):
                    chunks.append(
                        {
                            "chunk_index": idx,
                            "start": round(segment.start, 2),
                            "end": round(segment.end, 2),
                            "speaker": "Speaker 0",
                            "content": segment.text.strip(),
                        }
                    )
                return chunks

            parsed_chunks = await loop.run_in_executor(None, collect_segments)
            logger.info(
                f"🎉 [MeetingPilot] Transcription completed. Total chunks: {len(parsed_chunks)}"
            )
            return parsed_chunks

        except Exception as e:
            logger.error(f"❌ [MeetingPilot] Transcription failed: {str(e)}")
            raise e


transcription_service = TranscriptionService()
