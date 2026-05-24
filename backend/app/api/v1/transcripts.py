import uuid
from datetime import datetime

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.meeting import Meeting
from app.models.transcript import TranscriptChunk
from app.schemas.transcript import (
    TranscriptChunkRead,
    TranscriptChunkUpdate,
    TranscriptListRead,
)

router = APIRouter()


@router.get("/meetings/{meeting_id}/transcripts", response_model=TranscriptListRead)
async def get_meeting_transcripts(
    meeting_id: str,
    speaker: str | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.meeting_id == meeting_uuid)
        .order_by(TranscriptChunk.start.asc())
        .all()
    )

    if not chunks:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_uuid).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会议不存在")
        if meeting.status in ("uploading", "transcribing"):
            return TranscriptListRead(meeting_id=meeting_uuid, chunks=[])
        raise HTTPException(status_code=404, detail="未找到该会议的转录内容")

    filtered = chunks
    if speaker:
        filtered = [c for c in filtered if c.speaker == speaker]
    if keyword:
        filtered = [c for c in filtered if keyword in c.content]

    return TranscriptListRead(meeting_id=meeting_uuid, chunks=filtered)


@router.get("/transcripts/{chunk_id}", response_model=TranscriptChunkRead)
async def get_transcript_chunk(chunk_id: str):
    return {
        "id": chunk_id,
        "meeting_id": "meet_a7b2c9",
        "speaker": "张三",
        "start": 0.0,
        "end": 4.25,
        "content": "大家好，今天主要对齐一下支付模块的延期问题。",
        "confidence": 0.96,
        "updated_at": None,
    }


@router.patch("/transcripts/{chunk_id}", response_model=TranscriptChunkRead)
async def update_transcript_chunk(chunk_id: str, data: TranscriptChunkUpdate):
    return {
        "id": chunk_id,
        "meeting_id": "meet_a7b2c9",
        "speaker": data.speaker or "李四",
        "start": 0.0,
        "end": 4.25,
        "content": data.content or "支付模块延期到周五。",
        "confidence": 0.96,
        "updated_at": datetime.now(),
    }
