from datetime import datetime

from fastapi import APIRouter, Query

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
):
    mock_chunks = [
        {
            "id": "chunk_1001",
            "meeting_id": meeting_id,
            "speaker": "张三",
            "start": 0.0,
            "end": 4.25,
            "content": "大家好，今天主要对齐一下支付模块的延期问题。",
            "confidence": 0.96,
            "updated_at": None,
        },
        {
            "id": "chunk_1002",
            "meeting_id": meeting_id,
            "speaker": "李四",
            "start": 4.5,
            "end": 12.8,
            "content": "支付模块由于第三方回调问题，需要延期到周五完成。目前测试环境已经复现了这个问题。",
            "confidence": 0.94,
            "updated_at": None,
        },
        {
            "id": "chunk_1003",
            "meeting_id": meeting_id,
            "speaker": "王五",
            "start": 13.0,
            "end": 20.5,
            "content": "那原定周三上线的计划需要调整了，建议推迟到周五一起上线。",
            "confidence": 0.95,
            "updated_at": None,
        },
        {
            "id": "chunk_1004",
            "meeting_id": meeting_id,
            "speaker": "张三",
            "start": 21.0,
            "end": 28.3,
            "content": "同意，王五你负责跟进支付回调的修复，周四前给我反馈。",
            "confidence": 0.97,
            "updated_at": None,
        },
        {
            "id": "chunk_1005",
            "meeting_id": meeting_id,
            "speaker": "王五",
            "start": 28.5,
            "end": 32.0,
            "content": "好的，我会尽快处理。",
            "confidence": 0.98,
            "updated_at": None,
        },
    ]
    
    filtered = mock_chunks
    if speaker:
        filtered = [c for c in filtered if c["speaker"] == speaker]
    if keyword:
        filtered = [c for c in filtered if keyword in c["content"]]
    
    return {
        "meeting_id": meeting_id,
        "chunks": filtered,
    }


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
