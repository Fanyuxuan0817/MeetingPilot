from datetime import datetime, timedelta

from fastapi import APIRouter

from app.schemas.decision import DecisionRead, DecisionConflictRead, ConflictLevel
from app.schemas.common import JobResponse, JobStatus

router = APIRouter()


@router.get("/meetings/{meeting_id}/decisions")
async def get_meeting_decisions(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "items": [
            {
                "id": "dec_301",
                "topic": "上线时间",
                "decision": "支付模块延期到周五上线",
                "version": 2,
                "source_chunk_id": "chunk_1003",
                "created_at": datetime.now() - timedelta(hours=1),
            },
            {
                "id": "dec_302",
                "topic": "任务负责人",
                "decision": "王五负责支付回调修复",
                "version": 1,
                "source_chunk_id": "chunk_1004",
                "created_at": datetime.now() - timedelta(hours=1),
            },
            {
                "id": "dec_303",
                "topic": "测试策略",
                "decision": "周四前完成支付回调回归测试",
                "version": 1,
                "source_chunk_id": "chunk_1005",
                "created_at": datetime.now() - timedelta(hours=1),
            },
        ],
    }


@router.get("/meetings/{meeting_id}/conflicts")
async def get_meeting_conflicts(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "items": [
            {
                "id": "conf_901",
                "topic": "上线时间",
                "current_decision": "周五上线",
                "previous_decision": "周三上线",
                "level": ConflictLevel.MEDIUM,
                "description": "本次会议更新了历史上线时间决策。",
                "current_source_chunk_id": "chunk_1003",
                "previous_meeting_id": "meet_b8c1d2",
            },
        ],
    }


@router.post("/meetings/{meeting_id}/conflicts/detect", response_model=JobResponse, status_code=202)
async def detect_conflicts(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "job_id": "job_f8q1v6",
        "status": JobStatus.RUNNING,
    }
