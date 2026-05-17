from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException

from app.schemas.meeting import (
    MeetingCreate,
    MeetingRead,
    MeetingUpdate,
    MeetingStatus,
)
from app.schemas.common import PaginationResponse, JobResponse, JobStatus

router = APIRouter()

# 支持的音频文件类型
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",      # MP3
    "audio/wav",       # WAV
    "audio/x-wav",     # WAV (alternative)
    "audio/mp4",       # M4A
    "audio/x-m4a",     # M4A (alternative)
}


@router.post("", response_model=MeetingRead, status_code=201)
async def create_meeting(data: MeetingCreate):
    return {
        "id": "meet_a7b2c9",
        "title": data.title,
        "description": data.description,
        "status": MeetingStatus.CREATED,
        "tags": data.tags or [],
        "duration": 0.0,
        "audio_url": None,
        "language": None,
        "created_at": datetime.now(),
        "updated_at": None,
    }


@router.post("/upload", response_model=JobResponse, status_code=202)
async def upload_meeting(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    language: str | None = Form(None),
    enable_speaker_diarization: bool = Form(True),
):
    # 验证文件类型（优先检查文件扩展名，防止客户端伪造 Content-Type）
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if file_ext not in {'mp3', 'wav', 'm4a'}:
        raise HTTPException(
            status_code=415,
            detail=f"不支持的文件格式 '{file_ext}'，请上传 mp3、wav 或 m4a 格式的音频文件"
        )
    
    return {
        "meeting_id": "meet_a7b2c9",
        "job_id": "job_9x2k1m",
        "status": JobStatus.RUNNING,
    }


@router.get("", response_model=PaginationResponse[MeetingRead])
async def list_meetings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    keyword: str | None = Query(None),
    status: MeetingStatus | None = Query(None),
    tag: str | None = Query(None),
):
    mock_meetings = [
        {
            "id": "meet_a7b2c9",
            "title": "产品迭代周会",
            "description": "讨论本周产品、研发和测试进度",
            "status": MeetingStatus.COMPLETED,
            "tags": ["产品", "周会"],
            "duration": 3600.5,
            "audio_url": "/storage/audio/meet_a7b2c9.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=1),
            "updated_at": datetime.now(),
        },
        {
            "id": "meet_b8c1d2",
            "title": "支付系统技术评审",
            "description": "支付回调问题排查",
            "status": MeetingStatus.COMPLETED,
            "tags": ["技术", "支付"],
            "duration": 2400.0,
            "audio_url": "/storage/audio/meet_b8c1d2.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=3),
            "updated_at": datetime.now() - timedelta(days=3),
        },
        {
            "id": "meet_c3d4e5",
            "title": "Q3 产品规划会",
            "description": "讨论 Q3 产品路线图",
            "status": MeetingStatus.TRANSCRIBING,
            "tags": ["产品", "规划"],
            "duration": 0.0,
            "audio_url": "/storage/audio/meet_c3d4e5.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(hours=2),
            "updated_at": datetime.now() - timedelta(hours=2),
        },
    ]
    
    filtered = mock_meetings
    if keyword:
        filtered = [m for m in filtered if keyword in m["title"]]
    if status:
        filtered = [m for m in filtered if m["status"] == status]
    if tag:
        filtered = [m for m in filtered if tag in m["tags"]]
    
    start = (page - 1) * size
    end = start + size
    items = filtered[start:end]
    
    return {
        "items": items,
        "total": len(filtered),
        "page": page,
        "size": size,
    }


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: str):
    # Mock 数据：只返回已知的会议ID，其他返回404
    mock_meetings = {
        "meet_a7b2c9": {
            "id": "meet_a7b2c9",
            "title": "产品迭代周会",
            "description": "讨论本周产品、研发和测试进度",
            "status": MeetingStatus.COMPLETED,
            "tags": ["产品", "周会"],
            "duration": 3600.5,
            "audio_url": "/storage/audio/meet_a7b2c9.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=1),
            "updated_at": datetime.now(),
        },
        "meet_b8c1d2": {
            "id": "meet_b8c1d2",
            "title": "支付系统技术评审",
            "description": "支付回调问题排查",
            "status": MeetingStatus.COMPLETED,
            "tags": ["技术", "支付"],
            "duration": 2400.0,
            "audio_url": "/storage/audio/meet_b8c1d2.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=3),
            "updated_at": datetime.now() - timedelta(days=3),
        },
        "meet_c3d4e5": {
            "id": "meet_c3d4e5",
            "title": "Q3 产品规划会",
            "description": "讨论 Q3 产品路线图",
            "status": MeetingStatus.TRANSCRIBING,
            "tags": ["产品", "规划"],
            "duration": 0.0,
            "audio_url": "/storage/audio/meet_c3d4e5.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(hours=2),
            "updated_at": datetime.now() - timedelta(hours=2),
        },
    }

    if meeting_id not in mock_meetings:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={
            "code": "MEETING_NOT_FOUND",
            "message": "会议不存在",
            "details": {"meeting_id": meeting_id}
        })

    return mock_meetings[meeting_id]


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(meeting_id: str, data: MeetingUpdate):
    # 检查会议是否存在
    mock_meetings = {
        "meet_a7b2c9": {
            "id": "meet_a7b2c9",
            "title": "产品迭代周会",
            "description": "讨论本周产品、研发和测试进度",
            "status": MeetingStatus.COMPLETED,
            "tags": ["产品", "周会"],
            "duration": 3600.5,
            "audio_url": "/storage/audio/meet_a7b2c9.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=1),
            "updated_at": datetime.now(),
        },
        "meet_b8c1d2": {
            "id": "meet_b8c1d2",
            "title": "支付系统技术评审",
            "description": "支付回调问题排查",
            "status": MeetingStatus.COMPLETED,
            "tags": ["技术", "支付"],
            "duration": 2400.0,
            "audio_url": "/storage/audio/meet_b8c1d2.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(days=3),
            "updated_at": datetime.now() - timedelta(days=3),
        },
        "meet_c3d4e5": {
            "id": "meet_c3d4e5",
            "title": "Q3 产品规划会",
            "description": "讨论 Q3 产品路线图",
            "status": MeetingStatus.TRANSCRIBING,
            "tags": ["产品", "规划"],
            "duration": 0.0,
            "audio_url": "/storage/audio/meet_c3d4e5.mp3",
            "language": "zh",
            "created_at": datetime.now() - timedelta(hours=2),
            "updated_at": datetime.now() - timedelta(hours=2),
        },
    }

    if meeting_id not in mock_meetings:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={
            "code": "MEETING_NOT_FOUND",
            "message": "会议不存在",
            "details": {"meeting_id": meeting_id}
        })

    original = mock_meetings[meeting_id]
    updated_fields = data.model_fields_set

    # 区分"用户没传"和"用户传了null想清空"
    # model_fields_set 包含用户实际传入的字段名
    # 如果字段在 model_fields_set 中，说明用户显式传了值（包括null）
    # 如果字段不在 model_fields_set 中，说明用户没传，保留原值
    result = dict(original)
    result["updated_at"] = datetime.now()

    if "title" in updated_fields:
        result["title"] = data.title
    if "description" in updated_fields:
        result["description"] = data.description
    if "tags" in updated_fields:
        result["tags"] = data.tags

    return result


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str):
    return None


@router.post("/{meeting_id}/transcribe", response_model=JobResponse, status_code=202)
async def retranscribe_meeting(
    meeting_id: str,
    language: str | None = None,
    enable_speaker_diarization: bool = True,
):
    return {
        "meeting_id": meeting_id,
        "job_id": "job_8m3p2x",
        "status": JobStatus.RUNNING,
    }


@router.get("/{meeting_id}/jobs")
async def get_meeting_jobs(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "jobs": [
            {
                "id": "job_9x2k1m",
                "type": "transcription",
                "status": "completed",
                "progress": 100,
                "message": "转录完成",
            },
            {
                "id": "job_s7k20d",
                "type": "summary",
                "status": "running",
                "progress": 60,
                "message": "正在生成结构化纪要",
            },
        ],
    }


@router.post("/{meeting_id}/agents/run", response_model=JobResponse, status_code=202)
async def run_agents(
    meeting_id: str,
    data: dict,
):
    agents = data.get("agents", ["summary", "action", "memory", "graph", "conflict"])
    return {
        "meeting_id": meeting_id,
        "job_id": "job_agent_001",
        "status": JobStatus.RUNNING,
    }
