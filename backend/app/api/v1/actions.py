from datetime import date, datetime, timedelta

from fastapi import APIRouter

from app.schemas.action_item import (
    ActionItemCreate,
    ActionItemRead,
    ActionItemUpdate,
    ActionStatus,
    Priority,
)
from app.schemas.common import JobResponse, JobStatus

router = APIRouter()


@router.get("/meetings/{meeting_id}/actions")
async def get_meeting_actions(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "items": [
            {
                "id": "act_501",
                "meeting_id": meeting_id,
                "task": "修复支付回调失败问题",
                "owner": "王五",
                "deadline": date.today() + timedelta(days=2),
                "priority": Priority.HIGH,
                "status": ActionStatus.TODO,
                "source_chunk_id": "chunk_1001",
                "updated_at": None,
            },
            {
                "id": "act_502",
                "meeting_id": meeting_id,
                "task": "补充支付回调异常日志",
                "owner": "王五",
                "deadline": date.today() + timedelta(days=1),
                "priority": Priority.MEDIUM,
                "status": ActionStatus.DOING,
                "source_chunk_id": "chunk_1002",
                "updated_at": datetime.now() - timedelta(hours=2),
            },
            {
                "id": "act_503",
                "meeting_id": meeting_id,
                "task": "更新上线计划文档",
                "owner": "张三",
                "deadline": date.today() + timedelta(days=1),
                "priority": Priority.LOW,
                "status": ActionStatus.DONE,
                "source_chunk_id": "chunk_1003",
                "updated_at": datetime.now() - timedelta(hours=4),
            },
        ],
    }


@router.post("/meetings/{meeting_id}/actions", response_model=ActionItemRead, status_code=201)
async def create_action(meeting_id: str, data: ActionItemCreate):
    return {
        "id": "act_504",
        "meeting_id": meeting_id,
        "task": data.task,
        "owner": data.owner,
        "deadline": data.deadline,
        "priority": data.priority,
        "status": ActionStatus.TODO,
        "source_chunk_id": data.source_chunk_id,
        "updated_at": None,
    }


@router.patch("/actions/{action_id}", response_model=ActionItemRead)
async def update_action(action_id: str, data: ActionItemUpdate):
    return {
        "id": action_id,
        "meeting_id": "meet_a7b2c9",
        "task": data.task or "补充支付回调异常日志并同步测试",
        "owner": data.owner or "王五",
        "deadline": data.deadline or date.today() + timedelta(days=3),
        "priority": data.priority or Priority.HIGH,
        "status": data.status or ActionStatus.DOING,
        "source_chunk_id": "chunk_1001",
        "updated_at": datetime.now(),
    }


@router.delete("/actions/{action_id}", status_code=204)
async def delete_action(action_id: str):
    return None


@router.post("/meetings/{meeting_id}/actions/extract", response_model=JobResponse, status_code=202)
async def extract_actions(meeting_id: str):
    return {
        "meeting_id": meeting_id,
        "job_id": "job_a2m9p0",
        "status": JobStatus.RUNNING,
    }


@router.post("/actions/{action_id}/sync/feishu")
async def sync_action_to_feishu(action_id: str, target: str = "task", notify_owner: bool = True):
    return {
        "action_id": action_id,
        "provider": "feishu",
        "external_id": "feishu_task_123",
        "status": "synced",
        "synced_at": datetime.now(),
    }
