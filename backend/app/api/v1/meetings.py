import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.models.job import Job
from app.models.meeting import Meeting, MeetingTag
from app.schemas.meeting import (
    MeetingCreate,
    MeetingRead,
    MeetingUpdate,
    MeetingStatus,
)
from app.schemas.common import PaginationResponse, JobResponse, JobStatus
from app.services.meeting_pipeline import run_transcription_pipeline

router = APIRouter()

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
}

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def _meeting_to_read(meeting: Meeting) -> dict:
    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "status": meeting.status,
        "tags": [t.tag for t in meeting.tags],
        "duration": meeting.duration,
        "audio_url": meeting.audio_url,
        "language": meeting.language,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
    }


@router.post("", response_model=MeetingRead, status_code=201)
async def create_meeting(data: MeetingCreate, db: Session = Depends(get_db)):
    new_meeting = Meeting(
        title=data.title,
        description=data.description,
        status=MeetingStatus.CREATED,
        started_at=data.started_at,
    )
    if data.tags:
        for tag in data.tags:
            new_meeting.tags.append(MeetingTag(tag=tag))
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return _meeting_to_read(new_meeting)


@router.post("/upload", response_model=JobResponse, status_code=202)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    language: str | None = Form(None),
    enable_speaker_diarization: bool = Form(True),
    db: Session = Depends(get_db),
):
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''

    if file_ext not in {'mp3', 'wav', 'm4a'}:
        raise HTTPException(
            status_code=415,
            detail=f"不支持的文件格式 '{file_ext}'，请上传 mp3、wav 或 m4a 格式的音频文件"
        )

    meeting_id = uuid.uuid4()
    audio_path = os.path.join(settings.UPLOAD_DIR, f"{meeting_id}.{file_ext}")

    try:
        with open(audio_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    new_meeting = Meeting(
        id=meeting_id,
        title=title,
        description=description,
        status="uploading",
        audio_url=f"/storage/audio/{meeting_id}.{file_ext}",
        language=language,
        started_at=datetime.now(timezone.utc),
    )
    db.add(new_meeting)

    new_job = Job(
        meeting_id=meeting_id,
        status="pending",
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    background_tasks.add_task(run_transcription_pipeline, meeting_id, audio_path)

    return JobResponse(
        meeting_id=str(meeting_id),
        job_id=str(new_job.id),
        status=JobStatus.RUNNING,
    )


@router.get("", response_model=PaginationResponse[MeetingRead])
async def list_meetings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    keyword: str | None = Query(None),
    status: MeetingStatus | None = Query(None),
    tag: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Meeting).filter(Meeting.deleted_at.is_(None))

    if keyword:
        query = query.filter(Meeting.title.ilike(f"%{keyword}%"))
    if status:
        query = query.filter(Meeting.status == status)
    if tag:
        query = query.join(MeetingTag).filter(MeetingTag.tag == tag)

    total = query.count()
    items = (
        query.order_by(Meeting.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "items": [_meeting_to_read(m) for m in items],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    meeting = db.query(Meeting).filter(Meeting.id == mid, Meeting.deleted_at.is_(None)).first()
    if not meeting:
        raise HTTPException(status_code=404, detail={
            "code": "MEETING_NOT_FOUND",
            "message": "会议不存在",
            "details": {"meeting_id": meeting_id}
        })

    return _meeting_to_read(meeting)


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(meeting_id: str, data: MeetingUpdate, db: Session = Depends(get_db)):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    meeting = db.query(Meeting).filter(Meeting.id == mid, Meeting.deleted_at.is_(None)).first()
    if not meeting:
        raise HTTPException(status_code=404, detail={
            "code": "MEETING_NOT_FOUND",
            "message": "会议不存在",
            "details": {"meeting_id": meeting_id}
        })

    updated_fields = data.model_fields_set

    if "title" in updated_fields and data.title is not None:
        meeting.title = data.title
    if "description" in updated_fields:
        meeting.description = data.description
    if "tags" in updated_fields and data.tags is not None:
        meeting.tags = [MeetingTag(tag=t) for t in data.tags]

    db.commit()
    db.refresh(meeting)

    return _meeting_to_read(meeting)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str, db: Session = Depends(get_db)):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    meeting = db.query(Meeting).filter(Meeting.id == mid, Meeting.deleted_at.is_(None)).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    meeting.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


@router.post("/{meeting_id}/transcribe", response_model=JobResponse, status_code=202)
async def retranscribe_meeting(
    meeting_id: str,
    language: str | None = None,
    enable_speaker_diarization: bool = True,
    db: Session = Depends(get_db),
):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    meeting = db.query(Meeting).filter(Meeting.id == mid, Meeting.deleted_at.is_(None)).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    if not meeting.audio_url:
        raise HTTPException(status_code=400, detail="该会议没有音频文件，无法重新转录")

    new_job = Job(meeting_id=mid, status="pending")
    db.add(new_job)
    meeting.status = MeetingStatus.TRANSCRIBING
    db.commit()
    db.refresh(new_job)

    audio_path = os.path.join(settings.UPLOAD_DIR, meeting.audio_url.split("/")[-1])
    from app.services.meeting_pipeline import run_transcription_pipeline
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_transcription_pipeline, mid, audio_path)

    return JobResponse(
        meeting_id=str(mid),
        job_id=str(new_job.id),
        status=JobStatus.RUNNING,
    )


@router.get("/{meeting_id}/jobs")
async def get_meeting_jobs(meeting_id: str, db: Session = Depends(get_db)):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的会议ID格式")

    meeting = db.query(Meeting).filter(Meeting.id == mid, Meeting.deleted_at.is_(None)).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    jobs = db.query(Job).filter(Job.meeting_id == mid).order_by(Job.created_at.desc()).all()

    return {
        "meeting_id": meeting_id,
        "jobs": [
            {
                "id": str(job.id),
                "type": "transcription",
                "status": job.status,
                "progress": 100 if job.status == "completed" else 0,
                "message": "转录完成" if job.status == "completed" else "处理中",
            }
            for job in jobs
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
