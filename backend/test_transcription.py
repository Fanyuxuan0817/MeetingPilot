import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from gtts import gTTS
from loguru import logger


def generate_test_audio(output_path: str):
    logger.info("Generating test audio with gTTS...")
    text = (
        "大家好，欢迎参加今天的项目进度会议。"
        "首先，我们来回顾一下上周的工作进展。"
        "前端团队已经完成了用户界面的重构，后端团队正在集成语音转录服务。"
        "接下来，我们需要讨论下一阶段的开发计划。"
        "请问大家有什么意见或建议吗？"
    )
    tts = gTTS(text=text, lang="zh-cn")
    tts.save(output_path)
    logger.info(f"Test audio saved to: {output_path}")


async def run_transcription(audio_path: str):
    from app.services.transcription_service import transcription_service

    logger.info("Starting transcription test...")
    chunks = await transcription_service.transcribe_audio(audio_path)

    print("\n" + "=" * 60)
    print("TRANSCRIPTION RESULTS")
    print("=" * 60)
    for chunk in chunks:
        print(
            f"  [{chunk['start']:>6.2f}s - {chunk['end']:>6.2f}s] "
            f"{chunk['speaker']}: {chunk['content']}"
        )
    print("=" * 60)
    print(f"Total chunks: {len(chunks)}")
    print("=" * 60 + "\n")

    return chunks


if __name__ == "__main__":
    audio_path = os.path.join(os.path.dirname(__file__), "test_audio.mp3")

    if not os.path.exists(audio_path):
        generate_test_audio(audio_path)
    else:
        logger.info(f"Reusing existing test audio: {audio_path}")

    asyncio.run(run_transcription(audio_path))
