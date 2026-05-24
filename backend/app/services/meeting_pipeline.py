import uuid

from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.job import Job, JobStatus
from app.models.meeting import Meeting, MeetingStatus
from app.models.transcript import TranscriptChunk
from app.services.transcription_service import transcription_service


async def run_transcription_pipeline(meeting_id: uuid.UUID, audio_path: str):
    """
    后台流水线：
    1. 更新 Meeting 状态为 transcribing，Job 状态为 running
    2. 调用 Whisper 转录
    3. 结果批量存入 transcript_chunks 表
    4. 更新 Meeting 状态为 completed，Job 状态为 completed
    5. 失败时记录 error_message 并标记 failed
    """
    logger.info(f"⚡ [Pipeline] 开始处理会议: {meeting_id}")

    db: Session = SessionLocal()

    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.TRANSCRIBING
            db.commit()

        job = db.query(Job).filter(Job.meeting_id == meeting_id).first()
        if job:
            job.status = JobStatus.RUNNING
            db.commit()

        chunks_data = await transcription_service.transcribe_audio(audio_path)

        db_chunks = [
            TranscriptChunk(
                meeting_id=meeting_id,
                start=chunk["start"],
                end=chunk["end"],
                speaker=chunk["speaker"],
                content=chunk["content"],
            )
            for chunk in chunks_data
        ]

        db.add_all(db_chunks)

        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.COMPLETED
            if chunks_data:
                meeting.duration = chunks_data[-1]["end"]

        job = db.query(Job).filter(Job.meeting_id == meeting_id).first()
        if job:
            job.status = JobStatus.COMPLETED

        db.commit()
        logger.info(
            f"✅ [Pipeline] 会议 {meeting_id} 转录并落库成功，共 {len(db_chunks)} 段。"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"❌ [Pipeline] 会议 {meeting_id} 处理失败: {str(e)}")
        try:
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.status = MeetingStatus.FAILED
                meeting.error_message = str(e)[:1000]
                db.commit()

            job = db.query(Job).filter(Job.meeting_id == meeting_id).first()
            if job:
                job.status = JobStatus.FAILED
                db.commit()
        except Exception as inner_e:
            logger.error(f"❌ [Pipeline] 更新失败状态时出错: {str(inner_e)}")
    finally:
        db.close()
