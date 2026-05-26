from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

app = FastAPI(
    title="MeetingPilot API",
    description="智能会议助手 - 后端 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

audio_dir = Path(__file__).resolve().parent.parent / "uploads" / "audio"
audio_dir.mkdir(parents=True, exist_ok=True)
test_src = Path(__file__).resolve().parent.parent / "test_audio.mp3"
if test_src.exists() and not (audio_dir / "test_audio.mp3").exists():
    import shutil
    shutil.copy2(test_src, audio_dir / "test_audio.mp3")

app.mount("/storage/audio", StaticFiles(directory=str(audio_dir)), name="audio")


@app.get("/")
async def root():
    return {"message": "Welcome to MeetingPilot API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
