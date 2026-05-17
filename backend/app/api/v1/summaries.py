from datetime import datetime

from fastapi import APIRouter

from app.schemas.summary import SummaryRead, RiskLevel
from app.schemas.common import JobResponse, JobStatus

router = APIRouter()


@router.get("/meetings/{meeting_id}/summary", response_model=SummaryRead)
async def get_meeting_summary(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "summary": {
            "overview": "本次会议主要讨论支付模块延期、接口联调和上线时间调整。",
            "topics": [
                {
                    "title": "支付模块延期",
                    "content": "支付模块由于第三方回调问题延期到周五完成。测试环境已复现问题，王五负责跟进修复。",
                    "source_chunk_ids": ["chunk_1001", "chunk_1002"],
                },
                {
                    "title": "上线时间调整",
                    "content": "原定周三上线计划推迟到周五，等待支付模块修复后一起上线。",
                    "source_chunk_ids": ["chunk_1003"],
                },
                {
                    "title": "任务分配",
                    "content": "王五负责支付回调修复，需在周四前反馈进度。",
                    "source_chunk_ids": ["chunk_1004"],
                },
            ],
            "decisions": [
                {
                    "topic": "上线时间",
                    "decision": "原定周三上线调整为周五上线",
                    "source_chunk_ids": ["chunk_1003"],
                },
                {
                    "topic": "任务负责人",
                    "decision": "王五负责支付回调修复",
                    "source_chunk_ids": ["chunk_1004"],
                },
            ],
            "risks": [
                {
                    "title": "第三方回调稳定性",
                    "level": RiskLevel.HIGH,
                    "description": "若回调问题未解决，会影响支付闭环验证。",
                },
                {
                    "title": "延期影响范围",
                    "level": RiskLevel.MEDIUM,
                    "description": "周五上线可能影响周末用户高峰期体验。",
                },
            ],
            "open_questions": [
                "测试环境是否能在周四前稳定复现回调问题？",
                "周五上线是否需要申请紧急发布流程？",
            ],
        },
        "generated_at": datetime.now(),
    }


@router.post("/meetings/{meeting_id}/summary/generate", response_model=JobResponse, status_code=202)
async def generate_meeting_summary(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "job_id": "job_s7k20d",
        "status": JobStatus.RUNNING,
    }
